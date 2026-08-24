import re

SKILL_CATALOG = [
    "Python", "FastAPI", "Django", "Flask", "JavaScript", "TypeScript", "React", "Node.js",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Machine Learning", "Data Science", "AWS",
    "Azure", "Docker", "Kubernetes", "Git", "REST API", "HTML", "CSS", "Java", "C++",
]


def _section(text: str, names: list[str]) -> str:
    pattern = r"(?is)(?:^|\n)\s*(?:" + "|".join(names) + r")\s*:?\s*\n?(.*?)(?=\n\s*(?:skills?|experience|work history|education|projects?|summary|profile)\s*:?[ \t]*\n|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def parse_resume(text: str) -> dict:
    text = re.sub(r"\\section\*?\{([^}]*)\}", r"\1\n", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email = next((re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", line).group(0) for line in lines if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", line)), None)
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    excluded = {"resume", "curriculum vitae", "cv"}
    name = next((line for line in lines[:5] if not line.startswith("%") and "@" not in line and not re.search(r"\d{5,}", line) and line.lower() not in excluded), "Unknown candidate")
    lower = text.lower()
    skills = [skill for skill in SKILL_CATALOG if skill.lower() in lower]
    exp_text = _section(text, ["experience", "work experience", "work history"])
    experience = []
    for item in re.split(r"\n(?=[A-Z][^\n]{1,60}(?:\||-))", exp_text):
        bits = re.split(r"\s+(?:\||at|-)\s+", item, maxsplit=1, flags=re.I)
        years_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", item, re.I)
        if item.strip():
            experience.append({"company": bits[1].strip() if len(bits) > 1 else "", "role": bits[0].strip(), "years": float(years_match.group(1)) if years_match else 0})
    edu_text = _section(text, ["education", "academic background"])
    education = []
    for item in edu_text.splitlines():
        if item.strip():
            parts = re.split(r"\s+(?:at|,|\|)\s+", item, maxsplit=1, flags=re.I)
            education.append({"degree": parts[0].strip(), "institution": parts[1].strip() if len(parts) > 1 else ""})
    project_text = _section(text, ["projects", "personal projects"])
    certification_text = _section(text, ["certifications", "certificates"])
    return {"name": name, "email": email, "phone": phone_match.group(0).strip() if phone_match else None, "skills": skills, "experience": experience[:10], "education": education[:10], "projects": [line for line in project_text.splitlines() if line][:10], "certifications": [line for line in certification_text.splitlines() if line][:10]}
