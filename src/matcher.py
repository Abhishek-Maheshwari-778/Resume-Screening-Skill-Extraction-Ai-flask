import math
import re
from collections import Counter
from extractor import extract_skills

def compute_tf_cosine(text1, text2):
    tokens1 = re.findall(r'\b\w+\b', text1.lower())
    tokens2 = re.findall(r'\b\w+\b', text2.lower())
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'to', 'is', 'in', 'it', 'for', 'of', 'with', 'on', 'as', 'at', 'by', 'from', 'this', 'that'}
    tokens1 = [t for t in tokens1 if t not in stop_words]
    tokens2 = [t for t in tokens2 if t not in stop_words]
    
    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator

def calculate_similarity(resume_text, job_description, catalog=None):
    """Calculates similarity score using a mix of TF-IDF and Keyword Overlap."""
    if not resume_text or not job_description:
        return 0.0, []
        
    # 1. TF-IDF Cosine Similarity
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        documents = [resume_text, job_description]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ImportError:
        tfidf_score = compute_tf_cosine(resume_text, job_description)
    
    # 2. Keyword Overlap (Flattening categories for comparison)
    resume_skills_dict = extract_skills(resume_text, categories=catalog)
    jd_skills_dict = extract_skills(job_description, categories=catalog)
    
    resume_skills = set([s for cat in resume_skills_dict.values() for s in cat])
    jd_skills = set([s for cat in jd_skills_dict.values() for s in cat])
    
    matched_skills = list(resume_skills.intersection(jd_skills))
    
    keyword_score = 0.0
    if jd_skills:
        keyword_score = len(matched_skills) / len(jd_skills)
        
    # 3. Weighted Average (60% keywords, 40% TF-IDF)
    final_score = (keyword_score * 0.6) + (tfidf_score * 0.4)
    
    return round(final_score * 100, 2), matched_skills

def rank_candidates(resumes, job_description, catalog=None):
    """Ranks multiple resumes based on similarity to job description."""
    rankings = []
    
    # Pre-extract JD skills for comparison
    jd_skills_dict = extract_skills(job_description, categories=catalog)
    jd_skills = set([s for cat in jd_skills_dict.values() for s in cat])
    
    for resume in resumes:
        score, matched = calculate_similarity(resume['text'], job_description, catalog=catalog)
        rankings.append({
            "name": resume.get('name', 'Unknown'),
            "email": resume.get('email', 'N/A'),
            "phone": resume.get('phone', 'N/A'),
            "score": score,
            "skills": resume.get('skills', {}), # Now a dict
            "summary": resume.get('summary', ''),
            "matched_skills": matched,
            "missing_skills": list(jd_skills - set(matched)),
            "experience": resume.get('experience', 'N/A'),
            "titles": resume.get('titles', []),
            "education": resume.get('education', []),
            "text": resume.get('text', '')
        })
    
    return sorted(rankings, key=lambda x: x['score'], reverse=True)

def compare_candidates(cand_a, cand_b):
    """Computes differences and similarities between two candidate profiles."""
    skills_a = set([s for cat in cand_a['skills'].values() for s in cat])
    skills_b = set([s for cat in cand_b['skills'].values() for s in cat])
    
    common = skills_a.intersection(skills_b)
    only_a = skills_a - skills_b
    only_b = skills_b - skills_a
    
    return {
        "common": list(common),
        "only_a": list(only_a),
        "only_b": list(only_b)
    }

if __name__ == "__main__":
    jd = "Looking for a Python developer with Machine Learning and SQL experience."
    resumes = [
        {"name": "Abhishek", "text": "Python and SQL expert with 3 years exp.", "skills": ["python", "sql"]}
    ]
    print(rank_candidates(resumes, jd))
