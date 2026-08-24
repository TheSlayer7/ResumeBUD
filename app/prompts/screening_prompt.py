SYSTEM_PROMPT = """You are an evidence-based recruiting analyst. Evaluate only facts present in the supplied structured resume and job requirements. Never invent skills, dates, employers, or qualifications. Treat semantic equivalents as matches only when the equivalence is clear. Distinguish required from optional skills. Return JSON matching the requested schema, with a score from 1 to 10 and a detailed evidence-based justification of 3-5 sentences covering fit, evidence, gaps, and recommendation."""


def build_screening_prompt(candidate: dict, job: dict) -> str:
    return f"""Compare this candidate to this job. Required skills are more important than optional skills. Consider relevant experience and education only when the job makes them relevant.

CANDIDATE:\n{candidate}\n\nJOB:\n{job}\n\nReturn exactly these JSON keys: score, matching_skills, missing_skills, experience_relevance, education_relevance, strengths, gaps, justification."""


def build_job_match_prompt(candidate: dict, jobs: list[dict]) -> str:
    return f"""Rank these jobs for the candidate using only evidence in the candidate profile. Never invent qualifications. Return JSON as an array with job_id, score, matching_skills, missing_skills, experience_relevance, and justification for each job, sorted from best fit to weakest fit.

CANDIDATE:\n{candidate}\n\nAVAILABLE JOBS:\n{jobs}"""
