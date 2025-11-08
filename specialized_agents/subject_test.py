import json
from google import genai
from utils.state_manager import get_active_state

def SubjectAgent(concept: str) -> str:
    """Generates the core, general explanation of a concept."""
    print("--- 🧠 SubjectAgent: Generating Core Explanation ---")
    active_state = get_active_state()
    
    prompt = (
        f"You are a master educator. Explain the core concept of '{concept}' clearly and concisely. "
        f"Do not use any localized analogies, cultural references, or advanced terms. "
        f"The explanation should be general and foundational, suitable for a general audience."
    )
    
    try:
        # Rely on genai.Client() to pick up the API key from the environment
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error in SubjectAgent: LLM call failed. Check API Key configuration. Error details: {e}"


def TestAgent(concept: str) -> dict:
    """Generates an active recall question and the expected answer for a concept."""
    print("--- 🧠 TestAgent: Generating Active Recall Question ---")
    active_state = get_active_state()
    
    prompt = (
        f"Generate one simple, open-ended active recall question about '{concept}'. "
        f"Then, provide the comprehensive expected answer (a few sentences) for that question. "
        f"Format the output strictly as a JSON object with two keys: 'question' and 'answer'."
    )
    
    try:
        # Rely on genai.Client() to pick up the API key from the environment
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING", "description": "The active recall question."},
                        "answer": {"type": "STRING", "description": "The detailed expected answer."}
                    },
                }
            )
        )
        
        test_data = json.loads(response.text)
        return test_data
        
    except Exception as e:
        print(f"Error in TestAgent: {e}")
        # Return a dictionary even on failure to prevent downstream KeyErrors
        return {"question": f"What is {concept}?", "answer": f"A brief explanation of {concept}."}