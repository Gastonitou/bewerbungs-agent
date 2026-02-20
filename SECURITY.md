# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Bewerbungs Agent, please report it by emailing the maintainers directly. **Do not** open a public issue.

We take security seriously and will respond to legitimate vulnerability reports within 48 hours.

## Security Best Practices

### 1. Credentials and Secrets

**Never commit the following to git:**
- `.env` files with real credentials
- `credentials.json` (Gmail API credentials)
- `token.json` (OAuth tokens)
- Database files with real user data
- Any API keys or secrets

**Always:**
- Use `.env.example` as a template
- Keep real credentials in `.env` (gitignored)
- Use different credentials for dev/staging/production
- Rotate API keys regularly

### 2. Gmail API Security

**OAuth Only:**
- Never store passwords
- Only OAuth 2.0 authentication
- Token stored locally, never transmitted

**Minimal Scopes:**
```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',    # Add labels
    'https://www.googleapis.com/auth/gmail.labels',    # Manage labels
]
```

**No Sending Permission:**
- We intentionally do NOT request `gmail.send` scope
- Creates drafts only, never sends emails automatically
- This prevents accidental or malicious email sending

### 3. Database Security

**User Isolation:**
- Every query filters by `user_id`
- No cross-user data access
- Plan limits enforced

**SQL Injection Prevention:**
- SQLAlchemy ORM used throughout
- Parameterized queries only
- No raw SQL with user input

**Sensitive Data:**
- No passwords stored
- Only OAuth tokens (encrypted)
- User data properly isolated

### 4. Input Validation

**All user inputs are validated:**
```python
# Email validation
email: str = Column(String(255), unique=True, nullable=False)

# Plan validation via Enum
plan: SubscriptionPlan = Column(SQLEnum(SubscriptionPlan))

# Status workflow enforced
def approve_application(db, application_id):
    app = get_application(db, application_id)
    if app.status != ApplicationStatus.REVIEW_REQUIRED:
        raise ValueError("Application not in correct status")
```

### 5. Third-Party Integrations

**Stripe:**
- Webhook signature verification required
- Test keys only in development
- Production keys via environment variables
- No keys in code

**Gmail:**
- OAuth flow requires user consent
- Tokens refreshed automatically
- Revocable from Google account settings

### 6. Multi-Tenant Security

**Data Isolation:**
```python
# Always filter by user_id
apps = db.query(Application).filter(
    Application.user_id == user_id
).all()
```

**Plan Enforcement:**
```python
# Check limits before creating
if app_count >= max_allowed:
    raise ValueError("Application limit reached")
```

### 7. Deployment Security

**Environment Variables:**
```bash
# Never in code
DATABASE_URL=postgresql://...
STRIPE_SECRET_KEY=sk_live_...
```

**HTTPS Only:**
- In production, use HTTPS for all web endpoints
- Secure cookie flags if using web interface
- HSTS headers recommended

**Database:**
- Use PostgreSQL in production (not SQLite)
- Enable SSL for database connections
- Regular backups
- Access restricted by IP/VPN

### 8. Known Limitations

**By Design:**
- Tool does NOT automatically submit applications
- User approval required (human-in-the-loop)
- No CAPTCHA bypassing
- No ToS violations

**Current Limitations:**
- Email classification is keyword-based (not ML)
- Cover letters use templates (not advanced AI)
- No end-to-end encryption (yet)

### 9. Secure Development

**Code Review:**
- All changes reviewed before merge
- Security-focused review for auth/payment code
- Dependency updates reviewed

**Dependencies:**
- Regular `pip audit` checks
- Only trusted packages
- Minimal dependencies
- Update frequently

**Testing:**
- Security tests included
- Authentication tests
- Input validation tests
- SQL injection prevention tests

### 10. User Responsibilities

Users must:
- Keep their `.env` secure
- Not share OAuth tokens
- Revoke access if compromised
- Use strong passwords for email
- Review applications before submission

## Security Checklist for Deployment

- [ ] All secrets in environment variables
- [ ] OAuth credentials properly secured
- [ ] Database using PostgreSQL with SSL
- [ ] HTTPS enabled for all endpoints
- [ ] Stripe webhook signature verification enabled
- [ ] Rate limiting implemented
- [ ] Logging configured (but no sensitive data logged)
- [ ] Regular backups configured
- [ ] Monitoring and alerting set up
- [ ] Security headers configured
- [ ] Dependencies up to date
- [ ] Security audit completed

## Compliance

### GDPR

**User Rights:**
- Right to access: `export-application --format json`
- Right to deletion: Delete user and all related data
- Right to portability: JSON export available
- Consent required: Explicit for Gmail access

**Data Processing:**
- Minimal data collection
- Purpose limitation (job applications only)
- Data minimization (only what's needed)
- Storage limitation (user can delete anytime)

### Privacy

**What we collect:**
- Email address (for identification)
- CV and profile data (user-provided)
- Gmail job alerts (user-authorized)
- Application documents (generated)

**What we DON'T collect:**
- Passwords (OAuth only)
- Credit card details (handled by Stripe)
- Personal messages unrelated to jobs
- Tracking or analytics

## Security Updates

We will:
- Patch security vulnerabilities promptly
- Notify users of critical security updates
- Maintain this security policy up to date
- Publish security advisories for severe issues

## Contact

For security concerns: Open a private security advisory on GitHub or contact maintainers directly.

For general questions: Use GitHub Issues or Discussions.

---

**Last Updated**: 2026-02-19  
**Version**: 0.1.0
