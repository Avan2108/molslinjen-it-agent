"""
Diagnostics Agent — Sequential troubleshooting pattern.

Rules (per UpdatedArch spec):
  - Asks exactly ONE question per turn
  - Accumulates a structured diagnostic summary in session state
  - Terminates early if user says "just raise a ticket" — collected steps preserved
  - Escalates to Ticket Agent after 5 unanswered steps or on resolution failure
"""

import json
from openai import AzureOpenAI
from app import store

_STOP_PHRASES_EN = [
    "just raise a ticket", "create a ticket", "open a ticket",
    "raise ticket", "make a ticket", "just open a ticket",
    "create ticket", "escalate",
]
_STOP_PHRASES_DA = [
    "opret en billet", "opret billet", "lav en billet",
    "eskalér", "bare opret", "eskalere", "opret sag",
]

_SYS_EN = """You are a diagnostics agent for Molslinjen IT Helpdesk using the Sequential diagnostic pattern.

STRICT RULES:
1. Ask EXACTLY ONE question per turn — never list multiple questions.
2. Questions must be specific and progressively narrow down the root cause.
3. After gathering enough info (3–5 steps), provide a resolution if you can.
4. If not resolved after 5 questions, or if the issue requires hands-on IT work, escalate.
5. If the user says they want a ticket, acknowledge and escalate immediately.

Return ONLY valid JSON with this exact shape:
{
  "question": "<next single question, or null if done>",
  "observation": "<brief note on what you learned from this step>",
  "resolved": false,
  "escalate": false,
  "resolution": "<step-by-step fix if resolved, else null>",
  "summary": "<running 1-line diagnostic summary>"
}

When resolved or escalating, set question=null and provide a clear summary."""

_SYS_DA = """Du er en diagnostikagent for Molslinjen IT Helpdesk og bruger det sekventielle diagnostikmønster.

STRENGE REGLER:
1. Stil præcis ÉT spørgsmål per svar — aldrig flere spørgsmål på én gang.
2. Spørgsmål skal progressivt indsnævre årsagen.
3. Efter nok information (3–5 trin): giv løsning hvis muligt.
4. Hvis ikke løst efter 5 spørgsmål eller kræver fysisk IT-arbejde: eskalér.
5. Hvis brugeren vil have oprettet en billet: anerkend og eskalér straks.

Returner KUN valid JSON med dette format:
{
  "question": "<næste enkelt spørgsmål, eller null hvis færdig>",
  "observation": "<kort note om hvad du lærte>",
  "resolved": false,
  "escalate": false,
  "resolution": "<trin-for-trin løsning hvis løst, ellers null>",
  "summary": "<løbende 1-linje diagnoseoversigt>"
}"""

_MAX_STEPS = 5


def _wants_ticket(message: str, locale: str) -> bool:
    msg     = message.lower()
    phrases = _STOP_PHRASES_DA if locale == "da" else _STOP_PHRASES_EN
    return any(p in msg for p in phrases)


def _fallback_question(step: int, locale: str) -> str:
    questions_en = [
        "When did this issue first start?",
        "Have you tried restarting the device?",
        "Does this happen on all devices or just one?",
        "Are you seeing any error messages? If so, what do they say?",
        "Has anything changed recently (updates, new software, password change)?",
    ]
    questions_da = [
        "Hvornår opstod problemet første gang?",
        "Har du prøvet at genstarte enheden?",
        "Sker det på alle enheder eller kun én?",
        "Ser du nogen fejlmeddelelser? Hvad siger de?",
        "Er der sket ændringer for nylig (opdateringer, ny software, adgangskodeskift)?",
    ]
    pool = questions_da if locale == "da" else questions_en
    return pool[min(step, len(pool) - 1)]


# ── Public API ────────────────────────────────────────────────────────────────

def handle(
    client: AzureOpenAI,
    deployment: str,
    session_id: str,
    message: str,
    history: list[dict],
    locale: str = "en",
) -> dict:
    """
    Process one diagnostic turn.
    Returns {"answer": str, "sources": [], "escalate": bool, "diagnostic_summary": str}.
    """
    state   = store.get_diagnostic_state(session_id)
    steps   = state.get("steps", [])
    n_steps = len(steps)

    # User bailing out to a ticket
    if _wants_ticket(message, locale):
        summary = state.get("problem_summary", message)
        store.clear_diagnostic_state(session_id)
        if locale == "da":
            msg = "Ingen bekymringer — jeg eskalerer dette. Brug knappen nedenfor til at oprette en billet med diagnoseoversigten."
        else:
            msg = "No problem — I'll escalate this. Use the button below to create a ticket with the diagnostic summary attached."
        return {"answer": msg, "sources": [], "escalate": True, "diagnostic_summary": summary}

    # Initialise state on first turn
    if not state.get("active"):
        store.set_diagnostic_state(session_id, {
            "active":          True,
            "steps":           [],
            "problem_summary": message,
        })
        state = store.get_diagnostic_state(session_id)

    # Build accumulated steps context
    steps_text = "\n".join(
        f"Step {i + 1}: Q={s['question']} | A={s.get('answer', '(pending)')}"
        for i, s in enumerate(steps)
    )
    user_prompt = (
        f"Problem reported: {state.get('problem_summary', message)}\n\n"
        f"Diagnostic steps so far:\n{steps_text if steps_text else 'None yet'}\n\n"
        f"User's latest response: {message}\n"
        f"Steps taken so far: {n_steps}/{_MAX_STEPS}"
    )

    sys = _SYS_DA if locale == "da" else _SYS_EN

    result: dict = {}
    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
    except Exception:
        result = {
            "question":   _fallback_question(n_steps, locale),
            "observation": "",
            "resolved":   False,
            "escalate":   False,
            "resolution": None,
            "summary":    state.get("problem_summary", message),
        }

    # Record new step
    new_question = result.get("question")
    if new_question:
        steps.append({"question": new_question, "answer": ""})

    is_done = result.get("resolved") or result.get("escalate") or n_steps >= _MAX_STEPS

    store.set_diagnostic_state(session_id, {
        "active":          not is_done,
        "steps":           steps,
        "problem_summary": state.get("problem_summary", message),
    })

    if is_done:
        store.clear_diagnostic_state(session_id)

    # Build answer text
    if result.get("resolved"):
        answer_text = result.get("resolution") or result.get("summary", "Issue resolved!")
        escalate    = False
    elif result.get("escalate") or n_steps >= _MAX_STEPS:
        summary     = result.get("summary", state.get("problem_summary", ""))
        if locale == "da":
            answer_text = f"Baseret på diagnostikken eskalerer jeg dette til IT-support. Oversigt: {summary}"
        else:
            answer_text = f"Based on the diagnostics, I'm escalating this to IT support. Summary: {summary}"
        escalate = True
    else:
        answer_text = result.get("question", _fallback_question(n_steps, locale))
        escalate    = False

    return {
        "answer":             answer_text,
        "sources":            [],
        "escalate":           escalate,
        "diagnostic_summary": result.get("summary", state.get("problem_summary", "")),
    }


def record_user_answer(session_id: str, answer: str):
    """Fill in the last unanswered diagnostic step with the user's reply."""
    state = store.get_diagnostic_state(session_id)
    steps = state.get("steps", [])
    if steps and steps[-1].get("answer") == "":
        steps[-1]["answer"] = answer
        store.set_diagnostic_state(session_id, {**state, "steps": steps})
