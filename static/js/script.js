/**
 * TalentFlow AI - Intelligence Engine v2.2
 * Core Features: Multi-mode analysis, Matrix comparisons, and Sorting
 */

let state = {
    resumes: [],
    jd: null,
    skills: null,
    results: null,
    chart: null,
    mode: 'recruiter', // or 'candidate'
    sortOrder: 'desc'
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
    if(icon) icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

function bindEvents() {
    // Mode Switchers
    const btnRecruiter = document.getElementById('recruiterMode');
    const btnCandidate = document.getElementById('candidateMode');
    const jdBox = document.getElementById('jdBoxContainer');

    btnRecruiter?.addEventListener('click', () => {
        state.mode = 'recruiter';
        btnRecruiter.classList.add('active');
        btnCandidate.classList.remove('active');
        jdBox.style.display = 'block';
        checkBtn();
    });

    btnCandidate?.addEventListener('click', () => {
        state.mode = 'candidate';
        btnCandidate.classList.add('active');
        btnRecruiter.classList.remove('active');
        jdBox.style.display = 'none';
        checkBtn();
    });

    // File Inputs
    const resumeInput = document.getElementById('resumeFiles');
    const jdInput = document.getElementById('jdFile');
    const skillsInput = document.getElementById('skillsFile');

    resumeInput?.addEventListener('change', (e) => {
        state.resumes = Array.from(e.target.files);
        document.getElementById('resumeList').innerText = `${state.resumes.length} Files Prepared`;
        checkBtn();
    });

    jdInput?.addEventListener('change', (e) => {
        state.jd = e.target.files[0];
        document.getElementById('jdFileName').innerText = state.jd.name;
        checkBtn();
    });

    skillsInput?.addEventListener('change', (e) => {
        state.skills = e.target.files[0];
        document.getElementById('skillsFileName').innerText = state.skills.name;
    });

    // Buttons
    document.getElementById('analyzeBtn')?.addEventListener('click', runInference);
    document.getElementById('resetBtn')?.addEventListener('click', resetApp);
    document.getElementById('sortAccuracy')?.addEventListener('click', toggleSort);
    document.getElementById('toggleTable')?.addEventListener('click', toggleView('matrixContainer'));
    document.getElementById('toggleCharts')?.addEventListener('click', toggleView('chartsContainer'));
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    document.querySelector('#themeToggle i').className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    if (state.results) renderSignalChart();
}

function toggleView(id) {
    return (e) => {
        const el = document.getElementById(id);
        const isActive = el.style.display !== 'none';
        el.style.display = isActive ? 'none' : 'block';
        e.currentTarget.classList.toggle('active');
    };
}

function toggleSort() {
    state.sortOrder = state.sortOrder === 'desc' ? 'asc' : 'desc';
    renderCandidateList();
    document.getElementById('sortAccuracy').innerHTML = `Sort: Accuracy <i class="fas fa-sort-amount-${state.sortOrder === 'desc' ? 'down' : 'up'}"></i>`;
}

function checkBtn() {
    const btn = document.getElementById('analyzeBtn');
    if (!btn) return;
    if (state.mode === 'recruiter') {
        btn.disabled = !(state.resumes.length > 0 && state.jd);
    } else {
        btn.disabled = !(state.resumes.length > 0);
    }
}

async function runInference() {
    const loading = document.getElementById('loadingSection');
    const resultsArea = document.getElementById('resultsSection');
    const workspace = document.getElementById('uploadWorkspace');
    const btn = document.getElementById('analyzeBtn');
    const progress = document.getElementById('progressFill');

    btn.style.display = 'none';
    loading.style.display = 'block';
    workspace.style.opacity = '0.3';

    let pVal = 0;
    const interval = setInterval(() => {
        pVal += 10;
        if (pVal > 90) clearInterval(interval);
        progress.style.width = pVal + '%';
    }, 150);

    try {
        const formData = new FormData();
        state.resumes.forEach(f => formData.append('resumes', f));
        if (state.mode === 'recruiter') formData.append('jd', state.jd);
        if (state.skills) formData.append('skills', state.skills);

        // Upload
        const up = await fetch('/api/upload', { method: 'POST', body: formData });
        const upData = await up.json();

        // Analyze
        const an = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(upData)
        });
        
        state.results = await an.json();
        clearInterval(interval);
        progress.style.width = '100%';

        setTimeout(() => {
            loading.style.display = 'none';
            workspace.style.display = 'none';
            resultsArea.style.display = 'block';
            document.getElementById('resetBtn').style.display = 'flex';
            
            renderInference();
            
            window.scrollTo({ top: resultsArea.offsetTop - 120, behavior: 'smooth' });
        }, 400);

    } catch (e) {
        clearInterval(interval);
        alert('Engine Timeout: ' + e.message);
        loading.style.display = 'none';
        btn.style.display = 'block';
        workspace.style.opacity = '1';
    }
}

function renderInference() {
    renderCandidateList();
    renderSignalChart();
    renderSummary();
    renderMatrix();
    
    // Sidebar Sidebar
    const side = document.getElementById('jdSideContent');
    const jd = state.results.jd_details;
    if (state.mode === 'recruiter') {
        side.innerHTML = `
            <div style="margin-bottom: 20px;">
                <label style="font-size: 0.6rem; font-weight: 800; color: var(--text-muted);">ROLES</label>
                <div style="font-weight: 700;">${jd.titles.join(', ') || 'N/A'}</div>
            </div>
            <div style="margin-bottom: 20px;">
                <label style="font-size: 0.6rem; font-weight: 800; color: var(--text-muted);">EXP</label>
                <div style="font-weight: 700;">${jd.experience || 'Not Defined'}</div>
            </div>
            <div style="margin-top: 20px; border-top: 1px solid var(--border); padding-top: 20px;">
                <label style="font-size: 0.6rem; font-weight: 800; color: var(--text-muted);">KEY SKILL TAGS</label>
                <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px;">
                    ${[].concat(...Object.values(jd.skills)).slice(0, 10).map(s => `<span class="tag tag-match">${s}</span>`).join('')}
                </div>
            </div>
        `;
    } else {
        side.innerHTML = `<p style="font-size: 0.8rem; color: var(--text-muted);">Individual Profiling active. No mandate comparison.</p>`;
    }
}

function renderCandidateList() {
    const list = document.getElementById('candidateList');
    const candidates = [...state.results.candidates].sort((a,b) => {
        return state.sortOrder === 'desc' ? b.score - a.score : a.score - b.score;
    });

    list.innerHTML = candidates.map((c, i) => `
        <div class="result-card animate" style="animation-delay: ${i*0.1}s">
            ${state.mode === 'recruiter' ? `<div class="score-text">${c.score}%</div>` : ''}
            <h3>${c.name}</h3>
            <p style="font-size: 0.8rem; color: var(--text-muted);">${c.email} &nbsp;|&nbsp; ${c.phone}</p>
            <p style="margin: 15px 0; color: var(--primary); font-weight: 700;">"${c.summary}"</p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div><label style="font-size: 0.6rem; color: var(--text-muted);">SIGNAL</label><div style="font-weight: 700; font-size: 0.85rem;">${c.experience}</div></div>
                <div><label style="font-size: 0.6rem; color: var(--text-muted);">POSITION</label><div style="font-weight: 700; font-size: 0.85rem;">${c.titles[0] || 'N/A'}</div></div>
                <div><label style="font-size: 0.6rem; color: var(--text-muted);">ACADEMICS</label><div style="font-weight: 700; font-size: 0.85rem;">${c.education[0] || 'N/A'}</div></div>
            </div>
            <div style="margin-top: 20px;">
                <div style="font-size: 0.6rem; font-weight: 800; color: var(--text-muted);">SKILLS EXTRACTED</div>
                <div>${[].concat(...Object.values(c.skills)).slice(0, 15).map(s => `<span class="tag tag-match" style="background: var(--bg-accent); border: 1px solid var(--border); color: var(--text-main);">${s}</span>`).join('')}</div>
            </div>
        </div>
    `).join('');
}

function renderMatrix() {
    const table = document.getElementById('matrixTable');
    const candidates = state.results.candidates;
    if (candidates.length === 0) return;

    // Build common skills set
    const allSkills = new Set();
    candidates.forEach(c => {
        [].concat(...Object.values(c.skills)).forEach(s => allSkills.add(s));
    });
    const skillsList = Array.from(allSkills).slice(0, 8); // Limit columns

    let html = `<thead><tr><th>Candidate</th>${skillsList.map(s => `<th>${s}</th>`).join('')}<th>Score</th></tr></thead><tbody>`;
    
    candidates.forEach(c => {
        const cSkills = [].concat(...Object.values(c.skills)).map(s => s.toLowerCase());
        html += `<tr><td><b>${c.name}</b></td>`;
        skillsList.forEach(s => {
            const has = cSkills.includes(s.toLowerCase());
            html += `<td style="text-align: center;">${has ? '<i class="fas fa-check" style="color: var(--primary);"></i>' : '<i class="fas fa-times" style="color: var(--text-muted); opacity: 0.3;"></i>'}</td>`;
        });
        html += `<td><span style="color: var(--primary); font-weight: 800;">${c.score}%</span></td></tr>`;
    });
    
    html += '</tbody>';
    table.innerHTML = html;
}

function renderSummary() {
    // Already in existing sections, just updating count
    document.getElementById('sortAccuracy').classList.add('active');
}

function renderSignalChart() {
    const ctx = document.getElementById('signalsChart');
    if (state.chart) state.chart.destroy();
    
    state.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: state.results.candidates.map(c => c.name.split(' ')[0]),
            datasets: [{
                label: 'Match Signal',
                data: state.results.candidates.map(c => c.score),
                backgroundColor: '#10b981'
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function resetApp() {
    state.resumes = [];
    state.jd = null;
    state.results = null;
    document.getElementById('resumeList').innerText = '';
    document.getElementById('jdFileName').innerText = '';
    document.getElementById('skillsFileName').innerText = 'Attach Excel Catalog';
    document.getElementById('uploadWorkspace').style.display = 'block';
    document.getElementById('uploadWorkspace').style.opacity = '1';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('analyzeBtn').style.display = 'block';
    document.getElementById('resetBtn').style.display = 'none';
    checkBtn();
}

function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const t = document.querySelector(this.getAttribute('href'));
            if (t) window.scrollTo({ top: t.offsetTop - 80, behavior: 'smooth' });
        });
    });
}
