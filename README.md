# AI Voice Reporter

## Overview

This application is a powerful document processing tool that extracts text from various file formats, performs AI-powered summarization, and provides text-to-speech capabilities. Built for Jupyter Notebook environments, it combines optical character recognition (OCR), document parsing, Large Language Model (LLM) summarization, and speech synthesis into a single, user-friendly interface.

## Features

- **Multi-format Support**: Process PDF, DOCX, JPG, JPEG, and PNG files
- **Multilingual OCR**: Extract text in English, French, Spanish, German, and more
- **AI Summarization**: Generate concise summaries using Groq's LLama 3.3 70B model
- **Text-to-Speech**: Convert summaries to natural-sounding audio
- **Character Statistics**: View character count of extracted text
- **Modern UI**: Clean, intuitive interface with loading indicators

## Requirements

### Python Libraries

```
pip install os-sys hashlib mimetypes ipywidgets Pillow pytesseract PyPDF2 python-docx groq TTS
pip install git+https://github.com/coqui-ai/TTS.git
```

### External Dependencies

1. **Tesseract OCR** (for image text extraction)
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

2. **Language Data** (for multilingual support)
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr-fra tesseract-ocr-spa tesseract-ocr-deu`
   - **Other OS**: Download language data from [Tesseract GitHub](https://github.com/tesseract-ocr/tessdata)

3. **Groq API Key**
   - Sign up at [Groq](https://www.groq.com)
   - Replace placeholder API key with your own

4. **GPU Support** (recommended for TTS)
   - CUDA-compatible GPU for faster text-to-speech processing

## How It Works

### Workflow

1. **Upload**: User selects a document file (PDF, DOCX, or image)
2. **Configure**: User selects the document language
3. **Process**: Application extracts text using appropriate method based on file type
4. **Summarize**: The extracted text is sent to Groq's LLama 3.3 model for summarization
5. **Vocalize**: Summary is converted to speech using the XTTS v2 model

### Technical Breakdown

#### 1. Environment Setup
```python
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
os.environ["GROQ_API_KEY"] = "your-api-key-here"
```

#### 2. UI Components
The application uses ipywidgets to create an intuitive interface:
- File upload button with format restrictions
- Language selection dropdown
- Process button
- Output display area
- Loading indicator

#### 3. Text Extraction Logic
Different extraction methods are used based on file type:
- **Images**: OCR via Tesseract
- **PDFs**: Text extraction via PyPDF2
- **DOCX**: Document parsing via python-docx

#### 4. AI Processing
- Extracted text is sent to Groq's API
- Uses the LLama 3.3 70B model for high-quality summarization
- Summary is formatted as a war correspondent's report

#### 5. Text-to-Speech
- Generates audio from the summary using XTTS v2
- Multilingual capability with custom voice cloning potential

## Usage Guide

1. **Start the Application**:
   - Run the notebook in Jupyter/Colab
   - The UI will appear below the code cell

2. **Upload a Document**:
   - Click the "Upload" button
   - Select a supported file (.pdf, .docx, .jpg, .jpeg, .png)

3. **Select Language**:
   - Choose the primary language of your document
   - This affects OCR accuracy for images

4. **Process**:
   - Click "Extract Text"
   - Wait for processing (progress indicator will show)

5. **Review Results**:
   - View extracted text
   - Read the AI-generated summary
   - Play the audio version

## Customization Options

### Change the Summary Style
Modify the prompt to change the summary style:
```python
response = client.chat.completions.create(
    messages=[{"role": "user", "content": f"Summarize this as a [STYLE] in about 300-400 words: {extracted_text}"}],
    model="llama-3.3-70b-versatile",
)
```

Replace `[STYLE]` with options like:
- "business executive"
- "academic researcher"
- "social media post"
- "news article"

### Change TTS Voice
To use a different voice:
1. Provide a different speaker sample WAV file
2. Modify the speaker_wav path:
```python
speaker_wav = "/path/to/different_speaker.wav"
```

### Add More Languages
Extend the language dropdown by adding more options:
```python
language_dropdown = widgets.Dropdown(
    options=[
        ("English", "eng"), 
        ("French", "fra"), 
        ("Spanish", "spa"), 
        ("German", "deu"),
        ("Italian", "ita"),
        ("Portuguese", "por")
    ],
    value="eng",
    description="Language:"
)
```

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Ensure file size is under Jupyter's limit
   - Check that file format is supported

2. **OCR Text Quality Poor**
   - Ensure image resolution is sufficient
   - Verify correct language is selected
   - Check Tesseract installation

3. **API Key Error**
   - Verify Groq API key is correct
   - Check internet connection

4. **TTS Not Working**
   - Ensure GPU is available if using CUDA acceleration
   - Check TTS models are properly installed

## Advanced Features & Extensions

### Potential Enhancements

1. **Batch Processing**
   - Process multiple files at once
   - Add code:
   ```python
   upload_btn = widgets.FileUpload(accept=".pdf,.docx,.jpg,.jpeg,.png", multiple=True)
   ```

2. **Custom Summarization Options**
   - Add length and style controls
   - Implement different LLM providers

3. **Document Translation**
   - Add translation capabilities
   - Integrate with translation APIs

4. **Content Analysis**
   - Extract entities, sentiment, and key points
   - Visualize document statistics

## Security Considerations

1. The application processes files locally within the Jupyter environment
2. API keys should be stored securely, not hardcoded in notebooks
3. Consider implementing file scanning for production use
4. Be aware of data privacy when sending content to external APIs

## License & Attribution

This code is provided for educational purposes. When using in production:

1. Respect the terms of service for all APIs (Groq)
2. Ensure compliance with Tesseract OCR license (Apache 2.0)
3. Check TTS model licensing for commercial applications

---

*Created: March 13, 2025*
