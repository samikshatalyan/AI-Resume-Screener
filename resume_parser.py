import re
from pdfminer.high_level import extract_text
from docx import Document
from PIL import Image
import pytesseract

# If needed, set tesseract.exe path manually, e.g.:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(path):
    try:
        return extract_text(path)
    except Exception as e:
        print("PDF parse error:", e)
        return ""

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print("DOCX parse error:", e)
        return ""

def extract_text_from_image(path):
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print("IMAGE parse error:", e)
        return ""

def extract_text_from_file(path):
    lp = path.lower()
    if lp.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif lp.endswith(".docx"):
        return extract_text_from_docx(path)
    elif lp.endswith(".txt"):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print("TXT parse error:", e)
            return ""
    elif lp.endswith((".png", ".jpg", ".jpeg", ".bmp")):
        return extract_text_from_image(path)
    else:
        # fallback: try pdf
        return extract_text_from_pdf(path)

def estimate_experience_years(text):
    years = re.findall(r'\b(20\d{2})\b', text)
    years = [int(y) for y in years] if years else []
    if len(years) >= 2:
        return max(years) - min(years)

    m = re.search(r'(\d+)\s+years?', text.lower())
    if m:
        try:
            return int(m.group(1))
        except:
            return None

    return None
