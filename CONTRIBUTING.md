# Contributing to Bewerbungs Agent

Thank you for your interest in contributing to Bewerbungs Agent!

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Format code: `black src/ tests/`
7. Check linting: `flake8 src/ tests/`
8. Commit with clear messages
9. Push and create a pull request

## Development Setup

```bash
# Clone repository
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent

# Run setup script
bash setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for public functions
- Keep functions focused and testable
- Use meaningful variable names

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_user_service.py

# Run with coverage
pytest --cov=bewerbungs_agent --cov-report=html
```

## Project Structure

```
bewerbungs-agent/
├── src/bewerbungs_agent/    # Main package
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── cli/                 # CLI commands
│   └── utils/               # Utilities
├── tests/                   # Test files
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
└── docs/                    # Documentation
```

## Key Principles

### Security First

- Never commit secrets or credentials
- Always use OAuth for authentication
- Validate all user inputs
- Follow secure coding practices

### Human Approval Gate

The core principle is **never auto-submit applications**:

- Always require explicit user approval
- Use the status workflow: DRAFT → REVIEW_REQUIRED → USER_APPROVED → READY_TO_SUBMIT
- Make approval commands clear and confirmable

### Multi-Tenant Ready

- Isolate user data properly
- Respect plan limits
- Design for scalability

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Update API documentation as needed

## Questions?

Open an issue or start a discussion!
