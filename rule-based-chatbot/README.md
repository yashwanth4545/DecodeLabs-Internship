# Project 1 — Rule-Based AI Chatbot

> A professional rule-based conversational AI that responds to user queries using regex pattern matching and intent classification — built without any ML library.

<!-- Add project screenshot here -->

---

## Overview

This chatbot demonstrates how intelligent-seeming conversations can be built using deterministic rules. It identifies the user's **intent** from their message and maps it to a relevant response — all using Python's control flow and regular expressions.

## Features

- **Intent Engine** — Matches user input against 15+ defined intents (greetings, help, weather, jokes, etc.)
- **Pattern Matching** — Uses compiled regex for fast, accurate pattern recognition
- **Rich Terminal UI** — Colorful banners, panels, and formatted output using the `rich` library
- **Fallback Handling** — Gracefully handles unrecognized inputs

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| `rich` | Terminal UI (banners, colored text, panels) |
| `re` (regex) | Pattern matching |
| `TypedDict` | Structured intent definitions |

## Project Structure

```
rule-based-chatbot/
├── chatbot/
│   ├── __init__.py
│   ├── engine.py       # Core matching & response logic
│   ├── intents.py      # Intent definitions with patterns & responses
│   └── utils.py        # Rich terminal display utilities
├── main.py             # Entry point
└── requirements.txt
```

## How to Run

```bash
cd rule-based-chatbot
pip install -r requirements.txt
python main.py
```

## How It Works

```
User Input
    │
    ▼
Preprocess (lowercase, strip)
    │
    ▼
Match against intent patterns (regex)
    │
    ▼
Select random response from matched intent
    │
    ▼
Display formatted response
```

---

*Part of DecodeLabs AI Internship — Project 1*
