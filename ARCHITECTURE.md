# Architecture Documentation

## System Overview

Bewerbungs Agent is a multi-tenant SaaS application for job application automation with mandatory human approval gates.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Interface                       │
│  (bewerbungs-agent command with sub-commands)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Service Layer                            │
├─────────────────────────────────────────────────────────────┤
│  - UserService / ProfileService                             │
│  - JobService                                               │
│  - ApplicationService (with approval workflow)              │
│  - DocumentService (cover letters, CV optimization)         │
│  - GmailService (OAuth, sync, classify)                     │
│  - StripeService (subscription management)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Database Layer                            │
├─────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)      │
│  Tables: users, profiles, jobs, applications,               │
│          documents, emails                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
┌───────────▼──────┐   ┌────────▼──────────┐
│   Gmail API      │   │  Stripe API       │
│   (OAuth 2.0)    │   │  (Webhooks)       │
└──────────────────┘   └───────────────────┘
```

## Data Flow

### Application Preparation Flow

```
1. Gmail Sync
   ┌──────────┐
   │  Gmail   │
   └────┬─────┘
        │ OAuth 2.0
        ▼
   ┌──────────┐      ┌──────────────┐
   │ Gmail    │──────│ Email        │
   │ Service  │      │ (job_alert)  │
   └──────────┘      └──────┬───────┘
                            │
2. Prepare Applications     │
   ┌────────────────────────▼─────────┐
   │ Parse job details                │
   │ Create Job record                │
   │ Calculate fit score              │
   │ Create Application (DRAFT)       │
   │ Generate Documents               │
   │ → Status: REVIEW_REQUIRED        │
   └────────────┬─────────────────────┘
                │
3. Human Review & Approval (CRITICAL)
                │
   ┌────────────▼─────────────────────┐
   │ User reviews via review-queue    │
   │ User runs approve-application    │
   │ → Status: USER_APPROVED          │
   │ → Status: READY_TO_SUBMIT        │
   └────────────┬─────────────────────┘
                │
4. Export & Manual Submission
                │
   ┌────────────▼─────────────────────┐
   │ export-application               │
   │ User manually submits            │
   │ → Status: SUBMITTED (user marks) │
   └──────────────────────────────────┘
```

## Application Workflow State Machine

```
┌───────┐
│ DRAFT │ ← Initial creation
└───┬───┘
    │
    │ mark_for_review()
    ▼
┌─────────────────┐
│ REVIEW_REQUIRED │ ← Awaiting user review
└───┬─────────────┘
    │
    │ approve_application() ← APPROVAL GATE
    ▼
┌──────────────────┐
│ USER_APPROVED    │ ← User explicitly approved
└───┬──────────────┘
    │
    │ mark_ready_to_submit()
    ▼
┌──────────────────┐
│ READY_TO_SUBMIT  │ ← Documents exported
└───┬──────────────┘
    │
    │ mark_submitted() (manual)
    ▼
┌──────────┐
│SUBMITTED │
└────┬─────┘
     │
     ├──→ REJECTED
     ├──→ INTERVIEW
     └──→ OFFER
```

## Database Schema

```
users
├── id (PK)
├── email (unique)
├── plan (enum: free/pro/agency)
├── stripe_customer_id
└── created_at, updated_at, is_active

profiles
├── id (PK)
├── user_id (FK → users)
├── full_name, phone, location
├── skills (JSON: ["Python", "SQL", ...])
├── cv_text (TEXT)
├── experience_years
├── education (JSON: [{...}, ...])
├── work_history (JSON: [{...}, ...])
├── preferences (JSON: {...})
└── languages (JSON: [{...}, ...])

jobs
├── id (PK)
├── source (enum: gmail/manual/csv)
├── url, company, role
├── description, requirements
├── location, salary_range
├── application_type, application_email
└── raw_data (JSON), created_at

applications
├── id (PK)
├── user_id (FK → users)
├── job_id (FK → jobs)
├── status (enum: workflow states)
├── fit_score (0-100)
├── created_at, updated_at
├── approved_at, submitted_at
└── user_notes

documents
├── id (PK)
├── application_id (FK → applications)
├── cover_letter_de (TEXT)
├── cover_letter_en (TEXT)
├── cv_optimization_notes (TEXT)
├── form_answers (JSON: {...})
├── generated_at
└── generation_method

emails
├── id (PK)
├── user_id (FK → users)
├── message_id (Gmail ID, unique)
├── thread_id, subject, sender
├── received_at
├── category (enum: job_alert/rejection/interview/offer)
├── confidence (0-1)
├── body_text (TEXT)
├── labels (JSON: [...])
├── job_id (FK → jobs, nullable)
├── application_id (FK → applications, nullable)
└── processed (boolean)
```

## Security Architecture

### Authentication & Authorization

```
User
  │
  ├─ CLI Authentication
  │    └─ User ID required for all commands
  │
  ├─ Gmail OAuth 2.0
  │    ├─ Scopes: gmail.readonly, gmail.modify, gmail.labels
  │    ├─ Token stored locally (token.json)
  │    └─ No gmail.send scope (safety)
  │
  └─ Stripe (Future)
       ├─ Webhook signature verification
       └─ Customer ID linked to user
```

### Data Isolation

```python
# All queries filter by user_id
apps = db.query(Application).filter(
    Application.user_id == user_id
).all()

# Plan limits enforced
if app_count >= max_allowed:
    raise ValueError("Limit reached")
```

### No Secrets in Code

```
✓ Environment variables (.env)
✓ OAuth tokens (local files, gitignored)
✓ Pydantic settings with validation
✗ No hardcoded secrets
✗ No passwords stored
```

## Multi-Tenant Architecture

### Plan-Based Limits

```python
FREE:    10 applications/month
PRO:     100 applications/month
AGENCY:  Unlimited applications
```

### Subscription Management

```
Stripe Webhook → StripeService → Update User Plan
   │
   ├─ subscription.created → Upgrade plan
   ├─ subscription.deleted → Downgrade to free
   └─ invoice.paid → Track payment
```

## Service Responsibilities

### UserService
- Create/read/update users
- Manage subscription plans
- Enforce plan limits

### ProfileService
- Manage user profiles
- Store CV and skills data
- Track preferences

### JobService
- Create job records
- Search and filter jobs
- Support multiple sources

### ApplicationService
- Create applications (with limit checks)
- Manage approval workflow
- Track application lifecycle
- Enforce approval gates

### DocumentService
- Generate cover letters (DE/EN)
- Calculate fit scores
- Create CV optimization notes
- Generate form answers

### GmailService
- OAuth authentication
- Sync emails from Gmail
- Classify emails by category
- Create draft emails (not send)
- Add labels to emails

### StripeService
- Handle subscription webhooks
- Manage customer records
- Process subscription events

## CLI Command Structure

```
bewerbungs-agent
├── init                    # Setup database
├── create-user            # User management
├── create-profile         # Profile management
├── sync-gmail             # Email synchronization
├── prepare-applications   # Create draft applications
├── review-queue           # Show pending reviews
├── approve-application    # ⚠️ APPROVAL GATE
├── export-application     # Export documents
├── report-metrics         # View statistics
└── classify-emails        # Email classification
```

## Extension Points

### Future Web Interface

```
Web App
  ├── Flask/FastAPI backend
  ├── React/Vue frontend
  ├── Same service layer
  └── REST API endpoints
       ├── POST /api/applications
       ├── GET /api/applications/:id
       ├── POST /api/applications/:id/approve
       └── GET /api/applications/:id/export
```

### Future AI Integration

```
DocumentService
  ├── Template-based (current)
  ├── OpenAI GPT (future)
  │    ├── Advanced cover letters
  │    ├── CV tailoring
  │    └── Interview prep
  └── Custom ML model
       ├── Fit score prediction
       └── Job matching
```

### Future Browser Automation

```
Selenium/Playwright
  ├── Navigate to job portal
  ├── Fill application form
  ├── Stop at "Submit" button
  └── Wait for user click
```

## Deployment Architecture

### Development
```
Local Machine
  ├── SQLite database
  ├── credentials.json (local)
  ├── token.json (local)
  └── .env (gitignored)
```

### Production (Future)
```
Cloud Provider (AWS/GCP/Azure)
  ├── Application Server
  │    ├── Gunicorn/uWSGI
  │    └── Docker container
  ├── PostgreSQL Database
  │    ├── SSL enabled
  │    └── Automated backups
  ├── Redis (caching/queue)
  ├── Environment Variables
  │    └── Secrets Manager
  └── Load Balancer + HTTPS
```

## Scalability Considerations

### Horizontal Scaling
- Stateless services
- Database connection pooling
- Background jobs via Celery/RQ

### Performance Optimization
- Database indexing (user_id, status, message_id)
- Caching (Redis for sessions)
- Async operations for email sync
- Batch document generation

### Monitoring
- Application logs
- Error tracking (Sentry)
- Performance metrics (Prometheus)
- User analytics (privacy-respecting)

## Compliance & Legal

### GDPR Requirements
- User consent required
- Right to data export
- Right to deletion
- Minimal data collection
- Purpose limitation

### Terms of Service Compliance
- No ToS violations
- No CAPTCHA bypassing
- No unauthorized automation
- Human approval required

---

**Version**: 0.1.0  
**Last Updated**: 2026-02-19
