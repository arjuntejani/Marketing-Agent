"""LLM model interface module.

This module centralizes model invocation so the rest of the project can import
`generate_response` without hardcoding provider-specific calls elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import requests


class LLMClient(Protocol):
    """Protocol for pluggable LLM clients."""

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 256) -> str:
        """Generate a text response from a prompt."""


@dataclass
class OllamaClient:
    """Local Ollama client implementation."""

    base_url: str = "http://localhost:11434"
    model_name: str = "llama3:8b"
    timeout: int = 60

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 256) -> str:
        """Generate text with Ollama's HTTP API."""
        if not isinstance(prompt, str) or not prompt.strip():
            return ""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": float(temperature),
                "num_predict": int(max_tokens),
            },
        }

        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError, TypeError):
            return ""

        return str(data.get("response", "")).strip()


# Default client instance used by the project.
_default_client: LLMClient = OllamaClient()


def set_llm_client(client: LLMClient) -> None:
    """Set the project-wide LLM client (for swapping providers later)."""
    global _default_client
    _default_client = client


def generate_response(prompt: str, temperature: float = 0.7, max_tokens: int = 256) -> str:
    """Generate a response via the configured LLM client."""
    return _default_client.generate(prompt=prompt, temperature=temperature, max_tokens=max_tokens)
