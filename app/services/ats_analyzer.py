import re


SECTION_ALIASES = {
    "skills": ("skills", "technical skills", "core skills", "technologies"),
    "experience": ("experience", "work experience", "professional experience", "work history"),
    "education": ("education", "academic background"),
    "projects": ("projects", "personal projects", "selected projects"),
}


def _found_sections(text: str) -> set[str]:
    sections = set()
    for line in text.splitlines():
        line = re.sub(r"\\(?:sub)?section\*?\s*\{([^}]*)\}", r"\1", line, flags=re.I)
        heading = re.sub(r"[^a-z ]", " ", line.lower())
        heading = re.sub(r"\s+", " ", heading).strip()
        for section, aliases in SECTION_ALIASES.items():
            if heading in aliases:
                sections.add(section)
    return sections


def analyze_ats(text: str, parsed: dict, *, used_ocr: bool = False) -> tuple[float, list[str]]:
    lower = text.lower()
    score = 20.0 if len(text.strip()) >= 100 else 5.0
    feedback = []
    if parsed.get("email"):
        score += 15
    else:
        feedback.append("Add a plain-text email address near the top of the resume.")
    if re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text):
        score += 10
    else:
        feedback.append("Add a readable phone number for reliable ATS contact extraction.")
    found_sections = _found_sections(text)
    found = len(found_sections)
    score += found * 10
    if found < 3:
        feedback.append("Use clear standard headings such as Skills, Experience, Education, and Projects.")
    if parsed.get("skills"):
        score += 10
    else:
        feedback.append("List skills as selectable plain text instead of relying on icons or images.")
    if parsed.get("experience"):
        score += 10
    else:
        feedback.append("Add structured role, employer, and date details under Experience.")
    if len(text) > 15000:
        feedback.append("Consider shortening the resume; very long documents can reduce recruiter scanability.")
    if used_ocr:
        score -= 25
        feedback.append("This resume required OCR; upload a PDF with selectable text for more reliable ATS extraction.")
    score = max(0.0, min(100.0, round(score, 1)))
    if score >= 80:
        feedback.insert(0, "Highly extractable: standard sections and contact details are clear.")
    elif score >= 55:
        feedback.insert(0, "Mostly extractable: a few formatting or structure improvements would help.")
    else:
        feedback.insert(0, "Low extractability: simplify formatting and use selectable text for ATS reliability.")
    return score, feedback