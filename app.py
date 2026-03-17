import os
from flask import Flask, render_template, request, redirect, url_for, flash
from resume_parser import extract_text_from_file, estimate_experience_years
from utils import find_skills, score_by_keywords, clean_text
import json
import joblib

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'

SKILLSET_DIR = 'skillsets'
MODEL_PATH = 'models/resume_classifier.pkl'

# Load profiles from JSON files
profiles = {}
if os.path.isdir(SKILLSET_DIR):
    for fname in os.listdir(SKILLSET_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(SKILLSET_DIR, fname), 'r', encoding='utf-8-sig') as fh:
                p = json.load(fh)
                profiles[p['title']] = p

# Try load classifier (optional ML)
classifier = None
if os.path.exists(MODEL_PATH):
    try:
        classifier = joblib.load(MODEL_PATH)   # {'vec': ..., 'clf': ...}
        print("Loaded ML classifier from", MODEL_PATH)
    except Exception as e:
        print("Could not load classifier:", e)
        classifier = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profile_name = request.form.get('profile')
        profile = profiles.get(profile_name)
        file = request.files.get('resume')

        if not profile:
            flash("Select a valid job role.")
            return redirect(url_for('index'))

        if not file or file.filename == '':
            flash("Please upload a resume file.")
            return redirect(url_for('index'))

        os.makedirs('uploads', exist_ok=True)
        tmp_path = os.path.join('uploads', file.filename)
        file.save(tmp_path)

        text = extract_text_from_file(tmp_path)
        if not text.strip():
            flash("Could not extract text from this file. Try a clearer PDF/DOCX/TXT/Image.")
            return redirect(url_for('index'))

        exp = estimate_experience_years(text)
        required = profile['required_skills']
        optional = profile.get('optional_skills', [])

        matched_required = find_skills(text, required)
        matched_optional = find_skills(text, optional)

        keyword_score = score_by_keywords(matched_required, required)
        fit_score = int(keyword_score * 100)

        ml_prediction = None
        if classifier is not None:
            try:
                vec = classifier['vec'].transform([clean_text(text)])
                proba = float(classifier['clf'].predict_proba(vec)[0][1])
                ml_prediction = proba
                fit_score = int(0.6 * fit_score + 0.4 * proba * 100)
            except Exception as e:
                print("ML prediction error:", e)

        result = {
            'profile': profile_name,
            'fit_score': fit_score,
            'matched_required': matched_required,
            'missing_required': [s for s in required if s not in matched_required],
            'matched_optional': matched_optional,
            'experience_est_years': exp,
            'ml_prediction': ml_prediction
        }

        return render_template('index.html', profiles=list(profiles.keys()), result=result)

    return render_template('index.html', profiles=list(profiles.keys()), result=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
