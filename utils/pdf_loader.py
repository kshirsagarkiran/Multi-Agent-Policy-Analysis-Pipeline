import os
import pdfplumber

def load_pdfs(pdf_dir):
    pdf_texts = {}
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                pdf_texts[filename] = text
    return pdf_texts
