"""Load environment variables and shared configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b"
KNOWLEDGE_BASE = str(ROOT_DIR / "data")
OUTPUT_TOKENS = 512
USER_ID = os.getenv("COUNSELLOR_USER_ID", "1")


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value in {"##", "###"}:
        print(
            f"Missing or placeholder {name}. "
            f"Copy .env.example to .env and set your API keys."
        )
        sys.exit(1)
    return value


def get_groq_api_key() -> str:
    return _require_env("GROQ_API_KEY")


def get_mem0_api_key() -> str:
    return _require_env("MEM0_API_KEY")


def get_tavily_api_key() -> str:
    return _require_env("TAVILY_API_KEY")
