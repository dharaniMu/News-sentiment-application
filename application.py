import os
import sys
import logging
import pickle
import signal
import subprocess
from multiprocessing import Process
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from gtts import gTTS
import pandas as pd
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="News Sentiment Analysis API",
    description="API for company news sentiment analysis with TTS capabilities",
    version="1.0.0"
)

# Define the path to data directory - updated for correct structure
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
COMPANY_LIST_FILE = os.path.join(DATA_DIR, "company_list.csv")

@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the News Sentiment Analysis API"}

@app.get("/companies")
async def get_companies():
    try:
        logger.info(f"Checking for company list file at: {COMPANY_LIST_FILE}")
        if not os.path.exists(COMPANY_LIST_FILE):
            raise HTTPException(status_code=404, detail=f"Company list file not found: {COMPANY_LIST_FILE}")
        
        df = pd.read_csv(COMPANY_LIST_FILE)
        df.columns = df.columns.str.strip()
        
        if "Company" not in df.columns:
            logger.error(f"Expected column 'Company' not found. Found columns: {df.columns.tolist()}")
            raise HTTPException(status_code=500, detail="Column 'Company' not found in dataset")
        
        companies = df["Company"].dropna().unique().tolist()
        logger.info(f"Retrieved companies: {companies}")
        return {"companies": companies}
    except Exception as e:
        logger.error(f"Error retrieving company list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving company list: {str(e)}")

@app.get("/sentiment/{company_name}")
async def get_sentiment(company_name: str):
    try:
        file_name = f"{company_name.lower()}.pkl"
        file_path = os.path.join(DATA_DIR, file_name)
        
        logger.info(f"Looking for sentiment file at: {file_path}")
        if not os.path.exists(file_path):
            logger.warning(f"File not found for company: {company_name}")
            raise HTTPException(status_code=404, detail=f"Analysis for {company_name} not found")
        
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        logger.info(f"Sentiment data fetched for {company_name}")
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error fetching sentiment data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sentiment data: {str(e)}")

def generate_hindi_tts(text, company_name):
    try:
        if not text.strip():
            raise ValueError("No valid text for TTS")
        
        logger.info(f"Generating TTS for {company_name}")
        tts = gTTS(text=text, lang='hi')
        audio_path = os.path.join(DATA_DIR, f"{company_name}_summary.mp3")
        tts.save(audio_path)
        logger.info(f"TTS saved to {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        return None

@app.get("/audio/{company_name}")
async def get_audio(company_name: str):
    try:
        file_name = f"{company_name.lower()}.pkl"
        file_path = os.path.join(DATA_DIR, file_name)
        
        if not os.path.exists(file_path):
            logger.warning(f"Audio file not found for {company_name}")
            raise HTTPException(status_code=404, detail=f"Analysis for {company_name} not found")
        
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        final_sentiment = data.get("Final Sentiment Analysis", "No sentiment analysis available")
        audio_path = generate_hindi_tts(final_sentiment, company_name)
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        logger.info(f"Audio file generated for {company_name}")
        return FileResponse(audio_path, media_type="audio/mp3", filename=f"{company_name}_summary.mp3")
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

# ========================= RUNNING SECTION ========================= #
def run_fastapi():
    """Run the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    logger.info(f"Using data directory: {DATA_DIR}")
    logger.info(f"Company list file: {COMPANY_LIST_FILE}")
    run_fastapi()