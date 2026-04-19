import os
import docx

import pypdf

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using pypdf."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    
    # Simple cleaning: remove multiple spaces and newlines if needed
    # but keep basic structure for NER
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text

def extract_text(file_path):
    """Extracts text from a file based on its extension."""
    if not os.path.exists(file_path):
        return ""
        
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    else:
        print(f"Unsupported file format: {ext}")
        return ""

if __name__ == "__main__":
    # Quick test
    test_file = "data/resumes/Abhishek_resume.pdf"
    if os.path.exists(test_file):
        print(f"Extracting from {test_file}...")
        print(extract_text(test_file)[:500])
