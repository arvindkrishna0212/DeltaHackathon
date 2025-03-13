import os
import io
import tempfile
import gradio as gr
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document
from groq import Groq
import torch
from TTS.api import TTS

# Set API key for Groq
os.environ["GROQ_API_KEY"] = "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"
# Agree to TTS terms
os.environ["COQUI_TOS_AGREED"] = "1"

# Initialize TTS model outside the function for better performance
def initialize_tts():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=(device=="cuda"))
    return tts

# File Processing Logic
def extract_text_from_file(file_path, language='eng'):
    """Extract text from various file formats"""
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in ['.jpg', '.jpeg', '.png']:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang=language)
        return text

    elif file_ext == '.pdf':
        text = ""
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text or "No extractable text found in PDF."

    elif file_ext == '.docx':
        document = Document(file_path)
        return "\n".join([p.text for p in document.paragraphs])

    else:
        return "Unsupported file format."

# Main processing function for Gradio
def process_document(file, language):
    if file is None:
        return "Please upload a file first.", None, None

    # Extract text from file
    extracted_text = extract_text_from_file(file.name, language)
    if not extracted_text or extracted_text == "Unsupported file format.":
        return "Failed to extract text or unsupported format.", None, None

    char_count = len(extracted_text)

    # Summarize with Groq
    try:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Summarize this as a war reporter in about 300-400 words: {extracted_text}. Just the report is enough. Nothing else."}],
            model="llama-3.3-70b-versatile",
        )
        summary = response.choices[0].message.content
    except Exception as e:
        return f"Error during summarization: {str(e)}", None, None

    # Text-to-Speech
    try:
        tts = initialize_tts()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()

        # Use a sample speaker file (this would need to be supplied)
        sample_speaker = "sample_speaker.wav"  # Update this path for your setup

        tts.tts_to_file(
            text=summary,
            speaker_wav=sample_speaker,
            language="en",
            file_path=temp_file.name
        )

        # Return results
        full_result = f"""
## Extracted Text
{extracted_text[:1000]}{"..." if len(extracted_text) > 1000 else ""}

## Character Count
{char_count}

## Summary
{summary}
        """
        return full_result, summary, temp_file.name
    except Exception as e:
        return f"{extracted_text}\n\nCharacter Count: {char_count}\n\nSummary: {summary}\n\nError generating audio: {str(e)}", summary, None

# Create Gradio interface
def create_app():
    with gr.Blocks(title="Document Extraction & Summarization", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Document Extraction, Summarization & Text-to-Speech")

        with gr.Row():
            with gr.Column(scale=2):
                file_input = gr.File(label="Upload Document (PDF, DOCX, JPG, PNG)")
                language = gr.Dropdown(
                    choices=[("English", "eng"), ("French", "fra"), ("Spanish", "spa"), ("German", "deu")],
                    value="eng",
                    label="Language"
                )
                process_btn = gr.Button("Extract & Summarize", variant="primary")

            with gr.Column(scale=3):
                with gr.Tab("Full Results"):
                    output_text = gr.Markdown()
                with gr.Tab("Summary & Audio"):
                    summary_text = gr.Textbox(label="Summary", lines=10)
                    audio_output = gr.Audio(label="Audio Summary")

        process_btn.click(
            process_document,
            inputs=[file_input, language],
            outputs=[output_text, summary_text, audio_output]
        )

        gr.Markdown("""
        ## How to Use
        1. Upload a document (PDF, DOCX, JPG, PNG)
        2. Select the language of the text
        3. Click "Extract & Summarize"
        4. View the extracted text, summary, and listen to the audio version
        """)

    return app

# Launch the app
if __name__ == "__main__":
    # Make sure you have a sample speaker file
    if not os.path.exists("sample_speaker.wav"):
        print("Warning: sample_speaker.wav not found. The TTS functionality will not work.")
        print("Please provide a sample speaker file named 'sample_speaker.wav'")

    app = create_app()
    app.launch(share=True)  # share=True creates a public link
