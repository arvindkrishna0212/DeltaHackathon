import os
import io
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document

def extract_text_from_file(file_path, language='eng'):
    """Extract text from a file based on its format."""
    ext = os.path.splitext(file_path)[1].lower()
    
    with open(file_path, 'rb') as f:
        file_content = f.read()

    if ext in ['.jpg', '.jpeg', '.png']:
        image = Image.open(io.BytesIO(file_content))
        return pytesseract.image_to_string(image, lang=language)

    elif ext == '.pdf':
        text = ""
        with io.BytesIO(file_content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text or "No extractable text found."

    elif ext == '.docx':
        document = Document(io.BytesIO(file_content))
        return "\n".join([p.text for p in document.paragraphs])

    else:
        return "Unsupported file format."

if __name__ == "__main__":
    file_path = input("Enter the path to the file: ")
    language = input("Enter the OCR language (default: eng): ") or "eng"
    extracted_text = extract_text_from_file(file_path, language)
    print("\n--- Extracted Text ---\n", extracted_text)
