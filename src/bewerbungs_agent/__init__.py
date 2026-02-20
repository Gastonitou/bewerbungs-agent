"""
Bewerbungs Agent - Job Application Automation Tool

A legally compliant, SaaS-ready job application preparation system.
"""

__version__ = "0.1.0"
__author__ = "Bewerbungs Agent Team"

from bewerbungs_agent.models import (
    User,
    Profile,
    Job,
    Application,
    Document,
    Email,
    ApplicationStatus,
    SubscriptionPlan,
)

__all__ = [
    "User",
    "Profile",
    "Job",
    "Application",
    "Document",
    "Email",
    "ApplicationStatus",
    "SubscriptionPlan",
]
