SYSTEM_PROMPT = """You are an evidence-based recruiting analyst. Evaluate only facts present in the supplied structured resume and job requirements. Never invent skills, dates, employers, or qualifications. Treat semantic equivalents as matches only when the equivalence is clear. Distinguish required from optional skills.

Return exactly one valid JSON object, never a number or markdown. Use this schema: score (number from 1 to 10), matching_skills (array of strings), missing_skills (array of required-skill strings), experience_relevance (string), education_relevance (string), strengths (array of strings), gaps (array of strings), recommendation (string), and justification (string of 3-5 evidence-based sentences covering fit, evidence, gaps, and recommendation). Use empty arrays when there is no evidence; do not omit keys or invent evidence."""


def build_screening_prompt(candidate: dict, job: dict) -> str:
    return f"""Compare this candidate to this job. Required skills are more important than optional skills. Consider relevant experience and education only when the job makes them relevant.

CANDIDATE:\n{candidate}\n\nJOB:\n{job}\n\nReturn exactly this JSON shape:\n{{"score": 7.5, "matching_skills": ["Python"], "missing_skills": ["FastAPI"], "experience_relevance": "Relevant backend experience is present.", "education_relevance": "Relevant technical education is present.", "strengths": ["Demonstrated Python experience"], "gaps": ["FastAPI is not evidenced"], "recommendation": "Consider", "justification": "Use only evidence from the supplied profile and requirements. Explain the score, matches, gaps, and recommendation in 3-5 sentences."}}\nDo not return any additional keys or prose outside the JSON object."""


def build_job_match_prompt(candidate: dict, jobs: list[dict]) -> str:
    return f"""Rank these jobs for the candidate using only evidence in the candidate profile. Never invent qualifications. Return JSON as an array with job_id, score, matching_skills, missing_skills, experience_relevance, and justification for each job, sorted from best fit to weakest fit.

CANDIDATE:\n{candidate}\n\nAVAILABLE JOBS:\n{jobs}"""
