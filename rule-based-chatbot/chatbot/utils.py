"""
Terminal display utilities — powered by Rich.

Provides banner, message formatting, and session summary using
Rich panels, rules, and styled text so the chatbot looks like
a proper terminal OS dashboard.
"""

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich import box

console = Console()


def print_banner() -> None:
    """Print the Rich startup banner."""
    content = (
        "[bold white]  RULE-BASED AI CHATBOT  [/]\n"
        "[dim]  Powered by Control Flow Logic[/]\n\n"
        "[cyan]  Type [bold]'help'[/] to see available commands.[/]\n"
        "[cyan]  Type [bold]'bye'[/] or [bold]'exit'[/] to end the session.[/]"
    )
    console.print()
    console.print(Panel(content, border_style="cyan", expand=False))
    console.print()


def print_user(text: str) -> None:
    """Print a formatted user input line."""
    label = Text(" You  ›", style="bold green")
    msg   = Text(f" {text}", style="white")
    console.print(label + msg)


def print_bot(text: str) -> None:
    """Print a formatted bot response inside a panel."""
    console.print(Panel(
        f"[cyan]{text}[/]",
        border_style="cyan",
        title="[bold cyan] Bot [/]",
        title_align="left",
        padding=(0, 1),
    ))
    console.print()


def print_session_stats(messages: int, duration_seconds: float) -> None:
    """Print session summary panel."""
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    content = (
        f"[bold cyan]Messages exchanged[/]  {messages}\n"
        f"[bold cyan]Session duration  [/]  {minutes}m {seconds}s"
    )
    console.print(Rule("[dim]Session Summary[/]", style="cyan"))
    console.print(Panel(content, border_style="dim cyan", expand=False))
    console.print()
