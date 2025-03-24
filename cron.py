#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# cron.py - Scheduled Data Processing
# This file is responsible for periodically fetching news and generating sentiment analysis
# for all companies in the list and saving the results

import pandas as pd
import pickle
import os
import logging
from utils.news_scraper import get_news_articles
from utils.gemini_service import process_articles
import time
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cron.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define paths
COMPANY_LIST_PATH = "data/company_list.csv"
OUTPUT_DIR = "data/output"

def ensure_directories():
    """
    Ensure that necessary directories exist
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.info(f"Ensured output directory exists: {OUTPUT_DIR}")

def process_company(company_name):
    """
    Process a single company: fetch news, perform analysis, and save results
    
    Args:
        company_name (str): Name of the company to process
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Processing company: {company_name}")
        
        # Step 1: Fetch news articles
        articles = get_news_articles(company_name, limit=10)
        if not articles:
            logger.warning(f"No articles found for {company_name}")
            return False
        
        logger.info(f"Retrieved {len(articles)} articles for {company_name}")
        
        # Step 2: Process articles with Gemini AI
        result = process_articles(company_name, articles)
        if not result:
            logger.warning(f"Failed to process articles for {company_name}")
            return False
            
        # Step 3: Save results as pickle file
        output_path = os.path.join(OUTPUT_DIR, f"{company_name.lower()}.pkl")
        with open(output_path, 'wb') as f:
            pickle.dump(result, f)
            
        logger.info(f"Successfully saved analysis for {company_name} to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {company_name}: {str(e)}", exc_info=True)
        return False

def run_cron_job():
    """
    Main function to run the cron job for all companies
    """
    try:
        # Ensure output directory exists
        ensure_directories()
        
        # Load company list
        companies_df = pd.read_csv(COMPANY_LIST_PATH)

        # Debugging: Print available column names
        logger.info(f"Available columns in CSV: {list(companies_df.columns)}")

        # Strip any extra spaces in column names
        companies_df.columns = companies_df.columns.str.strip()

        # Ensure 'Company' column exists
        if 'Company' not in companies_df.columns:
            raise ValueError(f"Error: 'Company' column not found! Available columns: {list(companies_df.columns)}")

        company_list = companies_df['Company'].dropna().tolist()
        
        logger.info(f"Starting cron job for {len(company_list)} companies")
        
        # Process each company with progress bar
        successful = 0
        for company in tqdm(company_list, desc="Processing companies"):
            if process_company(company):
                successful += 1
            # Add a small delay to avoid overwhelming APIs
            time.sleep(2)
            
        logger.info(f"Cron job completed. Successfully processed {successful}/{len(company_list)} companies")
        
    except Exception as e:
        logger.error(f"Error running cron job: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Run the cron job when script is executed directly
    run_cron_job()

