import os
import hashlib
import mimetypes
import io
import asyncio
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document
import streamlit as st
import torchaudio
from TTS.api import TTS
from groq import Groq
import logging

# ---------------------------
# Setup logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Fix torchaudio backend issue
# ---------------------------
try:
    torchaudio.set_audio_backend("sox_io")
    logger.info("Successfully set audio backend to sox_io")
except Exception as e:
    logger.warning(f"Could not set torchaudio backend: {e}")
    logger.info("Continuing with default torchaudio backend")

# Ensure proper event loop handling for Streamlit
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---------------------------
# Environment Setup
# ---------------------------
os.environ["COQUI_TOS_AGREED"] = "1"

# Set up Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# ---------------------------
# FileFormat Helper Class
# ---------------------------
class FileFormat:
    def __init__(self, filename, mime_type, binary, file_hash):
        self.filename = filename
        self.mime_type = mime_type
        self.binary = binary
        self.hash = file_hash

    @classmethod
    def from_file(cls, file_obj, filename=None):
        if not filename:
            filename = "uploaded_file"
        mime_type, _ = mimetypes.guess_type(filename)
        binary = file_obj.read()
        file_hash = hashlib.sha256(binary).hexdigest()
        return cls(filename, mime_type, binary, file_hash)

# ---------------------------
# Text Extraction Function
# ---------------------------
def extract_text_from_file(file_obj, filename, language='eng'):
    try:
        file_format = FileFormat.from_file(file_obj, filename)
        ext = os.path.splitext(file_format.filename)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            st.info(f"Processing image file: {file_format.filename} using OCR")
            image = Image.open(io.BytesIO(file_format.binary))
            text = pytesseract.image_to_string(image, lang=language)
            return text

        elif ext == '.pdf':
            st.info(f"Processing PDF file: {file_format.filename} using PDF extraction")
            text = ""
            with io.BytesIO(file_format.binary) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if not text.strip():
                text = "No extractable text found in PDF. It may be a scanned document."
            return text

        elif ext == '.docx':
            st.info(f"Processing DOCX file: {file_format.filename} using DOCX extraction")
            with io.BytesIO(file_format.binary) as docx_file:
                document = Document(docx_file)
                text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            return text

        else:
            return f"Unsupported file format: {ext}"
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        logger.error(f"Text extraction error: {str(e)}", exc_info=True)
        return f"Error processing file: {str(e)}"

# ---------------------------
# Text-to-Speech Function
# ---------------------------
def generate_audio(summary):
    with st.spinner("🔊 Generating audio..."):
        try:
            # Load TTS model
            st.info("Loading XTTS v2 model...")
            logger.info("Initializing TTS model: xtts_v2")
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
            
            # Create a default speaker reference audio if missing
            speaker_wav_path = "sample_speaker.wav"
            if not os.path.exists(speaker_wav_path):
                st.warning("Speaker reference file not found. Creating a temporary reference...")
                logger.warning("Speaker reference file missing, creating fallback")
                
                # Set a shorter summary for testing to avoid memory issues
                test_text = "This is a test audio file for text to speech synthesis."
                
                # Use a fallback model to create a speaker reference
                fallback_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
                fallback_tts.tts_to_file(text=test_text, file_path=speaker_wav_path)
                st.success("Created temporary speaker reference file.")
            
            # Check if the summary is too long - XTTS might struggle with very long text
            if len(summary) > 1000:
                st.warning("Summary is very long. Processing first 1000 characters to avoid memory issues.")
                logger.warning(f"Truncating long summary from {len(summary)} to 1000 chars")
                summary = summary[:1000] + "..."
            
            # Generate speech and store it in memory
            st.info("Generating speech with XTTS v2...")
            logger.info("Starting speech generation")
            audio_buffer = io.BytesIO()
            tts.tts_to_file(
                text=summary, 
                speaker_wav=speaker_wav_path, 
                language="en", 
                file_path=audio_buffer
            )
            audio_buffer.seek(0)  # Reset pointer for playback
            logger.info("Successfully generated audio")
            return audio_buffer
            
        except Exception as e:
            st.error(f"Failed to generate audio: {str(e)}")
            logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
            
            # Fallback to simpler TTS model if XTTS fails
            try:
                st.warning("Attempting to use fallback TTS model...")
                fallback_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
                audio_buffer = io.BytesIO()
                fallback_tts.tts_to_file(text=summary[:500] + "...", file_path=audio_buffer)
                audio_buffer.seek(0)
                st.success("Generated audio with fallback model")
                return audio_buffer
            except Exception as fallback_error:
                st.error(f"Fallback TTS also failed: {str(fallback_error)}")
                logger.error(f"Fallback TTS failed: {str(fallback_error)}", exc_info=True)
                return None

# ---------------------------
# Main Streamlit Application
# ---------------------------
def main():
    st.title("📰 Document Summarizer & Text-to-Speech App 🎙️")
    st.write("Upload a document (PDF, DOCX, or an image) and get a war-time reporter style summary with audio playback.")

    # Add a note about Streamlit Cloud limitations
    st.info("⚠️ Note: On Streamlit Cloud, the XTTS v2 model may experience memory limitations. If audio generation fails, try a shorter document or summary.")

    uploaded_file = st.file_uploader("Choose a file", type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'pdf', 'docx'])
    language = st.text_input("Enter OCR language code (default: eng)", value="eng")

    if uploaded_file is not None:
        try:
            # Read file bytes and create a BytesIO buffer
            file_bytes = uploaded_file.read()
            file_buffer = io.BytesIO(file_bytes)
            file_buffer.seek(0)  # Reset buffer pointer

            extracted_text = extract_text_from_file(file_buffer, uploaded_file.name, language=language)
            st.subheader("📜 Extracted Text")
            st.text_area("Text", value=extracted_text, height=300)

            if st.button("🔍 Generate Summary and Audio"):
                try:
                    with st.spinner("Generating summary..."):
                        # Generate summary using Groq API
                        response = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"I want you to summarize this text in about 300 words as if you are a reporter during the time of a war: {extracted_text}",
                                }
                            ],
                            model="llama-3.3-70b-versatile",
                        )
                        summary = response.choices[0].message.content

                    st.subheader("📝 Summary")
                    st.write(summary)

                    # Generate and play audio
                    audio_buffer = generate_audio(summary)
                    if audio_buffer:
                        st.audio(audio_buffer, format="audio/wav")
                    else:
                        st.error("❌ Audio generation failed. Please try with a shorter document.")
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
                    logger.error(f"Summary generation error: {str(e)}", exc_info=True)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"File processing error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Document Summarizer & TTS",
        page_icon="📰",
        layout="wide"
    )
    main()
