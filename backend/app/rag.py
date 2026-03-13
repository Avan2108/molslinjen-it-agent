"""
RAG engine — Retrieval-Augmented Generation using Azure OpenAI.

All credentials are read from environment variables (set in backend/.env).
When the Azure resources are provisioned, fill in backend/.env and restart.
No code changes required — just plug in the values.
"""

import os
import math
import pathlib
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Azure OpenAI configuration — all values come from environment variables.
# See backend/.env.example for the full list of required variables.
# ---------------------------------------------------------------------------

AZURE_ENDPOINT        = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY         = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_API_VERSION     = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
CHAT_DEPLOYMENT       = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
EMBEDDING_DEPLOYMENT  = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

# ---------------------------------------------------------------------------
# Azure OpenAI client — initialised once at startup.
# If credentials are missing the server still starts; calls will fail with a
# clear error until the .env values are filled in.
# ---------------------------------------------------------------------------

client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
)

# ---------------------------------------------------------------------------
# Document loading & chunking
# ---------------------------------------------------------------------------

def _load_chunks() -> list[str]:
    """Load all Markdown documents from the documents/ folder and split by paragraph."""
    doc_dir = pathlib.Path(__file__).parent / "documents"
    chunks: list[str] = []
    for md_file in sorted(doc_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks.extend(paragraphs)
    return chunks


CHUNKS: list[str] = _load_chunks()

# ---------------------------------------------------------------------------
# Embeddings — generated once at startup for all document chunks.
# ---------------------------------------------------------------------------

def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Azure OpenAI embeddings."""
    response = client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=texts,
    )
    return [item.embedding for item in response.data]


# Embed all chunks once when the server starts.
# When SharePoint integration is added, this will be replaced by a vector DB
# (e.g. Azure AI Search or pgvector) that is populated by an ingestion pipeline.
try:
    CHUNK_EMBEDDINGS: list[list[float]] = _embed_texts(CHUNKS) if CHUNKS else []
    print(f"[RAG] Embedded {len(CHUNK_EMBEDDINGS)} chunks successfully.")
except Exception as e:
    print(f"[RAG] WARNING: Could not embed documents at startup ({e}). "
          "Azure OpenAI credentials may not be configured yet. "
          "The server will start but AI answers will not work until credentials are set in backend/.env")
    CHUNK_EMBEDDINGS = []

# ---------------------------------------------------------------------------
# Retrieval — cosine similarity search
# ---------------------------------------------------------------------------

def _cosine(a: list[float], b: list[float]) -> float:
    dot    = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _retrieve(query: str, top_k: int = 2) -> list[tuple[str, float]]:
    """Return the top-k most relevant chunks and their similarity scores."""
    q_emb  = _embed_texts([query])[0]
    scored = [(_cosine(q_emb, emb), chunk) for emb, chunk in zip(CHUNK_EMBEDDINGS, CHUNKS)]
    scored.sort(reverse=True)
    return [(chunk, score) for score, chunk in scored[:top_k]]

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SYSTEM_EN = """You are a friendly and helpful IT helpdesk assistant for Mols-Linjen (a Danish ferry company).
Answer ONLY based on the provided context.
Use a warm, conversational tone and complete sentences.
IMPORTANT RULES:
- Be thorough — include ALL relevant details, steps, timelines, and conditions from the context. Do not leave out important information.
- If there are multiple steps or conditions (e.g. standard vs non-standard), explain all of them clearly.
- Answer ONLY the specific topic the user asked about. Do NOT include information about unrelated topics.
- End with a helpful closing like "Let me know if you need anything else!".
- If the answer is not in the context, politely say so and suggest contacting IT support.
Always respond in English."""

SYSTEM_DA = """Du er en venlig og hjælpsom IT-helpdesk-assistent for Mols-Linjen (et dansk færgeselskab).
Svar KUN baseret på den givne kontekst.
Brug en varm og samtalebaseret tone og hele sætninger.
VIGTIGE REGLER:
- Vær grundig — inkluder ALLE relevante detaljer, trin, tidsfrister og betingelser fra konteksten. Udelad ikke vigtig information.
- Hvis der er flere trin eller betingelser (f.eks. standard vs. ikke-standard), forklar dem alle tydeligt.
- Svar KUN på det specifikke emne, brugeren spurgte om. Inkluder IKKE information om ikke-relaterede emner.
- Afslut med noget hjælpsomt som "Lad mig vide, hvis du har brug for mere hjælp!".
- Hvis svaret ikke er i konteksten, sig venligt at du ikke har den information og foreslå at kontakte IT-support.
Svar altid på dansk."""

# ---------------------------------------------------------------------------
# IT-action keywords — triggers escalation even when confidence is high.
# When FreshService integration is active, escalation will create a real ticket.
# ---------------------------------------------------------------------------

IT_ACTION_KEYWORDS = [
    "request", "install", "broken", "not working", "stolen", "lost", "reset",
    "access", "permission", "can't", "cannot", "error", "issue", "problem",
    "help", "setup", "configure", "connect", "vpn", "password", "locked",
    "anmod", "installere", "virker ikke", "stjålet", "mistet", "nulstil",
    "adgang", "fejl", "problem", "hjælp", "opsæt", "forbinde", "adgangskode",
]

# ---------------------------------------------------------------------------
# Main answer function
# ---------------------------------------------------------------------------

def answer(question: str, history: list[dict], language: str = "en") -> dict:
    """
    Retrieve relevant context and generate an answer using Azure OpenAI.

    Returns:
        {
            "answer":   str,
            "sources":  list[str],
            "escalate": bool,
        }
    """
    # Guard: if Azure credentials are not configured, return a friendly message
    # and escalate=True so the full ticket creation flow is still visible/testable.
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        msg = (
            "The AI assistant is not configured yet. You can still create a support "
            "ticket and an IT agent will help you directly."
            if language != "da" else
            "AI-assistenten er endnu ikke konfigureret. Du kan stadig oprette en "
            "supportbillet, og en IT-medarbejder vil hjælpe dig."
        )
        return {"answer": msg, "sources": [], "escalate": True}

    chunks_with_scores = _retrieve(question)
    best_score = chunks_with_scores[0][1] if chunks_with_scores else 0.0
    context = "\n\n---\n\n".join(chunk for chunk, _ in chunks_with_scores)

    # Build conversation history context (last 4 turns)
    history_text = ""
    for turn in history[-4:]:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"

    system_prompt = SYSTEM_DA if language == "da" else SYSTEM_EN

    user_prompt = f"""Previous conversation:
{history_text}
Context from knowledge base:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    answer_text = response.choices[0].message.content.strip()

    # Escalate if low confidence OR if question is IT-actionable
    question_lower = question.lower()
    is_actionable  = any(kw in question_lower for kw in IT_ACTION_KEYWORDS)
    escalate       = best_score < 0.55 or is_actionable

    # Extract source headings from top chunks
    sources: list[str] = []
    for chunk, _ in chunks_with_scores:
        first_line = chunk.split("\n")[0].lstrip("#").strip()
        if first_line and first_line not in sources:
            sources.append(first_line)

    return {
        "answer":   answer_text,
        "sources":  sources[:2],
        "escalate": escalate,
    }
