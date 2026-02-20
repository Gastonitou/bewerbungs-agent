# Example Usage Guide

This guide shows practical examples of using the Bewerbungs Agent.

## Setup

### 1. Installation

```bash
# Clone and setup
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent
bash setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `credentials.json`
6. Place in project root

### 3. Initialize Database

```bash
bewerbungs-agent init
```

## Basic Workflow

### Step 1: Create User Account

```bash
# Create free tier user
bewerbungs-agent create-user --email john.doe@example.com --plan free

# Create pro user
bewerbungs-agent create-user --email premium@example.com --plan pro
```

### Step 2: Create Profile

```bash
# Using inline CV text
bewerbungs-agent create-profile \
  --user-id 1 \
  --name "John Doe" \
  --skills "Python, JavaScript, SQL, Docker, Kubernetes, AWS" \
  --cv-text "Senior Software Engineer with 10 years of experience..."

# Using CV file
bewerbungs-agent create-profile \
  --user-id 1 \
  --name "John Doe" \
  --skills "Python, JavaScript, SQL, Docker, Kubernetes, AWS" \
  --cv-text ~/Documents/my_cv.txt
```

### Step 3: Sync Gmail Job Alerts

```bash
# First time: will open browser for OAuth
bewerbungs-agent sync-gmail --user-id 1

# Subsequent runs: uses saved token
bewerbungs-agent sync-gmail --user-id 1
```

**Output:**
```
Syncing Gmail for user 1...
✓ Synced 15 emails
  - job_alert: 12
  - rejection: 2
  - interview: 1
```

### Step 4: Prepare Applications

```bash
# Prepare up to 10 applications from job alerts
bewerbungs-agent prepare-applications --user-id 1 --limit 10
```

**Output:**
```
Preparing applications for user 1...
Found 12 unprocessed job alerts
  ✓ Created application #1 - Fit: 85.0%
  ✓ Created application #2 - Fit: 72.5%
  ✓ Created application #3 - Fit: 90.0%
  ...
✓ Prepared 10 applications for review
```

### Step 5: Review Queue

```bash
bewerbungs-agent review-queue --user-id 1
```

**Output:**
```
Applications pending review (10):

Application ID: 1
  Company: Tech Corp
  Role: Senior Python Developer
  Fit Score: 85.0%
  Created: 2026-02-19 07:00:00
  Cover Letter (EN): Dear Hiring Manager,

I am writing to express...

Application ID: 2
  Company: DataCo
  Role: Data Engineer
  Fit Score: 72.5%
  Created: 2026-02-19 07:01:00
  Cover Letter (EN): Dear Hiring Manager,
...
```

### Step 6: Approve Application (CRITICAL)

```bash
bewerbungs-agent approve-application --application-id 1
```

**Output:**
```
Application #1
  Company: Tech Corp
  Role: Senior Python Developer
  Fit Score: 85.0%

Approve this application? [y/N]: y
✓ Application approved and ready for submission
  Use 'export-application' to get documents
```

### Step 7: Export Application

```bash
# Text format (human-readable)
bewerbungs-agent export-application --application-id 1

# JSON format (for automation)
bewerbungs-agent export-application --application-id 1 --format json > application_1.json
```

**Output (text):**
```
Application #1
Company: Tech Corp
Role: Senior Python Developer
Status: ready_to_submit

--- Cover Letter (English) ---
Dear Hiring Manager,

I am writing to express my strong interest in the Senior Python Developer 
position at Tech Corp.

With 10 years of experience and expertise in Python, SQL, Docker, I am 
confident I can contribute effectively to your team.

Key highlights of my background:
- Proven expertise in Python, JavaScript, SQL, Docker, Kubernetes
- Strong track record in delivering high-quality results
- Excellent communication and collaboration skills

I am particularly excited about this opportunity at Tech Corp because it 
aligns perfectly with my career goals and expertise.

I would welcome the opportunity to discuss how my skills and experience 
can benefit your team.

Best regards,
John Doe
john.doe@example.com

--- Cover Letter (German) ---
[German version...]

--- CV Optimization Notes ---
Highlight experience with: Python, REST APIs, microservices...
Emphasize these relevant skills: Python, SQL, Docker, Kubernetes, AWS
Tailor your CV to emphasize Senior Python Developer experience
Use keywords from the job description
Quantify achievements where possible
```

### Step 8: View Metrics

```bash
bewerbungs-agent report-metrics --user-id 1
```

**Output:**
```
Metrics for john.doe@example.com (Plan: SubscriptionPlan.FREE)
Total Applications: 10
Max Allowed: 10

By Status:
  draft: 2
  review_required: 5
  user_approved: 2
  ready_to_submit: 1

Average Fit Score: 78.5%
```

## Advanced Usage

### Using with CSV Import

```python
# Example: Import jobs from CSV
import csv
from bewerbungs_agent.services import JobService
from bewerbungs_agent.utils import db_session
from bewerbungs_agent.models import JobSource

with db_session() as db:
    with open('jobs.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            JobService.create_job(
                db,
                source=JobSource.CSV_IMPORT,
                company=row['company'],
                role=row['role'],
                description=row['description'],
                requirements=row['requirements'],
                location=row.get('location', ''),
                url=row.get('url', ''),
            )
```

### Email Draft Creation

```python
# Example: Create Gmail draft (not sent)
from bewerbungs_agent.services import GmailService

gmail = GmailService()
gmail.authenticate()

draft = gmail.create_draft(
    to="jobs@company.com",
    subject="Application for Senior Python Developer",
    body=cover_letter_text
)

print(f"Draft created: {draft['id']}")
# User can review and send from Gmail UI
```

### Batch Approval

```python
# Example: Review and approve multiple applications
from bewerbungs_agent.services import ApplicationService
from bewerbungs_agent.models import ApplicationStatus
from bewerbungs_agent.utils import db_session

with db_session() as db:
    # Get applications with high fit scores
    apps = ApplicationService.list_applications(
        db,
        user_id=1,
        status=ApplicationStatus.REVIEW_REQUIRED
    )
    
    for app in apps:
        if app.fit_score >= 80:
            print(f"Auto-approving #{app.id} with fit score {app.fit_score}%")
            ApplicationService.approve_application(db, app.id)
            ApplicationService.mark_ready_to_submit(db, app.id)
```

## Safety Features

### 1. Human Approval Required

Every application must go through approval:
- `DRAFT` → Generated, not reviewed
- `REVIEW_REQUIRED` → Awaiting user review
- `USER_APPROVED` → User explicitly approved
- `READY_TO_SUBMIT` → Ready for manual submission

### 2. Plan Limits

Free plan users are limited to prevent abuse:
```bash
# Trying to exceed limit
bewerbungs-agent prepare-applications --user-id 1 --limit 20
```

**Output:**
```
✗ Application limit reached for FREE plan. Maximum: 10, Current: 10
```

### 3. No Automatic Submission

The tool **NEVER** submits applications automatically. It only:
- Prepares documents
- Creates draft emails (in Gmail, not sent)
- Exports application packages for manual submission

## Troubleshooting

### Gmail Authentication Issues

```bash
# If you get authentication errors:
rm token.json
bewerbungs-agent sync-gmail --user-id 1
# This will trigger new OAuth flow
```

### Database Reset

```bash
# If you need to start fresh:
rm bewerbungs_agent.db
bewerbungs-agent init
```

### Check Application Status

```python
from bewerbungs_agent.services import ApplicationService
from bewerbungs_agent.utils import db_session

with db_session() as db:
    app = ApplicationService.get_application(db, application_id=1)
    print(f"Status: {app.status}")
    print(f"Fit Score: {app.fit_score}%")
    print(f"Approved at: {app.approved_at}")
```

## Integration Examples

### Web Dashboard (Future)

```python
from flask import Flask, render_template
from bewerbungs_agent.services import ApplicationService
from bewerbungs_agent.utils import db_session

app = Flask(__name__)

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    with db_session() as db:
        apps = ApplicationService.list_applications(db, user_id=user_id)
        return render_template('dashboard.html', applications=apps)
```

### Slack Notifications

```python
import requests
from bewerbungs_agent.models import EmailCategory

def notify_interview(email):
    if email.category == EmailCategory.INTERVIEW:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={
                "text": f"🎉 Interview invitation from {email.sender}!"
            }
        )
```

## Best Practices

1. **Review Before Approving**: Always review generated documents
2. **Regular Syncs**: Run `sync-gmail` daily to catch new opportunities
3. **Track Metrics**: Use `report-metrics` to monitor progress
4. **Backup Data**: Regularly backup your database
5. **Update Profile**: Keep your skills and CV current
6. **Respect Limits**: Don't try to bypass plan limits

## Getting Help

- **Documentation**: See README.md
- **Issues**: [GitHub Issues](https://github.com/Gastonitou/bewerbungs-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gastonitou/bewerbungs-agent/discussions)
