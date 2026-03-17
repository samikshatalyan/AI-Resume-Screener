import os
import random
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def generate_synthetic(required_skills, n=500):
    X, y = [], []
    for _ in range(n):
        k = random.randint(0, len(required_skills))
        chosen = random.sample(required_skills, k) if k > 0 else []
        text = " ".join(chosen) + " experience in projects and teamwork"
        X.append(text)
        y.append(1 if k >= max(1, len(required_skills)//2) else 0)
    return X, y

if __name__ == "__main__":
    required_skills = [
        "python","machine learning","data analysis","pandas","numpy",
        "matplotlib","statistics","sql","scikit-learn","data visualization"
    ]
    X, y = generate_synthetic(required_skills, n=500)
    vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
    Xv = vec.fit_transform(X)
    clf = LogisticRegression(max_iter=500)
    clf.fit(Xv, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump({"vec": vec, "clf": clf}, os.path.join("models","resume_classifier.pkl"))
    print("Saved model to models/resume_classifier.pkl")
