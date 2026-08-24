from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate, Job, ScreeningResult
from ..schemas import ChatRequest, ChatResponse, JobMatchResponse, ScreenRequest, ScreeningResponse
from ..services.llm_service import LLMService, LLMServiceError
from ..services.screening_service import screen_candidates

router = APIRouter(tags=["Screening"])


def to_response(result: ScreeningResult) -> ScreeningResponse:
    eval_dict = result.evaluation or {}
    return ScreeningResponse(job_id=result.job_id, candidate_id=result.candidate_id, candidate_name=result.candidate.name, **eval_dict)


@router.post("/screen", response_model=list[ScreeningResponse], summary="Screen candidates against a job")
def screen(payload: ScreenRequest, db: Session = Depends(get_db)):
    job = db.get(Job, payload.job_id)
    candidates = db.scalars(select(Candidate).where(Candidate.id.in_(payload.candidate_ids))).all()
    if not job:
        raise HTTPException(404, "Job not found.")
    if len(candidates) != len(set(payload.candidate_ids)):
        raise HTTPException(404, "One or more candidates were not found.")
    try:
        return [to_response(result) for result in screen_candidates(db, job, candidates)]
    except LLMServiceError as exc:
        raise HTTPException(503, str(exc)) from exc


@router.get("/screen/results/{job_id}", response_model=list[ScreeningResponse], summary="Get ranked screening results")
def results(job_id: int, db: Session = Depends(get_db)):
    if not db.get(Job, job_id):
        raise HTTPException(404, "Job not found.")
    rows = db.scalars(select(ScreeningResult).where(ScreeningResult.job_id == job_id).order_by(ScreeningResult.score.desc())).all()
    return [to_response(row) for row in rows]


@router.get("/screen/results/{job_id}/download", summary="Download screening results as CSV")
def download_results(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    
    import csv
    import io
    from fastapi.responses import StreamingResponse

    rows = db.scalars(select(ScreeningResult).where(ScreeningResult.job_id == job_id).order_by(ScreeningResult.score.desc())).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Candidate Name", "Match Score", "Recommendation", "Matching Skills", "Missing Skills", "Justification"])
    
    for i, row in enumerate(rows):
        eval_dict = row.evaluation or {}
        writer.writerow([
            i + 1,
            row.candidate.name,
            f"{(row.score * 10):.0f}%",
            eval_dict.get("recommendation", "Consider"),
            ", ".join(eval_dict.get("matching_skills", [])),
            ", ".join(eval_dict.get("missing_skills", [])),
            eval_dict.get("justification", "")
        ])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=screening_report_{job_id}.csv"}
    )


@router.get("/candidates/{candidate_id}/job-matches", response_model=list[JobMatchResponse], summary="Rank jobs for a candidate")
def candidate_job_matches(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found.")
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    rows = []
    service = LLMService()
    for job in jobs:
        evaluation = service.evaluate({"name": candidate.name, "skills": candidate.skills, "experience": candidate.experience, "education": candidate.education, "projects": candidate.projects, "certifications": candidate.certifications}, {"title": job.title, "description": job.description, "required_skills": job.required_skills, "optional_skills": job.optional_skills, "experience_requirement": job.experience_requirement, "education_requirement": job.education_requirement})
        rows.append(JobMatchResponse(job_id=job.id, job_title=job.title, company=job.company, candidate_id=candidate.id, candidate_name=candidate.name, **evaluation.model_dump()))
    return sorted(rows, key=lambda row: row.score, reverse=True)


@router.post("/candidates/{candidate_id}/chat", response_model=ChatResponse, summary="Ask questions about a candidate resume")
def candidate_chat(candidate_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found.")
    answer, provider = LLMService().chat({"name": candidate.name, "skills": candidate.skills, "experience": candidate.experience, "education": candidate.education, "projects": candidate.projects, "certifications": candidate.certifications}, payload.message)
    return ChatResponse(answer=answer, provider=provider)


@router.post("/chat", response_model=ChatResponse, summary="Ask the workspace assistant a question")
def workspace_chat(payload: ChatRequest):
    answer, provider = LLMService().workspace_chat(payload.message)
    return ChatResponse(answer=answer, provider=provider)


@router.get("/jobs/{job_id}/top-candidates", response_model=list[ScreeningResponse], summary="Rank candidates for a job")
def top_candidates(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    ranked = screen_candidates(db, job, candidates)
    return [to_response(result) for result in sorted(ranked, key=lambda result: result.score, reverse=True)]
