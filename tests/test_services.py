from app.schemas import Evaluation
from app.prompts.screening_prompt import build_screening_prompt
from app.services.resume_parser import parse_resume
from app.services.llm_service import LLMService
from app.services.pdf_parser import PDFExtractionError, extract_pdf_text
from app.services.ats_analyzer import analyze_ats


def test_resume_parser_extracts_structured_fields():
    parsed = parse_resume("Jane Doe\njane@example.com\nPython FastAPI SQL\n\nExperience\nSoftware Engineer - Acme Labs 3 years\n\nEducation\nB.Tech Computer Science at State University")
    assert parsed["name"] == "Jane Doe"
    assert parsed["email"] == "jane@example.com"
    assert "Python" in parsed["skills"]
    assert parsed["experience"][0]["years"] == 3
    assert parsed["education"][0]["institution"] == "State University"


def test_pdf_parser_rejects_invalid_input():
    try:
        extract_pdf_text(b"not a pdf")
        assert False
    except PDFExtractionError as error:
        assert "valid PDF" in str(error)


def test_local_screening_is_explainable_without_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    result = LLMService().evaluate({"skills": ["Python", "SQL"], "experience": [], "education": []}, {"required_skills": ["Python", "FastAPI"], "optional_skills": ["Docker"]})
    assert 1 <= result.score <= 10
    assert result.matching_skills == ["Python"]
    assert "FastAPI" in result.missing_skills
    assert result.justification


def test_screening_prompt_requires_structured_json():
    prompt = build_screening_prompt({"skills": ["Python"]}, {"required_skills": ["Python"]})
    for key in ("score", "matching_skills", "missing_skills", "experience_relevance", "justification"):
        assert f'"{key}"' in prompt
    assert "Do not return any additional keys or prose outside the JSON object." in prompt


def test_evaluation_schema_rejects_out_of_range_score():
    try:
        Evaluation(score=11, experience_relevance="", education_relevance="", justification="")
        assert False
    except ValueError:
        pass


def test_ats_analyzer_rewards_extractable_resume():
    text = "Jane Doe\njane@example.com\n+1 555 123 4567\n\nSkills\nPython, SQL\n\nExperience\nBackend Engineer - Acme - 3 years\n\nEducation\nBSc Computer Science"
    parsed = parse_resume(text)
    score, feedback = analyze_ats(text, parsed)
    assert score >= 70
    assert feedback
