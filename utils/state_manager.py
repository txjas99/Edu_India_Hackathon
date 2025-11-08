import uuid
import os
import time

# --- Global State Variables ---
# Use a global dictionary to hold all user profiles and their dynamic state.
ALL_USER_STATES = {
    "Urban Service Worker (Bengaluru)": {
        "name": "Urban Service Worker",
        "location": "Bengaluru, Karnataka",
        "background": "Retail/Service Industry",
        "language": "Kannada",
        "mastery_score": 1,
        "mastery_increment": 0,
        "revision_history": {},
        "pending_answer": None # Will store {'concept': str, 'expected_answer': str}
    },
    "Rural Farmer (Maharashtra)": {
        "name": "Rural Farmer",
        "location": "Pune, Maharashtra",
        "background": "Agriculture/Farming",
        "language": "Marathi",
        "mastery_score": 3,
        "mastery_increment": 0,
        "revision_history": {},
        "pending_answer": None
    }
}

# --- CRITICAL FIX: Global variable to hold the currently selected state key ---
# This ensures all modules know which profile is active.
ACTIVE_USER_KEY = list(ALL_USER_STATES.keys())[0] # Default to the first profile

def get_active_state() -> dict:
    """Retrieves the current user's profile and dynamic state."""
    # Returns the state for the key, or the default state if the key is missing
    return ALL_USER_STATES.get(ACTIVE_USER_KEY, ALL_USER_STATES[list(ALL_USER_STATES.keys())[0]])

def set_active_state(user_key: str):
    """Sets the globally active user profile by its key."""
    global ACTIVE_USER_KEY
    if user_key in ALL_USER_STATES:
        ACTIVE_USER_KEY = user_key

def set_pending_answer(concept: str, expected_answer: str):
    """Sets the state to wait for a user response to a test question."""
    active_state = get_active_state()
    # Store the expected data structure
    active_state['pending_answer'] = {
        'concept': concept,
        'expected_answer': expected_answer
    }

def clear_pending_answer():
    """Clears the pending answer state after grading is complete."""
    active_state = get_active_state()
    active_state['pending_answer'] = None

def update_state(concept: str):
    """Updates the user's revision history after a lesson."""
    active_state = get_active_state()
    if concept not in active_state['revision_history']:
        active_state['revision_history'][concept] = []
        
    # Log current time as a simple timestamp
    active_state['revision_history'][concept].append(time.time())

def increase_mastery(increment: int):
    """Increments the mastery score and potentially levels up the user."""
    active_state = get_active_state()
    
    active_state['mastery_increment'] += increment
    
    if active_state['mastery_increment'] >= 3:
        # Increase score, but cap it at 5
        active_state['mastery_score'] = min(5, active_state['mastery_score'] + 1)
        active_state['mastery_increment'] = 0 # Reset increment
        return True # Indicate level up happened
    
    return False # No level up