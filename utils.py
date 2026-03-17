import re
import string

def clean_text(t):
    if not t:
        return ""
    t = t.lower()
    t = t.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    t = re.sub(r"\s+", " ", t).strip()
    return t

def find_skills(text, skills):
    t = clean_text(text)
    found = []
    for s in skills:
        pattern = r"\b" + re.escape(s.lower()) + r"\b"
        if re.search(pattern, t):
            found.append(s)
    return found

def score_by_keywords(found, required):
    if not required:
        return 0.0
    return len(found) / len(required)
