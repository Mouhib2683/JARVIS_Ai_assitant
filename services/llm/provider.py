
import os
from typing import Protocol

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODEL = "openrouter/free"


class LLMProvider(Protocol):
    """Interface for interchangeable language-model providers."""

    def generate_reply(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str: ...


class MockLLMProvider:
    """Free test provider; this is not a real AI model."""

    def generate_reply(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        return (
            "JARVIS is currently operating in mock mode. "
            f"I received your message: {message}"
        )


class OpenRouterLLMProvider:
    """Cloud AI provider using OpenRouter's free-model router."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OpenRouter API key is missing. Check your local .env file."
            )

    def generate_reply(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a capable personal AI assistant. "
                    "Be clear, helpful, composed, and concise. "
                    "Use a subtle British butler personality."
                ),
            }
        ]

        for item in history or []:
            role = item.get("role")
            content = item.get("content")

            if role in ("user", "assistant") and isinstance(content, str):
                if content.strip():
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})

        payload = {
            "model": FREE_MODEL,
            "messages": messages,
        }

        try:
            response = httpx.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=45.0,
            )
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "OpenRouter took too long to respond. Please try again."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not connect to OpenRouter. Check your internet connection."
            ) from exc

        if response.status_code == 429:
            raise RuntimeError(
                "OpenRouter rate limit reached. Please wait and try again."
            )
        if response.status_code in (401, 403):
            raise RuntimeError(
                "OpenRouter rejected the API key or access. Check your key and account."
            )
        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenRouter returned HTTP {response.status_code}. Please try again."
            )

        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "OpenRouter returned an unexpected response."
            ) from exc

        if not isinstance(reply, str) or not reply.strip():
            raise RuntimeError("OpenRouter returned an empty reply.")

        return reply.strip()
