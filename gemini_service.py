#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import logging
import google.generativeai as genai
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Google Generative AI with API key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables. Set this variable before running the script.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Use a free-tier Gemini model (gemini-1.5-flash)
DEFAULT_MODEL = "gemini-1.5-flash"

def generate_request_prompt(company_name, articles):
    """
    Generate the prompt for Gemini to analyze articles
    """
    prompt = f"""You are a financial news analyst tasked with analyzing news articles about {company_name}.
I will provide you with several news articles, and you need to:
1. Summarize each article concisely
2. Determine the sentiment (Positive, Negative, or Neutral) for each article
3. Extract key topics from each article
4. Conduct a comparative analysis across all articles
5. Provide an overall sentiment analysis for {company_name} based on all articles

Provide your response in structured JSON format as follows:
```
{{
  "Company": "{company_name}",
  "Articles": [
    {{
      "Title": "Article title",
      "Summary": "Brief summary",
      "Sentiment": "Positive/Negative/Neutral",
      "Topics": ["Topic1", "Topic2", "Topic3"]
    }}
  ],
  "Comparative Analysis": {{
    "Sentiment Distribution": {{
      "Positive": count,
      "Negative": count,
      "Neutral": count
    }},
    "Topic Overlap": {{
      "Common Topics": ["Topic1", "Topic2"],
      "Unique Topics": ["TopicX", "TopicY"]
    }}
  }},
  "Final Sentiment Analysis": "Overall sentiment summary"
}}
```

Here are the articles about {company_name}:
"""
    
    for i, article in enumerate(articles):
        prompt += f"\n--- ARTICLE {i+1} ---\n"
        prompt += f"TITLE: {article.get('title', 'No title')}\n"
        prompt += f"CONTENT: {article.get('content', 'No content')}\n"
    
    prompt += "\nPlease analyze these articles and provide the response in JSON format."
    return prompt

def process_articles(company_name, articles):
    """
    Process articles using Gemini model for sentiment analysis
    """
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not set. Cannot proceed with Gemini analysis.")
        return None

    prompt = generate_request_prompt(company_name, articles)
    model = genai.GenerativeModel(DEFAULT_MODEL)
    
    try:
        logger.info(f"Sending request to Gemini model for {company_name}")
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_str = response_text[json_start:json_end]
        result = json.loads(json_str)
        
        logger.info(f"Successfully processed articles for {company_name}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response from Gemini: {e}")
        return None
    except Exception as e:
        logger.error(f"Error using Gemini model: {e}")
        return None

