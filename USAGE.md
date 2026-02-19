# Usage Guide for Bewerbungs-Agent

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example configuration:
```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` and configure:
- Gmail settings (email address, folder names)
- OpenAI API key
- Agent team configuration

### 3. Gmail API Setup (Optional, for production use)

If you want to connect to real Gmail:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop app)
5. Download as `credentials.json` in project root
6. First run will open browser for authentication

### 4. Running the Agent

**Test mode (no credentials needed):**
```bash
python main.py --test-connection
```

**Process unread emails:**
```bash
python main.py
```

**Process specific emails:**
```bash
python main.py --query "from:hr@company.com"
```

**Show statistics:**
```bash
python main.py --stats
```

## Testing

### Run all tests:
```bash
python run_tests.py
```

### Run specific test file:
```bash
pytest tests/test_classifier.py -v
```

### Run demo:
```bash
python demo.py
```

## Features in Detail

### 1. Email Classification

The agent classifies emails as:
- **Acceptance (Zusage)**: Job offers, positive responses
- **Rejection (Absage)**: Rejections, negative responses
- **Unknown**: Unclear emails requiring manual review

Classification uses:
- OpenAI GPT-4 (if API key provided)
- Fallback keyword matching (German & English)

### 2. Attachment Processing

Supports:
- PDF files (via PyPDF2)
- DOCX files (via python-docx)
- Text extraction for classification

### 3. Email Organization

Automatically moves emails to folders:
- Acceptances → "Zusagen"
- Rejections → "Absagen"
- Unknown → "Verarbeitet"

Folder names are configurable in `config.yaml`.

### 4. Agent Team

Three specialized agents:
- **Reviewer**: Reviews documents and unclear cases
- **Feedback Writer**: Handles responses
- **Scheduler**: Manages interviews and onboarding

Tasks are automatically distributed based on email type.

### 5. Logging

All actions logged to:
- `logs/agent.log` (file)
- Console (configurable)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Configuration Options

### Gmail Settings
```yaml
gmail:
  email: "your-email@gmail.com"
  credentials_file: "credentials.json"
  token_file: "token.json"
  folders:
    rejections: "Absagen"
    acceptances: "Zusagen"
    processed: "Verarbeitet"
```

### OpenAI Settings
```yaml
openai:
  api_key: "sk-..."
  model: "gpt-4"
  temperature: 0.3
```

### Agent Features
```yaml
agent:
  features:
    classify_emails: true
    analyze_attachments: true
    move_to_folders: true
    team_distribution: true
```

### Logging Settings
```yaml
logging:
  level: "INFO"
  file: "logs/agent.log"
  console: true
```

## Advanced Usage

### Environment Variables

Override config with environment variables:
```bash
export BEWERBUNGS_CONFIG=/path/to/config.yaml
export GMAIL_EMAIL=your-email@gmail.com
export OPENAI_API_KEY=sk-...
export LOG_LEVEL=DEBUG
```

### Custom Queries

Gmail search query syntax:
```bash
# From specific sender
python main.py --query "from:hr@company.com"

# Subject contains
python main.py --query "subject:Bewerbung"

# Date range
python main.py --query "after:2026/01/01"

# Combine criteria
python main.py --query "from:hr@company.com subject:Zusage"
```

### Programmatic Usage

```python
from src.bewerbungs_agent.agent import BewerbungsAgent

# Initialize agent
agent = BewerbungsAgent(config_path='config.yaml')

# Test connections
connections = agent.test_connection()
print(f"Gmail: {connections['gmail']}")
print(f"OpenAI: {connections['openai']}")

# Process emails
results = agent.run(query='is:unread', max_emails=10)
print(f"Processed: {results['processed']}")
print(f"Acceptances: {results['acceptances']}")
print(f"Rejections: {results['rejections']}")

# Get statistics
stats = agent.get_agent_stats()
print(stats)
```

## Troubleshooting

### Problem: Gmail not connecting
**Solution:**
- Verify `credentials.json` exists
- Run with `--test-connection` to check
- Ensure Gmail API is enabled
- Check token.json has valid credentials

### Problem: OpenAI classification not working
**Solution:**
- Verify API key in config.yaml
- Check OpenAI account has credits
- Agent will fallback to keyword matching

### Problem: No emails found
**Solution:**
- Check query syntax
- Verify emails exist: `--query "is:inbox"`
- Check Gmail authentication

### Problem: Attachments not processing
**Solution:**
- Ensure PyPDF2 and python-docx installed
- Check attachment file types (PDF/DOCX only)
- Review logs for errors

## Security Best Practices

1. **Never commit credentials:**
   - Keep `credentials.json` and `token.json` out of git
   - Use `.gitignore` (already configured)

2. **Store API keys securely:**
   - Use environment variables for production
   - Don't share config.yaml with API keys

3. **OAuth2 tokens:**
   - Tokens auto-refresh
   - Delete `token.json` to re-authenticate

4. **Data privacy:**
   - All processing happens locally
   - No data sent to external services except APIs

## Performance Tips

1. **Limit email processing:**
   ```bash
   python main.py --max-emails 5
   ```

2. **Use specific queries:**
   ```bash
   python main.py --query "is:unread from:hr@company.com"
   ```

3. **Disable features if not needed:**
   ```yaml
   agent:
     features:
       analyze_attachments: false  # Skip if no attachments
   ```

4. **Adjust log level:**
   ```yaml
   logging:
     level: "WARNING"  # Less verbose
   ```

## Getting Help

- Check logs in `logs/agent.log`
- Run with `--test-connection` to diagnose
- Review test results: `python run_tests.py`
- Open issue on GitHub

## Examples

### Example 1: Test without credentials
```bash
python demo.py
```

### Example 2: Process today's emails
```bash
python main.py --query "after:$(date +%Y/%m/%d)"
```

### Example 3: Dry run (test mode)
```bash
python main.py --test-connection
```

### Example 4: Full processing with stats
```bash
python main.py --query "is:unread" --max-emails 20 --stats
```
