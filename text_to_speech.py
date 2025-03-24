#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import requests
from gtts import gTTS
import logging
import time
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
AUDIO_DIR = "data/output/audio"

def ensure_directories():
    """Ensure that necessary directories exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)

def translate_to_hindi(text):
    """
    Translate English text to Hindi using Google Translate API.
    
    Args:
        text (str): English text to translate
        
    Returns:
        str: Hindi translation of the text
    """
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "hi",
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse the response JSON
        result = response.json()
        translated_text = ''.join([item[0] for item in result[0] if item[0]])

        logger.info(f"✅ Translation successful! Hindi text: {translated_text[:100]}")
        
        # Verify the translation actually happened
        if not translated_text or translated_text == text:
            logger.error("⚠️ Translation failed! Returning original English text.")
            return text  # Fallback to English if translation fails
        
        return translated_text
    except Exception as e:
        logger.error(f"❌ Error translating text to Hindi: {str(e)}")
        return text  # Fallback to English if error

def generate_hindi_tts(text, company_name):
    """
    Generate Text-to-Speech in Hindi for the given text.
    
    Args:
        text (str): Text to convert to speech (translated to Hindi)
        company_name (str): Name of the company (for file naming)
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        ensure_directories()

        # Translate text to Hindi
        hindi_text = translate_to_hindi(text)
        
        # 🔍 Debugging: Print the actual text being converted
        logger.info(f"📢 Generating TTS for: {hindi_text[:100]}")
        
        # Delete old file if it exists (Avoid caching issues)
        file_name = f"{company_name.lower().replace(' ', '_')}_summary.mp3"
        file_path = os.path.join(AUDIO_DIR, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Deleted old TTS file: {file_path}")

        # Generate TTS
        tts = gTTS(text=hindi_text, lang='hi', slow=False)
        
        # Save the audio file
        tts.save(file_path)

        # Validate if file exists and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            logger.error(f"❌ Audio file generation failed! File too small or missing: {file_path}")
            raise Exception("TTS Audio file was not generated properly.")
        
        logger.info(f"✅ Successfully generated Hindi TTS: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Error generating Hindi TTS: {str(e)}")
        return None

# Run test
if __name__ == "__main__":
    test_text = "Apple has released a new iPhone model with advanced AI features."
    generate_hindi_tts(test_text, "Apple")

