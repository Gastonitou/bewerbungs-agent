"""Unit tests for user service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bewerbungs_agent.models import Base, User, Profile, SubscriptionPlan
from bewerbungs_agent.services.user_service import UserService, ProfileService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_create_user(db_session):
    """Test user creation."""
    user = UserService.create_user(db_session, "test@example.com", SubscriptionPlan.FREE)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.plan == SubscriptionPlan.FREE
    assert user.is_active == 1


def test_get_user_by_email(db_session):
    """Test getting user by email."""
    created = UserService.create_user(db_session, "test@example.com")
    
    user = UserService.get_user_by_email(db_session, "test@example.com")
    
    assert user is not None
    assert user.email == created.email


def test_update_user_plan(db_session):
    """Test updating user plan."""
    user = UserService.create_user(db_session, "test@example.com", SubscriptionPlan.FREE)
    
    updated = UserService.update_user_plan(db_session, user.id, SubscriptionPlan.PRO)
    
    assert updated.plan == SubscriptionPlan.PRO


def test_get_max_applications(db_session):
    """Test max applications by plan."""
    user_free = UserService.create_user(db_session, "free@example.com", SubscriptionPlan.FREE)
    user_pro = UserService.create_user(db_session, "pro@example.com", SubscriptionPlan.PRO)
    user_agency = UserService.create_user(db_session, "agency@example.com", SubscriptionPlan.AGENCY)
    
    assert UserService.get_max_applications(user_free) == 10
    assert UserService.get_max_applications(user_pro) == 100
    assert UserService.get_max_applications(user_agency) > 1000


def test_create_profile(db_session):
    """Test profile creation."""
    user = UserService.create_user(db_session, "test@example.com")
    
    profile = ProfileService.create_profile(
        db_session,
        user.id,
        "John Doe",
        ["Python", "SQL", "Docker"],
        "This is my CV text"
    )
    
    assert profile.user_id == user.id
    assert profile.full_name == "John Doe"
    assert "Python" in profile.skills


def test_get_profile(db_session):
    """Test getting profile."""
    user = UserService.create_user(db_session, "test@example.com")
    created = ProfileService.create_profile(
        db_session, user.id, "John Doe", ["Python"], "CV text"
    )
    
    profile = ProfileService.get_profile(db_session, user.id)
    
    assert profile is not None
    assert profile.id == created.id


def test_update_profile(db_session):
    """Test updating profile."""
    user = UserService.create_user(db_session, "test@example.com")
    ProfileService.create_profile(
        db_session, user.id, "John Doe", ["Python"], "CV text"
    )
    
    updated = ProfileService.update_profile(
        db_session,
        user.id,
        full_name="Jane Doe",
        skills=["Python", "JavaScript"]
    )
    
    assert updated.full_name == "Jane Doe"
    assert "JavaScript" in updated.skills
