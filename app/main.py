"""
main.py
-------
SOLID principles applied:
  S — Single responsibility: this file owns only the Streamlit UI.
      All LLM, data access, and business logic live in their own modules.

To switch LLM provider: set LLM_PROVIDER env var to 'ollama' or 'qwen'
in docker-compose.yaml — no code changes needed anywhere.
"""

import os
import streamlit as st
from qdrant_client import QdrantClient

from llm_provider import create_llm_provider
from wine_repository import WineRepository
from wine_pairing_service import WinePairingService, WineLinkEnricher

st.set_page_config(page_title="RAG ChatBot", page_icon="🤖", layout="centered")

WELCOME_TEXT = "Enter the dish or cuisine (e.g., 'Bolognese lasagna'):"
GENERIC_RUNTIME_ERROR = (
    "I hit an issue while generating recommendations. "
    "Please try again in a few seconds."
)


@st.cache_resource
def build_services():
    """Construct and cache all services for the lifetime of the Streamlit session."""
    llm = create_llm_provider(
        provider=os.environ.get("LLM_PROVIDER", "ollama"),
        ollama_url=os.environ.get("OLLAMA", "http://ollama:11434"),
        qwen_api_url=os.environ.get("QWEN_API_URL", "http://wiphack30qx5aw.cloudloka.com:8000/v1"),
    )
    qdrant = QdrantClient(os.environ["QDRANT_CLIENT"])
    repo = WineRepository()
    pairing_service = WinePairingService(llm=llm, qdrant=qdrant)
    enricher = WineLinkEnricher(repository=repo)
    return pairing_service, enricher


def _render_messages() -> None:
    """Render chat history from Streamlit session state."""
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


def _append_assistant_message(content: str) -> None:
    """Append and render an assistant message in one place."""
    st.session_state.messages.append({"role": "assistant", "content": content})
    st.chat_message("assistant").write(content)


def show():
    st.title("🤖 RAG ChatBot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": WELCOME_TEXT}]

    _render_messages()

    try:
        pairing_service, enricher = build_services()
    except Exception as exc:
        st.error(
            "Service initialization failed. Check `LLM_PROVIDER`, `QDRANT_CLIENT`, "
            "and related API connectivity."
        )
        st.exception(exc)
        return

    if user_input := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        try:
            pairing_hint = pairing_service.get_pairing_hint(user_input)
            raw_response = pairing_service.get_wine_recommendations(user_input, pairing_hint)
            enriched = enricher.enrich(raw_response)
            _append_assistant_message(enriched)
        except Exception as exc:
            _append_assistant_message(GENERIC_RUNTIME_ERROR)
            with st.expander("Technical details"):
                st.exception(exc)


if __name__ == "__main__":
    show()
