"""In-memory store for sessions, tickets, analytics, and diagnostic state."""

import datetime
from collections import Counter

# { session_id: [{ user, assistant, sources, escalate, timestamp }] }
_sessions: dict[str, list[dict]] = {}

# { ticket_id: ticket_dict }
_tickets: dict[str, dict] = {}

# question frequency
_question_counter: Counter = Counter()

# feedback { message_id: rating }
_feedback: dict[str, str] = {}

_ticket_counter = [1000]   # mutable so we can increment

# { session_id: { active, steps, problem_summary } }
_diagnostics: dict[str, dict] = {}


# ── Session / history ──────────────────────────────────────────────────────────

def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def add_message(
    session_id: str,
    user: str,
    assistant: str,
    sources: list,
    escalate: bool,
):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({
        "user":      user,
        "assistant": assistant,
        "sources":   sources,
        "escalate":  escalate,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    })


# ── Diagnostic state ───────────────────────────────────────────────────────────

def get_diagnostic_state(session_id: str) -> dict:
    """Return the current diagnostic state for a session (empty dict if none)."""
    return _diagnostics.get(session_id, {})


def set_diagnostic_state(session_id: str, state: dict):
    """Persist diagnostic state for a session."""
    _diagnostics[session_id] = state


def clear_diagnostic_state(session_id: str):
    """Mark diagnostic session as inactive (keeps summary for ticket context)."""
    if session_id in _diagnostics:
        _diagnostics[session_id]["active"] = False


# ── Analytics ──────────────────────────────────────────────────────────────────

def record_question(question: str):
    _question_counter[question] += 1


def record_feedback(session_id: str, message_id: str, rating: str):
    _feedback[message_id] = rating


# ── Tickets ───────────────────────────────────────────────────────────────────

TICKET_STATUSES = ["Open", "In Progress", "Pending", "Resolved"]


def create_ticket(
    session_id: str,
    summary: str,
    description: str,
    user_name: str,
) -> dict:
    _ticket_counter[0] += 1
    ticket_id = f"INC-{_ticket_counter[0]}"
    ticket = {
        "ticket_id":     ticket_id,
        "summary":       summary,
        "description":   description,
        "user_name":     user_name,
        "status":        "Open",
        "created_at":    datetime.datetime.utcnow().isoformat(),
        "session_id":    session_id,
        "estimated_wait": "2–4 hours",
    }
    _tickets[ticket_id] = ticket
    return ticket


def get_ticket(ticket_id: str) -> dict | None:
    return _tickets.get(ticket_id)


def list_user_tickets(user_name: str) -> list[dict]:
    return [t for t in _tickets.values() if t.get("user_name") == user_name]


# ── Admin stats ───────────────────────────────────────────────────────────────

def get_stats() -> dict:
    total_conversations = len(_sessions)
    total_messages      = sum(len(v) for v in _sessions.values())
    escalated           = sum(
        1 for turns in _sessions.values()
        for turn in turns if turn.get("escalate")
    )
    thumbs_up    = sum(1 for r in _feedback.values() if r == "up")
    thumbs_down  = sum(1 for r in _feedback.values() if r == "down")
    total_fb     = thumbs_up + thumbs_down
    satisfaction = round((thumbs_up / total_fb) * 100) if total_fb else 0

    top_questions = [
        {"question": q, "count": c}
        for q, c in _question_counter.most_common(8)
    ]

    return {
        "total_conversations": total_conversations,
        "total_messages":      total_messages,
        "total_tickets":       len(_tickets),
        "escalated_count":     escalated,
        "satisfaction_rate":   satisfaction,
        "thumbs_up":           thumbs_up,
        "thumbs_down":         thumbs_down,
        "top_questions":       top_questions,
    }


def get_all_conversations() -> list[dict]:
    result = []
    for sid, turns in _sessions.items():
        result.append({
            "session_id":    sid,
            "message_count": len(turns),
            "last_message":  turns[-1]["timestamp"] if turns else None,
            "escalated":     any(t.get("escalate") for t in turns),
            "turns":         turns,
        })
    return result


def get_all_tickets() -> list[dict]:
    return list(_tickets.values())
