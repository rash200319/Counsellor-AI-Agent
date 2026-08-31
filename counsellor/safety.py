"""Crisis detection and light empathy post-processing."""

from __future__ import annotations

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "hurt myself",
    "self-harm",
    "self harm",
    "want to die",
    "wanna die",
    "take my own life",
    "end it all",
    "no reason to live",
    "better off dead",
]

CRISIS_RESPONSE = (
    "**Immediate Crisis Notice**\n"
    "I'm really concerned for your safety. You deserve help right now. "
    "Please talk to someone you trust or call a hotline immediately.\n\n"
    "**In the US, you can call or text 988.**\n"
    "If you are elsewhere, contact local emergency services or a crisis line."
)

EMPATHY_PHRASES = [
    "i understand how you feel",
    "i'm sorry to hear that",
    "that sounds really tough",
    "i'm here to help",
    "i care about your well-being",
]


def is_crisis(user_input: str) -> bool:
    text = user_input.lower()
    return any(keyword in text for keyword in CRISIS_KEYWORDS)


def crisis_message() -> str:
    return CRISIS_RESPONSE


def apply_empathy_fallback(generated_response: str) -> str:
    text = generated_response.lower()
    is_failure = (
        "i'm not able to respond" in text
        or "i'm having trouble connecting" in text
    )
    shows_empathy = any(phrase in text for phrase in EMPATHY_PHRASES)
    return generated_response
