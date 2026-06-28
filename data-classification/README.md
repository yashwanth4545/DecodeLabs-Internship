# Project 2 — Data Classification

> A supervised machine learning pipeline that trains, evaluates, and compares multiple classification models on the Iris dataset — displayed in a rich terminal dashboard.

<!-- Add project screenshot here -->

---

## Overview

This project demonstrates the full **supervised learning workflow**: loading data, preprocessing, training multiple models, evaluating performance, and presenting results in a professional dashboard. Two classifiers are trained and compared side-by-side.

## Features

- **Two ML Models** — Decision Tree and K-Nearest Neighbors (KNN)
- **Full ML Pipeline** — Data loading → splitting → training → evaluation → reporting
- **Rich Dashboard** — Accuracy tables, classification reports, confusion matrix display
- **Progress Bars** — Animated pipeline execution with `rich` progress indicators
- **Dataset Insights** — Feature statistics, class distribution, data overview panels

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| `scikit-learn` | ML models & evaluation metrics |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `rich` | Terminal dashboard (tables, panels, progress bars) |

## Project Structure

```
data-classification/
├── classifier/
│   ├── __init__.py
│   ├── data_loader.py   # Iris dataset loading & splitting
│   ├── model.py         # Decision Tree & KNN training/evaluation
│   └── report.py        # Rich dashboard output
├── main.py              # Entry point — pipeline orchestration
└── requirements.txt
```

## How to Run

```bash
cd data-classification
pip install -r requirements.txt
python main.py
```

## Results

The pipeline outputs:
- Train/test split summary
- Model accuracy scores
- Full classification report (precision, recall, F1-score)
- Side-by-side model comparison

## Dataset

**Iris Dataset** — 150 samples, 4 features (sepal/petal length & width), 3 classes (Setosa, Versicolor, Virginica).

---

*Part of DecodeLabs AI Internship — Project 2*
