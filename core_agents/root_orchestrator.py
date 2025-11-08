# Import all specialized agents
from specialized_agents.content_generator import ContentGeneratorAgent
from specialized_agents.subject_test import SubjectAgent, TestAgent
from specialized_agents.scheduler import SchedulerAgent
from specialized_agents.answer_agent import AnswerAgent 

# Import utilities for state management (CRITICAL: clear_pending_answer is needed for robustness)
from utils.state_manager import update_state, get_active_state, set_pending_answer, clear_pending_answer


def OrchestrationAgent(concept: str) -> str:
    """
    Manages the complex workflow for a lesson request:
    1. Gets core concept (SubjectAgent).
    2. Gets localized analogy (ContentGeneratorAgent).
    3. Gets active recall question (TestAgent).
    4. Combines results and updates state.
    """
    print("\n--- 🧠 OrchestrationAgent (Workflow Manager) Executing ---")
    
    # 1. Subject Agent runs (Core Concept) - Parallel step 1
    core_explanation = SubjectAgent(concept)
    
    # 2. Content Generator Agent runs (Localization) - Parallel step 2
    localized_analogy = ContentGeneratorAgent(core_explanation) 
    
    # 3. Test Agent runs (Active Recall) - Sequential step 3 (after concept is ready)
    test_data = TestAgent(concept) 
    
    # Check if TestAgent returned a dict (question and answer)
    if isinstance(test_data, dict) and 'question' in test_data and 'answer' in test_data:
        active_recall_q = test_data['question']
        # State change: Set pending answer before responding to the user
        set_pending_answer(concept, test_data['answer'])
    else:
        active_recall_q = test_data.get('question', 'Could not generate a question.')
    
    # 4. Integrate and Present the full lesson experience
    final_response = (
        f"**Subject: {concept.title()}**\n\n"
        f"**Core Concept (from Subject Agent):**\n> {core_explanation}\n\n"
        f"**Localized Analogy (from Content Generator Agent):**\n> {localized_analogy}\n\n"
        f"--- Active Recall Check ---\n"
        f"**Question (from Test Agent):**\n> {active_recall_q}"
    )
    
    # 5. Log the concept study to state
    update_state(concept)
    
    return final_response


def RootAgent(user_query: str) -> str:
    """
    The main delegation agent. Directs user requests to the appropriate sub-agent 
    or starts the full orchestration workflow.
    """
    print(f"\n=======================================================")
    print(f"=== 🤖 RootAgent: Received Request: '{user_query}' ===")
    print(f"=======================================================")
    
    query = user_query.lower()
    
    # 0. Check for Pending Answer State FIRST
    active_user_state = get_active_state()

    # CRITICAL FIX: Explicitly check if the value is NOT None.
    if active_user_state.get('pending_answer') is not None: 
        pending_data = active_user_state.get('pending_answer')
        
        # Ensure the pending data is valid (concept and answer keys exist)
        if isinstance(pending_data, dict) and 'concept' in pending_data and 'expected_answer' in pending_data:
            print("--- 🧠 RootAgent: Delegating to AnswerAgent (Waiting for response) ---")
            # Delegate to AnswerAgent with the user's response and the expected answer data
            return AnswerAgent(user_query, pending_data)
        else:
            # Fallback if state is corrupted, clear it and inform the user
            print("--- ⚠️ RootAgent: Pending state corrupted, clearing state. ---")
            clear_pending_answer()
            return "There was an issue processing your test answer. Let's restart the test or ask me to explain a concept."


    # 1. Check for 'explain' or 'teach'
    if "explain" in query or "teach" in query:
        # Delegation 1: Lesson Request -> OrchestrationAgent
        keyword = "explain" if "explain" in query else "teach"
        concept = query.split(keyword, 1)[-1].strip() or "Cloud Computing" 
        return OrchestrationAgent(concept)
    
    # 2. Check for 'revise' or 'schedule'
    elif "revise" in query or "study next" in query or "schedule" in query:
        # Delegation 2: Revision Request -> SchedulerAgent
        return SchedulerAgent()
        
    # 3. Check for 'test me on' or 'quiz on' (This is where pending_answer is SET)
    elif "test me on" in query or "quiz on" in query or "test me" in query:
        # Delegation 3: Test Only Request -> TestAgent
        
        keyword = ""
        if "test me on" in query:
            keyword = "test me on"
        elif "quiz on" in query:
            keyword = "quiz on"
        elif "test me" in query:
            keyword = "test me"
            
        topic = query.split(keyword, 1)[-1].strip()
        if not topic:
             return "Please specify a topic for the test, e.g., 'test me on Photosynthesis'."
        
        test_data = TestAgent(topic)
        
        if isinstance(test_data, dict) and 'question' in test_data:
            # set_pending_answer is called to store the expected answer
            set_pending_answer(topic, test_data['answer'])
            return f"--- Active Recall Check ---\n**Question (from Test Agent):**\n> {test_data['question']}"
        else:
            return test_data # Returns generic error string if TestAgent fails
        
    else:
        # Fallback for conversational queries
        return "I can help you! Ask me to 'explain <topic>', 'study next', or 'test me on <topic>'."