from groq import Groq
import json
import re
from PyPDF2 import PdfReader
import spacy
from .LLM import extract_skills_llm
from django.core.mail import send_mail
from django.conf import settings

# ✅ Lazy loading model (IMPORTANT FIX)
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

# ✅ Load spacy once (OK)
nlp = spacy.load("en_core_web_sm")

Text_initial = ''

# CLEAN TEXT ..............................................................
def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text.lower()).strip()


# GENERATE VECTOR ..........................................................
def generate_vector(text):
    model = get_model()
    emb_res = model.encode(text, convert_to_tensor=True)
    return emb_res


# EXTRACT RESUME ..........................................................
def extract(resume):
    reader = PdfReader(resume)
    full_text = ""
    for page in reader.pages:
        ftext = page.extract_text()
        if ftext:
            full_text += ftext + "\n"
    return full_text


# SKILL SCORE .............................................................
def jaccard_skill_score(data, required_skills):
    resume_set = set(skill.lower().strip() for skill in data)
    required_set = set(skill.lower().strip() for skill in required_skills)

    matched_skills = resume_set.intersection(required_set)
    unmatched_skills = required_set.difference(resume_set)

    matched = ", ".join(matched_skills)
    unmatched = ", ".join(unmatched_skills)

    if len(required_set) == 0:
        score = 0.0
    else:
        score = len(matched_skills) / len(required_set) * 100

    return {
        "score": round(score, 2),
        "matched": matched,
        "unmatched": unmatched
    }


# ENTITY SCORE ............................................................
def entity_score_spacy(resume_text):
    doc = nlp(resume_text)

    important = {"ORG", "DATE", "GPE", "WORK_OF_ART", "PERSON"}

    detected_labels = {ent.label_ for ent in doc.ents}
    matched = detected_labels.intersection(important)

    score = len(matched) / len(important) * 100

    return round(score, 2)


# SEMANTIC SIMILARITY .....................................................
def semantic_similarity(resume_vector, jd_vector):
    from sentence_transformers import util
    similarity = util.cos_sim(jd_vector, resume_vector).item()
    return round(similarity * 100, 2)


# POOL SCORE ..............................................................
def pool_score(final_score):
    if final_score >= 0.75:
        return "Excellent"
    elif final_score >= 0.50:
        return "Good"
    else:
        return "Low"


# ATS SCORE ...............................................................
def atscore(data):
    score = 0

    if data.get('email_present', False):
        score += 0.2

    if data.get('phone_present', False):
        score += 0.2

    if 'sections_found' in data and isinstance(data['sections_found'], list):
        section_count = len(data['sections_found'])
        if section_count >= 4:
            score += 0.2
        elif section_count >= 2:
            score += 0.1

    if data.get('table_like_patterns_detected', False):
        score -= 0.05
    else:
        score += 0.15

    length = data.get('resume_length', 'short')
    if length == 'medium':
        score += 0.05
    elif length == 'long':
        score += 0.1

    return round(score * 100, 2)


# EMAIL FUNCTION ..........................................................
def send_shortlist_email(candidate_email, candidate_name, job_title, company):
    subject = "Congratulations! You Have Been Shortlisted"

    message = f"""
Dear {candidate_name},

We are pleased to inform you that you have been shortlisted for the position of
{job_title} at {company}.

Our team will contact you soon with further details.

Best regards,
{company}
Recruitment Team
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [candidate_email],
        fail_silently=False,
    )