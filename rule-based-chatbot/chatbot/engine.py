"""
Core rule-based matching engine.

Patterns are compiled once at startup for performance.
Intents are evaluated in declaration order — higher-priority intents
should appear first in intents.py.
"""

import re
import random
from datetime import datetime
from dataclasses import dataclass

from .intents import INTENTS, get_fallback


@dataclass
class _CompiledIntent:
    tag: str
    patterns: list[re.Pattern]
    responses: list[str]
    terminal: bool


@dataclass
class MatchResult:
    response: str
    intent_tag: str
    is_terminal: bool
    matched: bool


class ResponseEngine:
    """
    Rule-based intent matching engine.

    1. Compiles all regex patterns at construction time.
    2. On each process() call, scans patterns in order and returns the first match.
    3. Resolves dynamic response tokens (__TIME__, __DATE__).
    4. Returns a MatchResult — no I/O, no side effects.
    """

    def __init__(self) -> None:
        self._intents: list[_CompiledIntent] = []
        self._dynamic_tokens: dict[str, callable] = {
            "__TIME__": lambda: f"The current time is {datetime.now().strftime('%I:%M %p')}.",
            "__DATE__": lambda: f"Today is {datetime.now().strftime('%A, %B %d, %Y')}.",
        }
        self._compile_intents()

    def _compile_intents(self) -> None:
        for intent in INTENTS:
            self._intents.append(_CompiledIntent(
                tag=intent["tag"],
                patterns=[re.compile(p, re.IGNORECASE) for p in intent["patterns"]],
                responses=intent["responses"],
                terminal=intent["terminal"],
            ))

    def process(self, user_input: str) -> MatchResult:
        sanitised = user_input.strip()
        for intent in self._intents:
            for pattern in intent.patterns:
                if pattern.search(sanitised):
                    raw = random.choice(intent.responses)
                    response = self._resolve(raw)
                    return MatchResult(
                        response=response,
                        intent_tag=intent.tag,
                        is_terminal=intent.terminal,
                        matched=True,
                    )
        return MatchResult(
            response=get_fallback(),
            intent_tag="fallback",
            is_terminal=False,
            matched=False,
        )

    def _resolve(self, response: str) -> str:
        resolver = self._dynamic_tokens.get(response)
        return resolver() if resolver else response
