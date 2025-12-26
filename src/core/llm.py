
import requests
import json
import streamlit as st
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt):
        pass

class GoogleGeminiProvider(LLMProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        # Updated to gemini-2.5-flash based on available models for this key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
    def generate_text(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
                return f"API Error ({response.status_code}): {response.text}"
                
            result = response.json()
            # Extract text from response structure
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "No content generated."
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error connecting to Gemini API: {str(e)}"

class FallbackProvider(LLMProvider):
    """Simple rule-based 'generator' if no API key is provided."""
    def generate_text(self, prompt):
        return "I am running in Offline Mode. Semantic search is active, but generative explanations require an API Key. Please enter a Google Gemini API Key in the sidebar to unlock full generative capabilities."

def get_llm_provider(api_key=None, provider_type="gemini"):
    if api_key:
        if provider_type == "gemini":
            return GoogleGeminiProvider(api_key)
    return FallbackProvider()
