"""
Knowledge Agent — answers questions using RAG.

Search priority:
  1. Azure AI Search (hybrid semantic + keyword) — when AZURE_SEARCH_* vars are set
  2. Local markdown cosine similarity            — always available as fallback

Supports vision: pass base64-encoded images for screenshot analysis (up to 3).
"""

import os
import math
import pathlib
from openai import AzureOpenAI

# ── Azure AI Search (optional) ────────────────────────────────────────────────

_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
_SEARCH_KEY      = os.environ.get("AZURE_SEARCH_KEY", "")
_SEARCH_INDEX    = os.environ.get("AZURE_SEARCH_INDEX", "helpdesk-kb")


def _search_available() -> bool:
    return bool(_SEARCH_ENDPOINT and _SEARCH_KEY)


def _azure_search(query: str, top_k: int = 5) -> list[str]:
    """Hybrid semantic + keyword search via Azure AI Search REST API."""
    import requests
    url     = f"{_SEARCH_ENDPOINT}/indexes/{_SEARCH_INDEX}/docs/search?api-version=2023-11-01"
    headers = {"Content-Type": "application/json", "api-key": _SEARCH_KEY}
    body    = {
        "search":               query,
        "queryType":            "semantic",
        "semanticConfiguration": "default",
        "top":                  top_k,
        "select":               "content,sourcefile",
    }
    resp = requests.post(url, json=body, headers=headers, timeout=10)
    resp.raise_for_status()
    return [doc.get("content", "") for doc in resp.json().get("value", [])]


# ── Local fallback (markdown chunks + cosine similarity) ─────────────────────

def _load_chunks() -> list[str]:
    doc_dir = pathlib.Path(__file__).parent.parent / "documents"
    chunks: list[str] = []
    for md in sorted(doc_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        chunks.extend(p.strip() for p in text.split("\n\n") if p.strip())
    return chunks


_LOCAL_CHUNKS: list[str]       = _load_chunks()
_LOCAL_EMBEDDINGS: list[list[float]] = []   # populated lazily on first query


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def _local_search(
    client: AzureOpenAI,
    embedding_deployment: str,
    query: str,
    top_k: int = 3,
) -> list[tuple[str, float]]:
    global _LOCAL_EMBEDDINGS

    if not _LOCAL_EMBEDDINGS and _LOCAL_CHUNKS:
        try:
            resp = client.embeddings.create(
                model=embedding_deployment,
                input=_LOCAL_CHUNKS,
            )
            _LOCAL_EMBEDDINGS = [item.embedding for item in resp.data]
        except Exception:
            # Embeddings unavailable — return first chunks with neutral score
            return [(c, 0.5) for c in _LOCAL_CHUNKS[:top_k]]

    if not _LOCAL_EMBEDDINGS:
        return []

    q_resp = client.embeddings.create(model=embedding_deployment, input=[query])
    q_emb  = q_resp.data[0].embedding

    scored = sorted(
        [(_cosine(q_emb, emb), chunk)
         for emb, chunk in zip(_LOCAL_EMBEDDINGS, _LOCAL_CHUNKS)],
        reverse=True,
    )
    return [(chunk, score) for score, chunk in scored[:top_k]]


# ── System prompts ────────────────────────────────────────────────────────────

_SYS_EN = """You are a helpful IT helpdesk assistant for Molslinjen (a Danish ferry company).
Answer ONLY from the provided context. Be thorough — include all relevant steps and conditions.
Cite source document names where possible.
If the answer is not in the context, say so politely and suggest contacting IT support.
End responses with a helpful closing like "Let me know if you need anything else!"
Respond in English."""

_SYS_DA = """Du er en hjælpsom IT-helpdesk-assistent for Molslinjen (et dansk færgeselskab).
Svar KUN ud fra den givne kontekst. Vær grundig og inkluder alle relevante trin og betingelser.
Nævn kildenavne hvor muligt.
Hvis svaret ikke er i konteksten, sig det venligt og foreslå at kontakte IT-support.
Afslut svar med noget som "Sig til, hvis du har brug for mere hjælp!"
Svar på dansk."""

_IT_ACTION_KEYWORDS = [
    "request", "install", "broken", "not working", "stolen", "lost", "reset",
    "access", "permission", "can't", "cannot", "error", "issue", "problem",
    "help", "setup", "configure", "connect", "vpn", "password", "locked",
    "anmod", "installere", "virker ikke", "stjålet", "mistet", "nulstil",
    "adgang", "fejl", "problem", "hjælp", "opsæt", "forbinde", "adgangskode",
]


# ── Main answer function ──────────────────────────────────────────────────────

def answer(
    client: AzureOpenAI,
    chat_deployment: str,
    embedding_deployment: str,
    question: str,
    history: list[dict],
    locale: str = "en",
    images: list[str] | None = None,
) -> dict:
    """
    Returns {"answer": str, "sources": list[str], "confidence": float, "escalate": bool}.
    images: list of base64-encoded image strings (up to 3) for vision analysis.
    """

    # ── 1. Retrieve relevant context ─────────────────────────────────────────
    sources_raw: list[str] = []
    confidence  = 0.5
    context     = ""

    if _search_available():
        try:
            chunks     = _azure_search(question, top_k=5)
            context    = "\n\n---\n\n".join(chunks)
            sources_raw = [c.split("\n")[0].lstrip("#").strip() for c in chunks[:2]]
            confidence  = 0.75
        except Exception:
            pass   # fall through to local search

    if not context:
        local_results = _local_search(client, embedding_deployment, question, top_k=3)
        context       = "\n\n---\n\n".join(c for c, _ in local_results)
        sources_raw   = [c.split("\n")[0].lstrip("#").strip() for c, _ in local_results]
        confidence    = local_results[0][1] if local_results else 0.0

    sources = [s for s in sources_raw if s][:2]

    # ── 2. Build prompt ───────────────────────────────────────────────────────
    history_text = "\n".join(
        f"User: {t['user']}\nAssistant: {t['assistant']}"
        for t in history[-4:]
    )
    text_prompt = (
        f"Previous conversation:\n{history_text}\n\n"
        f"Context from knowledge base:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    # Vision: include up to 3 images as multimodal content parts
    if images:
        user_content: list | str = [{"type": "text", "text": text_prompt}]
        for img_b64 in images[:3]:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url":    f"data:image/jpeg;base64,{img_b64}",
                    "detail": "low",
                },
            })
    else:
        user_content = text_prompt

    system_prompt = _SYS_DA if locale == "da" else _SYS_EN

    # ── 3. Call LLM ───────────────────────────────────────────────────────────
    resp = client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    answer_text = resp.choices[0].message.content.strip()

    # Escalate if confidence is low OR the question implies IT action is needed
    q_lower      = question.lower()
    is_actionable = any(kw in q_lower for kw in _IT_ACTION_KEYWORDS)
    escalate      = confidence < 0.55 or is_actionable

    return {
        "answer":     answer_text,
        "sources":    sources,
        "confidence": round(confidence, 3),
        "escalate":   escalate,
    }
