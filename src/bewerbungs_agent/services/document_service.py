"""Document generation service for cover letters and CV optimization."""

from typing import Optional
from sqlalchemy.orm import Session

from bewerbungs_agent.models import Document, Profile, Job


class DocumentService:
    """Service for generating application documents."""

    @staticmethod
    def generate_cover_letter_template(
        profile: Profile, job: Job, language: str = "en"
    ) -> str:
        """
        Generate a cover letter using templates.
        In production, this would integrate with AI services.
        """
        template_en = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.role} position at {job.company}.

With {profile.experience_years or 'several'} years of experience and expertise in {', '.join(profile.skills[:3]) if profile.skills else 'relevant skills'}, I am confident I can contribute effectively to your team.

Key highlights of my background:
- Proven expertise in {', '.join(profile.skills[:5]) if profile.skills else 'relevant technologies'}
- Strong track record in delivering high-quality results
- Excellent communication and collaboration skills

I am particularly excited about this opportunity at {job.company} because it aligns perfectly with my career goals and expertise.

I would welcome the opportunity to discuss how my skills and experience can benefit your team.

Best regards,
{profile.full_name}
{profile.phone or ''}
{profile.user.email}
"""

        template_de = f"""Sehr geehrte Damen und Herren,

mit großem Interesse bewerbe ich mich auf die Position {job.role} bei {job.company}.

Mit {profile.experience_years or 'mehrjähriger'} Berufserfahrung und Expertise in {', '.join(profile.skills[:3]) if profile.skills else 'relevanten Bereichen'} bin ich überzeugt, einen wertvollen Beitrag zu Ihrem Team leisten zu können.

Meine wichtigsten Qualifikationen:
- Fundierte Kenntnisse in {', '.join(profile.skills[:5]) if profile.skills else 'relevanten Technologien'}
- Nachweisbare Erfolge in der Umsetzung anspruchsvoller Projekte
- Ausgeprägte Kommunikations- und Teamfähigkeit

Ich freue mich sehr über die Möglichkeit, meine Fähigkeiten und Erfahrungen bei {job.company} einzubringen.

Gerne stelle ich mich Ihnen in einem persönlichen Gespräch vor.

Mit freundlichen Grüßen,
{profile.full_name}
{profile.phone or ''}
{profile.user.email}
"""

        return template_de if language == "de" else template_en

    @staticmethod
    def calculate_fit_score(profile: Profile, job: Job) -> float:
        """
        Calculate how well a profile matches a job (0-100).
        Simple keyword matching - in production, use ML/NLP.
        """
        if not profile.skills or not job.requirements:
            return 50.0  # Default score
        
        # Simple keyword matching
        profile_skills = set([s.lower() for s in profile.skills])
        job_text = (job.requirements + " " + job.description).lower()
        
        matches = sum(1 for skill in profile_skills if skill in job_text)
        score = min(100.0, (matches / max(len(profile_skills), 1)) * 100)
        
        # Boost if location matches
        if profile.location and job.location:
            if profile.location.lower() in job.location.lower():
                score = min(100.0, score + 10)
        
        return round(score, 1)

    @staticmethod
    def generate_cv_optimization_notes(profile: Profile, job: Job) -> str:
        """Generate suggestions for optimizing CV for this job."""
        notes = []
        
        if job.requirements:
            notes.append(f"Highlight experience with: {job.requirements[:100]}...")
        
        if profile.skills:
            notes.append(f"Emphasize these relevant skills: {', '.join(profile.skills[:5])}")
        
        notes.append(f"Tailor your CV to emphasize {job.role} experience")
        notes.append("Use keywords from the job description")
        notes.append("Quantify achievements where possible")
        
        return "\n".join(notes)

    @staticmethod
    def generate_form_answers(profile: Profile, job: Job) -> dict:
        """Generate pre-filled answers for common application form fields."""
        return {
            "full_name": profile.full_name,
            "email": profile.user.email if profile.user else "",
            "phone": profile.phone or "",
            "location": profile.location or "",
            "experience_years": profile.experience_years or 0,
            "education": profile.education or [],
            "skills": profile.skills or [],
            "motivation": f"I am very interested in the {job.role} position at {job.company}. "
                         f"My background in {', '.join(profile.skills[:3]) if profile.skills else 'relevant areas'} "
                         f"makes me a strong candidate for this role.",
            "availability": "Immediate / Upon agreement",
            "salary_expectations": profile.preferences.get("salary_range") if profile.preferences else "Negotiable",
        }

    @staticmethod
    def create_document(
        db: Session,
        application_id: int,
        profile: Profile,
        job: Job,
    ) -> Document:
        """Create complete document package for an application."""
        document = Document(
            application_id=application_id,
            cover_letter_en=DocumentService.generate_cover_letter_template(
                profile, job, "en"
            ),
            cover_letter_de=DocumentService.generate_cover_letter_template(
                profile, job, "de"
            ),
            cv_optimization_notes=DocumentService.generate_cv_optimization_notes(
                profile, job
            ),
            form_answers=DocumentService.generate_form_answers(profile, job),
            generation_method="template",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_document(db: Session, application_id: int) -> Optional[Document]:
        """Get document for an application."""
        return db.query(Document).filter(
            Document.application_id == application_id
        ).first()
