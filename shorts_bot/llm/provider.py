"""LLM provider selection — Gemini (free) preferred over OpenAI."""

from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from shorts_bot.config import settings

GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"


@dataclass(frozen=True)
class LlmBackend:
    client: OpenAI
    model: str
    provider: str  # "gemini" | "openai"


def get_llm_backend() -> LlmBackend | None:
    """Return active chat backend. Gemini first (free tier), then OpenAI."""
    if settings.has_gemini:
        return LlmBackend(
            client=OpenAI(
                api_key=settings.gemini_api_key,
                base_url=GEMINI_OPENAI_BASE,
            ),
            model=settings.gemini_model,
            provider="gemini",
        )
    if settings.has_openai:
        return LlmBackend(
            client=OpenAI(api_key=settings.openai_api_key),
            model=settings.openai_model,
            provider="openai",
        )
    return None


def has_full_chat() -> bool:
    return settings.has_gemini or settings.has_openai


def chat_provider_label() -> str:
    if settings.has_gemini:
        return "gemini"
    if settings.has_openai:
        return "openai"
    return "offline"
