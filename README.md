# Bewerbungs Agent - Job Application Automation Tool

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **legally compliant**, **SaaS-ready** job application automation system that helps users prepare high-quality job applications with built-in human approval gates.

## 🚨 LEGAL DISCLAIMER

**This tool assists with preparing job applications but NEVER submits applications without explicit user consent.**

- ✅ Automatically prepares application documents
- ✅ Generates tailored cover letters and CV optimization suggestions
- ✅ Requires human approval before any submission
- ❌ Does NOT automatically submit applications
- ❌ Does NOT bypass CAPTCHAs or bot detection
- ❌ Does NOT violate terms of service of job platforms

**By using this tool, you agree that you are responsible for reviewing and approving all applications before submission.**

## 🎯 Features

### Core Functionality

- **Multi-Source Job Intake**
  - Gmail job alert parsing
  - Manual URL input
  - CSV import (LinkedIn/Indeed exports)
  
- **Intelligent Document Generation**
  - Tailored cover letters (German & English)
  - CV keyword optimization suggestions
  - Pre-filled form answers
  - Fit score calculation (0-100%)

- **Human-in-the-Loop Workflow**
  - Status flow: `DRAFT → REVIEW_REQUIRED → USER_APPROVED → READY_TO_SUBMIT`
  - Explicit approval required for every application
  - Safe export options (PDF, text, draft emails)

- **Email Intelligence**
  - Automatic classification (job alerts, rejections, interviews, offers)
  - Gmail integration via OAuth (no password storage)
  - Email labeling and tracking

- **SaaS-Ready Architecture**
  - Multi-tenant user isolation
  - Subscription tiers (Free, Pro, Agency)
  - Usage limits and tracking
  - PostgreSQL-ready database abstraction

## 📋 Requirements

- Python 3.11 or higher
- Gmail account (for email integration)
- Google Cloud project with Gmail API enabled

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to the project root
6. Update `.env` with your credentials

### 6. Initialize Database

```bash
bewerbungs-agent init
```

## 📖 Usage

### Command-Line Interface

#### Create a User

```bash
bewerbungs-agent create-user --email user@example.com --plan free
```

#### Create User Profile

```bash
bewerbungs-agent create-profile \
  --user-id 1 \
  --name "John Doe" \
  --skills "Python, SQL, Machine Learning, Docker" \
  --cv-text "path/to/cv.txt"
```

#### Sync Gmail Job Alerts

```bash
bewerbungs-agent sync-gmail --user-id 1
```

This will:
- Authenticate with Gmail (first time only)
- Fetch job-related emails
- Classify them automatically
- Store in database

#### Prepare Applications (DRAFT)

```bash
bewerbungs-agent prepare-applications --user-id 1 --limit 10
```

This creates DRAFT applications but **does NOT submit** them.

#### Review Queue

```bash
bewerbungs-agent review-queue --user-id 1
```

Shows applications awaiting your review.

#### Approve Application (CRITICAL STEP)

```bash
bewerbungs-agent approve-application --application-id 1
```

**This is the human approval gate.** Only after approval is the application ready for submission.

#### Export Application Documents

```bash
# Text format
bewerbungs-agent export-application --application-id 1

# JSON format (for automation)
bewerbungs-agent export-application --application-id 1 --format json
```

#### View Metrics

```bash
bewerbungs-agent report-metrics --user-id 1
```

## 🏗️ Architecture

### Database Schema

```
users
├── id (PK)
├── email (unique)
├── plan (free/pro/agency)
├── stripe_customer_id
└── created_at

profiles
├── id (PK)
├── user_id (FK)
├── full_name
├── skills (JSON)
├── cv_text
├── education (JSON)
└── preferences (JSON)

jobs
├── id (PK)
├── source (gmail/manual/csv)
├── company
├── role
├── description
├── requirements
└── application_url

applications
├── id (PK)
├── user_id (FK)
├── job_id (FK)
├── status (workflow)
├── fit_score (0-100)
├── approved_at
└── submitted_at

documents
├── id (PK)
├── application_id (FK)
├── cover_letter_de
├── cover_letter_en
├── cv_optimization_notes
└── form_answers (JSON)

emails
├── id (PK)
├── user_id (FK)
├── message_id (Gmail)
├── category (classification)
├── confidence
└── processed
```

### Application Workflow

```
┌─────────┐
│  DRAFT  │  ← Initial creation
└────┬────┘
     │
     ▼
┌─────────────────┐
│ REVIEW_REQUIRED │  ← Awaiting user review
└────┬────────────┘
     │
     ▼ (User approval required)
┌──────────────────┐
│  USER_APPROVED   │  ← User explicitly approved
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ READY_TO_SUBMIT  │  ← Documents ready for export
└────┬─────────────┘
     │
     ▼ (Manual submission by user)
┌──────────┐
│SUBMITTED │
└──────────┘
```

## 🔒 Security & Privacy

### Data Protection

- ✅ OAuth 2.0 only (no password storage)
- ✅ User data isolation (multi-tenant ready)
- ✅ GDPR-compliant data handling
- ✅ Local SQLite or secure PostgreSQL
- ✅ No automatic external data sharing

### Credentials Management

- **Never commit** `.env` or `credentials.json` to git
- Use environment variables for production
- Rotate API keys regularly
- Use Stripe test keys for development

## 💰 Subscription Tiers

| Feature | Free | Pro | Agency |
|---------|------|-----|--------|
| Applications/month | 10 | 100 | Unlimited |
| Gmail Integration | ✅ | ✅ | ✅ |
| Cover Letter Gen | ✅ | ✅ | ✅ |
| AI Enhancement | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ✅ | ✅ |
| Multi-user | ❌ | ❌ | ✅ |

## 🧪 Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
flake8 src/ tests/
```

### Type Checking

```bash
mypy src/
```

## 📝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/Gastonitou/bewerbungs-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gastonitou/bewerbungs-agent/discussions)

## 🙏 Acknowledgments

This tool is designed to **assist** job seekers, not replace their judgment. Always review applications before submission.

---

**Remember**: This tool prepares applications; **you** decide when to submit them. 🎯