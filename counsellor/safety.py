"""Input/output safety guardrails for the counsellor agent."""

from __future__ import annotations

import re

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

SCOPE_RESPONSE = (
    "I'm designed to support conversations about feelings, stress, relationships, "
    "and mental well-being. I can't help with that request, but I'm happy to talk "
    "through something you're experiencing."
)

PRIVACY_RESPONSE = (
    "I can't provide hidden instructions, system prompts, source code, API keys, "
    "or other private implementation details. I can explain how I support your "
    "mental well-being or help you think through a personal concern."
)

# These are intentionally high-confidence indicators. The guardrail should not
# reject ordinary counselling messages merely because they contain a common word.
SENSITIVE_PATTERNS = (
    r"\b(system|developer|hidden|秘密)\s+prompt\b",
    r"\b(system|developer)\s+instructions?\b",
    r"\b(ignore|disregard|reveal|show|print|泄露)\b.{0,50}\b(prompt|instructions?|rules?)\b",
    r"\b(source\s+code|codebase|repository|repo|\.env|environment\s+variables?)\b",
    r"\b(api|access|secret|private|auth|bearer)\s*(key|token|credential)s?\b",
    r"\b(show|give|tell|reveal|print|dump)\b.{0,50}\b(your|the)\b.{0,30}\b(prompt|instructions?|tools?|code)\b",
    r"\b(your|the|original|full|complete)\s+(system\s+)?prompt\b",
)

OFF_TOPIC_PATTERNS = (
    r"\b(linked\s+list|binary\s+tree|algorithm|leetcode|debug|program|python|javascript|java|sql)\b",
    r"\b(write|generate|fix|review|explain)\b.{0,50}\b(code|function|class|script|query)\b",
    r"\b(weather|recipe|football|stock price|travel itinerary|capital of|president)\b",
)

COUNSELLING_SIGNALS = (
    "feel", "feeling", "emotion", "anxious", "anxiety", "stress", "stressed",
    "depress", "sad", "lonely", "anger", "angry", "sleep", "burnout", "grief",
    "panic", "worry", "worried", "relationship", "breakup", "trauma", "self-esteem",
    "mental health", "wellbeing", "well-being", "cope", "coping", "overwhelmed",
    "conflict", "family", "friend", "partner", "work", "school", "advice",
    "help me", "on my mind", "can't handle", "cannot handle",
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


def is_sensitive_request(user_input: str) -> bool:
    """Return True for prompt-injection and private implementation requests."""
    text = re.sub(r"\s+", " ", user_input.lower()).strip()
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in SENSITIVE_PATTERNS)


def is_out_of_scope_request(user_input: str) -> bool:
    """Return True for clear non-counselling requests.

    This is a conservative lexical check: ambiguous personal messages still reach
    the counsellor, while obvious coding/general-purpose questions are stopped.
    """
    text = re.sub(r"\s+", " ", user_input.lower()).strip()
    if any(signal in text for signal in COUNSELLING_SIGNALS):
        return False
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in OFF_TOPIC_PATTERNS)


def scope_message() -> str:
    return SCOPE_RESPONSE


def privacy_message() -> str:
    return PRIVACY_RESPONSE


def contains_sensitive_output(response: str) -> bool:
    """Detect likely prompt/code leakage in a model response."""
    text = response.lower()
    markers = (
        "system prompt", "developer message", "api_key", "groq_api_key",
        "mem0_api_key", "tavily_api_key", "system instructions", "source code",
    )
    return any(marker in text for marker in markers)


def apply_empathy_fallback(generated_response: str) -> str:
    text = generated_response.lower()
    is_failure = (
        "i'm not able to respond" in text
        or "i'm having trouble connecting" in text
    )
    shows_empathy = any(phrase in text for phrase in EMPATHY_PHRASES)
    if not shows_empathy and not is_failure:
        return (
            "I want you to know that I care about your well-being. "
            + generated_response
        )

    return generated_response
