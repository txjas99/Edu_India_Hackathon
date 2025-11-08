import json
from google import genai
from utils.state_manager import get_active_state, clear_pending_answer, increase_mastery

def AnswerAgent(user_answer: str, pending_data: dict) -> str:
    """Grades the user's answer against the expected answer and updates mastery."""
    print("--- 🧠 AnswerAgent: Grading User Response and Updating State ---")
    active_state = get_active_state()
    
    concept = pending_data['concept']
    expected_answer = pending_data['expected_answer']
    
    # 1. Clear the pending state immediately to prevent infinite loops
    clear_pending_answer()
    
    # 2. Construct the prompt for the grading agent
    prompt = (
        f"Task: Grade the user's response for the concept '{concept}'. "
        f"The grading is on a scale of 0 (completely wrong) to 3 (excellent and comprehensive)."
        f"Output your final decision strictly as a JSON object with three keys: 'score', 'feedback', and 'mastery_increment'."
        f"Use the following data:"
        f"\n\n--- Data ---"
        f"Expected Answer: {expected_answer}"
        f"User Response: {user_answer}"
        f"\n\n--- JSON Structure ---"
        f"score (int): 0-3."
        f"feedback (string): Explain why the user received that score and what they missed."
        f"mastery_increment (int): The score (0-3) to add to the user's mastery progress."
    )
    
    grading_result = {
        "score": 0, 
        "feedback": "Grading failed due to an API error. Please try the test again.",
        "mastery_increment": 0
    }
    
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
                        "score": {"type": "INTEGER"},
                        "feedback": {"type": "STRING"},
                        "mastery_increment": {"type": "INTEGER"}
                    }
                }
            )
        )
        
        grading_result = json.loads(response.text)
        
    except Exception as e:
        print(f"Error in AnswerAgent API call: {e}")
        grading_result['feedback'] = f"Grading failed due to an API error. Check API Key configuration. Error details: {e}"


    # 3. Update Mastery State
    # Ensure increment is an integer, default to 0 if missing or invalid
    try:
        increment = int(grading_result.get('mastery_increment', 0)) 
    except (TypeError, ValueError):
        increment = 0
        
    level_up = increase_mastery(increment)
    
    # Get current state again to display updated mastery score
    current_state = get_active_state()
    
    # 4. Construct Final Response
    mastery_message = ""
    if level_up:
        mastery_message = f"**🌟 MASTERY LEVEL UP!** Your overall mastery score increased to {current_state['mastery_score']}/5! Keep up the great work!"
    elif increment > 0:
        mastery_message = f"**Mastery Progress:** Gained {increment} point(s). Current mastery progress is {current_state['mastery_increment']}/3 towards the next level."
    else:
        mastery_message = "No mastery progress gained this time. Don't worry, every review helps!"


    final_response = (
        f"--- ✅ Test Graded: {concept.title()} ---\n\n"
        f"**Score:** {grading_result.get('score', 0)}/3\n\n"
        f"**Feedback:** {grading_result.get('feedback', 'No feedback provided.')}\n\n"
        f"***\n"
        f"{mastery_message}"
    )
    
    return final_response