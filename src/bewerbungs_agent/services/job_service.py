"""Job management service."""

from typing import List, Optional
from sqlalchemy.orm import Session

from bewerbungs_agent.models import Job, JobSource


class JobService:
    """Service for managing job postings."""

    @staticmethod
    def create_job(
        db: Session,
        source: JobSource,
        company: str,
        role: str,
        description: str = "",
        requirements: str = "",
        **kwargs
    ) -> Job:
        """Create a new job posting."""
        job = Job(
            source=source,
            company=company,
            role=role,
            description=description,
            requirements=requirements,
            **kwargs
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        """Get job by ID."""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def list_jobs(db: Session, limit: int = 50, offset: int = 0) -> List[Job]:
        """List all jobs."""
        return db.query(Job).offset(offset).limit(limit).all()

    @staticmethod
    def search_jobs(
        db: Session,
        company: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Job]:
        """Search jobs with filters."""
        query = db.query(Job)
        
        if company:
            query = query.filter(Job.company.ilike(f"%{company}%"))
        if role:
            query = query.filter(Job.role.ilike(f"%{role}%"))
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        
        return query.all()
