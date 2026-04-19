# Resume Screening & Skill Extraction AI (Flask Edition)

An advanced AI-powered platform designed to streamline recruitment by automatically screening resumes and extracting key technical and soft skills using NLP (Natural Language Processing) and NER (Named Entity Recognition).

## 🚀 Features
- **Intelligent Screening**: Ranks candidates against a Job Description using a hybrid TF-IDF Cosine Similarity and Keyword Matching algorithm.
- **Skill Extraction**: Automatically identifies and categorizes technical skills, soft skills, and tool proficiencies.
- **Dual Format Support**: Processes both PDF and DOCX resumes seamlessly.
- **Interactive Dashboard**: Premium glassmorphism UI with real-time filtering, match scoring visualizations, and candidate comparisons.
- **Custom Catalogs**: Support for custom skills catalogs via XLSX for industry-specific tailoring.

## 🛠️ Technology Stack
- **Backend**: Flask (Python 3.x)
- **NLP Engine**: spaCy, en_core_web_sm
- **Text Extraction**: pypdf, python-docx
- **Machine Learning**: Scikit-Learn (TF-IDF), Pandas
- **Frontend**: Vanilla HTML5, CSS3 (Premium Glassmorphism), Modern JavaScript (ES6+)

## 📦 Installation & Setup

1. **Clone the project**
   ```bash
   git clone https://github.com/Abhishek-Maheshwari-778/Resume-Screening-Skill-Extraction-Ai-flask.git
   cd Resume-Screening-Skill-Extraction-Ai-flask
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the Application**
   ```bash
   python flask_app.py
   ```
   *The app will be available at `http://localhost:5000`*

## 👤 Owner
**Abhishek Maheshwari**
- Project Lead & AI Developer
- [LinkedIn Profile](https://www.linkedin.com/in/abhishekmaheshwari2436/)
- [GitHub Profile](https://github.com/Abhishek-Maheshwari-778)

---
*Developed as part of the Final Year Project at Invertis University (BCA 2023–26).*
