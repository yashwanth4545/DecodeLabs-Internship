"""
AI Recommendation Engine — Entry Point
========================================

Project  : AI Recommendation Logic
Language : Python 3.10+
Paradigm : Pattern matching + similarity scoring + live web search

How it works
------------
  1. User types any interest or topic (no commands, just natural text)
  2. App silently searches DuckDuckGo in the background
  3. Results are scored by relevance to the user's query
  4. Top recommendations displayed in a Rich dashboard table

No login. No API key. No errors shown to user.

Usage
-----
  python main.py
"""

import sys
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from recommender import (
    search,
    rank,
    print_banner,
    print_searching,
    print_results,
    print_no_network,
    print_goodbye,
)

console = Console()


def run() -> None:
    print_banner()

    while True:
        # Clean input prompt — feels like an app, not a terminal
        try:
            query = console.input("[bold green] Search ›[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            print_goodbye()
            break

        # Empty input — just re-prompt, no error
        if not query:
            continue

        # Exit commands
        if query.lower() in {"quit", "exit", "bye", "q"}:
            print_goodbye()
            break

        print_searching(query)

        # Background search with animated spinner
        raw_results = []
        with Live(
            Text("  Searching...", style="dim cyan"),
            console=console,
            refresh_per_second=10,
            transient=True,
        ):
            raw_results = search(query, max_results=15)

        # No results = network issue
        if not raw_results:
            print_no_network()
            continue

        # Score and rank results
        ranked = rank(raw_results, query, top_n=6)

        # Display dashboard
        print_results(ranked, query)


if __name__ == "__main__":
    run()
