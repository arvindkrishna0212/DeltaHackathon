import os
import hashlib
import mimetypes
import io
import ipywidgets as widgets
from IPython.display import display, Javascript, Audio, HTML
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document
from groq import Groq
from TTS.api import TTS

# Set API key
os.environ["GROQ_API_KEY"] = "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"

# UI Components
upload_btn = widgets.FileUpload(accept=".pdf,.docx,.jpg,.jpeg,.png", multiple=False)
language_dropdown = widgets.Dropdown(
    options=[("English", "eng"), ("French", "fra"), ("Spanish", "spa"), ("German", "deu")],
    value="eng",
    description="Language:",
    style={'description_width': 'initial'}
)
extract_btn = widgets.Button(description="Extract Text", button_style='primary')
output_area = widgets.Output()
loading_label = widgets.Label(value="", layout=widgets.Layout(margin="10px 0"))

# Enhanced UI with HTML/CSS
display(HTML("""
<style>
    .widget-label { font-size: 16px; font-weight: bold; }
    .widget-button { background-color: #007bff; color: white; font-size: 16px; border-radius: 8px; padding: 10px; }
    .loading-spinner { display: none; text-align: center; font-size: 16px; color: #007bff; }
</style>
"""))

# File Processing Logic
def extract_text_from_file(file_data, language='eng'):
    file_name = list(file_data.keys())[0]
    file_content = file_data[file_name]['content']
    ext = os.path.splitext(file_name)[1].lower()
    
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

# Click Event
def on_extract_clicked(b):
    with output_area:
        output_area.clear_output()
        loading_label.value = "Processing... Please wait."
        
        if not upload_btn.value:
            print("Please upload a file first.")
            loading_label.value = ""
            return
        
        file_data = upload_btn.value
        language = language_dropdown.value
        extracted_text = extract_text_from_file(file_data, language)
        
        print("\n--- Extracted Text ---\n", extracted_text)
        print("\nCharacter Count:", len(extracted_text))
        
        # Summarize with Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Summarize this as a war reporter in about 300-400 words: {extracted_text}. Just the report is enough. Nothing else."}],
            model="llama-3.3-70b-versatile",
        )
        summary = response.choices[0].message.content
        print("\n--- Summary ---\n", summary)
        
        # Text-to-Speech
        os.environ["COQUI_TOS_AGREED"] = "1"
        speaker_wav = "/content/sample_speaker.wav" 
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True, gpu=True)
        tts.tts_to_file(text=response.choices[0].message.content, speaker_wav=speaker_wav, language="en", file_path="output.wav")
        display(Audio("output.wav", autoplay=False))
        loading_label.value = "Done!"

extract_btn.on_click(on_extract_clicked)

# Display UI
display(upload_btn, language_dropdown, extract_btn, loading_label, output_area)
