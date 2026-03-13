from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from dotenv import load_dotenv

load_dotenv()

from agents import orchestrator
import store

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev server
        "http://localhost:5173",   # kept for backwards compat
        # Add your Azure App Service frontend URL here when deployed:
        # "https://<your-frontend-app>.azurewebsites.net",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"            # "en" or "da"
    images: list[str] = []          # base64-encoded images (up to 3) for vision

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: str                     # "up" or "down"

class TicketRequest(BaseModel):
    session_id: str
    summary: str
    description: str
    user_name: str = "Employee"
    priority: str = "medium"        # "low" | "medium" | "high" | "urgent"

class SummarizeRequest(BaseModel):
    session_id: str
    language: str = "en"

# ── Chat ───────────────────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(req: ChatRequest):
    result = orchestrator.process(
        session_id=req.session_id,
        message=req.message,
        language=req.language,
        images=req.images or None,
    )

    message_id = str(uuid.uuid4())
    store.add_message(
        req.session_id,
        req.message,
        result["answer"],
        result.get("sources", []),
        result.get("escalate", False),
    )
    store.record_question(req.message)

    return {
        "message_id": message_id,
        "answer":     result["answer"],
        "sources":    result.get("sources", []),
        "escalate":   result.get("escalate", False),
    }

@app.post("/feedback")
async def feedback(req: FeedbackRequest):
    store.record_feedback(req.session_id, req.message_id, req.rating)
    return {"ok": True}

# ── Tickets ────────────────────────────────────────────────────────────────────

@app.post("/tickets/summarize")
async def summarize_ticket(req: SummarizeRequest):
    return orchestrator.summarize_ticket(req.session_id, req.language)

@app.post("/tickets")
async def create_ticket(req: TicketRequest):
    ticket = store.create_ticket(
        req.session_id, req.summary, req.description, req.user_name
    )
    return ticket

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        return {"error": "Ticket not found"}
    return ticket

# ── Admin ──────────────────────────────────────────────────────────────────────

@app.get("/admin/stats")
async def admin_stats():
    return store.get_stats()

@app.get("/admin/conversations")
async def admin_conversations():
    return store.get_all_conversations()

@app.get("/admin/tickets")
async def admin_tickets():
    return store.get_all_tickets()

# ── Suggested questions ────────────────────────────────────────────────────────

@app.get("/suggestions")
async def suggestions(language: str = "en"):
    if language == "da":
        return {"suggestions": [
            "Hvad er vores adgangskodepolitik?",
            "Hvordan opretter jeg forbindelse til VPN?",
            "Hvornår afgår næste færge fra Aarhus?",
            "Hvad er billetpriserne Aarhus–Odden?",
            "Hvordan anmoder jeg om ny software?",
            "Hvad gør jeg, hvis min laptop er stjålet?",
            "Hvad er IT-supportens åbningstider?",
        ]}
    return {"suggestions": [
        "What is our password policy?",
        "How do I connect to VPN?",
        "When is the next ferry from Aarhus?",
        "What are the ticket prices for Aarhus–Odden?",
        "How do I request new software?",
        "What should I do if my laptop is stolen?",
        "What are IT support hours?",
    ]}
