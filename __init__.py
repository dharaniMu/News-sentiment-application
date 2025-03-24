#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# utils/__init__.py - Package Initialization
# This file makes the utils directory a Python package

# Import key functions to make them accessible directly from the utils package
from utils.news_scraper import get_news_articles
from utils.text_to_speech import generate_hindi_tts, translate_to_hindi
from utils.gemini_service import process_articles

# Define package-level variables
__all__ = ['get_news_articles', 'generate_hindi_tts', 'translate_to_hindi', 'process_articles']

