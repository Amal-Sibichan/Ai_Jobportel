import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(
    api_key=api_key,
)
def extract_skills_llm(resume_text):
    prompt =  f"""
You are an ATS analyzer.

From the resume text below, detect ATS-related signals.
Return ONLY valid JSON. Do NOT explain anything.
JSON format:
{{
    "skills": [],
  "email_present": true/false,
  "phone_present": true/false,
  "sections_found": [],
  "table_like_patterns_detected": true/false,
  "resume_length": "short" | "medium" | "long"
}}

DEFINITION RULES:
- skills: list of technical skills only (example: "python", "django", "rest api")
- email_present: true if any email is found
- phone_present: true if any phone number is found
- sections_found: section headings detected in the resume (example: "skills", "experience", "education")
- table_like_patterns_detected: true ONLY if text shows table patterns like '|', columns, or alignment artifacts
- resume_length:
  - short: less than 200 words
  - medium: 200–800 words
  - long: more than 800 words

If a field is not found, return false or an empty list.

DO NOT GUESS.
DO NOT ASSUME.
USE ONLY THE GIVEN TEXT.


Resume text:
\"\"\"
{resume_text}
\"\"\"
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.0,
    )

    atslist= response.choices[0].message.content
    start = atslist.find("{")
    end = atslist.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON found")

    json_text = atslist[start:end]
    return json_text 