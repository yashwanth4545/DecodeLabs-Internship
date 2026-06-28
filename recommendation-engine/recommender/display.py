"""
Rich display module.

Renders search results as a beautiful terminal dashboard —
panels, ranked result cards with match bars, and a summary footer.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn
from rich import box

from .filter import RankedResult

console = Console()


def print_banner() -> None:
    content = (
        "[bold white]  AI RECOMMENDATION ENGINE  [/]\n"
        "[dim]  Search anything — movies, books, music, tech, food...[/]\n\n"
        "[cyan]  Type your interest and press Enter.[/]\n"
        "[cyan]  Type [bold]'quit'[/] or [bold]'exit'[/] to close.[/]"
    )
    console.print()
    console.print(Panel(content, border_style="cyan", expand=False))
    console.print()


def print_searching(query: str) -> None:
    console.print(f"\n  [bold cyan]Searching for:[/] [white]{query}[/]\n")


def print_results(results: list[RankedResult], query: str) -> None:
    if not results:
        console.print(Panel(
            "[yellow]No results found. Try a different search query.[/]",
            border_style="yellow",
            expand=False,
        ))
        console.print()
        return

    console.print(Rule(f"[bold cyan]  Top Recommendations for: {query}  [/]", style="cyan"))
    console.print()

    table = Table(
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )
    table.add_column("#",        style="bold white",  width=3,  justify="center")
    table.add_column("Title",    style="bold yellow",  min_width=20)
    table.add_column("Summary",  style="white",        min_width=35)
    table.add_column("Match",    style="green",        width=10, justify="center")
    table.add_column("Link",     style="dim cyan",     min_width=20)

    for i, r in enumerate(results, 1):
        pct = r.match_pct
        bar_filled = int(pct / 10)
        bar = "[green]" + "█" * bar_filled + "[/]" + "[dim]" + "░" * (10 - bar_filled) + "[/]"
        match_cell = f"{bar}\n[bold green]{pct}%[/]"

        table.add_row(
            str(i),
            r.title,
            r.snippet,
            match_cell,
            r.url[:45] + "..." if len(r.url) > 45 else r.url,
        )

    console.print(table)
    console.print()


def print_no_network() -> None:
    console.print(Panel(
        "[red]Could not reach the internet. Check your connection and try again.[/]",
        border_style="red",
        expand=False,
    ))
    console.print()


def print_goodbye() -> None:
    console.print(Panel(
        "[cyan]Thanks for using the AI Recommendation Engine. Goodbye![/]",
        border_style="cyan",
        expand=False,
    ))
    console.print()
