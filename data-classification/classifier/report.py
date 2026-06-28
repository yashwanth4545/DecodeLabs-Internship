"""
Results display module — powered by Rich.

Renders evaluation results as a full terminal dashboard:
  - Per-model accuracy panel
  - Classification report table
  - Colour-coded confusion matrix
  - Side-by-side model comparison
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich import box

from .model import EvaluationResult

console = Console()

# Colour scheme for confusion matrix cells
_CELL_COLORS = ["green", "yellow", "red", "magenta", "cyan"]


def _confusion_matrix_table(result: EvaluationResult) -> Table:
    """Build a Rich Table for the confusion matrix."""
    names = result.target_names
    table = Table(
        title="Confusion Matrix",
        box=box.ROUNDED,
        border_style="blue",
        title_style="bold white",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Actual \\ Predicted", style="bold yellow", no_wrap=True)
    for name in names:
        table.add_column(name, justify="center")

    for i, row in enumerate(result.confusion):
        cells = []
        for j, val in enumerate(row):
            color = "bold green" if i == j else "bold red"
            cells.append(f"[{color}]{val}[/]")
        table.add_row(names[i], *cells)

    return table


def _classification_report_table(result: EvaluationResult) -> Table:
    """Parse sklearn's classification report string into a Rich Table."""
    table = Table(
        title="Classification Report",
        box=box.ROUNDED,
        border_style="blue",
        title_style="bold white",
        header_style="bold cyan",
    )
    table.add_column("Class",     style="bold yellow")
    table.add_column("Precision", justify="right", style="cyan")
    table.add_column("Recall",    justify="right", style="green")
    table.add_column("F1-Score",  justify="right", style="magenta")
    table.add_column("Support",   justify="right", style="white")

    lines = result.report.strip().splitlines()
    for line in lines[2:]:          # skip header lines
        parts = line.split()
        if len(parts) == 5:         # class rows: name p r f1 support
            table.add_row(parts[0], parts[1], parts[2], parts[3], parts[4])
        elif len(parts) == 6:       # multi-word class names
            table.add_row(f"{parts[0]} {parts[1]}", parts[2], parts[3], parts[4], parts[5])
        elif "accuracy" in line.lower() and len(parts) >= 2:
            table.add_section()
            table.add_row(
                "[bold]accuracy[/]", "", "",
                f"[bold green]{parts[-2]}[/]",
                f"[bold]{parts[-1]}[/]",
            )
        elif "macro" in line or "weighted" in line:
            if len(parts) >= 5:
                table.add_row(
                    f"[dim]{parts[0]} {parts[1]}[/]",
                    f"[dim]{parts[2]}[/]", f"[dim]{parts[3]}[/]",
                    f"[dim]{parts[4]}[/]", f"[dim]{parts[5] if len(parts) > 5 else ''}[/]",
                )

    return table


def print_report(results: list[EvaluationResult], split_info: dict) -> None:
    """Render the full dashboard report."""

    console.print()
    console.print(Rule("[bold cyan]  DATA CLASSIFICATION RESULTS  [/]", style="cyan"))
    console.print()

    # Split info panel
    split_text = (
        f"[bold cyan]Train samples[/]  {split_info['train_size']}\n"
        f"[bold cyan]Test  samples[/]  {split_info['test_size']}\n"
        f"[bold cyan]Features     [/]  {split_info['features']}\n"
        f"[bold cyan]Classes      [/]  {', '.join(split_info['classes'])}"
    )
    console.print(Panel(split_text, title="[bold white]Pipeline Configuration[/]", border_style="cyan", expand=False))
    console.print()

    # Per-model results
    for result in results:
        acc_pct = result.accuracy * 100
        acc_color = "bold green" if acc_pct >= 95 else "bold yellow" if acc_pct >= 80 else "bold red"

        console.print(Rule(f"[bold white]  {result.model_name}  [/]", style="white"))
        console.print()
        console.print(Panel(
            f"[{acc_color}]{acc_pct:.2f}%[/]",
            title="[bold white]Accuracy[/]",
            border_style="green" if acc_pct >= 95 else "yellow",
            expand=False,
        ))
        console.print()
        console.print(Columns([_classification_report_table(result), _confusion_matrix_table(result)]))
        console.print()

    # Final comparison
    console.print(Rule("[bold cyan]  MODEL COMPARISON  [/]", style="cyan"))
    console.print()

    comp_table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", show_header=True)
    comp_table.add_column("Model",    style="bold yellow")
    comp_table.add_column("Accuracy", justify="center")
    comp_table.add_column("Result",   justify="center")

    best = max(results, key=lambda r: r.accuracy)
    for r in results:
        is_best = r.model_name == best.model_name
        acc_str = f"[bold green]{r.accuracy * 100:.2f}%[/]" if is_best else f"{r.accuracy * 100:.2f}%"
        badge = "[bold green]BEST[/]" if is_best else "[dim]--[/]"
        comp_table.add_row(r.model_name, acc_str, badge)

    console.print(comp_table)
    console.print()
