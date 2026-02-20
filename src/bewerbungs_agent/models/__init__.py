"""Database models for the Job Application Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""

    FREE = "free"
    PRO = "pro"
    AGENCY = "agency"


class ApplicationStatus(str, Enum):
    """Application lifecycle status."""

    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    USER_APPROVED = "user_approved"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"


class JobSource(str, Enum):
    """Source of job posting."""

    GMAIL = "gmail"
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    URL = "url"


class EmailCategory(str, Enum):
    """Email classification categories."""

    JOB_ALERT = "job_alert"
    REJECTION = "rejection"
    INTERVIEW = "interview"
    OFFER = "offer"
    OTHER = "other"


class User(Base):
    """User model for multi-tenant SaaS."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, plan={self.plan})>"


class Profile(Base):
    """User profile with CV data and preferences."""

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Personal Information
    full_name = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    
    # Professional Data
    skills = Column(JSON)  # List of skills
    cv_text = Column(Text)  # Full CV text for reference
    experience_years = Column(Integer)
    education = Column(JSON)  # List of education entries
    work_history = Column(JSON)  # List of work history entries
    
    # Preferences
    preferences = Column(JSON)  # Job preferences, salary expectations, etc.
    languages = Column(JSON)  # Languages and proficiency levels
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, name={self.full_name})>"


class Job(Base):
    """Job posting information."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    source = Column(SQLEnum(JobSource), nullable=False)
    url = Column(String(1024))
    
    # Job Details
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(255))
    salary_range = Column(String(100))
    
    # Application Information
    application_type = Column(String(50))  # form, email, portal
    application_email = Column(String(255))
    application_url = Column(String(1024))
    
    # Metadata
    raw_data = Column(JSON)  # Store original extracted data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, company={self.company}, role={self.role})>"


class Application(Base):
    """Application tracking with approval workflow."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Status and Workflow
    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.DRAFT,
        nullable=False,
        index=True,
    )
    fit_score = Column(Float)  # 0-100 confidence score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    submitted_at = Column(DateTime)
    
    # Notes
    user_notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    documents = relationship("Document", back_populates="application")

    def __repr__(self):
        return f"<Application(id={self.id}, status={self.status}, fit_score={self.fit_score})>"


class Document(Base):
    """Generated documents for applications."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    # Document Content
    cover_letter_de = Column(Text)
    cover_letter_en = Column(Text)
    cv_optimization_notes = Column(Text)
    form_answers = Column(JSON)  # Pre-filled form fields
    
    # Generation Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generation_method = Column(String(50))  # template, ai, hybrid
    
    # Relationships
    application = relationship("Application", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, application_id={self.application_id})>"


class Email(Base):
    """Tracked emails from Gmail."""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Gmail Data
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    thread_id = Column(String(255))
    subject = Column(String(512))
    sender = Column(String(255))
    received_at = Column(DateTime)
    
    # Classification
    category = Column(SQLEnum(EmailCategory), default=EmailCategory.OTHER)
    confidence = Column(Float)  # Classification confidence 0-1
    
    # Content
    body_text = Column(Text)
    labels = Column(JSON)  # Gmail labels
    
    # Linking
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    
    # Metadata
    processed = Column(Integer, default=0)  # 0 = not processed, 1 = processed
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Email(id={self.id}, category={self.category}, subject={self.subject})>"
