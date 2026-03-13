"""
Triage Agent — classifies every user message into one intent and detects locale.
Returns a typed handoff context consumed by the Orchestrator.

Intent values:
  knowledge_query  — user wants information (policy, procedure, how-to, schedule)
  ticket_action    — user needs IT to act (install, reset, fix hardware, access)
  ticket_status    — user asks about an existing ticket (mentions INC- or "my ticket")
  diagnostics      — something is broken and needs step-by-step troubleshooting
  off_topic        — unrelated to IT or Molslinjen
"""

import json
from openai import AzureOpenAI

_SYSTEM = """You are a triage agent for the Molslinjen IT Helpdesk.
Classify the user message into exactly one intent and detect locale.
Return ONLY valid JSON with this exact shape:
{"intent": "<value>", "locale": "<en or da>"}

Intent values:
- knowledge_query  : user wants information (policy, procedure, how-to, schedule)
- ticket_action    : user needs IT to act (install, reset, fix hardware, grant access)
- ticket_status    : user asks about an existing ticket (mentions INC- number or status)
- diagnostics      : user has something broken and needs step-by-step troubleshooting
- off_topic        : completely unrelated to IT or Molslinjen

Detect locale from the message language: "en" for English, "da" for Danish."""

# Keyword fallbacks (used when LLM call fails)
_KW_STATUS      = ["inc-", "ticket", "billet", "sag nr", "status", "my ticket"]
_KW_DIAGNOSTICS = ["not working", "broken", "virker ikke", "cannot connect",
                    "won't start", "keeps crashing", "screen", "black screen",
                    "frozen", "slow", "stuck", "error", "fejl"]
_KW_ACTION      = ["install", "access", "reset", "stolen", "lost", "request",
                   "permission", "installere", "adgang", "nulstil", "stjålet"]


def classify(
    client: AzureOpenAI,
    deployment: str,
    message: str,
    history: list[dict],
) -> dict:
    """Return {"intent": str, "locale": "en"|"da"}."""
    history_ctx = "\n".join(
        f"User: {t['user']}\nAssistant: {t['assistant']}"
        for t in history[-4:]
    )
    prompt = (
        f"Previous conversation:\n{history_ctx}\n\nNew message: {message}"
        if history_ctx else
        f"Message: {message}"
    )

    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.0,
            max_tokens=80,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        if "intent" in result and "locale" in result:
            return result
    except Exception:
        pass

    # Keyword fallback when LLM call fails or returns bad JSON
    msg = message.lower()
    da  = any(c in msg for c in "æøå")
    locale = "da" if da else "en"

    if any(k in msg for k in _KW_STATUS):
        return {"intent": "ticket_status", "locale": locale}
    if any(k in msg for k in _KW_DIAGNOSTICS):
        return {"intent": "diagnostics", "locale": locale}
    if any(k in msg for k in _KW_ACTION):
        return {"intent": "ticket_action", "locale": locale}
    return {"intent": "knowledge_query", "locale": locale}
