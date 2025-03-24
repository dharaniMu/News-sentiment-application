import streamlit as st
import pandas as pd
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000"
# Updated for correct file structure
COMPANY_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "company_list.csv")

def main():
    st.set_page_config(
        page_title="Company News Sentiment Analysis",
        page_icon="📰",
        layout="wide"
    )

    st.title("Company News Sentiment Analysis")
    st.markdown("""
        This application extracts news articles about a specific company, performs sentiment analysis,
        and provides a comparative analysis with text-to-speech output in Hindi.
    """)

    # Show API status
    try:
        status_response = requests.get(f"{API_URL}/")
        api_status = "🟢 API Connected" if status_response.status_code == 200 else "🔴 API Unavailable"
    except Exception:
        api_status = "🔴 API Unavailable"
    
    st.sidebar.write(f"API Status: {api_status}")
    
    # Load company list
    try:
        logger.info(f"Attempting to load company list from: {COMPANY_LIST_FILE}")
        st.sidebar.write(f"Looking for company list at: {COMPANY_LIST_FILE}")
        
        if not os.path.exists(COMPANY_LIST_FILE):
            raise FileNotFoundError(f"Company list file not found: {COMPANY_LIST_FILE}")
        
        companies_df = pd.read_csv(COMPANY_LIST_FILE)
        companies_df.columns = companies_df.columns.str.strip()
        
        if "Company" not in companies_df.columns:
            available_columns = companies_df.columns.tolist()
            st.sidebar.write(f"Available columns: {available_columns}")
            raise ValueError(f"Column 'Company' not found. Found columns: {available_columns}")
        
        company_list = companies_df["Company"].dropna().tolist()
        st.sidebar.write(f"Successfully loaded {len(company_list)} companies")
    except Exception as e:
        logger.error(f"Error loading company list: {e}")
        company_list = ["Google", "Amazon", "Tesla", "Microsoft", "Apple"]
        st.warning(f"Using default company list as company_list.csv couldn't be loaded. Error: {str(e)}")

    # Company selection
    selected_company = st.selectbox("Select a company", company_list)

    # Analysis button
    if st.button("Analyze"):
        with st.spinner(f"Analyzing news for {selected_company}..."):
            try:
                # Log the request we're about to make
                logger.info(f"Requesting sentiment data for {selected_company} from {API_URL}/sentiment/{selected_company}")
                
                response = requests.get(f"{API_URL}/sentiment/{selected_company}")
                
                # Log the response
                logger.info(f"Received response with status code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    display_results(data, selected_company)
                    
                    # Audio section
                    st.subheader("Audio Summary (Hindi)")
                    audio_response = requests.get(f"{API_URL}/audio/{selected_company}")
                    if audio_response.status_code == 200:
                        st.audio(audio_response.content, format="audio/mp3")
                    else:
                        st.warning(f"Audio summary not available. Error: {audio_response.text}")
                else:
                    st.error(f"Error fetching analysis: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the API. Make sure the FastAPI server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
                logger.error(f"Error in Analyze button: {str(e)}")

def display_results(data, company_name):
    st.header(f"Analysis Results for {company_name}")
    final_sentiment = data.get("Final Sentiment Analysis", "No sentiment analysis available")
    st.subheader("Overall Sentiment")
    st.write(final_sentiment)

    if "Comparative Sentiment Score" in data:
        st.subheader("Sentiment Distribution")
        sentiment_dist = data["Comparative Sentiment Score"].get("Sentiment Distribution", {})
        if sentiment_dist:
            sentiment_df = pd.DataFrame({
                'Sentiment': list(sentiment_dist.keys()), 
                'Count': list(sentiment_dist.values())
            })
            st.bar_chart(sentiment_df.set_index('Sentiment'))
        else:
            st.info("No sentiment distribution data available.")

    if "Articles" in data:
        st.subheader("Analyzed Articles")
        for i, article in enumerate(data["Articles"], start=1):
            with st.expander(f"Article {i}: {article.get('Title', 'No title')}"):
                st.write(f"**Source:** {article.get('Source', 'Unknown')}")
                st.write(f"**Date:** {article.get('Date', 'Unknown date')}")
                st.write(f"**Sentiment:** {article.get('Sentiment', 'Not analyzed')}")
                st.write("**Summary:**")
                st.write(article.get('Summary', 'No summary available'))

if __name__ == "__main__":
    logger.info(f"Starting Streamlit app with company list from: {COMPANY_LIST_FILE}")
    main()