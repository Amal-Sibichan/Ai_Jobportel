from groq import Groq
import json
from sentence_transformers import SentenceTransformer, util
import re
from PyPDF2 import PdfReader
import spacy
from .LLM import extract_skills_llm
model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")
Text_initial=''
# CLEAN TEXT ..............................................................

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text.lower()).strip()

# GENERATE VECTOR............................................................

def generate_vector(text):
    emb_res = model.encode(text, convert_to_tensor=True)

    return emb_res

# EXTRACT RESUME.................................................................

def extract(resume):
    reader = PdfReader(resume)
    full_text = ""
    for page in reader.pages:
        ftext = page.extract_text()
        if ftext:
            full_text += ftext + "\n"
    return full_text

# SKILL SCORE CALCULATION.......................................................
def jaccard_skill_score(data, required_skills):
    resume_set = set(skill.lower().strip() for skill in data)
    required_set = set(skill.lower().strip() for skill in required_skills)
    matched_skills = resume_set.intersection(required_set)
    unmatched_skills = required_set.difference(resume_set)
    matched=", ".join(matched_skills)
    unmatched=", ".join(unmatched_skills)
    if len(required_set) == 0:
        score = 0.0
    else:
        # Note: This is technically an "Overlap Coefficient" logic 
        # based on your original denominator of len(required_set)
        score = len(matched_skills) / len(required_set)

    return {
        "score": round(score, 2),
        "matched": matched,
        "unmatched": unmatched
    }

# FINDONG IMPORTENT ENTITIES............................................................................

def entity_score_spacy(resume_text):
    doc = nlp(resume_text)

    important = {"ORG", "DATE", "GPE", "WORK_OF_ART", "PERSON"}

    # Get unique entity labels
    detected_labels = {ent.label_ for ent in doc.ents}

    # Find which important entity types are present
    matched = detected_labels.intersection(important)

    # print("Detected entity types:", detected_labels)
    # print("Important entity types found:", matched)

    # Normalize score (max = number of important entity types)
    score = len(matched) / len(important)

    return round(score, 2)

# SEMANTIC SIMILARITY............................................................................

def semantic_similarity(resume_vector, jd_vector):
    similarity = util.cos_sim(jd_vector, resume_vector).item()
    return round(similarity, 2)


# POOLING............................................................................
def pool_score(scores,skill,ats,ent,sem):
        if skill < 0.3 or sem < 0.3 or ats < 0.3 or ent < 0.3:
            return "Poor"

    # Excellent
        if scores >= 0.75 and skill >= 0.6 and sem >= 0.6:
            return "Excellent"

    # Good
        if scores >= 0.6:
            return "Good"

    # Average
        if scores >= 0.4:
             return "Average"

        return "Poor"

# ATS SCORE............................................................................
def  atscore(data):
    score=0

    # email presence
    if data.get('email_present', False):
        score += 0.2

    # phone presence
    if data.get('phone_present', False):
        score += 0.2

    # sections found
    if 'sections_found' in data and isinstance(data['sections_found'], list):
        section_count = len(data['sections_found'])
        if section_count >= 4:
            score += 0.2
        elif section_count >= 2:
            score += 0.1

    # table-like patterns
    if  data.get('table_like_patterns_detected', False):
        score -= 0.05
    else:
        score += 0.15

    # resume length
    length = data.get('resume_length', 'short')
    if length == 'medium':
        score += 0.05
    elif length == 'long':
        score += 0.1

    return round(score, 2)




    


