"""FAQs router — static suggested questions by language."""

from fastapi import APIRouter

router = APIRouter(prefix="/faqs", tags=["faqs"])

_SUGGESTIONS: dict[str, list[str]] = {
    "en": [
        "I can't connect to VPN",
        "My computer won't start",
        "I need access to a shared drive",
        "How do I reset my password?",
        "My email isn't working",
        "I need to install new software",
        "My printer is not working",
    ],
    "da": [
        "Jeg kan ikke oprette forbindelse til VPN",
        "Min computer vil ikke starte",
        "Jeg har brug for adgang til et delt drev",
        "Hvordan nulstiller jeg min adgangskode?",
        "Min e-mail virker ikke",
        "Jeg skal installere ny software",
        "Min printer virker ikke",
    ],
}


@router.get("")
async def list_faqs(language: str = "en") -> dict:
    """Return suggested questions for the given language."""
    suggestions = _SUGGESTIONS.get(language, _SUGGESTIONS["en"])
    return {"suggestions": suggestions}
