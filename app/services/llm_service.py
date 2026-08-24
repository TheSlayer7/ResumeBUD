import json
import os

from ..prompts.screening_prompt import SYSTEM_PROMPT, build_screening_prompt
from ..schemas import Evaluation


class LLMServiceError(RuntimeError):
    pass


class LLMService:
    def evaluate(self, candidate: dict, job: dict) -> Evaluation:
        provider = os.getenv("LLM_PROVIDER", "local").lower()
        if provider == "local":
            return self._local_evaluation(candidate, job)
        if provider == "ollama":
            try:
                return self._ollama_evaluation(candidate, job)
            except Exception:
                return self._local_evaluation(candidate, job)
        if provider == "gemini":
            try:
                return self._gemini_evaluation(candidate, job)
            except Exception:
                return self._local_evaluation(candidate, job)
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            return self._local_evaluation(candidate, job)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0, response_format={"type": "json_object"}, messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_screening_prompt(candidate, job)}])
            return Evaluation.model_validate(json.loads(response.choices[0].message.content))
        except Exception as exc:
            raise LLMServiceError("The semantic evaluation service is currently unavailable.") from exc

    def _ollama_evaluation(self, candidate: dict, job: dict) -> Evaluation:
        import httpx

        response = httpx.post(
            f"{os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')}/api/chat",
            json={
                "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_screening_prompt(candidate, job)},
                ],
            },
            timeout=90,
        )
        response.raise_for_status()
        return Evaluation.model_validate(json.loads(response.json()["message"]["content"]))

    def _gemini_evaluation(self, candidate: dict, job: dict) -> Evaluation:
        import httpx

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMServiceError("GEMINI_API_KEY is not configured.")
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": api_key},
            json={
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": build_screening_prompt(candidate, job)}]}],
                "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
            },
            timeout=90,
        )
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return Evaluation.model_validate(json.loads(content))

    def chat(self, candidate: dict, message: str) -> tuple[str, str]:
        provider = os.getenv("LLM_PROVIDER", "local").lower()
        if provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            try:
                import httpx
                prompt = f"Answer the recruiter's question using only this candidate profile. Do not invent facts. Candidate: {candidate}\nQuestion: {message}"
                response = httpx.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')}:generateContent",
                    params={"key": os.getenv("GEMINI_API_KEY")},
                    json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}},
                    timeout=60,
                )
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"], "Gemini"
            except Exception as exc:
                return self._local_chat(candidate, message), f"Local fallback (Gemini unavailable: {type(exc).__name__})"
        return self._local_chat(candidate, message), "Local"

    def _local_chat(self, candidate: dict, message: str) -> str:
        skills = ", ".join(candidate.get("skills", [])) or "no skills were detected"
        experience = "; ".join(f"{item.get('role', 'Role')} at {item.get('company', 'an employer')} ({item.get('years', 0)} years)" for item in candidate.get("experience", [])) or "no experience was detected"
        question = message.lower()
        if "good" in question or "strength" in question or "skill" in question:
            return f"Based on the extracted resume evidence, the strongest signals are: {skills}. Experience evidence: {experience}."
        if "improv" in question or "gap" in question:
            return "Focus on adding measurable outcomes to experience bullets, naming the tools used in projects, and clearly stating missing role requirements. The current profile does not provide enough evidence for more specific advice."
        return f"I can help review this resume. It currently shows {len(candidate.get('skills', []))} skills, {len(candidate.get('experience', []))} experience entries, and {len(candidate.get('education', []))} education entries. Ask me about strengths, gaps, skills, or interview preparation."

    def workspace_chat(self, message: str) -> tuple[str, str]:
        provider = os.getenv("LLM_PROVIDER", "local").lower()
        if provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            try:
                import httpx
                prompt = f"You are ResumeBUD, a concise recruiting workspace assistant. Answer this question about using the app in under 80 words. Do not claim to perform actions you cannot perform.\nQuestion: {message}"
                response = httpx.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')}:generateContent",
                    params={"key": os.getenv("GEMINI_API_KEY")},
                    json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}},
                    timeout=60,
                )
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"], "Gemini"
            except Exception as exc:
                return self._local_workspace_chat(message), f"Local fallback (Gemini unavailable: {type(exc).__name__})"
        return self._local_workspace_chat(message), "Local"

    def _local_workspace_chat(self, message: str) -> str:
        question = message.lower()
        if "upload" in question:
            return "Open Resumes to add PDF, TXT, or TEX files. The app will extract the candidate details automatically."
        if "screen" in question or "match" in question:
            return "Open Screening, choose a job and candidates, then run Analyze to compare them."
        if "job" in question:
            return "Open Jobs to create, search, and inspect role briefs."
        if "candidate" in question or "resume" in question:
            return "Open Candidates to search profiles and inspect best-fit roles."
        return "I can help you navigate Resumes, Jobs, Screening, Candidates, and Settings. What would you like to do?"

    def _local_evaluation(self, candidate: dict, job: dict) -> Evaluation:
        candidate_skills = {skill.lower(): skill for skill in candidate.get("skills", [])}
        required = job.get("required_skills", [])
        optional = job.get("optional_skills", [])
        matching = [skill for skill in required + optional if skill.lower() in candidate_skills]
        missing = [skill for skill in required if skill.lower() not in candidate_skills]
        required_score = len([skill for skill in required if skill not in missing]) / max(len(required), 1)
        optional_score = len([skill for skill in optional if skill in matching]) / max(len(optional), 1)
        score = round(max(1, min(10, 1 + 8 * (required_score * 0.8 + optional_score * 0.2))), 1)
        recommendation = "Strong Match" if score >= 8 else "Good Match" if score >= 6 else "Consider" if score >= 4 else "Not Recommended"
        exp_relevance = "Strong" if candidate.get("experience") else "Limited evidence"
        strengths = ([f"Matches {len(matching)} listed skill requirement(s)"] if matching else ["No listed skills matched directly"])
        gaps = ([f"No demonstrated experience with {', '.join(missing)}"] if missing else ["No required skill gaps were identified"])
        evidence = ", ".join(matching) if matching else "no directly matching listed skills"
        gap_text = ", ".join(missing) if missing else "none from the required list"
        experience_text = "Relevant experience is present in the extracted profile." if candidate.get("experience") else "The resume does not contain structured experience evidence."
        justification = (f"This candidate matches {len(matching)} of {len(required)} required skills, including {evidence}. "
                 f"{experience_text} The main evidence gap is {gap_text}. "
                 f"The recommendation is {recommendation.lower()} based on the weighted local comparison; this result is deterministic and uses only extracted resume fields.")
        return Evaluation(score=score, matching_skills=matching, missing_skills=missing, experience_relevance=exp_relevance, education_relevance="Not assessed", strengths=strengths, gaps=gaps, recommendation=recommendation, justification=justification)
