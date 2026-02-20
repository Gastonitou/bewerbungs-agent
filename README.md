# Bewerbungs-Agent

AI Agent for Application Management - Automated email analysis and task distribution for job applications.

## Features

- **Email Import**: Automatically reads job application emails from Gmail
- **AI Classification**: Uses OpenAI to classify emails as acceptances or rejections
- **Email Organization**: Automatically moves emails to appropriate folders
- **Attachment Analysis**: Processes PDF and Word document attachments
- **Task Distribution**: Automatically distributes tasks to an agent team
- **Comprehensive Logging**: All actions are logged for transparency

## Technologies

- Python 3.8+
- OpenAI API (GPT-4)
- Google Gmail API with OAuth2
- PyPDF2 for PDF processing
- python-docx for Word document processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the agent:
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
```

## Configuration

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download the credentials as `credentials.json`
6. Place `credentials.json` in the project root

### OpenAI API Setup

1. Get your API key from [OpenAI](https://platform.openai.com/)
2. Add it to `config.yaml`:
```yaml
openai:
  api_key: "sk-your-api-key-here"
```

### Configuration File

Edit `config.yaml` to customize:
- Email folders for organization
- OpenAI model and parameters
- Agent team configuration
- Feature toggles
- Logging settings

## Usage

### Running the Agent

Process unread emails:
```bash
python main.py
```

Process specific emails with query:
```bash
python main.py --query "from:hr@company.com"
```

Test connections without processing:
```bash
python main.py --test-connection
```

Show detailed statistics:
```bash
python main.py --stats
```

### Command-Line Options

- `--config PATH`: Path to configuration file (default: config.yaml)
- `--query QUERY`: Gmail search query (default: is:unread)
- `--max-emails N`: Maximum emails to process (default: 10)
- `--test-connection`: Test API connections only
- `--stats`: Show detailed agent statistics

## Testing

Run the test suite:
```bash
python run_tests.py
```

Or with pytest directly:
```bash
pytest tests/ -v
```

## Architecture

### Components

- **BewerbungsAgent**: Main orchestrator
- **GmailClient**: Gmail API integration
- **EmailParser**: Email content parsing
- **AttachmentProcessor**: PDF/DOCX processing
- **EmailClassifier**: OpenAI-based classification
- **AgentTeam**: Task distribution system

### Workflow

1. Agent fetches emails from Gmail
2. Each email is parsed and attachments are processed
3. OpenAI classifies the email type
4. Email is moved to appropriate folder
5. Tasks are distributed to the agent team
6. All actions are logged

## Agent Team

The agent team consists of:
- **Reviewer**: Reviews application documents
- **Feedback Writer**: Writes feedback for applicants
- **Scheduler**: Schedules interviews and onboarding

Tasks are automatically assigned based on email classification.

## Security

- OAuth2 authentication for Gmail
- API keys stored in configuration (not in code)
- No sensitive data stored externally
- All processing happens locally

## Logging

All actions are logged to:
- File: `logs/agent.log`
- Console (configurable)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Development

### Project Structure

```
bewerbungs-agent/
├── src/
│   └── bewerbungs_agent/
│       ├── __init__.py
│       ├── agent.py              # Main agent
│       ├── config.py             # Configuration
│       ├── gmail_client.py       # Gmail integration
│       ├── email_parser.py       # Email parsing
│       ├── attachment_processor.py # Attachment handling
│       ├── classifier.py         # Email classification
│       ├── agent_team.py         # Task distribution
│       └── logger.py             # Logging setup
├── tests/
│   ├── test_agent.py
│   ├── test_config.py
│   ├── test_email_parser.py
│   ├── test_classifier.py
│   ├── test_agent_team.py
│   └── test_attachment_processor.py
├── main.py                       # CLI interface
├── run_tests.py                  # Test runner
├── requirements.txt              # Dependencies
├── config.example.yaml           # Example configuration
└── README.md                     # This file
```

## Troubleshooting

### Gmail API Issues

- Ensure `credentials.json` is in the correct location
- Run with `--test-connection` to verify setup
- Check that Gmail API is enabled in Google Cloud Console

### OpenAI API Issues

- Verify your API key is correct
- Check your OpenAI account has credits
- Agent falls back to keyword-based classification if API fails

### No Emails Found

- Check your Gmail query syntax
- Verify emails exist matching the query
- Try `--query "is:inbox"` to process all inbox emails

## License

This project is for educational and personal use.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions