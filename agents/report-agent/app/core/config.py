from __future__ import annotations

import os


def get_llm_provider() -> str:
    return os.getenv("REPORT_LLM_PROVIDER", "template").strip().lower()


def get_openai_compatible_url() -> str:
    return os.getenv("REPORT_LLM_URL", "https://api.openai.com/v1/chat/completions")


def get_openai_compatible_model() -> str:
    return os.getenv("REPORT_LLM_MODEL", "gpt-4o-mini")


def get_openai_compatible_api_key() -> str | None:
    value = os.getenv("REPORT_LLM_API_KEY")
    return value.strip() if value else None
