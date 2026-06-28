"""
Advanced relevance scoring engine.

Scoring signals (multi-factor):
  1. Title keyword hits      — weighted 3x (most important)
  2. Snippet keyword hits    — weighted 1x
  3. Exact phrase match      — +30% bonus
  4. URL keyword match       — +10% bonus
  5. Result position weight  — earlier results get slight boost
  6. Stop-word filtering     — common words ignored (the, is, a...)
  7. TF-IDF style penalty    — single-char and 2-char words ignored
"""

import re
import math
from dataclasses import dataclass
from .search import SearchResult

# Words that carry no meaning for scoring
STOP_WORDS = {
    "the", "is", "are", "was", "were", "and", "or", "but", "for",
    "not", "with", "this", "that", "from", "have", "has", "had",
    "you", "your", "they", "their", "will", "can", "how", "what",
    "when", "where", "who", "which", "all", "any", "more", "also",
    "its", "been", "get", "got", "just", "into", "than", "then",
    "each", "both", "our", "about", "would", "could", "should",
}


@dataclass
class RankedResult:
    title: str
    url: str
    snippet: str
    score: float
    match_pct: int
    signals: dict   # breakdown of what matched (for transparency)


def _clean(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower())


def _keywords(query: str) -> list[str]:
    """Extract meaningful keywords — strip stop words and short tokens."""
    tokens = _clean(query).split()
    return [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]


def _hit_count(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


def _exact_phrase_bonus(text: str, query: str) -> float:
    """Reward exact phrase match in title or snippet."""
    phrase = _clean(query)
    return 0.30 if phrase in text else 0.0


def _url_bonus(url: str, keywords: list[str]) -> float:
    url_clean = _clean(url)
    hits = _hit_count(url_clean, keywords)
    return min(hits * 0.05, 0.10)


def _position_weight(position: int) -> float:
    """Earlier search results are typically more relevant."""
    return max(0.10 - (position * 0.007), 0.0)


def score_result(result: SearchResult, keywords: list[str], query: str, position: int) -> RankedResult:
    """
    Compute multi-signal relevance score for a single result.

    Returns a RankedResult with score (0.0–1.0) and signal breakdown.
    """
    title   = _clean(result.title)
    snippet = _clean(result.snippet)

    if not keywords:
        return RankedResult(
            title=result.title, url=result.url, snippet=result.snippet,
            score=0.1, match_pct=10, signals={}
        )

    title_hits   = _hit_count(title, keywords)
    snippet_hits = _hit_count(snippet, keywords)

    # Base score: weighted keyword hits
    max_possible   = len(keywords) * 3 + len(keywords)   # title×3 + snippet×1
    raw_hits_score = (title_hits * 3 + snippet_hits * 1) / max_possible

    # Bonuses
    phrase_bonus   = _exact_phrase_bonus(title + " " + snippet, query)
    url_bonus      = _url_bonus(result.url, keywords)
    position_bonus = _position_weight(position)

    final_score = min(raw_hits_score + phrase_bonus + url_bonus + position_bonus, 1.0)

    signals = {
        "title_hits":   title_hits,
        "snippet_hits": snippet_hits,
        "exact_phrase": phrase_bonus > 0,
        "url_match":    url_bonus > 0,
        "base_score":   round(raw_hits_score * 100),
    }

    snippet_text = result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet

    return RankedResult(
        title=result.title,
        url=result.url,
        snippet=snippet_text,
        score=final_score,
        match_pct=max(int(final_score * 100), 5),
        signals=signals,
    )


def rank(results: list[SearchResult], query: str, top_n: int = 6) -> list[RankedResult]:
    """Score, rank, and return top N results."""
    keywords = _keywords(query)
    ranked = [
        score_result(r, keywords, query, i)
        for i, r in enumerate(results)
    ]
    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:top_n]
