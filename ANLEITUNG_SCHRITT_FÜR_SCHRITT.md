# 📝 Bewerbungs-Agent - Schritt-für-Schritt Anleitung

## 🎯 Diese Anleitung zeigt Ihnen GENAU, wie Sie die Schritte durchführen

Folgen Sie einfach dieser Anleitung von oben nach unten!

---

## Schritt 1: Zum Projekt-Verzeichnis wechseln

```bash
cd /home/runner/work/bewerbungs-agent/bewerbungs-agent
```

**Was passiert:** Sie wechseln in das Projekt-Verzeichnis.

---

## Schritt 2: Dependencies installieren

```bash
pip install -r requirements.txt
```

**Was passiert:** 
- Python installiert alle benötigten Bibliotheken
- Dauert ca. 30 Sekunden
- Sie sehen viele Zeilen mit "Successfully installed..."

**Erwartete Ausgabe:**
```
Successfully installed google-auth-2.27.0 openai-1.12.0 PyPDF2-3.0.1 ...
```

---

## Schritt 3: Alle Tests ausführen

```bash
python run_tests.py
```

**Was passiert:**
- 33 automatische Tests werden ausgeführt
- Jeder Test prüft eine Funktion des Agents
- Dauert ca. 2-3 Sekunden

**Erwartete Ausgabe:**
```
============================================================
Bewerbungs-Agent Test Suite
============================================================
...
✓ All tests passed!
============================================================
```

✅ **Erfolg!** Wenn Sie diese Meldung sehen, funktioniert alles!

---

## Schritt 4: Interaktive Demo starten

```bash
python demo.py
```

**Was passiert:**
- Zeigt 4 Demos der Agent-Funktionen
- Demonstriert Klassifizierung von E-Mails
- Zeigt Agenten-Team in Aktion
- Brauchen Sie mehrmals ENTER drücken

**Erwartete Ausgabe:**
```
DEMO 1: Email Classification
Testing: German Rejection
Result: REJECTION
Confidence: 80.00%
...
```

📌 **Tipp:** Drücken Sie ENTER nach jeder Demo, um die nächste zu sehen.

---

## Schritt 5: Agent im Test-Modus starten

```bash
python main.py --test-connection
```

**Was passiert:**
- Agent wird initialisiert
- Verbindungen werden getestet
- Läuft OHNE Gmail/OpenAI Zugangsdaten
- Zeigt Status aller Komponenten

**Erwartete Ausgabe:**
```
============================================================
Bewerbungs-Agent - AI Agent for Application Management
============================================================
✓ Agent initialized successfully

Testing connections...
  Gmail API: ✗ Not connected (test mode)
  OpenAI API: ✗ Not connected (fallback mode)
```

✅ **Das ist normal!** Im Test-Modus sind keine echten Verbindungen nötig.

---

## Schritt 6: Agent-Hilfe anzeigen

```bash
python main.py --help
```

**Was passiert:**
- Zeigt alle verfügbaren Befehle
- Erklärt alle Optionen

**Erwartete Ausgabe:**
```
usage: main.py [-h] [--config CONFIG] [--query QUERY] ...

Bewerbungs-Agent - AI Agent for Application Management

options:
  --config CONFIG       Path to configuration file
  --query QUERY         Gmail search query
  --max-emails N        Maximum emails to process
  --test-connection     Test connections
  --stats              Show statistics
```

---

## 🎉 Fertig! Grundlegende Tests abgeschlossen

Sie haben jetzt erfolgreich:
- ✅ Dependencies installiert
- ✅ Alle 33 Tests ausgeführt
- ✅ Die Demo gesehen
- ✅ Den Agent im Test-Modus gestartet

---

## 🚀 Nächste Schritte (Optional)

### Schritt 7: Mit echten E-Mails arbeiten (benötigt Zugangsdaten)

#### 7.1 Konfiguration erstellen

```bash
cp config.example.yaml config.yaml
```

**Was passiert:** Erstellt Ihre persönliche Konfigurationsdatei.

#### 7.2 Konfiguration bearbeiten

```bash
nano config.yaml
```
oder
```bash
vi config.yaml
```

**Was ändern:**
```yaml
gmail:
  email: "ghassenlaajili6@gmail.com"  # ← Ihre E-Mail hier

openai:
  api_key: "sk-..."  # ← Ihr OpenAI Key hier (optional)
```

**Speichern:** 
- In nano: `Ctrl+X`, dann `Y`, dann `Enter`
- In vi: `ESC`, dann `:wq`, dann `Enter`

#### 7.3 Gmail API einrichten

**Wichtig:** Sie brauchen eine `credentials.json` Datei von Google Cloud Console.

**Wie Sie die Datei bekommen:**

1. Gehen Sie zu https://console.cloud.google.com/
2. Erstellen Sie ein neues Projekt oder wählen Sie ein bestehendes
3. Gehen Sie zu "APIs & Services" → "Library"
4. Suchen Sie "Gmail API" und aktivieren Sie sie
5. Gehen Sie zu "APIs & Services" → "Credentials"
6. Klicken Sie "Create Credentials" → "OAuth client ID"
7. Wählen Sie "Desktop app" als Anwendungstyp
8. Laden Sie die JSON-Datei herunter
9. Benennen Sie sie um in `credentials.json`
10. Legen Sie sie ins Projekt-Verzeichnis:
    ```bash
    mv ~/Downloads/client_secret_*.json credentials.json
    ```

#### 7.4 Agent mit echten E-Mails starten

```bash
python main.py
```

**Was passiert:**
- Beim ersten Start öffnet sich Ihr Browser
- Sie müssen sich bei Google anmelden
- Google fragt nach Berechtigung für Gmail-Zugriff
- Nach Bestätigung: Agent verarbeitet E-Mails!

**Erwartete Ausgabe:**
```
Processing Results:
Total processed: 5
  Acceptances: 2
  Rejections: 3
  Unknown: 0
```

---

## 📊 Praktische Beispiele

### Beispiel 1: Nur 5 E-Mails verarbeiten
```bash
python main.py --max-emails 5
```

### Beispiel 2: E-Mails von bestimmtem Absender
```bash
python main.py --query "from:hr@firma.de"
```

### Beispiel 3: E-Mails mit Betreff "Bewerbung"
```bash
python main.py --query "subject:Bewerbung"
```

### Beispiel 4: Mit Statistiken
```bash
python main.py --stats
```

---

## 🔧 Fehlerbehebung

### Problem: "pip: command not found"
**Lösung:**
```bash
python -m pip install -r requirements.txt
```

### Problem: "python: command not found"
**Lösung:** Versuchen Sie:
```bash
python3 run_tests.py
python3 demo.py
python3 main.py --test-connection
```

### Problem: Tests schlagen fehl
**Lösung:**
```bash
# Dependencies neu installieren
pip install -r requirements.txt --force-reinstall

# Einzelnen Test ausführen
pytest tests/test_classifier.py -v
```

### Problem: "Permission denied"
**Lösung:**
```bash
chmod +x main.py
chmod +x demo.py
chmod +x run_tests.py
```

---

## 📁 Wichtige Dateien

| Datei | Beschreibung |
|-------|--------------|
| `main.py` | Hauptprogramm - Startet den Agent |
| `demo.py` | Demonstrations-Skript |
| `run_tests.py` | Führt alle Tests aus |
| `config.yaml` | Ihre Konfiguration (nach Schritt 7.1) |
| `credentials.json` | Gmail-Zugangsdaten (nach Schritt 7.3) |
| `requirements.txt` | Liste aller Dependencies |

---

## 📚 Weitere Hilfe

- **Schnellstart:** Lesen Sie `SCHNELLSTART.md`
- **Ausführliche Tests:** Lesen Sie `TEST_ANLEITUNG.md`
- **Englische Doku:** Lesen Sie `README.md` oder `USAGE.md`

---

## ✅ Checkliste

Gehen Sie diese Liste durch:

- [ ] Schritt 1: Verzeichnis gewechselt ✓
- [ ] Schritt 2: Dependencies installiert ✓
- [ ] Schritt 3: Tests ausgeführt (33/33 bestanden) ✓
- [ ] Schritt 4: Demo gesehen ✓
- [ ] Schritt 5: Agent im Test-Modus gestartet ✓
- [ ] Schritt 6: Hilfe angezeigt ✓

**Optional (für echte E-Mails):**
- [ ] Schritt 7.1: config.yaml erstellt
- [ ] Schritt 7.2: E-Mail-Adresse eingetragen
- [ ] Schritt 7.3: credentials.json von Google heruntergeladen
- [ ] Schritt 7.4: Agent mit echten E-Mails gestartet

---

## 💡 Zusammenfassung

**Für schnelles Testen (KEINE Zugangsdaten nötig):**
```bash
pip install -r requirements.txt
python run_tests.py
python demo.py
python main.py --test-connection
```

**Für Produktiv-Einsatz (MIT Zugangsdaten):**
```bash
cp config.example.yaml config.yaml
# config.yaml bearbeiten
# credentials.json hinzufügen
python main.py
```

---

🎉 **Viel Erfolg mit Ihrem Bewerbungs-Agent!**

Bei Fragen schauen Sie in die anderen Dokumentations-Dateien oder führen Sie einfach die Befehle aus - sie sind sicher und zeigen Ihnen, was der Agent kann!
