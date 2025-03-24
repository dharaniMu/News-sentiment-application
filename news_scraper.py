#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# **✅ Use NewsAPI Instead of Guardian API**
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Load NewsAPI key from environment variable
NEWS_API_URL = "https://newsapi.org/v2/everything"  # NewsAPI endpoint

def get_news_articles(company_name, limit=5):
    """
    Fetch news articles from NewsAPI.

    Args:
        company_name (str): Company name for news search.
        limit (int): Number of articles to retrieve.

    Returns:
        list: A list of articles with title, content, URL, and published date.
    """
    if not NEWS_API_KEY:
        raise ValueError("🚨 NEWS_API_KEY is missing. Set it in your environment variables!")

    params = {
        "q": company_name,
        "pageSize": limit,
        "apiKey": NEWS_API_KEY,
        "language": "en",  # ✅ Get only English news
        "sortBy": "publishedAt",  # ✅ Get the latest news first
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "articles" not in data:
            logger.error("❌ No 'articles' found in API response")
            return []

        articles = [
            {
                "title": article["title"],
                "content": article.get("description", "No content available"),  # ✅ Use `description` if content is missing
                "url": article["url"],
                "published_date": article["publishedAt"],
            }
            for article in data["articles"]
        ]

        if not articles:
            logger.warning(f"⚠️ No articles found for {company_name}")

        logger.info(f"✅ Fetched {len(articles)} articles for {company_name}")
        return articles

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error fetching news: {e}")
        return []

