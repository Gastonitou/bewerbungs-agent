"""Unit tests for application service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bewerbungs_agent.models import Base, ApplicationStatus, SubscriptionPlan, JobSource
from bewerbungs_agent.services.user_service import UserService
from bewerbungs_agent.services.job_service import JobService
from bewerbungs_agent.services.application_service import ApplicationService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    return UserService.create_user(db_session, "test@example.com", SubscriptionPlan.PRO)


@pytest.fixture
def test_job(db_session):
    """Create a test job."""
    return JobService.create_job(
        db_session,
        JobSource.MANUAL,
        "Test Company",
        "Software Engineer",
        "Great job opportunity",
        "Python, SQL"
    )


def test_create_application(db_session, test_user, test_job):
    """Test application creation."""
    app = ApplicationService.create_application(
        db_session, test_user.id, test_job.id, 85.5
    )
    
    assert app.id is not None
    assert app.user_id == test_user.id
    assert app.job_id == test_job.id
    assert app.status == ApplicationStatus.DRAFT
    assert app.fit_score == 85.5


def test_application_plan_limit(db_session):
    """Test that application creation respects plan limits."""
    # Create user with free plan (limit: 10)
    user = UserService.create_user(db_session, "free@example.com", SubscriptionPlan.FREE)
    
    # Create 10 applications (should succeed)
    for i in range(10):
        job = JobService.create_job(
            db_session, JobSource.MANUAL, f"Company {i}", "Role", "Desc", "Req"
        )
        ApplicationService.create_application(db_session, user.id, job.id)
    
    # Try to create 11th application (should fail)
    job = JobService.create_job(
        db_session, JobSource.MANUAL, "Company 11", "Role", "Desc", "Req"
    )
    
    with pytest.raises(ValueError, match="Application limit reached"):
        ApplicationService.create_application(db_session, user.id, job.id)


def test_mark_for_review(db_session, test_user, test_job):
    """Test marking application for review."""
    app = ApplicationService.create_application(
        db_session, test_user.id, test_job.id
    )
    
    updated = ApplicationService.mark_for_review(db_session, app.id)
    
    assert updated.status == ApplicationStatus.REVIEW_REQUIRED


def test_approve_application(db_session, test_user, test_job):
    """Test approving application."""
    app = ApplicationService.create_application(
        db_session, test_user.id, test_job.id
    )
    ApplicationService.mark_for_review(db_session, app.id)
    
    approved = ApplicationService.approve_application(db_session, app.id)
    
    assert approved.status == ApplicationStatus.USER_APPROVED
    assert approved.approved_at is not None


def test_mark_ready_to_submit(db_session, test_user, test_job):
    """Test marking application ready to submit."""
    app = ApplicationService.create_application(
        db_session, test_user.id, test_job.id
    )
    ApplicationService.mark_for_review(db_session, app.id)
    ApplicationService.approve_application(db_session, app.id)
    
    ready = ApplicationService.mark_ready_to_submit(db_session, app.id)
    
    assert ready.status == ApplicationStatus.READY_TO_SUBMIT


def test_workflow_sequence(db_session, test_user, test_job):
    """Test complete application workflow."""
    # Create
    app = ApplicationService.create_application(
        db_session, test_user.id, test_job.id, 90.0
    )
    assert app.status == ApplicationStatus.DRAFT
    
    # Mark for review
    app = ApplicationService.mark_for_review(db_session, app.id)
    assert app.status == ApplicationStatus.REVIEW_REQUIRED
    
    # Approve (CRITICAL GATE)
    app = ApplicationService.approve_application(db_session, app.id)
    assert app.status == ApplicationStatus.USER_APPROVED
    assert app.approved_at is not None
    
    # Ready to submit
    app = ApplicationService.mark_ready_to_submit(db_session, app.id)
    assert app.status == ApplicationStatus.READY_TO_SUBMIT
    
    # Mark submitted
    app = ApplicationService.mark_submitted(db_session, app.id)
    assert app.status == ApplicationStatus.SUBMITTED
    assert app.submitted_at is not None


def test_list_applications_by_status(db_session, test_user):
    """Test listing applications by status."""
    # Create jobs and applications with different statuses
    job1 = JobService.create_job(db_session, JobSource.MANUAL, "Co1", "Role1", "", "")
    job2 = JobService.create_job(db_session, JobSource.MANUAL, "Co2", "Role2", "", "")
    
    app1 = ApplicationService.create_application(db_session, test_user.id, job1.id)
    app2 = ApplicationService.create_application(db_session, test_user.id, job2.id)
    ApplicationService.mark_for_review(db_session, app2.id)
    
    # List draft applications
    drafts = ApplicationService.list_applications(
        db_session, user_id=test_user.id, status=ApplicationStatus.DRAFT
    )
    assert len(drafts) == 1
    assert drafts[0].id == app1.id
    
    # List review required
    reviews = ApplicationService.list_applications(
        db_session, user_id=test_user.id, status=ApplicationStatus.REVIEW_REQUIRED
    )
    assert len(reviews) == 1
    assert reviews[0].id == app2.id
