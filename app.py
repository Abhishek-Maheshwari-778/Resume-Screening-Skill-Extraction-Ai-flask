from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import pandas as pd
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

ALLOWED_EXTENSIONS_RESUME = {'pdf', 'docx'}
ALLOWED_EXTENSIONS_JD = {'pdf', 'docx', 'txt'}
ALLOWED_EXTENSIONS_SKILLS = {'xlsx'}

def allowed_file(filename, allowed_types):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_types

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        # Check if files are present
        if 'resumes' not in request.files or 'jd' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400
        
        resumes = request.files.getlist('resumes')
        jd_file = request.files['jd']
        skills_file = request.files.get('skills')
        
        # Validate files
        if not resumes or resumes[0].filename == '':
            return jsonify({'error': 'No resume files uploaded'}), 400
        
        if jd_file.filename == '':
            return jsonify({'error': 'No job description file uploaded'}), 400
        
        # Validate file types
        for resume in resumes:
            if not allowed_file(resume.filename, ALLOWED_EXTENSIONS_RESUME):
                return jsonify({'error': f'Invalid file type for resume: {resume.filename}'}), 400
        
        if not allowed_file(jd_file.filename, ALLOWED_EXTENSIONS_JD):
            return jsonify({'error': f'Invalid file type for job description: {jd_file.filename}'}), 400
        
        if skills_file and skills_file.filename != '' and not allowed_file(skills_file.filename, ALLOWED_EXTENSIONS_SKILLS):
            return jsonify({'error': f'Invalid file type for skills catalog: {skills_file.filename}'}), 400
        
        # Save files
        resume_paths = []
        for resume in resumes:
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', filename)
            resume.save(resume_path)
            resume_paths.append(resume_path)
        
        jd_filename = secure_filename(jd_file.filename)
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', jd_filename)
        jd_file.save(jd_path)
        
        skills_path = None
        if skills_file and skills_file.filename != '':
            skills_filename = secure_filename(skills_file.filename)
            skills_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', skills_filename)
            skills_file.save(skills_path)
        
        return jsonify({
            'message': 'Files uploaded successfully',
            'resume_count': len(resume_paths),
            'jd_file': jd_filename,
            'skills_file': os.path.basename(skills_path) if skills_path else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_resumes():
    try:
        data = request.get_json()
        
        # Get file paths from session or reconstruct them
        jd_filename = data.get('jd_file')
        skills_filename = data.get('skills_file')
        resume_count = data.get('resume_count', 0)
        
        if not jd_filename:
            return jsonify({'error': 'Job description file not found'}), 400
        
        # Reconstruct file paths
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', jd_filename)
        
        if not os.path.exists(jd_path):
            return jsonify({'error': 'Job description file not found on server'}), 400
        
        # Get resume files (filtering out the JD file and other non-resume files)
        resume_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes')
        resume_files = [f for f in os.listdir(resume_dir) if f.endswith(('.pdf', '.docx')) and f != jd_filename]
        
        # We should only process the ones that were actually uploaded in this request
        # For simplicity in this demo, we assume the upload dir is cleared or we just take the last N.
        # But let's just use what's there for now.
        
        # Load skills catalog if provided
        catalog = None
        if skills_filename:
            skills_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', skills_filename)
            if os.path.exists(skills_path):
                catalog = load_skills_catalog(skills_path)
        
        # Extract job description details
        job_desc = extract_text(jd_path)
        jd_details = extract_details(job_desc, catalog=catalog)
        
        # Process resumes
        processed_resumes = []
        for resume_file in resume_files:
            resume_path = os.path.join(resume_dir, resume_file)
            text = extract_text(resume_path)
            details = extract_details(text, catalog=catalog)
            details['text'] = text
            details['filename'] = resume_file
            processed_resumes.append(details)
        
        # Rank candidates
        all_results = rank_candidates(processed_resumes, job_desc, catalog=catalog)
        
        # Prepare response
        response = {
            'jd_details': {
                'titles': jd_details.get('titles', []),
                'experience': jd_details.get('experience', ''),
                'education': jd_details.get('education', []),
                'skills': jd_details.get('skills', {})
            },
            'candidates': all_results,
            'total_resumes': len(processed_resumes)
        }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_candidates_api():
    try:
        data = request.get_json()
        candidate1_name = data.get('candidate1')
        candidate2_name = data.get('candidate2')
        candidates = data.get('candidates', [])
        
        if not candidate1_name or not candidate2_name:
            return jsonify({'error': 'Both candidates must be selected'}), 400
        
        # Find candidates
        cand1 = next((c for c in candidates if c['name'] == candidate1_name), None)
        cand2 = next((c for c in candidates if c['name'] == candidate2_name), None)
        
        if not cand1 or not cand2:
            return jsonify({'error': 'One or both candidates not found'}), 404
        
        # Compare candidates
        diff = compare_candidates(cand1, cand2)
        
        return jsonify(diff)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_csv', methods=['POST'])
def download_csv():
    try:
        data = request.get_json()
        candidates = data.get('candidates', [])
        
        if not candidates:
            return jsonify({'error': 'No candidates data provided'}), 400
        
        # Create DataFrame
        table_data = []
        for i, r in enumerate(candidates):
            table_data.append({
                "Rank": i + 1,
                "Name": r['name'],
                "Score (%)": r['score'],
                "Email": r['email'],
                "Phone": r['phone'],
                "Experience": r['experience'],
                "Education": ", ".join(r['education']) if r['education'] else "—",
                "Matched Skills": ", ".join(r['matched_skills']) if r['matched_skills'] else "—",
                "Missing Skills": ", ".join(r['missing_skills']) if r['missing_skills'] else "—",
            })
        
        df = pd.DataFrame(table_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            df.to_csv(tmp_file.name, index=False)
            path = tmp_file.name
        
        return send_file(path, as_attachment=True, download_name='resume_ranking_results.csv', mimetype='text/csv')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
