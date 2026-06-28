# DecodeLabs — AI Internship Projects

> Three production-quality AI projects built during the DecodeLabs internship programme.

---

## Projects

| # | Project | Tech Stack | Run |
|---|---------|-----------|-----|
| 1 | [Rule-Based AI Chatbot](./rule-based-chatbot/) | Python, Regex, Rich | `python main.py` |
| 2 | [Data Classification](./data-classification/) | scikit-learn, pandas, Rich | `python main.py` |
| 3 | [AI Recommendation Engine](./recommendation-engine/) | CustomTkinter, BeautifulSoup, DuckDuckGo | `python app.py` |

---

## Project 1 — Rule-Based AI Chatbot

![Banner](./rule-based-chatbot/banner.png)

A professional terminal-based chatbot built using pure rule-based NLP — no external AI APIs.

**Features:**
- Pattern matching with regex-based intent engine
- Multi-topic responses (greetings, weather, jokes, general knowledge)
- Rich terminal UI with colored panels and banners

**Run:**
```bash
cd rule-based-chatbot
pip install -r requirements.txt
python main.py
```

---

## Project 2 — Data Classification

![Banner](./data-classification/banner.png)

Supervised machine learning pipeline using the Iris dataset — two models compared side by side.

**Features:**
- Decision Tree & K-Nearest Neighbours classifiers
- 95%+ accuracy on test data
- Rich dashboard — confusion matrix, accuracy tables, progress bars

**Run:**
```bash
cd data-classification
pip install -r requirements.txt
python main.py
```

---

## Project 3 — AI Recommendation Engine

![Banner](./recommendation-engine/banner.png)

Desktop application that searches the web and recommends movies, music, books, travel, food, and more — powered by live data, no API keys needed.

**Features:**
- Live web search via DuckDuckGo (no API key)
- Category-specific scrapers: Last.fm (music), Wikipedia attractions (travel), Wikipedia book categories (books)
- "Discover Anything" premium dark-mode desktop UI
- Streaming results — cards appear one by one
- 7 categories: Movies, Music, Books, Travel, Food, Sports, Tech

**Run:**
```bash
cd recommendation-engine
pip install -r requirements.txt
python app.py
```

---

## Tech Stack Overview

```
Python 3.10+
├── rich                 — Terminal UI (P1, P2)
├── scikit-learn         — ML models (P2)
├── pandas / numpy       — Data processing (P2)
├── customtkinter        — Desktop GUI (P3)
├── ddgs                 — DuckDuckGo search (P3)
├── requests             — HTTP scraping (P3)
└── beautifulsoup4       — HTML parsing (P3)
```

---

*Built as part of the DecodeLabs AI Internship Programme.*
