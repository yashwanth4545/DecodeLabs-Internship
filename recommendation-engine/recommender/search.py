"""
Silent background search module — streaming generator.

Yields results one-by-one as they arrive so the UI can
display each card immediately without waiting for all results.
"""

from dataclasses import dataclass
from typing import Generator
from ddgs import DDGS


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def search_stream(query: str, max_results: int = 12) -> Generator[SearchResult, None, None]:
    """
    Generator that yields SearchResult objects one by one as they arrive.

    Usage:
        for result in search_stream(query):
            display(result)   # called immediately per result

    Silently stops on any network / rate-limit error.
    """
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                yield SearchResult(
                    title=r.get("title", "").strip(),
                    url=r.get("href", "").strip(),
                    snippet=r.get("body", "").strip(),
                )
    except Exception:
        return


def search(query: str, max_results: int = 12) -> list[SearchResult]:
    """Blocking version — collects all results then returns list."""
    return list(search_stream(query, max_results=max_results))
