/**
 * TalentFlow AI - High Throughput Logic
 */

let state = {
    resumes: [],
    jd: null,
    skills: null,
    results: null
};

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    bindEvents();
    setupSmoothScroll();
});

function initTheme() {
    const theme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.querySelector('#themeToggle i');
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

function bindEvents() {
    const resumeInput = document.getElementById('resumeFiles');
    const jdInput = document.getElementById('jdFile');
    const skillsInput = document.getElementById('skillsFile');
    const themeToggle = document.getElementById('themeToggle');
    const analyzeBtn = document.getElementById('analyzeBtn');

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        const icon = themeToggle.querySelector('i');
        icon.className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    });

    resumeInput.addEventListener('change', (e) => {
        state.resumes = Array.from(e.target.files);
        document.getElementById('resumeList').innerText = `${state.resumes.length} Candidatures Attached`;
        checkBtn();
    });

    jdInput.addEventListener('change', (e) => {
        state.jd = e.target.files[0];
        document.getElementById('jdFileName').innerText = state.jd.name;
        checkBtn();
    });

    skillsInput.addEventListener('change', (e) => {
        state.skills = e.target.files[0];
    });

    analyzeBtn.addEventListener('click', runInference);
}

function checkBtn() {
    document.getElementById('analyzeBtn').disabled = !(state.resumes.length > 0 && state.jd);
}

function setupSmoothScroll() {
    document.querySelectorAll('.nav-link, .btn-cta').forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

async function runInference() {
    const loading = document.getElementById('loadingSection');
    const results = document.getElementById('resultsSection');
    const btn = document.getElementById('analyzeBtn');
    const progress = document.getElementById('progressFill');

    btn.style.display = 'none';
    loading.style.display = 'block';
    results.style.display = 'none';

    let progressVal = 0;
    const interval = setInterval(() => {
        progressVal += Math.random() * 20;
        if (progressVal > 95) clearInterval(interval);
        progress.style.width = Math.min(progressVal, 95) + '%';
    }, 150);

    try {
        const formData = new FormData();
        state.resumes.forEach(f => formData.append('resumes', f));
        formData.append('jd', state.jd);
        if (state.skills) formData.append('skills', state.skills);

        const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData });
        if (!uploadRes.ok) throw new Error('Artifact upload critical failure');
        const uploadData = await uploadRes.json();

        const analyzeRes = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(uploadData)
        });
        if (!analyzeRes.ok) throw new Error('Inference engine timeout');
        
        state.results = await analyzeRes.json();
        
        clearInterval(interval);
        progress.style.width = '100%';
        
        setTimeout(() => {
            renderInference();
            loading.style.display = 'none';
            results.style.display = 'block';
            btn.style.display = 'block';
            
            window.scrollTo({
                top: results.offsetTop - 120,
                behavior: 'smooth'
            });
        }, 500);

    } catch (err) {
        clearInterval(interval);
        alert('System Exception: ' + err.message);
        loading.style.display = 'none';
        btn.style.display = 'block';
    }
}

function renderInference() {
    const r = state.results;
    
    // Summary
    const avg = r.candidates.length > 0 ? Math.round(r.candidates.reduce((a, b) => a + b.score, 0) / r.candidates.length) : 0;
    document.getElementById('summaryGrid').innerHTML = `
        <div class="about-card"><h4>PROCESS</h4><div style="font-size: 2rem; font-weight: 800; color: var(--primary);">${r.total_resumes}</div><p>Artifacts</p></div>
        <div class="about-card"><h4>MATCH</h4><div style="font-size: 2rem; font-weight: 800; color: var(--primary);">${r.candidates.length > 0 ? r.candidates[0].score : 0}%</div><p>Max Fit</p></div>
        <div class="about-card"><h4>SIGNAL</h4><div style="font-size: 2rem; font-weight: 800; color: var(--primary);">${avg}%</div><p>Avg Quality</p></div>
        <div class="about-card"><h4>STATUS</h4><div style="font-size: 2rem; font-weight: 800; color: var(--primary);">ACTIVE</div><p>Real-time</p></div>
    `;

    // JD Breakdown
    const jd = r.jd_details;
    document.getElementById('jdDetailsGrid').innerHTML = `
        <div><label style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted);">ROLES</label><div>${jd.titles.join(', ') || 'General'}</div></div>
        <div><label style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted);">EXP_REQ</label><div>${jd.experience || 'Flexible'}</div></div>
        <div><label style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted);">ACADEMICS</label><div>${jd.education[0] || 'Any'}</div></div>
    `;

    // Candidate List
    document.getElementById('candidateList').innerHTML = r.candidates.map((c, i) => `
        <div class="result-card animate" style="animation-delay: ${i * 0.1}s">
            <div class="score-text">${c.score}%</div>
            <h4>${c.name}</h4>
            <p style="font-size: 0.8rem; color: var(--text-muted);">${c.email} &nbsp;|&nbsp; ${c.phone}</p>
            <p style="margin: 16px 0; color: var(--primary); font-weight: 700; font-style: italic;">"${c.summary}"</p>
            <div style="height: 4px; background: var(--border); border-radius: 99px; overflow: hidden; margin-bottom: 20px;">
                <div style="width: ${c.score}%; height: 100%; background: var(--primary);"></div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; font-size: 0.8rem; margin-bottom: 20px;">
                <div><label style="color: var(--text-muted); display: block;">SIGNAL</label>${c.experience}</div>
                <div><label style="color: var(--text-muted); display: block;">ALIGNED</label>${c.titles[0] || 'N/A'}</div>
                <div><label style="color: var(--text-muted); display: block;">DEGREE</label>${c.education[0] || 'N/A'}</div>
            </div>
            <div>
                <label style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted);">SYNCED_SKILLS</label>
                <div>${c.matched_skills.map(s => `<span class="tag tag-match">${s}</span>`).join('')}</div>
                ${c.missing_skills.length > 0 ? `<label style="font-size: 0.7rem; font-weight: 800; color: var(--text-muted); margin-top: 12px; display: block;">GAP_DETECTED</label>
                <div>${c.missing_skills.slice(0, 5).map(s => `<span class="tag tag-miss">${s}</span>`).join('')}</div>` : ''}
            </div>
        </div>
    `).join('');
}
