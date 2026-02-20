"""Classifier: use OpenAI to decide whether an email is a job offer, rejection, or other."""
import logging
import os
from typing import Literal

from openai import OpenAI

logger = logging.getLogger(__name__)

EmailCategory = Literal["zusage", "absage", "sonstiges"]

SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Bewerbungs-E-Mails analysiert. "
    "Entscheide anhand des folgenden E-Mail-Textes (und ggf. Anhangsinhalts), "
    "ob es sich um eine ZUSAGE (Einladung zum Vorstellungsgespräch oder Jobangebot), "
    "eine ABSAGE (Ablehnung) oder SONSTIGES handelt. "
    "Antworte ausschließlich mit einem dieser drei Wörter (Großschreibung egal): "
    "zusage, absage, sonstiges."
)


def classify_email(body: str, attachment_text: str = "") -> EmailCategory:
    """Return 'zusage', 'absage', or 'sonstiges' for the given email content."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    content = body
    if attachment_text:
        content += f"\n\n[Anhang]\n{attachment_text}"

    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content[:8000]},  # stay within token budget
        ],
        temperature=0,
        max_tokens=10,
    )
    raw = response.choices[0].message.content.strip().lower()
    if raw in ("zusage", "absage", "sonstiges"):
        return raw  # type: ignore[return-value]
    logger.warning("Unexpected classification response '%s', defaulting to 'sonstiges'", raw)
    return "sonstiges"
