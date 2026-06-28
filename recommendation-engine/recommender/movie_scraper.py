"""
Movie name extractor — no API key, no login.

Strategy:
  1. Search DuckDuckGo for the query → get list article URLs
  2. Fetch the top Wikipedia / list page
  3. Parse actual movie names from tables and bullet lists
  4. Return clean MovieItem objects with name, year, description

Falls back to raw search results if scraping fails.
"""

import re
import requests
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from .search import search, SearchResult

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 8


@dataclass
class MovieItem:
    name: str
    year: str = ""
    description: str = ""
    director: str = ""
    genre: str = ""
    url: str = ""
    score: int = 80


def _fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a page and return BeautifulSoup. Returns None on error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        pass
    return None


def _clean_name(text: str) -> str:
    """Remove citations, parenthetical notes, and extra whitespace."""
    text = re.sub(r"\[.*?\]", "", text)          # [1], [citation]
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_year(text: str) -> str:
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return m.group(0) if m else ""


def _enrich_from_wikipedia(movie: MovieItem) -> MovieItem:
    """
    Fetch the individual movie's Wikipedia page and extract:
    year, plot description, director, genre.
    Returns the same movie with fields filled in.
    """
    if not movie.url or "wikipedia.org" not in movie.url:
        return movie

    soup = _fetch_page(movie.url)
    if not soup:
        return movie

    # Extract infobox fields
    infobox = soup.find("table", class_=re.compile("infobox"))
    if infobox:
        for row in infobox.find_all("tr"):
            header = row.find("th")
            data   = row.find("td")
            if not header or not data:
                continue
            key = header.get_text(strip=True).lower()
            val = _clean_name(data.get_text(" ", strip=True))

            if "directed" in key or "director" in key:
                movie.director = val[:60]
            elif "release" in key and not movie.year:
                movie.year = _extract_year(val)
            elif "genre" in key:
                movie.genre = val[:60]

    # Year from title or first paragraph if still missing
    if not movie.year:
        title_tag = soup.find("title")
        if title_tag:
            movie.year = _extract_year(title_tag.get_text())

    # Always get plot from first real paragraph (overrides table data)
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 80 and not text.startswith("^") and "may refer" not in text:
            movie.description = text[:220] + ("..." if len(text) > 220 else "")
            break

    return movie


def _scrape_wikipedia_list(url: str) -> list[MovieItem]:
    """Extract movie names from a Wikipedia list-of-films page."""
    soup = _fetch_page(url)
    if not soup:
        return []

    movies: list[MovieItem] = []

    # Strategy 1 — wikitable rows (most Wikipedia film lists)
    for table in soup.find_all("table", class_=re.compile("wikitable")):
        rows = table.find_all("tr")
        for row in rows[1:]:           # skip header
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            # First cell with a link is usually the film title
            for cell in cells[:3]:
                link = cell.find("a")
                if link and link.get_text(strip=True):
                    name = _clean_name(link.get_text())
                    if len(name) > 2 and not name.isdigit():
                        year = _extract_year(row.get_text())
                        # Get description from next cells
                        desc_parts = [c.get_text(strip=True) for c in cells[1:4]]
                        desc = " | ".join(p for p in desc_parts if p)[:120]
                        href = "https://en.wikipedia.org" + link.get("href", "") if link.get("href", "").startswith("/") else link.get("href", "")
                        movies.append(MovieItem(name=name, year=year, description=desc, url=href))
                        break

    # Strategy 2 — bulleted list items (simpler Wikipedia pages)
    if not movies:
        for li in soup.find_all("li"):
            link = li.find("a")
            if link:
                name = _clean_name(link.get_text())
                if 3 < len(name) < 60 and not name.isdigit():
                    year = _extract_year(li.get_text())
                    href = "https://en.wikipedia.org" + link.get("href", "") if link.get("href", "").startswith("/") else ""
                    movies.append(MovieItem(name=name, year=year, url=href))

    return movies[:20]


def _find_best_list_url(results: list[SearchResult]) -> str | None:
    """Pick the most likely movie-list URL from search results."""
    preferred = ["wikipedia.org", "imdb.com", "boxofficeindia", "bollywoodhungama", "filmibeat"]
    for keyword in preferred:
        for r in results:
            if keyword in r.url.lower() and ("list" in r.url.lower() or "film" in r.url.lower() or "movie" in r.url.lower()):
                return r.url
    # fallback — first Wikipedia link
    for r in results:
        if "wikipedia.org" in r.url.lower():
            return r.url
    return None


def _scrape_any_list(url: str) -> list[MovieItem]:
    """Try to scrape movie names from any movie list page."""
    soup = _fetch_page(url)
    if not soup:
        return []

    movies: list[MovieItem] = []

    # Wikipedia wikitable
    for table in soup.find_all("table", class_=re.compile("wikitable")):
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            for cell in cells[:3]:
                link = cell.find("a")
                if link:
                    name = _clean_name(link.get_text())
                    if 3 < len(name) < 70 and not name.isdigit() and name not in {"Main page", "Contents", "Wikipedia"}:
                        year = _extract_year(row.get_text())
                        desc = " | ".join(c.get_text(strip=True) for c in cells[1:4])[:120]
                        href = ("https://en.wikipedia.org" + link.get("href", "")
                                if str(link.get("href", "")).startswith("/") else link.get("href", ""))
                        movies.append(MovieItem(name=name, year=year, description=desc, url=href))
                        break

    # h2/h3 headings (some list sites)
    if not movies:
        for tag in soup.find_all(["h2", "h3", "h4"]):
            text = _clean_name(tag.get_text())
            if 3 < len(text) < 70 and not any(w in text.lower() for w in ["contents", "navigation", "see also", "references", "external"]):
                year = _extract_year(text)
                movies.append(MovieItem(name=text, year=year, score=75))

    return [m for m in movies if m.name not in {"Main page", "Contents", "Current events", "Random article", "About Wikipedia"}][:20]


def search_movies_stream(query: str, max_items: int = 10):
    """
    Generator version — yields each MovieItem immediately after enriching it.
    UI can display each card the moment its details are ready.
    """
    base_movies = search_movies_raw(query, max_items)
    for movie in base_movies:
        enriched = _enrich_from_wikipedia(movie)
        yield enriched


def search_movies_raw(query: str, max_items: int = 10) -> list[MovieItem]:
    """Internal — returns basic movie list without enrichment."""
    attempts = [
        f"{query} films list site:wikipedia.org",
        f"list of {query} wikipedia",
        f"{query} movie names list wikipedia",
    ]
    for attempt in attempts:
        raw = search(attempt, max_results=8)
        for r in raw:
            if "wikipedia.org" in r.url and "Main_Page" not in r.url:
                movies = _scrape_any_list(r.url)
                if len(movies) >= 3:
                    return movies[:max_items]

    # Snippet fallback
    raw = search(f"best {query} list", max_results=12)
    fallback: list[MovieItem] = []
    seen: set[str] = set()
    for r in raw:
        for name in re.findall(r'"([A-Z][^"]{2,50})"', r.snippet):
            name = _clean_name(name)
            if name and name not in seen and len(name) > 3:
                seen.add(name)
                fallback.append(MovieItem(name=name, year=_extract_year(r.snippet),
                                          description=r.snippet[:100], url=r.url, score=75))
        for name in re.findall(r'\d+[\.\)]\s+([A-Z][A-Za-z\s:\-\']{3,50})', r.snippet):
            name = _clean_name(name).rstrip(".,")
            if name and name not in seen:
                seen.add(name)
                fallback.append(MovieItem(name=name, year=_extract_year(r.snippet), url=r.url, score=70))
    return fallback[:max_items]


def search_movies(query: str, max_items: int = 10) -> list[MovieItem]:
    """Blocking version — enriches all movies then returns full list."""
    return list(search_movies_stream(query, max_items))
