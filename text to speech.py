import os
from TTS.api import TTS
from IPython.display import Audio

def text_to_speech(text, output_path="output.wav", speaker_wav="/content/sample_speaker.wav", language="en"):
    """Convert text to speech and save it as an audio file."""
    os.environ["COQUI_TOS_AGREED"] = "1"
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True, gpu=True)
    tts.tts_to_file(text=text, speaker_wav=speaker_wav, language=language, file_path=output_path)
    return output_path

if __name__ == "__main__":
    text = input("Enter the text you want to convert to speech: ")
    output_file = text_to_speech(text)
    print(f"Speech saved to {output_file}")
