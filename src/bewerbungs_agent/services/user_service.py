"""User and profile management service."""

from typing import Optional
from sqlalchemy.orm import Session

from bewerbungs_agent.models import User, Profile, SubscriptionPlan


class UserService:
    """Service for managing users and profiles."""

    @staticmethod
    def create_user(db: Session, email: str, plan: SubscriptionPlan = SubscriptionPlan.FREE) -> User:
        """Create a new user."""
        user = User(email=email, plan=plan)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user_plan(db: Session, user_id: int, plan: SubscriptionPlan) -> Optional[User]:
        """Update user's subscription plan."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.plan = plan
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def get_max_applications(user: User) -> int:
        """Get maximum applications allowed for user's plan."""
        from bewerbungs_agent.utils.config import get_settings
        
        settings = get_settings()
        if user.plan == SubscriptionPlan.FREE:
            return settings.max_applications_free
        elif user.plan == SubscriptionPlan.PRO:
            return settings.max_applications_pro
        else:  # AGENCY
            return settings.max_applications_agency


class ProfileService:
    """Service for managing user profiles."""

    @staticmethod
    def create_profile(
        db: Session,
        user_id: int,
        full_name: str,
        skills: list,
        cv_text: str,
        **kwargs
    ) -> Profile:
        """Create a user profile."""
        profile = Profile(
            user_id=user_id,
            full_name=full_name,
            skills=skills,
            cv_text=cv_text,
            **kwargs
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_profile(db: Session, user_id: int) -> Optional[Profile]:
        """Get profile for a user."""
        return db.query(Profile).filter(Profile.user_id == user_id).first()

    @staticmethod
    def update_profile(db: Session, user_id: int, **updates) -> Optional[Profile]:
        """Update user profile."""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            db.commit()
            db.refresh(profile)
        return profile
