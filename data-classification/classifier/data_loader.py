"""
Data loading and exploration module.

Uses the built-in Iris dataset from scikit-learn — no external CSV needed.
Iris is the standard beginner classification dataset:
  - 150 samples, 4 features, 3 classes (Setosa, Versicolor, Virginica)
  - Perfectly balanced, clean, no missing values
"""

import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box

console = Console()


def load_dataset(test_size: float = 0.2, random_state: int = 42) -> tuple:
    """
    Load the Iris dataset and split into train/test sets.

    Returns:
        (X_train, X_test, y_train, y_test, feature_names, target_names)
    """
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name="species")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test, iris.feature_names, iris.target_names


def explore_dataset() -> None:
    """Print a Rich-formatted overview of the Iris dataset."""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)

    # --- Info panel ---
    info = (
        f"[bold cyan]Dataset[/]    Iris (Fisher, 1936)\n"
        f"[bold cyan]Samples[/]    {len(df)}\n"
        f"[bold cyan]Features[/]   {len(iris.feature_names)}\n"
        f"[bold cyan]Classes[/]    {', '.join(iris.target_names)}\n"
        f"[bold cyan]Missing[/]    {df.isnull().sum().sum()} values"
    )
    console.print(Panel(info, title="[bold white]Dataset Overview[/]", border_style="cyan", expand=False))

    # --- Class distribution table ---
    dist_table = Table(title="Class Distribution", box=box.ROUNDED, border_style="cyan", title_style="bold white")
    dist_table.add_column("Class", style="bold yellow")
    dist_table.add_column("Samples", justify="right", style="green")
    dist_table.add_column("Percentage", justify="right", style="cyan")

    for name, count in df["species"].value_counts().sort_index().items():
        pct = f"{count / len(df) * 100:.1f}%"
        dist_table.add_row(str(name), str(count), pct)

    # --- Feature stats table ---
    stats = df.describe()
    feat_table = Table(title="Feature Statistics", box=box.ROUNDED, border_style="cyan", title_style="bold white")
    feat_table.add_column("Feature", style="bold yellow", no_wrap=True)
    feat_table.add_column("Min",  justify="right", style="green")
    feat_table.add_column("Max",  justify="right", style="green")
    feat_table.add_column("Mean", justify="right", style="cyan")
    feat_table.add_column("Std",  justify="right", style="magenta")

    for feat in iris.feature_names:
        feat_table.add_row(
            feat,
            f"{stats[feat]['min']:.2f}",
            f"{stats[feat]['max']:.2f}",
            f"{stats[feat]['mean']:.2f}",
            f"{stats[feat]['std']:.2f}",
        )

    console.print(Columns([dist_table, feat_table]))
    console.print()
