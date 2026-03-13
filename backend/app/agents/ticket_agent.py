"""
Ticket Agent — creates and queries support tickets.

Integration priority:
  1. FreshService REST API v2 — when FRESHSERVICE_DOMAIN + FRESHSERVICE_API_KEY are set
  2. Local in-memory store   — always available as fallback (demo mode)
"""

import os
import json
from openai import AzureOpenAI
from app import store

# requests is imported lazily inside FreshService functions so the module
# loads cleanly even if the package is not yet installed.


_FS_DOMAIN_RAW = os.environ.get("FRESHSERVICE_DOMAIN", "")
# Accept either "molslinjen" or "molslinjen.freshservice.com"
_FS_DOMAIN  = (
    _FS_DOMAIN_RAW if "." in _FS_DOMAIN_RAW
    else f"{_FS_DOMAIN_RAW}.freshservice.com" if _FS_DOMAIN_RAW
    else ""
)
_FS_API_KEY = os.environ.get("FRESHSERVICE_API_KEY", "")

# FreshService priority: 1=urgent 2=high 3=medium 4=low
_PRIORITY_MAP = {"urgent": 1, "high": 2, "medium": 3, "low": 4}


def _fs_available() -> bool:
    return bool(_FS_DOMAIN and _FS_API_KEY)


# ── FreshService helpers ──────────────────────────────────────────────────────

def _fs_create(
    summary: str,
    description: str,
    user_email: str,
    priority: str = "medium",
) -> dict:
    import requests as http
    url     = f"https://{_FS_DOMAIN}/api/v2/tickets"
    payload = {
        "subject":     summary[:100],
        "description": description,
        "email":       user_email,
        "priority":    _PRIORITY_MAP.get(priority, 3),
        "status":      2,   # Open
        "source":      2,   # Portal
    }
    resp = http.post(url, json=payload, auth=(_FS_API_KEY, "X"), timeout=15)
    resp.raise_for_status()
    data = resp.json()["ticket"]
    return {
        "ticket_id":      f"INC-{data['id']}",
        "summary":         summary,
        "status":          "Open",
        "estimated_wait":  "2–4 hours",
        "freshservice_id": data["id"],
    }


def _fs_get(fs_id: int) -> dict | None:
    import requests as http
    url  = f"https://{_FS_DOMAIN}/api/v2/tickets/{fs_id}"
    resp = http.get(url, auth=(_FS_API_KEY, "X"), timeout=10)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data       = resp.json()["ticket"]
    status_map = {2: "Open", 3: "Pending", 4: "Resolved", 5: "Closed"}
    return {
        "ticket_id":     f"INC-{data['id']}",
        "summary":        data.get("subject", ""),
        "status":         status_map.get(data.get("status"), "Open"),
        "estimated_wait": "2–4 hours",
    }


# ── LLM confirmation message ──────────────────────────────────────────────────

_SYS_EN = """You are a ticket agent for Molslinjen IT Helpdesk.
Write a short, friendly confirmation message based on the ticket details.
Always include the ticket ID (INC-XXXX) and status.
End with a helpful closing sentence. Keep it under 3 sentences."""

_SYS_DA = """Du er en billetagent for Molslinjen IT Helpdesk.
Skriv en kort, venlig bekræftelsesbesked baseret på billetdetaljerne.
Inkluder altid billet-ID (INC-XXXX) og status.
Afslut med en hjælpsom sætning. Hold det under 3 sætninger."""


def _confirm_message(
    client: AzureOpenAI,
    deployment: str,
    ticket: dict,
    action: str,
    locale: str,
) -> str:
    sys    = _SYS_DA if locale == "da" else _SYS_EN
    prompt = f"Action: {action}\nTicket: {json.dumps(ticket, ensure_ascii=False)}"
    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        tid    = ticket.get("ticket_id", "?")
        status = ticket.get("status", "Open")
        if locale == "da":
            return f"Din billet {tid} er oprettet med status: {status}. Vi vender tilbage hurtigst muligt!"
        return f"Your ticket {tid} has been created with status: {status}. We'll be in touch soon!"


# ── Public API ────────────────────────────────────────────────────────────────

def generate_ticket_summary(
    client: AzureOpenAI,
    deployment: str,
    history: list,
    locale: str = "en",
) -> dict:
    """Generate a concise ticket title and description from chat history."""
    lines = []
    for turn in history:
        if turn.get("user"):
            lines.append(f"User: {turn['user']}")
        if turn.get("assistant"):
            lines.append(f"IT Assistant: {turn['assistant']}")
    conversation = "\n".join(lines) if lines else "No conversation recorded."

    if locale == "da":
        sys_prompt = (
            "Du er en IT helpdesk assistent. Baseret på samtalen nedenfor, generer:\n"
            "1. En kortfattet billettitel (maks 10 ord, ingen afsluttende tegnsætning)\n"
            "2. En klar beskrivelse af problemet til en supportmedarbejder (2-4 sætninger)\n\n"
            'Svar KUN med JSON: {"title": "...", "description": "..."}'
        )
    else:
        sys_prompt = (
            "You are an IT helpdesk assistant. Based on the conversation below, generate:\n"
            "1. A concise ticket title (max 10 words, no trailing punctuation)\n"
            "2. A clear description summarising the issue for a support agent (2-4 sentences)\n\n"
            'Respond ONLY with JSON: {"title": "...", "description": "..."}'
        )

    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": conversation},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=300,
        )
        data = json.loads(resp.choices[0].message.content)
        return {
            "title":       data.get("title", "")[:100].strip(),
            "description": data.get("description", "").strip(),
        }
    except Exception:
        return {"title": "", "description": ""}


def handle_create(
    client: AzureOpenAI,
    deployment: str,
    session_id: str,
    summary: str,
    description: str,
    user_name: str,
    priority: str = "medium",
    locale: str = "en",
) -> dict:
    """Create a ticket via FreshService (if configured) or local store."""
    ticket = None

    if _fs_available():
        try:
            email  = f"{user_name.lower().replace(' ', '.')}@molslinjen.dk"
            ticket = _fs_create(summary, description, email, priority)
            # Mirror in local store for admin dashboard
            store.create_ticket(session_id, summary, description, user_name)
        except Exception:
            ticket = None

    if ticket is None:
        ticket = store.create_ticket(session_id, summary, description, user_name)

    answer_text = _confirm_message(client, deployment, ticket, "created", locale)
    return {"answer": answer_text, "ticket": ticket, "sources": [], "escalate": False}


def handle_status(
    client: AzureOpenAI,
    deployment: str,
    ticket_id: str,
    user_name: str,
    locale: str = "en",
) -> dict:
    """Look up a ticket by ID."""
    ticket = store.get_ticket(ticket_id)

    if ticket is None and _fs_available():
        try:
            fs_id  = int(ticket_id.replace("INC-", ""))
            ticket = _fs_get(fs_id)
        except Exception:
            pass

    if ticket:
        answer_text = _confirm_message(client, deployment, ticket, "status_check", locale)
        return {"answer": answer_text, "ticket": ticket, "sources": [], "escalate": False}

    not_found = (
        f"Billet {ticket_id} blev ikke fundet. Kontroller ID'et og prøv igen."
        if locale == "da" else
        f"Ticket {ticket_id} was not found. Please check the ID and try again."
    )
    return {"answer": not_found, "ticket": None, "sources": [], "escalate": False}
