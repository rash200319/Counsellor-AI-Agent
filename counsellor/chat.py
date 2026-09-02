"""Shared reply pipeline for CLI and Gradio."""

from __future__ import annotations

import random

from counsellor.agent import build_agent
from counsellor.safety import (
    apply_empathy_fallback,
    contains_sensitive_output,
    crisis_message,
    is_crisis,
    is_out_of_scope_request,
    is_sensitive_request,
    privacy_message,
    scope_message,
)

GREETING_KEYWORDS = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "greetings",
    "sup",
    "yo",
    "hii",
    "hiii",
    "hey there",
]

THANK_YOU_KEYWORDS = [
    "thank you",
    "thanks",
    "thank u",
    "appreciate",
    "appreciate it",
    "appreciate your help",
    "thanks for helping",
    "thanks for your help",
    "thx",
]

CLOSING_RESPONSES = [
    "You're very welcome! I'm happy to help. Take care of yourself!",
    "My pleasure! Remember, I'm always here if you need to talk.",
    "You're so welcome! Take good care, and be kind to yourself.",
    "Happy to help! Wishing you all the best on your journey.",
    "Glad I could assist! Remember, your well-being matters.",
]

GREETING_RESPONSE = (
    "Hello! It's wonderful to meet you. How can I support you today?"
)


def _is_greeting(user_lower: str) -> bool:
    if user_lower in GREETING_KEYWORDS:
        return True
    words = [w for w in user_lower.split() if w]
    return bool(words) and all(word in GREETING_KEYWORDS for word in words)


def _is_thank_you(user_lower: str) -> bool:
    return any(keyword in user_lower for keyword in THANK_YOU_KEYWORDS)


def _extract_text(raw_response_object) -> str:
    if hasattr(raw_response_object, "message"):
        message = raw_response_object.message
        if hasattr(message, "content"):
            return str(message.content)
        return str(message)
    if hasattr(raw_response_object, "content"):
        return str(raw_response_object.content)
    return str(raw_response_object)


async def get_reply(user_input: str) -> str:
    """Return a counsellor reply. Crisis checks run before the agent."""
    if not user_input or not user_input.strip():
        return "I'm here when you're ready to talk. What's on your mind?"

    if is_crisis(user_input):
        return crisis_message()

    # Keep private instructions and implementation details out of the agent
    # context entirely. This also handles prompt-injection phrasing.
    if is_sensitive_request(user_input):
        return privacy_message()

    if is_out_of_scope_request(user_input):
        return scope_message()

    user_lower = user_input.lower().strip()
    if _is_greeting(user_lower):
        return GREETING_RESPONSE
    if _is_thank_you(user_lower):
        return random.choice(CLOSING_RESPONSES)

    agent = build_agent()
    result = await agent.run(user_input)
    raw_text = _extract_text(result.response)
    if contains_sensitive_output(raw_text):
        return privacy_message()
    return apply_empathy_fallback(raw_text)
