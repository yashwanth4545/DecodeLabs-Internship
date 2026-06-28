"""
Data Classification Using AI — Entry Point
============================================

Project  : Data Classification Using AI
Language : Python 3.10+
Paradigm : Supervised Machine Learning (scikit-learn)

Pipeline
--------
  1. Load the Iris dataset (150 samples, 4 features, 3 classes)
  2. Explore and understand the data
  3. Split into training (80%) and testing (20%) sets
  4. Train: Decision Tree & K-Nearest Neighbors
  5. Evaluate: accuracy, classification report, confusion matrix
  6. Compare both models side by side

Usage
-----
  python main.py
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.rule import Rule
from rich import box

from classifier.data_loader import load_dataset, explore_dataset
from classifier.model import ClassificationModel
from classifier.report import print_report

console = Console()


def print_banner() -> None:
    banner = (
        "[bold cyan]██████╗  █████╗ ████████╗ █████╗      █████╗ ██╗[/]\n"
        "[bold cyan]██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██╔══██╗██║[/]\n"
        "[bold cyan]██║  ██║███████║   ██║   ███████║    ███████║██║[/]\n"
        "[bold cyan]██║  ██║██╔══██║   ██║   ██╔══██║    ██╔══██║██║[/]\n"
        "[bold cyan]██████╔╝██║  ██║   ██║   ██║  ██║    ██║  ██║██║[/]\n"
        "[bold cyan]╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝[/]\n\n"
        "[white]  Data Classification Using AI  [/][dim]| Supervised Learning Pipeline[/]"
    )
    console.print(Panel(banner, border_style="cyan", expand=False))
    console.print()


def run() -> None:
    print_banner()

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, style="cyan", complete_style="green"),
        TextColumn("[green]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:

        # Step 1 — Explore
        t1 = progress.add_task("Exploring dataset...", total=100)
        progress.update(t1, advance=100)
        time.sleep(0.3)

    console.print(Rule("[bold white]  STEP 1 — Dataset Overview  [/]", style="cyan"))
    console.print()
    explore_dataset()

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, style="cyan", complete_style="green"),
        TextColumn("[green]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:

        # Step 2 — Load & split
        t2 = progress.add_task("Splitting dataset (80/20)...", total=100)
        X_train, X_test, y_train, y_test, feature_names, target_names = load_dataset(
            test_size=0.2, random_state=42
        )
        progress.update(t2, advance=100)
        time.sleep(0.3)

    console.print(Rule("[bold white]  STEP 2 — Data Split  [/]", style="cyan"))
    console.print()
    console.print(f"  [bold cyan]Train set[/]  {len(X_train)} samples  [dim](80%)[/]")
    console.print(f"  [bold cyan]Test  set[/]  {len(X_test)} samples  [dim](20%)[/]")
    console.print()

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30, style="cyan", complete_style="green"),
        TextColumn("[green]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:

        # Step 3 — Train models
        t3 = progress.add_task("Training Decision Tree...", total=100)
        progress.update(t3, advance=50)
        time.sleep(0.4)

        model = ClassificationModel(X_train, X_test, y_train, y_test, target_names)

        progress.update(t3, description="Training K-Nearest Neighbors...", advance=50)
        time.sleep(0.4)

        results = model.run_all()

    # Step 4 — Report
    print_report(
        results,
        split_info={
            "train_size": len(X_train),
            "test_size": len(X_test),
            "features": len(feature_names),
            "classes": list(target_names),
        },
    )


if __name__ == "__main__":
    run()
