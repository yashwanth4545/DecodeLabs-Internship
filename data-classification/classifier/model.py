"""
Classification model training and evaluation.

Trains two algorithms and lets you compare them side by side:
  1. Decision Tree  — explainable, tree-based, rule-driven
  2. K-Nearest Neighbors (KNN) — distance-based, non-parametric

Both are classic supervised learning algorithms suited for small datasets.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


@dataclass
class EvaluationResult:
    """Holds all evaluation metrics for a single trained model."""
    model_name: str
    accuracy: float
    report: str
    confusion: np.ndarray
    target_names: list[str]
    predictions: np.ndarray


class ClassificationModel:
    """
    Trains and evaluates classification algorithms on the provided data.

    Supports:
        - Decision Tree Classifier
        - K-Nearest Neighbors Classifier

    Usage:
        model = ClassificationModel(X_train, X_test, y_train, y_test, target_names)
        results = model.run_all()
    """

    def __init__(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        target_names: list[str],
    ) -> None:
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.target_names = list(target_names)

        # Algorithms to compare
        self._algorithms: dict = {
            "Decision Tree": DecisionTreeClassifier(
                max_depth=4,
                random_state=42,
            ),
            "K-Nearest Neighbors (k=5)": KNeighborsClassifier(
                n_neighbors=5,
            ),
        }

    def _evaluate(self, name: str, clf) -> EvaluationResult:
        """Train a single classifier and collect metrics."""
        clf.fit(self.X_train, self.y_train)
        preds = clf.predict(self.X_test)

        return EvaluationResult(
            model_name=name,
            accuracy=accuracy_score(self.y_test, preds),
            report=classification_report(
                self.y_test, preds, target_names=self.target_names
            ),
            confusion=confusion_matrix(self.y_test, preds),
            target_names=self.target_names,
            predictions=preds,
        )

    def run_all(self) -> list[EvaluationResult]:
        """Train and evaluate all registered algorithms. Returns results list."""
        results = []
        for name, clf in self._algorithms.items():
            result = self._evaluate(name, clf)
            results.append(result)
        return results
