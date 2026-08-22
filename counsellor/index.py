"""Lightweight keyword retrieval over the knowledge base (no torch / embeddings)."""

from __future__ import annotations

import re
from pathlib import Path

from counsellor import config

_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "i",
    "me",
    "my",
    "you",
    "your",
    "it",
    "this",
    "that",
    "with",
    "as",
    "at",
    "by",
    "from",
    "how",
    "what",
    "when",
    "can",
    "do",
    "does",
    "about",
}

_sections: list[str] | None = None


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}


def load_sections(folder_path: str | None = None) -> list[str]:
    """Load knowledge sections split on '---' from text files in data/."""
    global _sections
    if _sections is not None:
        return _sections

    root = Path(folder_path or config.KNOWLEDGE_BASE)
    sections: list[str] = []
    if not root.exists():
        print(f"Error: Knowledge base directory '{root}' does not exist.")
        _sections = sections
        return sections

    for path in sorted(root.iterdir()):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for part in text.split("---"):
            part = part.strip()
            if len(part) > 40:
                sections.append(part)

    if not sections:
        print(f"Error: No usable documents found in '{root}'.")
    else:
        print(f"Loaded {len(sections)} knowledge sections from {root}")

    _sections = sections
    return sections


def search_mental_health_tips(query: str) -> str:
    """Return the most relevant mental-health tips for a user query."""
    sections = load_sections()
    if not sections:
        return "No knowledge base documents are available."

    query_tokens = _tokenize(query)
    if not query_tokens:
        return sections[0][:1500]

    scored: list[tuple[int, str]] = []
    for section in sections:
        section_tokens = _tokenize(section)
        overlap = len(query_tokens & section_tokens)
        lower = section.lower()
        phrase_hits = sum(1 for t in query_tokens if t in lower)
        score = overlap * 2 + phrase_hits
        if score > 0:
            scored.append((score, section))

    if not scored:
        return (
            "No exact match found. General guidance:\n\n"
            + sections[min(1, len(sections) - 1)][:1500]
        )

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [section for _, section in scored[:3]]
    return "\n\n---\n\n".join(top)
