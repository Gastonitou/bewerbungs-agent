"""Application management service with approval workflow."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from bewerbungs_agent.models import Application, ApplicationStatus, User
from bewerbungs_agent.services.user_service import UserService


class ApplicationService:
    """Service for managing job applications."""

    @staticmethod
    def create_application(
        db: Session, user_id: int, job_id: int, fit_score: Optional[float] = None
    ) -> Application:
        """
        Create a new application in DRAFT status.
        Enforces plan limits.
        """
        # Check plan limits
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Count existing applications
        app_count = db.query(Application).filter(Application.user_id == user_id).count()
        max_allowed = UserService.get_max_applications(user)
        
        if app_count >= max_allowed:
            raise ValueError(
                f"Application limit reached for {user.plan} plan. "
                f"Maximum: {max_allowed}, Current: {app_count}"
            )
        
        application = Application(
            user_id=user_id,
            job_id=job_id,
            status=ApplicationStatus.DRAFT,
            fit_score=fit_score,
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def get_application(db: Session, application_id: int) -> Optional[Application]:
        """Get application by ID."""
        return db.query(Application).filter(Application.id == application_id).first()

    @staticmethod
    def list_applications(
        db: Session,
        user_id: Optional[int] = None,
        status: Optional[ApplicationStatus] = None,
    ) -> List[Application]:
        """List applications with optional filters."""
        query = db.query(Application)
        
        if user_id:
            query = query.filter(Application.user_id == user_id)
        if status:
            query = query.filter(Application.status == status)
        
        return query.all()

    @staticmethod
    def mark_for_review(db: Session, application_id: int) -> Optional[Application]:
        """Move application to REVIEW_REQUIRED status."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app and app.status == ApplicationStatus.DRAFT:
            app.status = ApplicationStatus.REVIEW_REQUIRED
            db.commit()
            db.refresh(app)
        return app

    @staticmethod
    def approve_application(db: Session, application_id: int) -> Optional[Application]:
        """
        Approve application (USER_APPROVED).
        This is the CRITICAL approval gate - only user can call this.
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if app and app.status == ApplicationStatus.REVIEW_REQUIRED:
            app.status = ApplicationStatus.USER_APPROVED
            app.approved_at = datetime.utcnow()
            db.commit()
            db.refresh(app)
        return app

    @staticmethod
    def mark_ready_to_submit(db: Session, application_id: int) -> Optional[Application]:
        """Mark application as ready for submission (after approval)."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app and app.status == ApplicationStatus.USER_APPROVED:
            app.status = ApplicationStatus.READY_TO_SUBMIT
            db.commit()
            db.refresh(app)
        return app

    @staticmethod
    def mark_submitted(db: Session, application_id: int) -> Optional[Application]:
        """Mark application as submitted."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app and app.status == ApplicationStatus.READY_TO_SUBMIT:
            app.status = ApplicationStatus.SUBMITTED
            app.submitted_at = datetime.utcnow()
            db.commit()
            db.refresh(app)
        return app

    @staticmethod
    def update_status(
        db: Session, application_id: int, status: ApplicationStatus
    ) -> Optional[Application]:
        """Update application status (for tracking rejections, interviews, offers)."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            app.status = status
            db.commit()
            db.refresh(app)
        return app

    @staticmethod
    def add_notes(db: Session, application_id: int, notes: str) -> Optional[Application]:
        """Add user notes to application."""
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            app.user_notes = notes
            db.commit()
            db.refresh(app)
        return app
