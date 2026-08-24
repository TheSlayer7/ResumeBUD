from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate
from ..schemas import CandidateResponse
from ..services.pdf_parser import PDFExtractionError, extract_pdf_text_with_metadata
from ..services.resume_parser import parse_resume
from ..services.ats_analyzer import analyze_ats

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED, summary="Upload and parse a PDF or text resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename or "resume.pdf"
    is_pdf = file.content_type == "application/pdf" or filename.lower().endswith(".pdf")
    is_text = file.content_type == "text/plain" or filename.lower().endswith((".txt", ".tex"))
    if not is_pdf and not is_text:
        raise HTTPException(415, "Only PDF, TXT, or TEX resumes are supported.")
    try:
        content = await file.read()
        if not content:
            raise HTTPException(422, "The uploaded resume is empty.")
        used_ocr = False
        if is_text:
            text = content.decode("utf-8", errors="replace").strip()
        else:
            text, used_ocr = extract_pdf_text_with_metadata(content)
        if not text:
            raise HTTPException(422, "The uploaded resume contains no readable text.")
        parsed = parse_resume(text)
        ats_score, ats_feedback = analyze_ats(text, parsed, used_ocr=used_ocr)
        candidate = Candidate(**parsed, ats_score=ats_score, ats_feedback=ats_feedback, used_ocr=used_ocr, raw_text=text, source_filename=filename)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate
    except PDFExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, "The resume could not be stored.") from exc


@router.get("", response_model=list[CandidateResponse], summary="List uploaded candidates")
def list_resumes(db: Session = Depends(get_db)):
    return db.query(Candidate).order_by(Candidate.created_at.desc()).all()


@router.get("/{candidate_id}", response_model=CandidateResponse, summary="Get a candidate profile")
def get_resume(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found.")
    return candidate
