# bewerbungs-agent

KI-gestützter Agent zur automatischen Verarbeitung von Bewerbungs-E-Mails.

## Funktionsumfang

| Funktion | Beschreibung |
|---|---|
| **E-Mail-Import** | Liest Bewerbungen aus dem Gmail-Postfach via Gmail API (OAuth2) |
| **Klassifikation** | GPT-4o klassifiziert jede E-Mail als *Zusage*, *Absage* oder *Sonstige* |
| **Sortierung** | Absagen werden automatisch in das Label „Absagen", Zusagen in „Zusagen" verschoben |
| **Attachment-Analyse** | PDF, DOCX und RTF-Anhänge werden extrahiert und in die Klassifikation einbezogen |
| **Teamwork** | Virtuelles Agenten-Team (Reviewer, FeedbackWriter, Archiver) übernimmt Folgeaufgaben |
| **Logging** | Alle Aktionen werden in `bewerbungs_agent.log` protokolliert (rotierende Dateien) |

## Voraussetzungen

- Python 3.11+
- Google Cloud-Projekt mit aktivierter Gmail API und heruntergeladenem `credentials.json`
- OpenAI API-Key

## Installation

```bash
pip install -r requirements.txt
```

## Konfiguration

Kopiere `config.yaml` und passe die Werte an:

```yaml
gmail:
  credentials_file: "credentials.json"   # OAuth2-Credentials aus der Google Cloud Console
  token_file: "token.json"               # Wird automatisch erstellt
  email_address: "deine@email.com"
  rejection_label: "Absagen"
  acceptance_label: "Zusagen"

openai:
  model: "gpt-4o"
```

Setze den OpenAI API-Key als Umgebungsvariable:

```bash
export OPENAI_API_KEY="sk-..."
```

## Verwendung

```bash
# Einmalig: Browser-Login für Gmail OAuth2
OPENAI_API_KEY=sk-... python -m agent.main --config config.yaml

# Testlauf ohne E-Mails zu verschieben
OPENAI_API_KEY=sk-... python -m agent.main --config config.yaml --dry-run
```

## Projektstruktur

```
bewerbungs-agent/
├── agent/
│   ├── __init__.py
│   ├── main.py               # Haupt-Orchestrierung
│   ├── gmail_client.py       # Gmail API (OAuth2, Lesen, Verschieben, Anhänge)
│   ├── classifier.py         # OpenAI-Klassifikation (Zusage/Absage/Sonstige)
│   ├── attachment_handler.py # Text-Extraktion aus PDF/DOCX/RTF
│   ├── task_manager.py       # Virtuelles Agenten-Team & Aufgabenverteilung
│   └── logger.py             # Strukturiertes Logging
├── config.yaml               # Konfigurationsdatei
├── requirements.txt
└── README.md
```

## Sicherheitshinweise

- `credentials.json` und `token.json` **niemals** in Git einchecken (`.gitignore` empfohlen).
- Anhänge werden nur im temporären Verzeichnis (`/tmp/...`) zwischengespeichert und sofort nach der Verarbeitung gelöscht.
- Es werden keine personenbezogenen Daten an externe Dienste gesendet, außer an die OpenAI API zur Klassifikation.