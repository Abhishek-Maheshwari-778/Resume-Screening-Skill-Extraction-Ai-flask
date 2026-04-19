from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from extractor import extract_skills

def calculate_similarity(resume_text, job_description, catalog=None):
    """Calculates similarity score using a mix of TF-IDF and Keyword Overlap."""
    if not resume_text or not job_description:
        return 0.0, []
        
    # 1. TF-IDF Cosine Similarity
    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
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
