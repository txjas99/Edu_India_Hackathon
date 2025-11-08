import streamlit as st
import sys
from io import StringIO
import os
# --- NEW IMPORT ---
from dotenv import load_dotenv

# CRITICAL: Load environment variables from the .env file immediately
load_dotenv() 

# Import the RootAgent and state management functions
# This must happen after load_dotenv() so the agents can find the key
try:
    # --- CRITICAL FIX for Modular Imports ---
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)
        
    from core_agents.root_orchestrator import RootAgent
    from utils.state_manager import ALL_USER_STATES, get_active_state, set_active_state
    
except Exception as e:
    st.error(f"Initialization Error: Could not load core modules. Details: {e}")
    st.stop()


# --- Streamlit Setup ---
st.set_page_config(page_title="EduIndia: Multi-Agent Learning Demo", layout="wide")

# Initialize chat history and log
if "messages" not in st.session_state:
    st.session_state.messages = []
if "log_content" not in st.session_state:
    st.session_state.log_content = "Run a query to see the multi-agent delegation trace."

# --- Custom Function to Run Agent and Capture Log ---
def run_agent_workflow(user_query):
    """Runs the RootAgent and captures both the log (print output) and the final response."""
    
    # 1. Capture the log output (the delegation trace)
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output
    
    # 2. Run the agent logic
    try:
        final_output = RootAgent(user_query)
    except Exception as e:
        final_output = f"An unhandled error occurred in the agent workflow: {e}"
        print(f"UNHANDLED ERROR: {e}")
    
    # 3. Restore stdout and get the log
    sys.stdout = old_stdout
    log_content = redirected_output.getvalue()
    
    return log_content, final_output

# Function to run when the user selection changes
def handle_user_switch():
    # 1. Get the selected user KEY (the full string name) from the session state
    selected_key = st.session_state.user_selector
    
    # 2. Set this KEY as the globally active state in utils/state_manager.py
    set_active_state(selected_key)
    
    # 3. Clear chat history and log for the new user session
    st.session_state.messages = []
    st.session_state.log_content = f"Switched user to {selected_key}. Ready for new queries."
    # Rerun is crucial to update the UI immediately with the new profile data
    st.rerun() 

# --- UI Layout ---

st.title("🇮🇳 EduIndia: AI Agents for Inclusive Learning")

# Sidebar for Context and Log
with st.sidebar:
    st.title("Agent Architecture Demo")
    
    # --- User Selector Setup ---
    user_options = list(ALL_USER_STATES.keys()) 
    
    # Determine the currently active key for the selector's default index
    current_active_key = user_options[0] # Default to the first user
    
    # Set the active state explicitly before the selectbox runs
    set_active_state(current_active_key)
    initial_index = 0

    # Streamlit Selectbox
    selected_profile_name = st.selectbox(
        "Select Active Learner Profile",
        options=user_options,
        index=initial_index,
        key="user_selector",
        on_change=handle_user_switch
    )
    
    # Re-set active state based on the final selection (in case of startup or RERUN)
    set_active_state(selected_profile_name) 

    # Get the active state (dynamically set by the selectbox/startup logic)
    active_user_state = get_active_state()
    
    st.header("Active Learner Context")
    profile_html = (
        f"**Profile:** {active_user_state['name']}<br>"
        f"**Location:** {active_user_state['location']}<br>"
        f"**Background:** {active_user_state['background']}<br>"
        f"**Language:** {active_user_state['language']}<br>"
        f"**Mastery:** {active_user_state['mastery_score']}/5 | "
        f"**Next Level:** {active_user_state['mastery_increment']}/3"
    )
    st.markdown(profile_html, unsafe_allow_html=True)
    
    st.subheader("Agent Delegation Log")
    # Log content displays the print statements from the agent workflow
    st.code(st.session_state.log_content, language='text')

# Initial greeting and instructions
if not st.session_state.messages:
    initial_message = (
        "Hello! I am EduIndia, your multi-agent adaptive learning assistant. "
        "I adjust lessons based on your background and schedule revisions based on your progress.<br><br>"
        "**Try these commands:**<br>"
        "1. `explain inflation` (To see localization and a new lesson)<br>"
        "2. `test me on inflation` (To start a test)<br>"
        "3. **Submit the answer** to the question above (To verify grading and mastery update)"
    )
    st.session_state.messages.append({"role": "assistant", "content": initial_message})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- Handle User Input ---
if user_query := st.chat_input("Enter your learning query here..."):
    
    # 1. Add user message to chat history and display
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # 2. Run the agent workflow and capture the log
    with st.spinner("Processing request... Agents are collaborating..."):
        log_content, final_response = run_agent_workflow(user_query)
    
    # 3. Store log for sidebar display
    st.session_state.log_content = log_content
    
    # 4. Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    
    # 5. Display assistant response
    with st.chat_message("assistant"):
        st.markdown(final_response, unsafe_allow_html=True)
        
    # Force rerun to update log and state immediately (e.g., mastery score)
    st.rerun()