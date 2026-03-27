"""
wine_pairing_service.py
-----------------------
SOLID principles applied:
  S — Two focused classes: WinePairingService (LLM + Qdrant orchestration)
      and WineLinkEnricher (hyperlink injection). Each owns one concern.
  D — WinePairingService depends on the LLMProvider abstraction, not on any
      concrete Ollama/Qwen class. Swap providers without touching this file.
"""

from llm_provider import LLMProvider
from wine_repository import WineRepository
from qdrant_client import QdrantClient


_SYSTEM_HINT = (
    "You are a sommelier with extensive knowledge of wines from around the world. "
    "Your goal is to provide the best possible information about wine taste paired with the food. "
    "Reply in just a single sentence, no other information."
)

_SYSTEM_RECOMMEND = (
    "You are a sommelier with extensive knowledge of wines from around the world. "
    "Your goal is to use the provided bullet point list of wines to suggest how to pair them with the food. "
    "Add additional, educative information about the wines. Five sentences at max."
)


class WinePairingService:
    """
    Orchestrates LLM + Qdrant to produce wine pairing recommendations.

    Depends on LLMProvider abstraction (D) — any registered provider works here.
    """

    def __init__(self, llm: LLMProvider, qdrant: QdrantClient, collection: str = "wines5"):
        self._llm = llm
        self._qdrant = qdrant
        self._collection = collection

    def get_pairing_hint(self, food_query: str) -> str:
        """Step 1 — ask the LLM for a one-sentence wine style description."""
        return self._llm.chat(system_prompt=_SYSTEM_HINT, user_prompt=food_query)

    def get_wine_recommendations(self, food_query: str, pairing_hint: str) -> str:
        """Step 2 — semantic search in Qdrant, then ask the LLM to explain the matches."""
        search_result = self._qdrant.query(
            collection_name=self._collection,
            query_text=pairing_hint,
        )
        return self._llm.chat(
            system_prompt=_SYSTEM_RECOMMEND,
            user_prompt=f"Pair {food_query} with {search_result}",
        )


class WineLinkEnricher:
    """
    Single responsibility: enrich a text response by hyperlinking known wine names.

    Knows nothing about LLMs or Qdrant.
    """

    def __init__(self, repository: WineRepository):
        self._repo = repository

    def enrich(self, text: str) -> str:
        """Replace wine name occurrences in text with markdown hyperlinks."""
        for name in self._repo.get_all_wine_names():
            if name in text:
                url = self._repo.get_wine_url(name)
                text = text.replace(name, f"[{name}]({url})")
        return text
