"""Command-line interface for the Job Application Agent."""

import click
from sqlalchemy.orm import Session

from bewerbungs_agent.utils.database import db_session, init_db
from bewerbungs_agent.models import ApplicationStatus, SubscriptionPlan
from bewerbungs_agent.services import (
    UserService,
    ProfileService,
    JobService,
    ApplicationService,
    DocumentService,
    GmailService,
)


@click.group()
def cli():
    """Bewerbungs Agent - Job Application Automation Tool"""
    pass


@cli.command()
def init():
    """Initialize the database."""
    click.echo("Initializing database...")
    init_db()
    click.echo("✓ Database initialized successfully!")


@cli.command()
@click.option('--email', required=True, help='User email address')
@click.option('--plan', type=click.Choice(['free', 'pro', 'agency']), default='free')
def create_user(email: str, plan: str):
    """Create a new user."""
    with db_session() as db:
        # Check if user exists
        existing = UserService.get_user_by_email(db, email)
        if existing:
            click.echo(f"✗ User with email {email} already exists!")
            return
        
        user = UserService.create_user(db, email, SubscriptionPlan(plan))
        click.echo(f"✓ Created user: {user.id} ({user.email}) - Plan: {user.plan}")


@cli.command()
@click.option('--user-id', required=True, type=int, help='User ID')
@click.option('--name', required=True, help='Full name')
@click.option('--skills', required=True, help='Comma-separated skills')
@click.option('--cv-text', required=True, help='CV text or path to file')
def create_profile(user_id: int, name: str, skills: str, cv_text: str):
    """Create or update user profile."""
    with db_session() as db:
        # Check if user exists
        user = UserService.get_user(db, user_id)
        if not user:
            click.echo(f"✗ User {user_id} not found!")
            return
        
        # Parse skills
        skills_list = [s.strip() for s in skills.split(',')]
        
        # Check if CV is a file
        import os
        if os.path.isfile(cv_text):
            with open(cv_text, 'r') as f:
                cv_text = f.read()
        
        # Create or update profile
        existing = ProfileService.get_profile(db, user_id)
        if existing:
            profile = ProfileService.update_profile(
                db, user_id, full_name=name, skills=skills_list, cv_text=cv_text
            )
            click.echo(f"✓ Updated profile for user {user_id}")
        else:
            profile = ProfileService.create_profile(
                db, user_id, name, skills_list, cv_text
            )
            click.echo(f"✓ Created profile for user {user_id}")


@cli.command()
@click.option('--user-id', required=True, type=int)
def sync_gmail(user_id: int):
    """Sync emails from Gmail."""
    click.echo(f"Syncing Gmail for user {user_id}...")
    
    try:
        gmail = GmailService()
        gmail.authenticate()
        
        with db_session() as db:
            emails = gmail.sync_emails(db, user_id)
            click.echo(f"✓ Synced {len(emails)} emails")
            
            # Show breakdown
            from collections import Counter
            categories = Counter(e.category for e in emails)
            for category, count in categories.items():
                click.echo(f"  - {category.value}: {count}")
    
    except Exception as e:
        click.echo(f"✗ Error: {e}")


@cli.command()
@click.option('--user-id', required=True, type=int)
@click.option('--limit', default=50, help='Maximum applications to prepare')
def prepare_applications(user_id: int, limit: int):
    """
    Prepare applications from job alerts.
    Creates DRAFT applications, does NOT submit.
    """
    click.echo(f"Preparing applications for user {user_id}...")
    
    with db_session() as db:
        # Get user and profile
        user = UserService.get_user(db, user_id)
        if not user:
            click.echo(f"✗ User {user_id} not found!")
            return
        
        profile = ProfileService.get_profile(db, user_id)
        if not profile:
            click.echo(f"✗ Profile not found for user {user_id}. Create one first!")
            return
        
        # Find job alert emails that haven't been processed
        from bewerbungs_agent.models import Email, EmailCategory
        job_emails = db.query(Email).filter(
            Email.user_id == user_id,
            Email.category == EmailCategory.JOB_ALERT,
            Email.processed == 0,
        ).limit(limit).all()
        
        click.echo(f"Found {len(job_emails)} unprocessed job alerts")
        
        created = 0
        for email in job_emails:
            # In production, extract job details from email
            # For now, create a basic job entry
            job = JobService.create_job(
                db,
                source='gmail',
                company=email.sender,
                role="Position from email",
                description=email.body_text[:500],
            )
            
            # Calculate fit score
            fit_score = DocumentService.calculate_fit_score(profile, job)
            
            # Create application
            try:
                app = ApplicationService.create_application(db, user_id, job.id, fit_score)
                
                # Generate documents
                doc = DocumentService.create_document(db, app.id, profile, job)
                
                # Mark for review
                ApplicationService.mark_for_review(db, app.id)
                
                # Mark email as processed
                email.processed = 1
                email.job_id = job.id
                email.application_id = app.id
                db.commit()
                
                created += 1
                click.echo(f"  ✓ Created application #{app.id} - Fit: {fit_score}%")
            
            except ValueError as e:
                click.echo(f"  ✗ {e}")
                break
        
        click.echo(f"✓ Prepared {created} applications for review")


@cli.command()
@click.option('--user-id', required=True, type=int)
def review_queue(user_id: int):
    """Show applications waiting for review."""
    with db_session() as db:
        apps = ApplicationService.list_applications(
            db, user_id=user_id, status=ApplicationStatus.REVIEW_REQUIRED
        )
        
        if not apps:
            click.echo("No applications pending review")
            return
        
        click.echo(f"Applications pending review ({len(apps)}):\n")
        
        for app in apps:
            click.echo(f"Application ID: {app.id}")
            click.echo(f"  Company: {app.job.company}")
            click.echo(f"  Role: {app.job.role}")
            click.echo(f"  Fit Score: {app.fit_score}%")
            click.echo(f"  Created: {app.created_at}")
            
            # Show document preview
            doc = DocumentService.get_document(db, app.id)
            if doc:
                click.echo(f"  Cover Letter (EN): {doc.cover_letter_en[:100]}...")
            click.echo()


@cli.command()
@click.option('--application-id', required=True, type=int)
def approve_application(application_id: int):
    """
    Approve an application for submission.
    CRITICAL: This is the human approval gate!
    """
    with db_session() as db:
        app = ApplicationService.get_application(db, application_id)
        
        if not app:
            click.echo(f"✗ Application {application_id} not found!")
            return
        
        if app.status != ApplicationStatus.REVIEW_REQUIRED:
            click.echo(f"✗ Application is in {app.status} status, cannot approve")
            return
        
        # Show details for confirmation
        click.echo(f"Application #{app.id}")
        click.echo(f"  Company: {app.job.company}")
        click.echo(f"  Role: {app.job.role}")
        click.echo(f"  Fit Score: {app.fit_score}%")
        click.echo()
        
        if click.confirm('Approve this application?'):
            app = ApplicationService.approve_application(db, application_id)
            app = ApplicationService.mark_ready_to_submit(db, application_id)
            click.echo(f"✓ Application approved and ready for submission")
            click.echo("  Use 'export-application' to get documents")
        else:
            click.echo("✗ Approval cancelled")


@cli.command()
@click.option('--application-id', required=True, type=int)
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def export_application(application_id: int, format: str):
    """Export application documents."""
    with db_session() as db:
        app = ApplicationService.get_application(db, application_id)
        
        if not app:
            click.echo(f"✗ Application {application_id} not found!")
            return
        
        doc = DocumentService.get_document(db, application_id)
        if not doc:
            click.echo(f"✗ No documents found for application {application_id}")
            return
        
        if format == 'json':
            import json
            output = {
                'application_id': app.id,
                'company': app.job.company,
                'role': app.job.role,
                'cover_letter_en': doc.cover_letter_en,
                'cover_letter_de': doc.cover_letter_de,
                'cv_notes': doc.cv_optimization_notes,
                'form_answers': doc.form_answers,
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"Application #{app.id}")
            click.echo(f"Company: {app.job.company}")
            click.echo(f"Role: {app.job.role}")
            click.echo(f"Status: {app.status}")
            click.echo("\n--- Cover Letter (English) ---")
            click.echo(doc.cover_letter_en)
            click.echo("\n--- Cover Letter (German) ---")
            click.echo(doc.cover_letter_de)
            click.echo("\n--- CV Optimization Notes ---")
            click.echo(doc.cv_optimization_notes)


@cli.command()
@click.option('--user-id', required=True, type=int)
def report_metrics(user_id: int):
    """Show application metrics for a user."""
    with db_session() as db:
        user = UserService.get_user(db, user_id)
        if not user:
            click.echo(f"✗ User {user_id} not found!")
            return
        
        apps = ApplicationService.list_applications(db, user_id=user_id)
        
        from collections import Counter
        status_counts = Counter(app.status for app in apps)
        
        click.echo(f"Metrics for {user.email} (Plan: {user.plan})")
        click.echo(f"Total Applications: {len(apps)}")
        click.echo(f"Max Allowed: {UserService.get_max_applications(user)}")
        click.echo("\nBy Status:")
        
        for status, count in status_counts.items():
            click.echo(f"  {status.value}: {count}")
        
        # Calculate average fit score
        scores = [app.fit_score for app in apps if app.fit_score]
        if scores:
            avg_score = sum(scores) / len(scores)
            click.echo(f"\nAverage Fit Score: {avg_score:.1f}%")


@cli.command()
def classify_emails():
    """Classify unprocessed emails."""
    click.echo("Email classification is done automatically during sync-gmail")
    click.echo("Use: bewerbungs-agent sync-gmail --user-id <id>")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
