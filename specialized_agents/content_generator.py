import json
import os
from google import genai
from utils.state_manager import get_active_state

# --- Helper function to get the initialized Gemini Client (API Key Check) ---
def get_gemini_client():
    """Initializes and returns the Gemini client using the environment variable."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)


def ContentGeneratorAgent(core_concept_explanation: str) -> str:
    """Localizes the core explanation using the active user's profile."""
    print("--- 🧠 ContentGeneratorAgent: Localizing Explanation ---")
    active_state = get_active_state()
    
    user_location = active_state['location']
    user_background = active_state['background']
    user_language = active_state['language']
    
    # Prompt the model to localize the explanation
    prompt = (
        f"Task: Localize the following core concept explanation. "
        f"Adapt it using a culturally relevant analogy specific to the user's background and location: {user_background} in {user_location}. "
        f"Then, provide the entire localized analogy translated into the user's local language: {user_language}. "
        f"Start the response with the localized analogy in English, followed by the local language version."
        f"\n\n--- Core Concept Explanation to Localize ---"
        f"{core_concept_explanation}"
    )
    
    try:
        # Use the robust client initialization
        client = get_gemini_client()
        
        # Using gemini-2.5-flash-preview-09-2025 for robust localization and translation
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt
        )
        return response.text
    except ValueError as e:
        return f"Configuration Error in ContentGeneratorAgent: {e} Please set the GEMINI_API_KEY."
    except Exception as e:
        return f"Error in ContentGeneratorAgent API call: {e}"