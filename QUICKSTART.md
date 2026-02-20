# Quick Start Guide

Get started with Bewerbungs Agent in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Gmail account
- Google Cloud project (free tier is fine)

## Installation (5 steps)

### 1. Clone Repository

```bash
git clone https://github.com/Gastonitou/bewerbungs-agent.git
cd bewerbungs-agent
```

### 2. Run Setup Script

```bash
bash setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Initialize database
- Create `.env` file

### 3. Setup Gmail API (one-time)

1. Go to https://console.cloud.google.com/
2. Create new project → Enable Gmail API
3. Create OAuth credentials → Desktop app
4. Download `credentials.json` → Place in project root

### 4. Activate Environment

```bash
source venv/bin/activate
```

### 5. Create Your Profile

```bash
# Create user account
bewerbungs-agent create-user --email your@email.com --plan free

# Create profile
bewerbungs-agent create-profile \
  --user-id 1 \
  --name "Your Name" \
  --skills "Python,SQL,Docker,AWS" \
  --cv-text "Your CV text or path to file"
```

## First Job Application (3 steps)

### Step 1: Sync Gmail

```bash
bewerbungs-agent sync-gmail --user-id 1
```

First time: Opens browser for Gmail authorization.  
Subsequent runs: Uses saved token.

### Step 2: Prepare Applications

```bash
bewerbungs-agent prepare-applications --user-id 1 --limit 5
```

Creates draft applications from job alerts. **Does NOT submit!**

### Step 3: Review & Approve

```bash
# See what's pending
bewerbungs-agent review-queue --user-id 1

# Approve one (CRITICAL: your approval required!)
bewerbungs-agent approve-application --application-id 1

# Export documents
bewerbungs-agent export-application --application-id 1
```

## What's Next?

- Read [README.md](README.md) for full documentation
- See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for advanced usage
- Check [SECURITY.md](SECURITY.md) for security best practices

## Troubleshooting

**Problem**: "Module not found"  
**Solution**: Make sure venv is activated: `source venv/bin/activate`

**Problem**: Gmail auth fails  
**Solution**: Check `credentials.json` is in root directory

**Problem**: "Application limit reached"  
**Solution**: Free plan limited to 10 apps. Upgrade or wait for next month.

## Need Help?

- [GitHub Issues](https://github.com/Gastonitou/bewerbungs-agent/issues)
- [GitHub Discussions](https://github.com/Gastonitou/bewerbungs-agent/discussions)

---

**Remember**: This tool prepares applications; **you** submit them! 🎯
