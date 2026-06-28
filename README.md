# DecodeLabs — AI Internship Projects

> Three AI projects built during the DecodeLabs internship program, demonstrating core concepts in rule-based systems, supervised machine learning, and intelligent recommendation engines.

---

## Projects

### 🤖 Project 1 — Rule-Based AI Chatbot
> `rule-based-chatbot/`

A professional rule-based conversational AI built without any external ML library. Uses regex pattern matching and intent classification to respond to user queries in real time.

**Tech Stack:** Python · Rich · Regex · TypedDict

---

### 📊 Project 2 — Data Classification
> `data-classification/`

Supervised machine learning pipeline that trains and evaluates Decision Tree and K-Nearest Neighbors classifiers on the Iris dataset, with a rich terminal dashboard.

**Tech Stack:** Python · scikit-learn · pandas · numpy · Rich

---

### 🔍 Project 3 — AI Recommendation Engine
> `recommendation-engine/`

A live AI-powered recommendation engine with a premium desktop GUI. Searches the web in real time across Movies, Music, Books, Travel, Food, Sports, and Tech categories — no API keys required.

**Tech Stack:** Python · CustomTkinter · BeautifulSoup · DuckDuckGo Search · Rich

---

## Setup

Each project has its own `requirements.txt`. Install and run independently:

```bash
# Project 1
cd rule-based-chatbot
pip install -r requirements.txt
python main.py

# Project 2
cd data-classification
pip install -r requirements.txt
python main.py

# Project 3
cd recommendation-engine
pip install -r requirements.txt
python app.py
```

---

## Structure

```
DecodeLabs-Internship/
├── rule-based-chatbot/        # P1 — Rule-Based AI Chatbot
├── data-classification/       # P2 — Data Classification
├── recommendation-engine/     # P3 — AI Recommendation Engine
└── README.md
```

---

*Built with Python · Internship @ DecodeLabs*
