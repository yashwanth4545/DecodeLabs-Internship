# Project 3 — AI Recommendation Engine

> A live AI-powered recommendation engine with a premium desktop GUI. Searches the web in real time across 7 categories — no API keys, no login required.

<!-- Add project screenshot here -->

---

## Overview

This project combines **real-time web search**, **intelligent content scraping**, and a **modern desktop UI** to build a fully functional recommendation engine. Users can search for Movies, Music, Books, Travel destinations, Food, Sports, and Tech tools — and get live, streaming results with enriched details.

## Features

- **Live Web Search** — Uses DuckDuckGo (no API key, no login needed)
- **7 Categories** — Movies, Music, Books, Travel, Food, Sports, Tech
- **Smart Scrapers** — Category-specific data extraction:
  - 🎵 **Music** → Last.fm track search (actual song names)
  - ✈ **Travel** → Wikipedia tourist attractions (actual place names)
  - 📚 **Books** → Wikipedia book category pages (actual book titles)
  - 🎬 **Movies** → Wikipedia film list pages
  - 🍜 **Food / ⚙ Tech / ⚽ Sports** → Intelligent snippet extraction
- **Streaming Results** — Cards appear one by one as data arrives
- **Premium Desktop UI** — Dark mode, category color themes, hover effects, animated loading
- **Multi-threaded** — UI never freezes during search operations
- **Relevance Scoring** — Multi-signal scoring (keyword hits, phrase match, URL match, position)

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| `customtkinter` | Modern desktop GUI |
| `ddgs` | DuckDuckGo search (no API key) |
| `requests` + `beautifulsoup4` | Web scraping |
| `rich` | Terminal utilities |
| `threading` | Non-blocking UI |

## Project Structure

```
recommendation-engine/
├── recommender/
│   ├── __init__.py
│   ├── search.py          # DuckDuckGo search with streaming
│   ├── filter.py          # Multi-signal relevance scoring
│   ├── catalog_scraper.py # Category-specific scrapers
│   └── display.py         # Rich terminal display
├── app.py                 # Desktop GUI application
├── main.py                # Terminal entry point
└── requirements.txt
```

## How to Run

```bash
cd recommendation-engine
pip install -r requirements.txt
python app.py        # Desktop GUI
# OR
python main.py       # Terminal mode
```

## How It Works

```
User Query + Category
        │
        ▼
DuckDuckGo Search (live)
        │
        ▼
Category-Specific Scraper
   ├── Music    → Last.fm
   ├── Travel   → Wikipedia attractions
   ├── Books    → Wikipedia categories
   └── Others   → Snippet extraction
        │
        ▼
Relevance Scoring & Ranking
        │
        ▼
Stream results → Desktop UI cards
```

---

*Part of DecodeLabs AI Internship — Project 3*
