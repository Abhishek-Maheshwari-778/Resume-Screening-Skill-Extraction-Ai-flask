from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from werkzeug.utils import secure_filename
import tempfile
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from parser import extract_text
from extractor import extract_details, load_skills_catalog
from matcher import rank_candidates, compare_candidates

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    resumes = request.files.getlist('resumes')
    jd_file = request.files.get('jd')
    skills_file = request.files.get('skills')

    if not resumes:
        return jsonify({'error': 'Missing resumes'}), 400

    # Save files temporarily
    temp_dir = tempfile.mkdtemp()
    
    jd_path = None
    if jd_file:
        jd_path = os.path.join(temp_dir, secure_filename(jd_file.filename))
        jd_file.save(jd_path)

    resume_paths = []
    for resume in resumes:
        path = os.path.join(temp_dir, secure_filename(resume.filename))
        resume.save(path)
        resume_paths.append(path)

    skills_path = None
    if skills_file:
        skills_path = os.path.join(temp_dir, secure_filename(skills_file.filename))
        skills_file.save(skills_path)

    return jsonify({
        'temp_dir': temp_dir,
        'jd_path': jd_path,
        'resume_paths': resume_paths,
        'skills_path': skills_path
    })

@app.route('/api/analyze', methods=['POST'])
def run_analysis():
    data = request.json
    jd_path = data.get('jd_path')
    resume_paths = data.get('resume_paths')
    skills_path = data.get('skills_path')

    try:
        # Load catalog if exists
        catalog = None
        if skills_path:
            catalog = load_skills_catalog(skills_path)

        # Parse JD if provided
        jd_text = ""
        jd_details = {'titles': [], 'skills': {}, 'experience': '', 'education': []}
        if jd_path:
            jd_text = extract_text(jd_path)
            jd_details = extract_details(jd_text, catalog=catalog)

        # Process resumes
        processed_resumes = []
        for path in resume_paths:
            text = extract_text(path)
            details = extract_details(text, catalog=catalog)
            details['filename'] = os.path.basename(path)
            details['text'] = text
            processed_resumes.append(details)

        # Rank (if JD provided) or just display (if individual)
        if jd_text:
            results = rank_candidates(processed_resumes, jd_text, catalog=catalog)
        else:
            # For individual check, set score to 100 or 0
            results = processed_resumes
            for r in results:
                r['score'] = 100
                r['matched_skills'] = [s for cat in r['skills'].values() for s in cat]
                r['missing_skills'] = []

        return jsonify({
            'total_resumes': len(resume_paths),
            'jd_details': jd_details,
            'candidates': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
