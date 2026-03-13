"""
Handoff Orchestrator — implements the Handoff Orchestration pattern.

Flow per turn:
  1. Resume active Diagnostics session if one exists → Diagnostics Agent
  2. Call Triage Agent to classify intent
  3. Route to appropriate Specialist Agent based on intent
  4. Return unified response to /chat endpoint

Specialist agents:
  knowledge_query  → Knowledge Agent  (RAG + optional vision)
  ticket_action    → Knowledge Agent  (answer) + escalate=True
  ticket_status    → Ticket Agent     (lookup)
  diagnostics      → Diagnostics Agent (sequential)
  off_topic        → Inline rejection message
"""

import os
import re
from openai import AzureOpenAI
from app.agents import triage_agent, knowledge_agent, ticket_agent, diagnostics_agent
from app import store

# ── Config from environment ───────────────────────────────────────────────────

_ENDPOINT         = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
_API_KEY          = os.environ.get("AZURE_OPENAI_API_KEY", "")
_API_VERSION      = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
_CHAT_DEPLOYMENT  = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
_EMBED_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

_OFF_TOPIC_EN = (
    "I'm specialised in Molslinjen IT support. I can help with IT issues, "
    "VPN, passwords, software requests, and ferry schedules. "
    "What IT-related question can I help you with?"
)
_OFF_TOPIC_DA = (
    "Jeg er specialiseret i Molslinjen IT-support. Jeg kan hjælpe med IT-problemer, "
    "VPN, adgangskoder, softwareanmodninger og færgeplaner. "
    "Hvad kan jeg hjælpe dig med?"
)

_NOT_CONFIGURED_EN = (
    "The AI assistant is not configured yet — Azure OpenAI credentials are missing. "
    "You can still create a support ticket and an IT agent will help you directly."
)
_NOT_CONFIGURED_DA = (
    "AI-assistenten er endnu ikke konfigureret — Azure OpenAI-legitimationsoplysninger mangler. "
    "Du kan stadig oprette en supportbillet, og en IT-medarbejder vil hjælpe dig direkte."
)


def _configured() -> bool:
    return bool(_ENDPOINT and _API_KEY)


def _make_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=_ENDPOINT,
        api_key=_API_KEY,
        api_version=_API_VERSION,
    )


def _not_configured_response(locale: str) -> dict:
    msg = _NOT_CONFIGURED_DA if locale == "da" else _NOT_CONFIGURED_EN
    return {"answer": msg, "sources": [], "escalate": True}


def summarize_ticket(session_id: str, language: str = "en") -> dict:
    """Generate AI title + description for a ticket from the session history."""
    if not _configured():
        return {"title": "", "description": ""}
    history = store.get_history(session_id)
    client  = _make_client()
    return ticket_agent.generate_ticket_summary(client, _CHAT_DEPLOYMENT, history, language)


def _extract_ticket_id(message: str) -> str | None:
    match = re.search(r"INC-\d+", message, re.IGNORECASE)
    return match.group(0).upper() if match else None


# ── Main entry point ──────────────────────────────────────────────────────────

def process(
    session_id: str,
    message: str,
    language: str = "en",
    images: list[str] | None = None,
) -> dict:
    """
    Process one user turn through the agent pipeline.

    Returns:
        {
            "answer":   str,
            "sources":  list[str],
            "escalate": bool,
        }
    """
    history = store.get_history(session_id)

    # ── Step 1: Resume active Diagnostics session ─────────────────────────────
    diag_state = store.get_diagnostic_state(session_id)
    if diag_state.get("active"):
        if not _configured():
            return _not_configured_response(language)
        client = _make_client()
        diagnostics_agent.record_user_answer(session_id, message)
        result = diagnostics_agent.handle(
            client, _CHAT_DEPLOYMENT, session_id, message, history, language
        )
        return {
            "answer":   result["answer"],
            "sources":  result.get("sources", []),
            "escalate": result.get("escalate", False),
        }

    # ── Step 2: Triage ────────────────────────────────────────────────────────
    if not _configured():
        return _not_configured_response(language)

    client = _make_client()
    triage = triage_agent.classify(client, _CHAT_DEPLOYMENT, message, history)
    intent = triage.get("intent", "knowledge_query")
    locale = triage.get("locale", language)

    # ── Step 3: Route to Specialist ───────────────────────────────────────────

    # Off-topic guardrail
    if intent == "off_topic":
        answer = _OFF_TOPIC_DA if locale == "da" else _OFF_TOPIC_EN
        return {"answer": answer, "sources": [], "escalate": False}

    # Ticket status lookup
    if intent == "ticket_status":
        ticket_id = _extract_ticket_id(message)
        if ticket_id:
            result = ticket_agent.handle_status(
                client, _CHAT_DEPLOYMENT, ticket_id, "User", locale
            )
            return {
                "answer":   result["answer"],
                "sources":  result.get("sources", []),
                "escalate": result.get("escalate", False),
            }
        # No INC- number found — treat as knowledge query
        intent = "knowledge_query"

    # Diagnostics — start a sequential session
    if intent == "diagnostics":
        result = diagnostics_agent.handle(
            client, _CHAT_DEPLOYMENT, session_id, message, history, locale
        )
        return {
            "answer":   result["answer"],
            "sources":  result.get("sources", []),
            "escalate": result.get("escalate", False),
        }

    # Ticket action — answer the question but always suggest a ticket
    if intent == "ticket_action":
        result = knowledge_agent.answer(
            client, _CHAT_DEPLOYMENT, _EMBED_DEPLOYMENT,
            message, history, locale, images
        )
        return {
            "answer":   result["answer"],
            "sources":  result.get("sources", []),
            "escalate": True,   # ticket_action always prompts ticket creation
        }

    # Default: knowledge_query
    result = knowledge_agent.answer(
        client, _CHAT_DEPLOYMENT, _EMBED_DEPLOYMENT,
        message, history, locale, images
    )
    return {
        "answer":   result["answer"],
        "sources":  result.get("sources", []),
        "escalate": result.get("escalate", False),
    }
