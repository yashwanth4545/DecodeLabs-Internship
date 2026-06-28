"""
Intent definitions for the rule-based chatbot.

Each intent has:
    tag       — unique identifier
    patterns  — list of regex strings matched against user input
    responses — list of possible replies (one chosen randomly at runtime)
    terminal  — True signals the engine to end the session after this reply
"""

import random
from typing import TypedDict


class Intent(TypedDict):
    tag: str
    patterns: list[str]
    responses: list[str]
    terminal: bool


INTENTS: list[Intent] = [
    {
        "tag": "greeting",
        "patterns": [
            r"\b(hi|hello|hey|howdy|greetings|sup|what'?s?\s*up)\b",
            r"\bgood\s*(morning|afternoon|evening|day|night)\b",
        ],
        "responses": [
            "Hello! How can I assist you today?",
            "Hey there! What can I do for you?",
            "Hi! Great to see you. What's on your mind?",
            "Greetings! How can I help you?",
            "Hey! I'm here and ready to help.",
        ],
        "terminal": False,
    },
    {
        "tag": "farewell",
        "patterns": [
            r"\b(bye|goodbye|see\s*you|cya|ttyl|farewell|later|peace\s*out)\b",
            r"\b(quit|exit|close|stop|end|done|finish)\b",
        ],
        "responses": [
            "Goodbye! Have a wonderful day!",
            "See you later! Take care of yourself.",
            "Bye! It was a pleasure talking with you.",
            "Farewell! Come back anytime you need help.",
            "Until next time! Stay awesome.",
        ],
        "terminal": True,
    },
    {
        "tag": "thanks",
        "patterns": [
            r"\b(thanks|thank\s*you|ty|thx|thank\s*u|appreciate\s*(it|that|you)?|cheers)\b",
        ],
        "responses": [
            "You're welcome! Anything else I can help with?",
            "Happy to help! Let me know if you need more.",
            "Anytime! What else can I do for you?",
            "My pleasure! Feel free to ask away.",
            "Glad I could assist! Is there anything else?",
        ],
        "terminal": False,
    },
    {
        "tag": "identity",
        "patterns": [
            r"\b(who\s*are\s*you|what\s*are\s*you|your\s*name|are\s*you\s*(a\s*)?(bot|robot|ai|human))\b",
            r"\btell\s*me\s*about\s*yourself\b",
        ],
        "responses": [
            "I'm a rule-based AI chatbot built on pure logic and control flow, no neural networks.",
            "I'm RuleBot, an AI assistant powered entirely by if-else decision trees and pattern matching.",
            "Call me RuleBot. I respond through well-defined rules, not machine learning.",
            "I'm an AI chatbot built with Python. My intelligence comes from carefully crafted rules.",
        ],
        "terminal": False,
    },
    {
        "tag": "capabilities",
        "patterns": [
            r"\b(what\s*can\s*you\s*do|help|commands|capabilities|features|options|how\s*do\s*you\s*work)\b",
        ],
        "responses": [
            (
                "Here's what I can help you with:\n"
                "  * Greet you and have a friendly conversation\n"
                "  * Tell you the current time and date\n"
                "  * Share jokes to brighten your day\n"
                "  * Answer questions about myself\n"
                "  * Give motivational quotes\n\n"
                "  Type 'bye' or 'exit' to end the session."
            ),
        ],
        "terminal": False,
    },
    {
        "tag": "time",
        "patterns": [
            r"\b(what\s*('?s|is)\s*(the\s*)?time|current\s*time|time\s*(right\s*now|is\s*it)?)\b",
            r"\btell\s*me\s*the\s*time\b",
        ],
        "responses": ["__TIME__"],
        "terminal": False,
    },
    {
        "tag": "date",
        "patterns": [
            r"\b(what.*date|today.*date|what.*day\s*(is\s*(it|today))?|current.*date|date.*today)\b",
            r"\bwhat\s*(day|month|year)\s*is\s*(it|today)\b",
        ],
        "responses": ["__DATE__"],
        "terminal": False,
    },
    {
        "tag": "joke",
        "patterns": [
            r"\b(joke|funny|humor|humour|laugh|lol|make\s*me\s*(laugh|smile)|tell\s*(me\s*)?a\s*joke)\b",
        ],
        "responses": [
            "Why do programmers prefer dark mode?\nBecause light attracts bugs!",
            "I told my computer I needed a break...\nNow it won't stop sending me Kit-Kat ads.",
            "Why was the math book sad?\nIt had too many problems.",
            "Why did the developer go broke?\nBecause they used up all their cache.",
            "What do you call a fish without eyes?\nA fsh.",
            "Why don't scientists trust atoms?\nBecause they make up everything.",
            "How many programmers does it take to change a light bulb?\nNone, that's a hardware problem.",
        ],
        "terminal": False,
    },
    {
        "tag": "weather",
        "patterns": [
            r"\b(weather|temperature|forecast|is\s*it\s*(hot|cold|raining|sunny)|will\s*it\s*rain)\b",
        ],
        "responses": [
            "I don't have access to live weather data. Check weather.com or your local weather app!",
            "As a rule-based bot I can't fetch real-time weather. A weather app will help you better!",
        ],
        "terminal": False,
    },
    {
        "tag": "motivation",
        "patterns": [
            r"\b(motivat(e|ion)|inspire|quote|wisdom|advice|encourage)\b",
            r"\b(i('?m|\s*am)\s*(feeling\s*)?(bored|stuck|lost|confused|unmotivated))\b",
        ],
        "responses": [
            '"The only way to do great work is to love what you do." - Steve Jobs',
            '"It does not matter how slowly you go as long as you do not stop." - Confucius',
            '"First, solve the problem. Then, write the code." - John Johnson',
            '"Every expert was once a beginner. Keep going!"',
            '"The best time to plant a tree was 20 years ago. The second best time is now."',
        ],
        "terminal": False,
    },
    {
        "tag": "positive_reaction",
        "patterns": [
            r"\b(great|awesome|amazing|wonderful|fantastic|excellent|brilliant|superb|perfect|nice|cool)\b",
        ],
        "responses": [
            "Glad to hear that!",
            "That's great to know!",
            "Awesome! Keep that energy going!",
            "Wonderful! Anything else I can help with?",
        ],
        "terminal": False,
    },
    {
        "tag": "negative_reaction",
        "patterns": [
            r"\b(sad|unhappy|depressed|terrible|awful|horrible|miserable|frustrated|angry|upset)\b",
            r"\b(not\s*(good|great|okay|ok|well)|feeling\s*(bad|down|low))\b",
        ],
        "responses": [
            "I'm sorry to hear that. I hope things look up for you soon.",
            "That sounds tough. Remember, every storm runs out of rain.",
            "I understand. Take it one step at a time, you've got this.",
            "Hang in there. Even the worst days have an end.",
        ],
        "terminal": False,
    },
    {
        "tag": "affirmation",
        "patterns": [
            r"\b(yes|yeah|yep|yup|sure|absolutely|definitely|of\s*course|correct|right|ok|okay)\b",
        ],
        "responses": [
            "Got it! What else can I help you with?",
            "Understood! Let me know if there's anything more.",
            "Alright! Feel free to ask anything.",
        ],
        "terminal": False,
    },
    {
        "tag": "negation",
        "patterns": [
            r"\b(no|nope|nah|never|not\s*really|no\s*thanks|i('?m|\s*am)\s*good)\b",
        ],
        "responses": [
            "No worries! Just say the word whenever you need me.",
            "Alright! I'm here whenever you need anything.",
            "Understood! Feel free to come back anytime.",
        ],
        "terminal": False,
    },
]

FALLBACK_RESPONSES: list[str] = [
    "I'm not sure I understand that. Could you rephrase?",
    "Hmm, that's outside my current knowledge. Type 'help' to see what I can do.",
    "I didn't quite catch that. Try asking something different!",
    "Interesting! But I'm not programmed to handle that just yet.",
    "My rules don't cover that one. Type 'help' to explore what I know.",
]


def get_fallback() -> str:
    return random.choice(FALLBACK_RESPONSES)
