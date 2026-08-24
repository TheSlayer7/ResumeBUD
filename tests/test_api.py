from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_docs_and_job_validation():
    assert client.get("/docs").status_code == 200
    response = client.post("/jobs", json={"title": "Backend", "description": "too short"})
    assert response.status_code == 422


def test_invalid_upload_type():
    response = client.post("/resumes/upload", files={"file": ("resume.docx", b"hello", "application/octet-stream")})
    assert response.status_code == 415


def test_candidate_chat_missing_candidate():
    response = client.post("/candidates/999999/chat", json={"message": "What am I good at?"})
    assert response.status_code == 404


def test_provider_can_switch_to_local():
    response = client.post("/settings/provider", json={"provider": "local"})
    assert response.status_code == 200
    assert response.json()["provider"] == "local"
