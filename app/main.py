from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import demo, jobs, resumes, screening, settings

load_dotenv()

app = FastAPI(title="Smart Resume Screener", version="1.0.0", description="Explainable resume-to-job matching API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(screening.router)
app.include_router(demo.router)
app.include_router(settings.router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="frontend")


@app.on_event("startup")
def startup():
    init_db()
