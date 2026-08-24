from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Candidate, Job, ScreeningResult
from .llm_service import LLMService


def screen_candidates(db: Session, job: Job, candidates: list[Candidate]) -> list[ScreeningResult]:
    results = []
    service = LLMService()
    for candidate in candidates:
        evaluation = service.evaluate({"name": candidate.name, "skills": candidate.skills, "experience": candidate.experience, "education": candidate.education, "projects": candidate.projects, "certifications": candidate.certifications}, {"title": job.title, "description": job.description, "required_skills": job.required_skills, "optional_skills": job.optional_skills, "experience_requirement": job.experience_requirement, "education_requirement": job.education_requirement})
        existing = db.scalar(select(ScreeningResult).where(ScreeningResult.job_id == job.id, ScreeningResult.candidate_id == candidate.id))
        if existing:
            existing.score = evaluation.score
            existing.evaluation = evaluation.model_dump()
            result = existing
        else:
            result = ScreeningResult(job_id=job.id, candidate_id=candidate.id, score=evaluation.score, evaluation=evaluation.model_dump())
            db.add(result)
        results.append(result)
    db.commit()
    return results
