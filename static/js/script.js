// Global variables
let uploadedFiles = {
    resumes: [],
    jd: null,
    skills: null
};

let analysisResults = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // File inputs
    const resumeInput = document.getElementById('resumeFiles');
    const jdInput = document.getElementById('jdFile');
    const skillsInput = document.getElementById('skillsFile');
    
    resumeInput.addEventListener('change', (e) => {
        uploadedFiles.resumes = Array.from(e.target.files);
        document.getElementById('resumeFilesList').textContent = `${uploadedFiles.resumes.length} resume(s) selected`;
        updateAnalyzeButton();
    });
    
    jdInput.addEventListener('change', (e) => {
        uploadedFiles.jd = e.target.files[0];
        document.getElementById('jdFileList').textContent = uploadedFiles.jd ? uploadedFiles.jd.name : '';
        updateAnalyzeButton();
    });
    
    // Filters
    document.getElementById('minScore').addEventListener('input', (e) => {
        document.getElementById('minScoreValue').textContent = e.target.value + '%';
        if (analysisResults) displayFilteredResults();
    });
    
    document.getElementById('topN').addEventListener('change', () => {
        if (analysisResults) displayFilteredResults();
    });
    
    document.getElementById('skillFilter').addEventListener('input', () => {
        if (analysisResults) displayFilteredResults();
    });
    
    // Analyze button
    document.getElementById('analyzeBtn').addEventListener('click', analyzeResumes);
}

function updateAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = !(uploadedFiles.resumes.length > 0 && uploadedFiles.jd);
}

async function analyzeResumes() {
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const btn = document.getElementById('analyzeBtn');
    
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    btn.disabled = true;
    
    // Simulation for progress bar
    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        if (progress > 90) clearInterval(interval);
        document.getElementById('progressFill').style.width = progress + '%';
    }, 100);

    try {
        const formData = new FormData();
        uploadedFiles.resumes.forEach(file => formData.append('resumes', file));
        formData.append('jd', uploadedFiles.jd);
        if (uploadedFiles.skills) formData.append('skills', uploadedFiles.skills);

        // Upload
        const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData });
        if (!uploadRes.ok) throw new Error('Upload failed');
        const uploadData = await uploadRes.json();

        // Analyze
        const analyzeRes = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(uploadData)
        });
        if (!analyzeRes.ok) throw new Error('Analysis failed');
        
        analysisResults = await analyzeRes.json();
        
        clearInterval(interval);
        document.getElementById('progressFill').style.width = '100%';
        
        setTimeout(() => {
            displayResults();
            loadingSection.style.display = 'none';
            resultsSection.style.display = 'block';
            btn.disabled = false;
        }, 500);

    } catch (error) {
        clearInterval(interval);
        console.error(error);
        alert('Analysis Error: ' + error.message);
        loadingSection.style.display = 'none';
        btn.disabled = false;
    }
}

function displayResults() {
    const jd = analysisResults.jd_details;
    const jdMetrics = document.getElementById('jdMetrics');
    jdMetrics.innerHTML = `
        <div class="metric-card">
            <div class="metric-value" style="font-size: 1.2rem;">${jd.titles.join(', ') || 'N/A'}</div>
            <div class="metric-label">Roles Profiled</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="font-size: 1.2rem;">${jd.experience || 'Not Specified'}</div>
            <div class="metric-label">Experience Bracket</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="font-size: 1.2rem;">${jd.education.join(', ') || 'Any'}</div>
            <div class="metric-label">Education</div>
        </div>
    `;

    const skillsBox = document.getElementById('jdSkillsBox');
    const skillsTags = document.getElementById('jdSkillsTags');
    const flatSkills = [].concat(...Object.values(jd.skills));
    
    if (flatSkills.length > 0) {
        skillsTags.innerHTML = flatSkills.map(s => `<span class="tag tag-muted">${s}</span>`).join('');
        skillsBox.style.display = 'block';
    } else {
        skillsBox.style.display = 'none';
    }

    displayFilteredResults();
}

function displayFilteredResults() {
    let candidates = analysisResults.candidates;
    const minScore = parseInt(document.getElementById('minScore').value);
    const topN = document.getElementById('topN').value;
    const highlightSkill = document.getElementById('skillFilter').value.toLowerCase();

    // Filter
    let filtered = candidates.filter(c => c.score >= minScore);
    
    if (highlightSkill) {
        filtered = filtered.filter(c => {
            const allSkills = [].concat(...Object.values(c.skills)).map(s => s.toLowerCase());
            return allSkills.some(s => s.includes(highlightSkill));
        });
    }

    if (topN !== 'all') {
        filtered = filtered.slice(0, parseInt(topN));
    }

    // Summary Metrics
    const metricsGrid = document.getElementById('summaryMetricsGrid');
    const avgScore = filtered.length > 0 ? Math.round(filtered.reduce((a, b) => a + b.score, 0) / filtered.length) : 0;
    
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <div class="metric-value">${analysisResults.total_resumes}</div>
            <div class="metric-label">Processed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${filtered.length}</div>
            <div class="metric-label">Shortlisted</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${filtered.length > 0 ? filtered[0].score : 0}%</div>
            <div class="metric-label">Top Match</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${avgScore}%</div>
            <div class="metric-label">Average Fit</div>
        </div>
    `;

    // Cards
    const container = document.getElementById('candidateCards');
    container.innerHTML = filtered.map((c, i) => `
        <div class="candidate-card animate-fade-in" style="animation-delay: ${i * 0.1}s">
            <div class="candidate-score-badge">${c.score}%</div>
            <div class="candidate-name">${c.name}</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
                ${c.email} &nbsp;•&nbsp; ${c.phone}
            </div>
            <div style="font-style: italic; color: var(--primary); font-size: 0.9rem; margin-bottom: 16px;">
                "${c.summary}"
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${c.score}%"></div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; font-size: 0.8rem;">
                <div>
                    <span style="display: block; color: var(--text-muted);">EXPERIENCE</span>
                    <span>${c.experience}</span>
                </div>
                <div>
                    <span style="display: block; color: var(--text-muted);">ROLE FIT</span>
                    <span>${c.titles.slice(0, 1) || 'Qualified'}</span>
                </div>
                <div>
                    <span style="display: block; color: var(--text-muted);">EDUCATION</span>
                    <span>${c.education[0] || 'Specified'}</span>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">MATCHED STRENGTHS</div>
                <div>${c.matched_skills.map(s => `<span class="tag tag-success">${s}</span>`).join('')}</div>
                ${c.missing_skills.length > 0 ? `
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 12px; margin-bottom: 8px;">IDENTIFIED GAPS</div>
                    <div>${c.missing_skills.slice(0, 10).map(s => `<span class="tag tag-danger">${s}</span>`).join('')}</div>
                ` : ''}
            </div>
        </div>
    `).join('');
}
