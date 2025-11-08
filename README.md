EduIndia: Adaptive Multi-Agent Learning System

This project is a powerful demonstration of a multi-agent architecture built on Streamlit and the Gemini API. It creates a truly personalized educational experience by delegating complex tasks to specialized AI agents.

Core Features and Benefits

The system is designed to provide high-quality, relevant education by adapting to the learner:

Contextual Localization: The system automatically adapts lesson analogies (e.g., using farming or retail terms) and provides full language translations based on the user's defined background, ensuring immediate relevance.

Stateful Assessment: The application knows when a test is active. It correctly delegates user answers to the Answer Agent for grading and feedback, rather than confusing them with normal conversation.

Mastery Tracking: Test scores are translated into a Mastery Score, providing a clear progress path and informing all future learning decisions.

Intelligent Scheduling: The Scheduler Agent analyzes the user's study history and progress to recommend the optimal next topic for revision, maximizing knowledge retention.

How the Agents Work

The system is managed by a central Root Agent that acts as the primary traffic controller for delegation.

When you ask the system to explain <topic>, the Root Agent triggers a chain of specialized agents:

Subject Agent generates the core explanation.

Content Generator Agent customizes the analogies and language for the active learner.

Test Agent creates an active recall question and stores the correct answer in the application state.

When you submit your answer, the Root Agent delegates it to the Answer Agent for grading and mastery update. Other commands, like study next, are delegated to the Scheduler Agent.

Setup and Run

To launch the app:

Install Dependencies:
pip install streamlit google-genai python-dotenv

Set API Key: Create a file named .env in the project root and add your key:
GEMINI_API_KEY="YOUR_API_KEY_HERE"

Run the application from your terminal:
streamlit run app.py
