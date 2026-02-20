"""
Email classification via OpenAI.

Classifies each email (together with extracted attachment text) as one of:
- "Zusage"  – acceptance / positive response
- "Absage"  – rejection
- "Sonstige" – other / unclear

Returns a structured result that includes the category, a confidence note,
and a brief German-language summary suitable for logging.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from agent.logger import get_logger

logger = get_logger("classifier")

CLASSIFICATION_CATEGORIES = ("Zusage", "Absage", "Sonstige")

_SYSTEM_PROMPT = """
Du bist ein KI-Assistent für Bewerbungsmanagement.
Analysiere die folgende E-Mail (inklusive etwaiger Anhangsinhalte) und klassifiziere sie in genau eine der folgenden Kategorien:

- Zusage: Das Unternehmen lädt den Bewerber zum Vorstellungsgespräch ein, gibt eine positive Rückmeldung oder bietet eine Stelle an.
- Absage: Das Unternehmen lehnt die Bewerbung ab.
- Sonstige: Alles andere (Eingangsbestätigung, Rückfragen, Newsletter usw.).

Antworte ausschließlich im folgenden JSON-Format – kein weiterer Text:
{
  "kategorie": "<Zusage|Absage|Sonstige>",
  "zusammenfassung": "<Kurze deutsche Zusammenfassung in 1-2 Sätzen>",
  "begruendung": "<Kurze Begründung der Klassifikation>"
}
""".strip()


@dataclass
class ClassificationResult:
    """Result of classifying a single email."""

    message_id: str
    subject: str
    category: str  # "Zusage" | "Absage" | "Sonstige"
    summary: str = ""
    reasoning: str = ""
    error: Optional[str] = field(default=None)

    @property
    def is_rejection(self) -> bool:
        return self.category == "Absage"

    @property
    def is_acceptance(self) -> bool:
        return self.category == "Zusage"


class Classifier:
    """Uses OpenAI to classify job-application emails."""

    def __init__(self, model: str = "gpt-4o", max_tokens: int = 1024, temperature: float = 0.2) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set."
            )
        self.client = OpenAI(api_key=api_key)

    def classify(
        self,
        message_id: str,
        subject: str,
        body: str,
        attachment_texts: Optional[list[str]] = None,
    ) -> ClassificationResult:
        """
        Classify a single email.

        Parameters
        ----------
        message_id : str
            Gmail message ID (used for logging / result tracking).
        subject : str
            Email subject line.
        body : str
            Plain-text email body.
        attachment_texts : list[str], optional
            Extracted text content from attachments.

        Returns
        -------
        ClassificationResult
        """
        user_content = self._build_user_content(subject, body, attachment_texts or [])

        logger.info("Classifying message %s (subject: '%s').", message_id, subject)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            logger.error("OpenAI API error for message %s: %s", message_id, exc)
            return ClassificationResult(
                message_id=message_id,
                subject=subject,
                category="Sonstige",
                error=str(exc),
            )

        raw = response.choices[0].message.content or ""
        return self._parse_response(message_id, subject, raw)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_content(
        subject: str, body: str, attachment_texts: list[str]
    ) -> str:
        parts = [
            f"**Betreff:** {subject}",
            "",
            "**E-Mail-Inhalt:**",
            body[:8000],  # Guard against very large emails
        ]

        for i, att_text in enumerate(attachment_texts, start=1):
            if att_text:
                parts += [
                    "",
                    f"**Anhang {i}:**",
                    att_text[:4000],  # Guard against very large attachments
                ]

        return "\n".join(parts)

    @staticmethod
    def _parse_response(
        message_id: str, subject: str, raw: str
    ) -> ClassificationResult:
        import json

        try:
            data = json.loads(raw)
            category = data.get("kategorie", "Sonstige")
            if category not in CLASSIFICATION_CATEGORIES:
                logger.warning(
                    "Unexpected category '%s' from OpenAI; defaulting to 'Sonstige'.",
                    category,
                )
                category = "Sonstige"
            return ClassificationResult(
                message_id=message_id,
                subject=subject,
                category=category,
                summary=data.get("zusammenfassung", ""),
                reasoning=data.get("begruendung", ""),
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error(
                "Failed to parse OpenAI response for message %s: %s | raw=%s",
                message_id,
                exc,
                raw[:200],
            )
            return ClassificationResult(
                message_id=message_id,
                subject=subject,
                category="Sonstige",
                error=f"Parse error: {exc}",
            )
