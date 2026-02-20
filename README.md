# bewerbungs-agent

> **KI-gestützter Bewerbungsmail-Manager** – liest dein Gmail-Postfach, klassifiziert Zusagen und Absagen mit OpenAI und sortiert die E-Mails automatisch in Labels.

---

## Funktionsumfang

| Feature | Details |
|---|---|
| 📥 **E-Mail-Import** | Liest ungelesene Mails aus deinem Gmail-Posteingang via Gmail API |
| 🤖 **KI-Klassifikation** | GPT-4o-mini unterscheidet Zusagen, Absagen und sonstige Mails |
| 📁 **Automatische Sortierung** | Zusagen → Label „Zusagen", Absagen → Label „Absagen" |
| 📎 **Anhang-Analyse** | PDF (inkl. OCR-Fallback), DOCX und RTF werden ausgelesen und in die Bewertung einbezogen |
| 📋 **Logging** | Alle Aktionen werden mit Zeitstempel in der Konsole protokolliert |

---

## Voraussetzungen

- Python 3.10+
- Ein **Google Cloud Projekt** mit aktivierter Gmail API und einer OAuth 2.0 Client-ID (Typ „Desktop")
- Ein **OpenAI API-Key**

---

## Einrichtung (einmalig)

### 1. Repository klonen & Abhängigkeiten installieren

```bash
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **OCR-Support (optional):** Für gescannte PDFs wird zusätzlich `tesseract-ocr` und `PyMuPDF` benötigt:
> ```bash
> sudo apt-get install tesseract-ocr  # Ubuntu/Debian
> brew install tesseract               # macOS
> pip install PyMuPDF pytesseract
> ```

### 2. Google Cloud & Gmail API einrichten

1. Öffne die [Google Cloud Console](https://console.cloud.google.com/).
2. Erstelle ein neues Projekt (oder nutze ein bestehendes).
3. Aktiviere die **Gmail API**: *APIs & Dienste → Bibliothek → Gmail API → Aktivieren*.
4. Erstelle OAuth 2.0-Zugangsdaten: *APIs & Dienste → Zugangsdaten → Zugangsdaten erstellen → OAuth-Client-ID → Anwendungstyp: Desktop*.
5. Lade die JSON-Datei herunter und speichere sie als **`credentials.json`** im Projektverzeichnis.

### 3. OpenAI API-Key konfigurieren

Erstelle eine `.env`-Datei im Projektverzeichnis:

```dotenv
OPENAI_API_KEY=sk-...dein-key...
# Optional: anderes Modell verwenden (Standard: gpt-4o-mini)
# OPENAI_MODEL=gpt-4o
```

> **Hinweis:** Die Datei `.env` ist in `.gitignore` eingetragen und wird **nicht** ins Repository eingecheckt.

---

## Nutzung

### Erster Start (OAuth-Authentifizierung)

Beim ersten Aufruf öffnet sich ein Browser-Fenster, in dem du dich mit deinem Google-Konto anmeldest und den Zugriff erlaubst. Das Token wird anschließend in `token.json` gespeichert – ab dann ist kein Browser-Login mehr nötig.

```bash
python main.py
```

### Verfügbare Optionen

```
usage: main.py [-h] [--inbox INBOX] [--zusage-label ZUSAGE_LABEL]
               [--absage-label ABSAGE_LABEL] [--max-emails MAX_EMAILS] [--verbose]

bewerbungs-agent – KI-gestützter Bewerbungsmail-Manager

options:
  -h, --help                     diese Hilfe anzeigen
  --inbox INBOX                  Gmail-Label für den Posteingang (Standard: INBOX)
  --zusage-label ZUSAGE_LABEL    Label für Zusagen/Einladungen (Standard: Zusagen)
  --absage-label ABSAGE_LABEL    Label für Absagen (Standard: Absagen)
  --max-emails MAX_EMAILS        Maximale Anzahl E-Mails pro Lauf (Standard: 50)
  -v, --verbose                  Ausführliche Debug-Ausgabe
```

### Beispiele

```bash
# Standardlauf – verarbeite bis zu 50 ungelesene Mails
python main.py

# Nur die letzten 10 Mails prüfen
python main.py --max-emails 10

# Eigene Label-Namen verwenden
python main.py --zusage-label "Interview" --absage-label "Rejected"

# Mit ausführlichem Logging
python main.py --verbose
```

### Beispielausgabe

```
2026-02-20 08:12:01  INFO      bewerbungs_agent.gmail_service – Fetching up to 50 unread emails from 'INBOX'
2026-02-20 08:12:03  INFO      bewerbungs_agent.gmail_service – Retrieved 3 messages
2026-02-20 08:12:03  INFO      bewerbungs_agent.agent – Processing: Ihre Bewerbung bei Firma XY
2026-02-20 08:12:04  INFO      bewerbungs_agent.agent –   ➜ Kategorie: absage      | Aktion: verschoben nach 'Absagen' | Anhänge: –
2026-02-20 08:12:04  INFO      bewerbungs_agent.agent – Processing: Einladung zum Gespräch
2026-02-20 08:12:05  INFO      bewerbungs_agent.agent –   ➜ Kategorie: zusage      | Aktion: verschoben nach 'Zusagen' | Anhänge: ['einladung.pdf']
2026-02-20 08:12:05  INFO      bewerbungs_agent.agent – Processing: Newsletter
2026-02-20 08:12:06  INFO      bewerbungs_agent.agent –   ➜ Kategorie: sonstiges   | Aktion: keine Aktion (sonstiges) | Anhänge: –
2026-02-20 08:12:06  INFO      bewerbungs_agent.agent – Fertig. 3 E-Mail(s) verarbeitet.

────────────────────────────────────────────────────────────
Betreff                                  Kategorie    Aktion
────────────────────────────────────────────────────────────
Ihre Bewerbung bei Firma XY              absage       verschoben nach 'Absagen'
Einladung zum Gespräch                   zusage       verschoben nach 'Zusagen'
Newsletter                               sonstiges    keine Aktion (sonstiges)
────────────────────────────────────────────────────────────
Gesamt: 3 E-Mail(s) verarbeitet.
```

---

## Projektstruktur

```
bewerbungs-agent/
├── bewerbungs_agent/
│   ├── __init__.py          # Paket-Einstiegspunkt
│   ├── agent.py             # Hauptorchestrator
│   ├── gmail_service.py     # Gmail OAuth2 & API-Wrapper
│   ├── classifier.py        # OpenAI-Klassifikation
│   └── attachment_handler.py# PDF / DOCX / RTF Textextraktion
├── main.py                  # CLI-Einstiegspunkt
├── requirements.txt         # Python-Abhängigkeiten
├── .env                     # Deine Secrets (NICHT einchecken!)
├── credentials.json         # Google OAuth-Zugangsdaten (NICHT einchecken!)
└── token.json               # Gespeichertes OAuth-Token (wird automatisch erstellt)
```

---

## Sicherheitshinweise

- `credentials.json` und `token.json` enthalten sensible Zugangsdaten und sind in `.gitignore` eingetragen – **niemals in ein öffentliches Repository einchecken**.
- Der Agent verwendet **nur Lese- und Label-Berechtigungen** (`gmail.readonly`, `gmail.modify`, `gmail.labels`). Das Senden von E-Mails ist bewusst **nicht** freigeschaltet.
- Anhangsinhalte werden ausschließlich lokal verarbeitet und **nicht extern gespeichert**.

---

## Lizenz

MIT