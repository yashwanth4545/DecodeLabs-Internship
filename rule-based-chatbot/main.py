"""
Rule-Based AI Chatbot — Entry Point
=====================================

Project  : Rule-Based AI Chatbot
Language : Python 3.10+
Paradigm : Control flow + if-else decision logic (no ML/neural networks)

Architecture
------------
  main.py              — Conversation loop and I/O handling
  chatbot/engine.py    — Pattern matching and response resolution
  chatbot/intents.py   — All intent definitions (patterns + responses)
  chatbot/utils.py     — Rich terminal dashboard UI

Usage
-----
  python main.py
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console

from chatbot import ResponseEngine
from chatbot.utils import print_banner, print_bot, print_user, print_session_stats

console = Console()


def run() -> None:
    """Main conversation loop."""
    engine = ResponseEngine()
    print_banner()

    message_count: int = 0
    session_start: float = time.time()

    while True:
        try:
            raw_input = console.input("[bold green] You  ›[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print()
            raw_input = "bye"

        if not raw_input:
            continue

        message_count += 1
        result = engine.process(raw_input)

        print_bot(result.response)

        if result.is_terminal:
            duration = time.time() - session_start
            print_session_stats(message_count, duration)
            break


if __name__ == "__main__":
    run()
