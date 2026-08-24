import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job
from ..schemas import JobCreate, JobResponse
from ..services.resume_parser import SKILL_CATALOG

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=201, summary="Create a job description")
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    inferred = [skill for skill in SKILL_CATALOG if skill.lower() in payload.description.lower()]
    required = list(dict.fromkeys(payload.required_skills + inferred))
    job = Job(**payload.model_dump(exclude={"required_skills"}), required_skills=required)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobResponse], summary="List jobs")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job
