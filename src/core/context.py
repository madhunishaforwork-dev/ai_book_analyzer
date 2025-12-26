
import json
import os
import uuid
import time
from collections import Counter
from datetime import datetime

CONTEXT_FILE = "user_data/user_context.json"

class ContextManager:
    def __init__(self):
        self.user_id = self._get_or_create_user_id()
        self.context = self._load_context()
        
    def _get_or_create_user_id(self):
        # In a web app, this might come from a cookie. 
        # Locally, we check if file exists or create a new one.
        if os.path.exists(CONTEXT_FILE):
            try:
                with open(CONTEXT_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('user_id', str(uuid.uuid4()))
            except:
                return str(uuid.uuid4())
        return str(uuid.uuid4())

    def _load_context(self):
        if os.path.exists(CONTEXT_FILE):
            try:
                with open(CONTEXT_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading context: {e}")
        
        # Default Context Structure
        return {
            "user_id": self.user_id,
            "session_history": [],
            "preferences": {
                "summary_depth": "Standard", # Standard, Concise, Detailed
                "interaction_style": "Neutral" # Neutral, Technical, Beginner
            },
            "topics_interested": [],
            "last_active": time.time()
        }

    def _save_context(self):
        os.makedirs(os.path.dirname(CONTEXT_FILE), exist_ok=True)
        with open(CONTEXT_FILE, 'w') as f:
            json.dump(self.context, f, indent=4)

    def log_interaction(self, action_type, query=None, details=None):
        """Logs an interaction to infer preferences."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": action_type, # e.g., "summary_generated", "question_asked"
            "query": query,
            "details": details
        }
        self.context['session_history'].append(interaction)
        
        # Simple Inference Logic
        if action_type == "summary_generated":
            # If user generated summary, maybe update topics?
            pass
            
        self._save_context()

    def get_adaptive_prompt_instruction(self):
        """Returns a string to prepend to LLM prompts based on history."""
        prefs = self.context['preferences']
        history = self.context['session_history']
        
        instruction = f"User Preference: {prefs['summary_depth']} depth. {prefs['interaction_style']} tone.\n"
        
        # Check for repeated clarifications
        clarifications = [i for i in history if i['type'] == 'question_asked' and 'explain' in str(i.get('query','')).lower()]
        if len(clarifications) > 2:
            instruction += "Note: User frequently asks for explanations. Prioritize simple clarity.\n"
            
        return instruction

    def clear_history(self):
        """Privacy reset."""
        self.context['session_history'] = []
        self.context['topics_interested'] = []
        self._save_context()
        return "History cleared."
