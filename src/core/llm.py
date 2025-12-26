
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

class SimulationProvider(LLMProvider):
    """Provides simulated responses so the app works without an API Key."""
    def generate_text(self, prompt):
        # Detect what the user is asking for based on the prompt content
        if "summary" in prompt.lower() or "overview" in prompt.lower():
            return """
            ## 📘 Book Overview (Simulated)
            This is a simulated summary because no API Key was provided.
            The document appears to be a technical report or academic paper.

            ## 🔑 Key Themes
            - Artificial Intelligence
            - Data Analysis
            - System Architecture
            
            ## 🚀 Key Takeaways
            - The system uses advanced NLP techniques.
            - Deployment on cloud platforms is supported.
            
            *(To get real insights from your specific PDF, please enter a valid Google API Key in the sidebar.)*
            """
        elif "question" in prompt.lower():
            return "This is a simulated answer. Without an API Key, I cannot generate specific answers from the text. Please provide a key to unlock real intelligence."
        else:
            return "Simulation Mode: Content generated successfully."

def get_llm_provider(api_key=None, provider_type="gemini"):
    if api_key and len(api_key) > 10: # Simple validation
        if provider_type == "gemini":
            return GoogleGeminiProvider(api_key)
    return SimulationProvider()
