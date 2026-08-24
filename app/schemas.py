from pydantic import BaseModel, ConfigDict, Field


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    years: float = 0


class Education(BaseModel):
    degree: str = ""
    institution: str = ""


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    candidate_id: int = Field(alias="id", serialization_alias="candidate_id")
    candidate_name: str = Field(alias="name", serialization_alias="candidate_name")
    email: str | None = None
    phone: str | None = None
    skills: list[str] = []
    experience: list[Experience] = []
    education: list[Education] = []
    projects: list[str] = []
    certifications: list[str] = []
    ats_score: float = 0
    ats_feedback: list[str] = []
    source_filename: str


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    company: str = ""
    description: str = Field(min_length=20)
    required_skills: list[str] = []
    optional_skills: list[str] = []
    experience_requirement: str | None = None
    education_requirement: str | None = None


class JobResponse(JobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ScreenRequest(BaseModel):
    job_id: int
    candidate_ids: list[int] = Field(min_length=1)


class Evaluation(BaseModel):
    score: float = Field(ge=1, le=10)
    matching_skills: list[str] = []
    missing_skills: list[str] = []
    experience_relevance: str
    education_relevance: str
    strengths: list[str] = []
    gaps: list[str] = []
    recommendation: str = "Consider"
    justification: str


class ScreeningResponse(Evaluation):
    candidate_id: int
    candidate_name: str
    job_id: int


class JobMatchResponse(ScreeningResponse):
    job_title: str
    company: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    provider: str
