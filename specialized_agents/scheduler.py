import json
from google import genai
from utils.state_manager import get_active_state
from datetime import datetime

def SchedulerAgent() -> str:
    """Determines the next best topic for the user to study based on revision history."""
    print("--- 🧠 SchedulerAgent: Determining Next Revision Topic ---")
    active_state = get_active_state()
    
    revision_history = active_state['revision_history']
    user_mastery = active_state['mastery_score']
    
    # Format history into a readable string for the LLM
    formatted_history = "No revision history found."
    if revision_history:
        history_list = []
        for concept, timestamps in revision_history.items():
            # Get the date of the last study session
            last_study_time = datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d %H:%M')
            study_count = len(timestamps)
            history_list.append(f"- Concept: {concept}, Last Studied: {last_study_time}, Times Studied: {study_count}")
        formatted_history = "\n".join(history_list)
        
    prompt = (
        f"You are a study planner. Based on the user's revision history, recommend the single best concept "
        f"for them to study next. The best concept should be one they haven't studied often or one studied long ago."
        f"Then, suggest a brief, encouraging study schedule for the next week."
        f"\n\n--- User Data ---"
        f"Mastery Score: {user_mastery}/5"
        f"Revision History:\n{formatted_history}"
        f"\n\n--- Output Structure ---"
        f"1. **Next Study Topic:** [Suggested Concept Name]"
        f"2. **Study Plan:** [A short, encouraging weekly plan]"
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
        return f"Error in SchedulerAgent: LLM call failed. Check API Key configuration. Error details: {e}"