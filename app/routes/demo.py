from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate, Job
from ..services.screening_service import screen_candidates

router = APIRouter(tags=["Demo"])


@router.post("/demo", summary="Seed a small labelled demo dataset")
def seed_demo(db: Session = Depends(get_db)):
    if not db.query(Candidate).filter(Candidate.source_filename == "DEMO DATA").first():
        db.add_all([
            Candidate(name="Ava Morgan", email="ava.demo@example.com", phone=None, skills=["Python", "FastAPI", "SQL", "Docker", "Git"], experience=[{"company": "Northstar Labs", "role": "Backend Engineer", "years": 4}], education=[{"degree": "BSc Computer Science", "institution": "State University"}], projects=["Payments API", "Candidate analytics dashboard"], certifications=["AWS Cloud Practitioner"], raw_text="Demo candidate", source_filename="DEMO DATA"),
            Candidate(name="Noah Patel", email="noah.demo@example.com", phone=None, skills=["JavaScript", "React", "Node.js", "SQL", "Git"], experience=[{"company": "Orbit Studio", "role": "Full Stack Developer", "years": 3}], education=[{"degree": "BTech Information Technology", "institution": "Metro Institute"}], projects=["Recruiting portal"], certifications=[], raw_text="Demo candidate", source_filename="DEMO DATA"),
            Candidate(name="Mia Chen", email="mia.demo@example.com", phone=None, skills=["Python", "Machine Learning", "Data Science", "SQL"], experience=[{"company": "Signal Works", "role": "Data Analyst", "years": 2}], education=[{"degree": "MSc Data Science", "institution": "Tech University"}], projects=["Demand forecasting model"], certifications=["Google Data Analytics"], raw_text="Demo candidate", source_filename="DEMO DATA"),
        ])
    job = db.query(Job).filter(Job.title == "Senior Backend Engineer").first()
    role_specs = [
        ("Senior Backend Engineer", ["Python", "FastAPI", "SQL", "REST API"], ["Docker", "AWS"], "3+ years"),
        ("Frontend React Engineer", ["JavaScript", "React", "TypeScript", "CSS"], ["Node.js", "Git"], "2+ years"),
        ("Data & ML Analyst", ["Python", "SQL", "Machine Learning", "Data Science"], ["AWS", "Java"], "2+ years"),
    ]
    jobs = []
    for title, required, optional, experience in role_specs:
        job = db.query(Job).filter(Job.title == title).first()
        if not job:
            job = Job(title=title, company="ResumeBUD", description=f"Join the product team as a {title}. Build measurable, reliable solutions and collaborate across disciplines.", required_skills=required, optional_skills=optional, experience_requirement=experience, education_requirement="Computer Science or equivalent")
            db.add(job)
        jobs.append(job)
    db.commit()
    candidates = db.query(Candidate).all()
    for job in jobs:
        screen_candidates(db, job, candidates)
    return {"created": True, "job_id": jobs[0].id, "job_count": len(jobs)}