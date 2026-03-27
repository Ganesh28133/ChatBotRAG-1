"""
llm_provider.py
---------------
SOLID principles applied:
  S  — Each class has one job: OllamaProvider wraps Ollama, QwenProvider wraps Qwen.
  O  — Add a new LLM by subclassing LLMProvider + registering in the factory.
       Existing code never needs to change.
  L  — Any LLMProvider subclass is a valid drop-in replacement.
  I  — Single, minimal interface: chat(system_prompt, user_prompt) -> str.
  D  — Callers depend on LLMProvider (abstraction), not on concrete clients.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for all LLM backends."""

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a system + user message and return the assistant reply."""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """Concrete LLM provider backed by a local Ollama instance."""

    def __init__(self, host: str, model: str = "mistral"):
        from ollama import Client
        self._client = Client(host=host)
        self._model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
        )
        return response["message"]["content"]


class QwenProvider(LLMProvider):
    """Concrete LLM provider backed by an OpenAI-compatible Qwen endpoint."""

    def __init__(self, base_url: str, model: str = "Qwen/Qwen3-8B", max_tokens: int = 512):
        from openai import OpenAI
        self._client = OpenAI(base_url=base_url, api_key="not-required")
        self._model = model
        self._max_tokens = max_tokens

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=self._max_tokens,
            stream=False,
        )
        return response.choices[0].message.content


# ── Factory ───────────────────────────────────────────────────────────────────
# Open/Closed: register new providers here without touching any other module.

_PROVIDER_REGISTRY = {
    "ollama": lambda cfg: OllamaProvider(
        host=cfg.get("ollama_url", "http://ollama:11434"),
        model=cfg.get("model", "mistral"),
    ),
    "qwen": lambda cfg: QwenProvider(
        base_url=cfg.get("qwen_api_url", "http://wiphack30qx5aw.cloudloka.com:8000/v1"),
        model=cfg.get("model", "Qwen/Qwen3-8B"),
        max_tokens=cfg.get("max_tokens", 512),
    ),
}


def create_llm_provider(provider: str, **cfg) -> LLMProvider:
    """
    Factory that returns the correct LLMProvider.

    To switch LLMs set the LLM_PROVIDER env var to 'ollama' or 'qwen'.
    To add a new provider: add an entry to _PROVIDER_REGISTRY — nothing else changes.
    """
    key = provider.lower()
    if key not in _PROVIDER_REGISTRY:
        raise ValueError(
            f"Unknown LLM provider '{key}'. Valid options: {list(_PROVIDER_REGISTRY)}"
        )
    return _PROVIDER_REGISTRY[key](cfg)
