"""
Universal catalog scraper — works for any category.

Each category has:
  - A search strategy (Wikipedia query pattern)
  - Fields to extract (title, author, year, description, etc.)
  - An infobox key map (what Wikipedia calls each field)

Supports: Movies, Books, Music, Food, Travel, Sports, Tech
"""

import re
import requests
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from .search import search

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}
TIMEOUT = 8

SKIP_NAMES = {
    "Main page", "Contents", "Current events", "Random article",
    "About Wikipedia", "Contact us", "Help", "Donate",
    "Learn to edit", "Community portal", "Recent changes",
    "Upload file", "Special pages", "Permanent link", "Page information",
    "Cite this page", "Get shortened URL", "Wikipedia", "Wikimedia",
    "Edit", "History", "Talk", "View source", "Log in", "Create account",
    "Move", "Watch", "Read", "Search", "Navigation", "Tools", "Print",
    "Languages", "Appearance", "In other projects", "From Wikipedia",
    "Download as PDF", "Printable version", "See also", "References",
    "External links", "Further reading", "Notes", "Bibliography",
    "Introduction", "Overview", "Background", "Summary", "Conclusion",
    "Top", "(Top)", "Jump to", "Skip to",
}

NAV_PATTERNS = re.compile(
    r"^(download|print|view|edit|talk|help|log|create|sign|jump|skip|see also|"
    r"complete guide|top \d|best \d|\d+ best|\d+ top|click here|read more)",
    re.IGNORECASE,
)

# Categories that work better with snippet extraction than page scraping
# Categories that use web search results directly (reliable, always works)
WEB_SEARCH_CATEGORIES = {"books", "travel", "food", "tech"}
# Categories that use Wikipedia table scraping (structured data available)
WIKI_TABLE_CATEGORIES  = {"movies", "music", "sports"}


# ── Universal Item ─────────────────────────────────────────────────────────

@dataclass
class CatalogItem:
    name: str
    category: str           # movies / books / music / food / travel / sports / tech
    subtitle: str  = ""     # author / artist / director / chef / country
    year: str      = ""
    genre: str     = ""
    description: str = ""
    url: str       = ""
    score: int     = 80


# ── Category config ────────────────────────────────────────────────────────

CATEGORY_CONFIG = {
    "movies": {
        "wiki_queries": [
            "{query} films list site:wikipedia.org",
            "list of {query} films wikipedia",
        ],
        "subtitle_keys": ["directed by", "director"],
        "subtitle_label": "Director",
        "year_keys":      ["release", "released"],
        "genre_keys":     ["genre"],
        "score":          85,
    },
    "books": {
        "wiki_queries": [
            "list of {query} novels site:en.wikipedia.org/wiki/List",
            "{query} fiction novels list wikipedia",
            "best {query} books goodreads list",
        ],
        "subtitle_keys": ["author", "written by"],
        "subtitle_label": "Author",
        "year_keys":      ["published", "publication", "release"],
        "genre_keys":     ["genre"],
        "score":          82,
    },
    "music": {
        "wiki_queries": [
            "{query} discography songs list site:wikipedia.org",
            "list of songs by {query} wikipedia",
            "{query} singles albums wikipedia discography",
        ],
        "subtitle_keys": ["artist", "performed by", "singer", "band", "written by"],
        "subtitle_label": "Artist",
        "year_keys":      ["released", "release date", "recorded"],
        "genre_keys":     ["genre"],
        "score":          80,
    },
    "food": {
        "wiki_queries": [
            "list of {query} dishes site:en.wikipedia.org/wiki/List",
            "{query} cuisine food items wikipedia list",
            "popular {query} recipes dishes list",
        ],
        "subtitle_keys": ["origin", "place of origin", "country of origin", "region"],
        "subtitle_label": "Origin",
        "year_keys":      [],
        "genre_keys":     ["course", "type"],
        "score":          78,
    },
    "travel": {
        "wiki_queries": [
            "list of tourist attractions {query} site:en.wikipedia.org/wiki/List",
            "{query} landmarks monuments wikipedia list",
            "top places visit {query} wikipedia",
        ],
        "subtitle_keys": ["country", "location", "state", "region"],
        "subtitle_label": "Location",
        "year_keys":      ["established", "founded"],
        "genre_keys":     ["type"],
        "score":          80,
    },
    "sports": {
        "wiki_queries": [
            "{query} players teams list site:wikipedia.org",
            "list of {query} athletes wikipedia",
            "{query} sports records wikipedia",
        ],
        "subtitle_keys": ["nationality", "country", "team", "club"],
        "subtitle_label": "Team/Country",
        "year_keys":      ["born", "active"],
        "genre_keys":     ["sport", "position"],
        "score":          80,
    },
    "tech": {
        "wiki_queries": [
            "comparison of {query} wikipedia",
            "list of {query} wikipedia",
            "{query} software list wikipedia",
        ],
        "subtitle_keys": ["developer", "developed by", "author", "company", "manufacturer"],
        "subtitle_label": "Developer",
        "year_keys":      ["initial release", "released", "launch"],
        "genre_keys":     ["type", "genre", "platform"],
        "score":          82,
    },
}


# ── Helpers ────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    text = re.sub(r"\[.*?\]", "", text)          # remove citations [1]
    text = re.sub(r"^\d+\s+", "", text)          # strip leading "1 " prefix
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_year(text: str) -> str:
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return m.group(0) if m else ""


def _fetch(url: str) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
    except Exception:
        pass
    return None


def _is_valid_name(name: str) -> bool:
    """Return True only if the name looks like a real item, not nav/UI text."""
    if not name or len(name) < 4:
        return False
    if name in SKIP_NAMES:
        return False
    if NAV_PATTERNS.match(name):
        return False
    if any(name.startswith(p) for p in ("Wikipedia:", "Help:", "File:", "Talk:", "Category:")):
        return False
    if re.match(r"^\d+$", name):
        return False
    if re.match(r"^\d+\s+\d", name):       # "1 1st arrondissement" type
        return False
    if "github.com" in name.lower() or "http" in name.lower():
        return False
    if " - " in name and ("github" in name.lower() or "www." in name.lower()):
        return False
    word_count = len(name.split())
    if word_count > 8:
        return False
    return True


def _enrich(item: CatalogItem, config: dict) -> CatalogItem:
    """Fetch item's Wikipedia page and fill subtitle, year, genre, description."""
    if not item.url or "wikipedia.org" not in item.url:
        return item

    soup = _fetch(item.url)
    if not soup:
        return item

    infobox = soup.find("table", class_=re.compile("infobox"))
    if infobox:
        for row in infobox.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue
            key = th.get_text(strip=True).lower()
            val = _clean(td.get_text(" ", strip=True))

            if not item.subtitle:
                if any(k in key for k in config["subtitle_keys"]):
                    item.subtitle = val[:60]

            if not item.year and config["year_keys"]:
                if any(k in key for k in config["year_keys"]):
                    item.year = _extract_year(val) or val[:20]

            if not item.genre and config["genre_keys"]:
                if any(k in key for k in config["genre_keys"]):
                    item.genre = val[:50]

    # Plot / description from first real paragraph
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 80 and "may refer" not in text:
            item.description = text[:220] + ("..." if len(text) > 220 else "")
            break

    return item


def _scrape_list_page(url: str, category: str) -> list[CatalogItem]:
    """Scrape a Wikipedia list page and return CatalogItems."""
    soup = _fetch(url)
    if not soup:
        return []

    items: list[CatalogItem] = []
    config = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG["movies"])

    # wikitable rows
    for table in soup.find_all("table", class_=re.compile("wikitable")):
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            for cell in cells[:3]:
                link = cell.find("a")
                if link:
                    name = _clean(link.get_text())
                    if len(name) > 2 and not name.isdigit() and name not in SKIP_NAMES:
                        year = _extract_year(row.get_text())
                        href = (
                            "https://en.wikipedia.org" + link["href"]
                            if str(link.get("href", "")).startswith("/") else link.get("href", "")
                        )
                        items.append(CatalogItem(
                            name=name, category=category,
                            year=year, url=href,
                            score=config["score"],
                        ))
                        break

    # Bullet list fallback
    if not items:
        for li in soup.find_all("li"):
            link = li.find("a")
            if link:
                name = _clean(link.get_text())
                if 3 < len(name) < 70 and name not in SKIP_NAMES:
                    href = (
                        "https://en.wikipedia.org" + link["href"]
                        if str(link.get("href", "")).startswith("/") else ""
                    )
                    items.append(CatalogItem(
                        name=name, category=category,
                        year=_extract_year(li.get_text()),
                        url=href, score=config["score"],
                    ))

    filtered = [
        i for i in items
        if _is_valid_name(i.name)
    ]
    return filtered[:20]


# ── Public API ─────────────────────────────────────────────────────────────

def _is_ascii_name(name: str) -> bool:
    """Reject names with non-ASCII characters (foreign language nav links)."""
    try:
        name.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


_BOOKS_GENRE_MAP = {
    "mystery":          "Category:Mystery_novels",
    "thriller":         "Category:Thriller_novels",
    "crime":            "Category:Crime_novels",
    "horror":           "Category:Horror_novels",
    "romance":          "Category:Romance_novels",
    "fantasy":          "Category:Fantasy_novels",
    "science fiction":  "Category:Science_fiction_novels",
    "sci-fi":           "Category:Science_fiction_novels",
    "historical":       "Category:Historical_novels",
    "adventure":        "Category:Adventure_novels",
}

_WIKI_NAV_EXACT = {
    "Main page", "Thrillers", "Mystery", "Romance", "Fantasy", "Horror",
    "Novels", "Fiction", "Books", "Literature", "Science fiction",
    "Adventure", "Category", "Crime fiction", "v", "t", "e",
    "France portal", "Tourism in France", "Tourism", "Portal",
}


_CATEGORY_ITEM_SKIP = re.compile(
    r"^(list of|lists of|comparison of|timeline of|index of|"
    r"this list|category:|template:|landmarks in|tourism in|"
    r"gentleman thief|lady thief|stock character|trope)",
    re.IGNORECASE,
)


def _scrape_wiki_category_items(category_path: str, item_category: str,
                                max_items: int) -> list[CatalogItem]:
    """Scrape a Wikipedia Category page using the mw-pages div (clean article list)."""
    url  = f"https://en.wikipedia.org/wiki/{category_path}"
    soup = _fetch(url)
    if not soup:
        return []

    cat_div = soup.find("div", id="mw-pages") or soup.find("div", class_="mw-category")
    if not cat_div:
        return []

    items: list[CatalogItem] = []
    seen: set[str] = set()

    for a in cat_div.find_all("a"):
        href = a.get("href", "")
        # Skip list/meta pages
        if not href.startswith("/wiki/") or ":" in href:
            continue
        if "/wiki/List_of" in href or "/wiki/Comparison_of" in href:
            continue
        name = _clean(a.get_text())
        if (name and len(name) > 4 and name not in seen
                and _is_valid_name(name) and _is_ascii_name(name)
                and not _CATEGORY_ITEM_SKIP.match(name)):
            seen.add(name)
            items.append(CatalogItem(
                name=name, category=item_category,
                url="https://en.wikipedia.org" + href, score=88,
            ))
        if len(items) >= max_items:
            break

    return items


_BOOK_CONCEPT_SKIP = re.compile(
    r"^(romance|thriller|mystery|crime|horror|fantasy|science fiction|historical|adventure|"
    r"spy|novel|novella|fiction|genre|cover|trope|convention|archetype)\s*(novel|fiction|genre)?$",
    re.IGNORECASE,
)
_BOOK_SUFFIX_SKIP = re.compile(r"\s+cover$|\s+trope$|\s+archetype$", re.IGNORECASE)


def _scrape_wiki_books_category(query: str, max_items: int) -> list[CatalogItem]:
    """Scrape Wikipedia category page for actual book titles."""
    query_lower = query.lower()
    category_path = "Category:Thriller_novels"           # default
    for keyword, cat in _BOOKS_GENRE_MAP.items():
        if keyword in query_lower:
            category_path = cat
            break

    raw = _scrape_wiki_category_items(category_path, "books", max_items + 5)

    # Filter out genre-concept articles (e.g. "Romance novel", "Clinch cover")
    filtered = [
        item for item in raw
        if not _BOOK_CONCEPT_SKIP.match(item.name)
        and not _BOOK_SUFFIX_SKIP.search(item.name)
    ]
    return filtered[:max_items]


def _scrape_lastfm(query: str, max_items: int) -> list[CatalogItem]:
    """Scrape Last.fm for actual track/song names."""
    search_q = query.replace(" songs", "").replace(" music", "").replace(" tracks", "").strip()
    url = f"https://www.last.fm/search/tracks?q={search_q.replace(' ', '+')}"
    soup = _fetch(url)
    if not soup:
        return []

    items: list[CatalogItem] = []
    seen: set[str] = set()

    for td in soup.find_all("td", class_="chartlist-name"):
        link = td.find("a")
        if link:
            name = _clean(link.get_text())
            if name and name not in seen and _is_valid_name(name) and _is_ascii_name(name):
                seen.add(name)
                items.append(CatalogItem(
                    name=name, category="music",
                    url="https://www.last.fm" + link.get("href", ""),
                    score=90,
                ))
        if len(items) >= max_items:
            break

    return items


def _scrape_wiki_attractions(query: str, max_items: int) -> list[CatalogItem]:
    """Scrape Wikipedia Category:Tourist_attractions_in_{location} for actual places."""
    # Strip generic travel words to get the location name
    for phrase in ("tourist places", "tourist attractions", "places to visit",
                   "things to do", "best places", "top places", "beach places",
                   "beaches", "sightseeing"):
        query = re.sub(re.escape(phrase), "", query, flags=re.IGNORECASE)

    location = query.strip().title()
    slug     = location.replace(" ", "_")

    # Try Category:Tourist_attractions_in_{slug} first (most accurate)
    items = _scrape_wiki_category_items(
        f"Category:Tourist_attractions_in_{slug}", "travel", max_items
    )
    if items:
        for item in items:
            item.score = 85
        return items

    # Try List_of_tourist_attractions_in_{slug}
    list_url = f"https://en.wikipedia.org/wiki/List_of_tourist_attractions_in_{slug}"
    soup = _fetch(list_url)
    if soup and not (soup.find("div", class_="noarticletext") or soup.find("div", id="noarticletext")):
        cat_items: list[CatalogItem] = []
        seen: set[str] = set()
        toc     = soup.find("div", id="toc")
        content = soup.find("div", id="mw-content-text")
        if content:
            for li in content.find_all("li"):
                if toc and toc in li.parents:
                    continue
                link = li.find("a")
                if not link or not link.get("href", "").startswith("/wiki/"):
                    continue
                name = _clean(link.get_text())
                if (name and name not in seen and name not in _WIKI_NAV_EXACT
                        and _is_valid_name(name) and _is_ascii_name(name)
                        and not re.match(
                            r"^(list|category|template|portal|tourism|history|festivals)",
                            name, re.IGNORECASE
                        )):
                    seen.add(name)
                    cat_items.append(CatalogItem(
                        name=name, category="travel",
                        url="https://en.wikipedia.org" + link.get("href", ""),
                        score=85,
                    ))
                if len(cat_items) >= max_items:
                    break
        if cat_items:
            return cat_items

    # Search fallback
    results = search(f"tourist attractions {query} site:en.wikipedia.org", max_results=5)
    for r in results:
        if "wikipedia.org" not in r.url:
            continue
        if "Category:Tourist_attractions_in" in r.url:
            cat_path = r.url.split("/wiki/")[-1]
            found = _scrape_wiki_category_items(cat_path, "travel", max_items)
            if found:
                return found
        if "List_of_tourist_attractions_in" in r.url:
            found = _scrape_wiki_attractions.__wrapped__ if hasattr(
                _scrape_wiki_attractions, "__wrapped__"
            ) else None
            if found:
                return found

    return []


def _snippet_extract(query: str, cat: str, max_items: int) -> list[CatalogItem]:
    """Extract item names directly from search snippets — clean and reliable."""
    results = search(f"best {query} top list", max_results=15)
    seen: set[str] = set()
    items: list[CatalogItem] = []
    config = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["movies"])

    for r in results:
        combined_text = r.title + " " + r.snippet

        # Quoted names: "The Silent Patient", "Eiffel Tower"
        for name in re.findall(r'"([A-Z][^"]{2,55})"', combined_text):
            name = _clean(name)
            if name and name not in seen and _is_valid_name(name) and _is_ascii_name(name):
                seen.add(name)
                items.append(CatalogItem(
                    name=name, category=cat,
                    year=_extract_year(combined_text),
                    description=r.snippet[:140],
                    url=r.url, score=config["score"],
                ))

        # Numbered list: "1. Vada Pav 2. Bhel Puri"
        # Non-greedy, stop before next number marker to avoid merging items
        for m in re.finditer(
            r'\d+[\.\)]\s+([A-Z][A-Za-z0-9\s\'\-&]{2,45}?)(?=\s*\d+[\.\)]|\s*[;·|•]|$)',
            combined_text,
        ):
            name = _clean(m.group(1)).rstrip(" .,:")
            if name and name not in seen and _is_valid_name(name) and _is_ascii_name(name):
                seen.add(name)
                items.append(CatalogItem(
                    name=name, category=cat,
                    year=_extract_year(combined_text),
                    url=r.url, score=config["score"] - 5,
                ))

        # Title itself if it looks like a real item (not "Top 10 Best...")
        title = _clean(r.title)
        if (title and title not in seen and _is_valid_name(title) and _is_ascii_name(title)
                and not re.match(r"^\d+|^top|^best|^list|^how", title, re.IGNORECASE)):
            seen.add(title)
            items.append(CatalogItem(
                name=title, category=cat,
                year=_extract_year(r.snippet),
                description=r.snippet[:140],
                url=r.url, score=config["score"] - 10,
            ))

    return items[:max_items]


def catalog_search_stream(query: str, category: str = "movies", max_items: int = 10):
    """
    Generator — yields CatalogItem one by one as each is enriched.

    Strategy per category:
      Movies / Music / Sports  → Wikipedia wikitable scraping (structured)
      Books / Food / Travel / Tech → Live web search results (always reliable)
    """
    cat = category.lower()
    config = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["movies"])

    # ── Music: Last.fm track search (most reliable) ──────────────────────────
    if cat == "music":
        items = _scrape_lastfm(query, max_items)
        if not items:
            items = _snippet_extract(query, cat, max_items)
        for item in items:
            yield item
        return

    # ── Books: Wikipedia category pages (actual book titles) ─────────────────
    if cat == "books":
        items = _scrape_wiki_books_category(query, max_items)
        if not items:
            items = _snippet_extract(query, cat, max_items)
        for item in items:
            yield _enrich(item, config)
        return

    # ── Travel: Wikipedia list of tourist attractions ─────────────────────────
    if cat == "travel":
        items = _scrape_wiki_attractions(query, max_items)
        if not items:
            items = _snippet_extract(query, cat, max_items)
        for item in items:
            yield _enrich(item, config)
        return

    # ── Food / Tech: snippet extraction ──────────────────────────────────────
    if cat in ("food", "tech"):
        items = _snippet_extract(query, cat, max_items)
        for item in items:
            yield item
        return

    # ── Wikipedia-table categories: structured names ──────────────────────────
    raw_items: list[CatalogItem] = []

    for pattern in config["wiki_queries"]:
        search_query = pattern.format(query=query)
        results = search(search_query, max_results=8)
        for r in results:
            if "wikipedia.org" in r.url and "Main_Page" not in r.url:
                found = _scrape_list_page(r.url, cat)
                if len(found) >= 3:
                    raw_items = found[:max_items]
                    break
        if raw_items:
            break

    # Fallback to snippet extraction if Wikipedia scraping fails
    if not raw_items:
        raw_items = _snippet_extract(query, cat, max_items)

    for item in raw_items:
        yield _enrich(item, config)
