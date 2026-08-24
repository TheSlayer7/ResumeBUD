<div align="center">
  <img src="https://img.icons8.com/external-flat-icons-inmotus-design/64/external-AI-artificial-intelligence-flat-icons-inmotus-design-3.png" alt="Logo" width="80" height="80">
  <h1 align="center">Smart Resume Screener (ResumeBUD)</h1>

  <p align="center">
    An intelligent, explainable resume screening service for parsing resumes, extracting skills, and matching candidates with job descriptions.
    <br />
    <a href="#features"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#demo-video">View Demo</a>
    ·
    <a href="#api-endpoints">API Reference</a>
    ·
    <a href="#screenshots">Screenshots</a>
  </p>
</div>

<!-- Badges -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</div>

<hr />

## 🎥 Demo Video

> **Watch the Loom Video Below:**  
> Watch the 2-3 minute demonstration of the Smart Resume Screener in action.  

<div align="center">
  <!-- LOOM VIDEO PLACEHOLDER -->
  <a href="YOUR_LOOM_VIDEO_LINK_HERE" target="_blank">
    <img src="https://cdn.loom.com/sessions/thumbnails/YOUR_LOOM_VIDEO_THUMBNAIL_ID.jpg" alt="Watch the video" width="600"/>
  </a>
</div>

*Replace the link and image above with your actual Loom video URL and thumbnail.*

## ✨ Features

- 📄 **Intelligent Resume Parsing:** Extract structured data (Name, Email, Phone, Skills, Experience, Education) using `PyMuPDF`.
- 🔍 **OCR Fallback:** Support for scanned/image-only PDFs via Tesseract.
- 🎯 **Semantic Matching & Scoring:** Compare resumes with job descriptions using LLMs (OpenAI, Gemini, Ollama) and output an explainable 1-10 match score with justification.
- 📊 **ATS Extractability Score:** Get feedback from 0-100 on how machine-readable a resume is.
- 💻 **Dashboard Interface:** Lightweight frontend for uploading resumes, creating jobs, and screening.
- 🔐 **Privacy-First Local Mode:** Includes a deterministic local scorer for use without API keys.

## 📸 Screenshots

| Dashboard Overview | Candidate Profile & Screening |
| :---: | :---: |
| <img src="https://placehold.co/600x400/1e1e2f/ffffff?text=Dashboard+Screenshot" alt="Dashboard" width="100%"> | <img src="https://placehold.co/600x400/1e1e2f/ffffff?text=Screening+Results+Screenshot" alt="Screening" width="100%"> |

*(Replace the placeholder images with screenshots of your running app)*

## 🛠️ Tech Stack & Tools Used

| Category | Technology |
|---|---|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=sqlalchemy&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| **AI & LLM** | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) ![Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat&logo=google-gemini&logoColor=white) |
| **PDF Processing**| `PyMuPDF`, `pytesseract` (OCR) |

## 🏗️ Architecture

```mermaid
graph TD;
    Client[Dashboard / API Client] --> API[FastAPI Backend];
    API --> Routes[Routes / Endpoints];
    Routes --> PDFService[PDF Parser Service];
    Routes --> ResumeService[Resume Extractor Service];
    Routes --> LLMService[LLM / Scoring Service];
    Routes --> ScreenService[Screening Service];
    
    PDFService --> OCR[Tesseract OCR Fallback];
    LLMService --> Provider{LLM Provider};
    Provider -->|OpenAI| OAI[OpenAI API];
    Provider -->|Gemini| GEM[Google Gemini API];
    Provider -->|Local| LOC[Ollama / Deterministic];
    
    Routes --> ORM[SQLAlchemy];
    ORM --> DB[(SQLite Database)];
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Tesseract OCR (Optional, for scanned PDFs)

### 1. Clone & Install

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file to set your preferred LLM provider. The project comes with a **Local Deterministic Scorer** by default, but you can configure an LLM:

**OpenAI (Recommended):**
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini
```

**Google Gemini (Free Tier):**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Ollama (Local):**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

### 3. Run the Server
```bash
python run.py
```
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) for the dashboard, or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger API documentation.

## 🔌 API Endpoints

- `POST /resumes/upload`: Upload a PDF/TXT resume to extract and store candidate data.
- `GET /resumes`: List all parsed candidates.
- `GET /resumes/{candidate_id}`: Retrieve a specific candidate's structured profile.
- `POST /jobs`: Create a new job listing with required skills.
- `POST /screen`: Screen candidates against a job description.
- `GET /screen/results/{job_id}`: Retrieve ranked screening results.

## 🧠 LLM Usage Guidance

**Prompts Design (`app/prompts/screening_prompt.py`):**
- Ensures evidence-only evaluation without inventing qualifications.
- Differentiates between 'nice-to-have' and 'required' skills.
- Demands machine-readable JSON output for explainability.
- Example LLM instruction: *"Compare the following resume with this job description and rate fit on 1–10 with justification, listing matching skills, gaps, and strengths."*

## 🛡️ Best Practices & Security

- **Secrets Management:** The repository includes a strict `.gitignore` to prevent committing `.env` files, API keys, or uploaded applicant resumes.
- **Data Privacy:** Local mode ensures no applicant data leaves your machine. Be mindful of terms when using cloud APIs.
