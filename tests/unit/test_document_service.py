"""Unit tests for document service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bewerbungs_agent.models import Base, SubscriptionPlan, JobSource
from bewerbungs_agent.services.user_service import UserService, ProfileService
from bewerbungs_agent.services.job_service import JobService
from bewerbungs_agent.services.application_service import ApplicationService
from bewerbungs_agent.services.document_service import DocumentService


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
def test_profile(db_session):
    """Create a test profile."""
    user = UserService.create_user(db_session, "test@example.com")
    profile = ProfileService.create_profile(
        db_session,
        user.id,
        "John Doe",
        ["Python", "SQL", "Docker", "Machine Learning"],
        "Experienced software engineer with 5 years of experience.",
        experience_years=5,
        location="Berlin"
    )
    return profile


@pytest.fixture
def test_job(db_session):
    """Create a test job."""
    return JobService.create_job(
        db_session,
        JobSource.MANUAL,
        "Tech Corp",
        "Senior Python Developer",
        "We are looking for an experienced Python developer with SQL and Docker experience.",
        "Python, SQL, Docker, REST APIs",
        location="Berlin"
    )


def test_generate_cover_letter_en(test_profile, test_job):
    """Test English cover letter generation."""
    letter = DocumentService.generate_cover_letter_template(
        test_profile, test_job, "en"
    )
    
    assert "Dear Hiring Manager" in letter
    assert test_job.company in letter
    assert test_job.role in letter
    assert test_profile.full_name in letter


def test_generate_cover_letter_de(test_profile, test_job):
    """Test German cover letter generation."""
    letter = DocumentService.generate_cover_letter_template(
        test_profile, test_job, "de"
    )
    
    assert "Sehr geehrte Damen und Herren" in letter
    assert test_job.company in letter
    assert test_job.role in letter
    assert test_profile.full_name in letter


def test_calculate_fit_score(test_profile, test_job):
    """Test fit score calculation."""
    score = DocumentService.calculate_fit_score(test_profile, test_job)
    
    assert 0 <= score <= 100
    # Should be high because profile has Python, SQL, Docker which match job
    assert score > 50


def test_calculate_fit_score_with_location_match(test_profile, test_job):
    """Test that location match boosts score."""
    score = DocumentService.calculate_fit_score(test_profile, test_job)
    
    # Both are in Berlin, should get location boost
    assert score > 50


def test_generate_cv_optimization_notes(test_profile, test_job):
    """Test CV optimization notes generation."""
    notes = DocumentService.generate_cv_optimization_notes(test_profile, test_job)
    
    assert len(notes) > 0
    assert "Python" in notes or "SQL" in notes


def test_generate_form_answers(test_profile, test_job):
    """Test form answers generation."""
    answers = DocumentService.generate_form_answers(test_profile, test_job)
    
    assert answers["full_name"] == test_profile.full_name
    assert answers["location"] == test_profile.location
    assert answers["experience_years"] == 5
    assert test_job.company in answers["motivation"]


def test_create_document(db_session, test_profile, test_job):
    """Test document creation."""
    # Create application first
    app = ApplicationService.create_application(
        db_session, test_profile.user_id, test_job.id
    )
    
    doc = DocumentService.create_document(
        db_session, app.id, test_profile, test_job
    )
    
    assert doc.application_id == app.id
    assert doc.cover_letter_en is not None
    assert doc.cover_letter_de is not None
    assert doc.cv_optimization_notes is not None
    assert doc.form_answers is not None
    assert test_job.company in doc.cover_letter_en


def test_get_document(db_session, test_profile, test_job):
    """Test getting document."""
    app = ApplicationService.create_application(
        db_session, test_profile.user_id, test_job.id
    )
    created = DocumentService.create_document(
        db_session, app.id, test_profile, test_job
    )
    
    doc = DocumentService.get_document(db_session, app.id)
    
    assert doc is not None
    assert doc.id == created.id
