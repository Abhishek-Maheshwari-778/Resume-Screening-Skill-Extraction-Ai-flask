import re

try:
    import spacy
    try:
        import en_core_web_sm
        nlp = en_core_web_sm.load()
    except Exception:
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = spacy.blank("en")
except ImportError:
    nlp = None

def extract_name(text):
    """Extracts candidate name using spaCy NER and fallbacks."""
    if nlp is not None:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.split('\n')[0].strip()
                if 2 <= len(name.split()) <= 4:
                    return name
    
    # Fallback: Often the first non-empty line is the name
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        first_line = lines[0]
        name_candidate = first_line.split('|')[0].split(',')[0].strip()
        if 2 <= len(name_candidate.split()) <= 4 and all(c.isalpha() or c.isspace() for c in name_candidate):
            return name_candidate
            
    return "Unknown"

def extract_email(text):
    """Extracts email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not Found"

def extract_phone(text):
    """Extracts phone numbers from text."""
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{10}\b'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else "Not Found"

def load_skills_catalog(file_or_path):
    """Loads a skills catalog from an Excel file with columns: Category, Skill."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_or_path, data_only=True)
        sheet = wb.active
        
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return None
            
        headers = [str(cell).strip().lower() for cell in rows[0] if cell is not None]
        cat_idx = headers.index("category") if "category" in headers else 0
        skill_idx = headers.index("skill") if "skill" in headers else (1 if len(headers) > 1 else 0)
        
        catalog = {}
        for row in rows[1:]:
            if len(row) <= max(cat_idx, skill_idx):
                continue
            cat = str(row[cat_idx]).strip() if row[cat_idx] is not None else ""
            skill = str(row[skill_idx]).strip().lower() if row[skill_idx] is not None else ""
            if not cat or not skill:
                continue
            catalog.setdefault(cat, [])
            if skill not in catalog[cat]:
                catalog[cat].append(skill)
        return catalog or None
    except ImportError:
        # Fallback to pure python csv just in case
        return None
    except Exception:
        return None

def extract_skills(text, categories=None):
    """Extracts skills and categorizes them."""
    categories = categories or {
        "Technical Skills": [
            "python", "java", "javascript", "sql", "react", "node.js", "docker", "aws", 
            "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "flask", "django",
            "c++", "c#", "html", "css", "mongodb", "postgresql", "fastapi", "keras",
            "opencv", "matplotlib", "seaborn", "linux", "bash", "rest api", "graphql",
            "springboot", "angular", "vue.js", "typescript", "php", "ruby", "go",
            "machine learning", "data analysis", "nlp", "deep learning", "big data", 
            "cloud computing", "computer vision", "predictive modeling", "time-series analysis", 
            "jupyter notebook", "llm", "automation", "artificial intelligence",
            "natural language processing", "generative ai", "prompt engineering",
            "spark", "hadoop", "mysql", "nosql", "data visualization"
        ],
        "Soft Skills & Business": [
            "communication", "leadership", "agile", "scrum", "problem solving", 
            "customer support", "training", "management", "project management", 
            "critical thinking", "collaboration", "teamwork", "presentation", 
            "negotiation", "strategy", "customer success"
        ],
        "Tools & Platforms": [
            "git", "jenkins", "kubernetes", "azure", "gcp", "tableau", "power bi", 
            "excel", "crm", "pms", "ota", "channel manager", "booking engine", 
            "hospitality tech", "revenue management", "hotel operations", 
            "opera", "ids", "amadeus", "sabre", "front office"
        ]
    }
    
    found_skills = {cat: [] for cat in categories}
    text_processed = text.lower()
    
    for category, skills in categories.items():
        for skill in skills:
            pattern = rf'\b{re.escape(skill)}\b'
            if re.search(pattern, text_processed):
                found_skills[category].append(skill)
    
    return found_skills

def extract_job_titles(text):
    """Extracts potential job titles/roles."""
    titles_list = [
        "Software Engineer", "Data Scientist", "Data Analyst", "Project Manager",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Machine Learning Engineer", "DevOps Engineer", "Cloud Architect",
        "System Administrator", "Product Manager", "UI/UX Designer", "Business Analyst",
        "Python Developer", "AI/ML Engineer", "Undergraduate", "Intern",
        "Customer Tech Support", "Executive", "Support Executive", "Hotel Manager"
    ]
    found_titles = []
    for title in titles_list:
        if re.search(rf'\b{re.escape(title)}\b', text, re.I):
            found_titles.append(title)
    return list(set(found_titles))

def extract_experience(text):
    """Attempts to find years of experience or date ranges."""
    # Priority 1: "X+ years experience"
    exp_pattern = r'(\d+\+?\s*(?:years?|yrs?))(?:\s+of)?\s+experience'
    match = re.search(exp_pattern, text, re.I)
    if match:
        return match.group(1)
        
    # Priority 2: Date ranges like "Aug 2023 – Present"
    date_range_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–—]\s*(?:Present|Current|[A-Z][a-z]+\s+\d{4}|[0-9]{4})\b'
    ranges = re.findall(date_range_pattern, text, re.I)
    if ranges:
        return "Active from: " + ranges[0]
        
    return "Not Specified"

def extract_education(text):
    """Extracts education info using regex and keywords."""
    edu_patterns = [
        r'\bBachelor of [A-Za-z\s]+',
        r'\bMaster of [A-Za-z\s]+',
        r'\bB\.?Tech\b', r'\bM\.?Tech\b', r'\bB\.?E\b', r'\bM\.?E\b',
        r'\bB\.?Sc\b', r'\bM\.?Sc\b', r'\bMBA\b', r'\bMCA\b', r'\bPhD\b',
        r'\bB\.?Com\b', r'\bM\.?Com\b', r'\bB\.?A\b', r'\bM\.?A\b',
        r'\bBachelor of Computer Applications\b'
    ]
    education = []
    for pattern in edu_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            education.append(match.group().strip())
    if not education:
        keywords = ["Bachelors", "Masters", "Graduate", "PhD", "Undergraduate"]
        for kw in keywords:
            if kw.lower() in text.lower():
                education.append(kw)
    return sorted(list(set(education)))

def generate_summary(details):
    """Generates a professional 1-sentence bio."""
    name = details.get('name', 'Candidate')
    title = details['titles'][0] if details['titles'] else "Professional"
    exp = details.get('experience', 'N/A')
    
    # Get top 3 technical skills from the new dict structure
    tech_skills = details.get('skills', {}).get('Technical Skills', [])
    top_skills = ", ".join(tech_skills[:3]) if tech_skills else ""
    
    summary = f"{name} is a {title}"
    if exp != "Not Specified" and exp != "N/A":
        summary += f" with {exp} of experience"
    if top_skills:
        summary += f", proficient in {top_skills}."
    else:
        summary += "."
        
    return summary

def extract_details(text, catalog=None):
    """Aggregates all extracted details."""
    details = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text, categories=catalog), # Now returns a dictionary
        "education": extract_education(text),
        "experience": extract_experience(text),
        "titles": extract_job_titles(text)
    }
    details['summary'] = generate_summary(details)
    return details

if __name__ == "__main__":
    sample_text = "Abhishek Maheshwari | abhishek@example.com\nAug 2023 – Present experience.\nSkills: Python, PMS, OTA"
    print(extract_details(sample_text))
