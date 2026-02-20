# 🚀 Bewerbungs-Agent - Schnellstart

## Sofort testen (ohne Zugangsdaten)

```bash
# 1. Tests ausführen
python run_tests.py

# 2. Demo starten
python demo.py

# 3. Agent testen
python main.py --test-connection
```

## Mit echten E-Mails verwenden

```bash
# 1. Konfiguration erstellen
cp config.example.yaml config.yaml

# 2. Ihre Daten eintragen
nano config.yaml
# → E-Mail-Adresse: ghassenlaajili6@gmail.com
# → OpenAI API-Key (optional)

# 3. Gmail-Zugangsdaten einrichten
# → credentials.json von Google Cloud Console

# 4. Agent starten
python main.py
```

## Wichtige Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `python run_tests.py` | Alle Tests ausführen |
| `python demo.py` | Interaktive Demo |
| `python main.py` | Agent starten |
| `python main.py --test-connection` | Verbindung testen |
| `python main.py --help` | Hilfe anzeigen |
| `python main.py --stats` | Mit Statistiken |
| `python main.py --query "from:hr@firma.de"` | Bestimmte E-Mails |

## Was der Agent macht

1. ✅ **Liest** E-Mails aus Gmail
2. 🤖 **Klassifiziert** als Zusage/Absage
3. 📂 **Sortiert** in Ordner (Zusagen/Absagen)
4. 📎 **Analysiert** PDF/DOCX-Anhänge
5. 👥 **Verteilt** Aufgaben an Agenten-Team
6. 📝 **Protokolliert** alle Aktionen

## Features

✅ Deutsche & englische E-Mails  
✅ KI-Klassifizierung (GPT-4)  
✅ Fallback ohne OpenAI (80% genau)  
✅ PDF & DOCX Anhänge  
✅ Automatische Ordner-Sortierung  
✅ 3 spezialisierte Agenten  
✅ Vollständiges Logging  

## Test-Status

**33/33 Tests bestanden ✅**

- Agent-Tests: 6/6 ✓
- Agenten-Team: 6/6 ✓
- Anhänge: 6/6 ✓
- Klassifizierung: 6/6 ✓
- Konfiguration: 5/5 ✓
- E-Mail-Parsing: 4/4 ✓

## Sicherheit

✅ Keine Schwachstellen (CodeQL)  
✅ OAuth2 für Gmail  
✅ Keine Passwörter im Code  
✅ Lokale Verarbeitung  

## Dokumentation

- `README.md` - Übersicht
- `USAGE.md` - Ausführliche Anleitung (EN)
- `TEST_ANLEITUNG.md` - Test-Guide (DE)
- `TEST_SUMMARY.md` - Test-Bericht
- `config.example.yaml` - Beispiel-Config

## Support

📖 Alle Anleitungen im Projekt-Ordner  
🧪 Tests zeigen Beispiele  
🎯 Demo zeigt alle Features  

---

**Status: ✅ EINSATZBEREIT**

Ihr Bewerbungs-Agent ist vollständig getestet und bereit!
