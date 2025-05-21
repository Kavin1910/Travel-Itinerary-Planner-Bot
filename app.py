import streamlit as st
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Check if environment variables are set
if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found in environment variables or Streamlit secrets")
if not GOOGLE_PLACES_API_KEY:
    st.error("⚠️ GOOGLE_PLACES_API_KEY not found in environment variables or Streamlit secrets")

# Try to get from Streamlit secrets if not in env
if not GEMINI_API_KEY and hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
    GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
if not GOOGLE_PLACES_API_KEY and hasattr(st, 'secrets') and 'GOOGLE_PLACES_API_KEY' in st.secrets:
    GOOGLE_PLACES_API_KEY = st.secrets['GOOGLE_PLACES_API_KEY']

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

def gemini_response(prompt):
    """Get response from Gemini API"""
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key is missing. Please add it to your environment variables or Streamlit secrets."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error contacting Gemini API: {str(e)}"

def search_places(query: str):
    """Search for places using Google Places API"""
    if not GOOGLE_PLACES_API_KEY:
        return "⚠️ Google Places API key is missing. Please add it to your environment variables or Streamlit secrets."
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "key": GOOGLE_PLACES_API_KEY}
        response = requests.get(url, params=params)
        results = response.json().get("results", [])
        if not results:
            return "No places found matching your query."
        top = results[0]
        return f"I recommend {top['name']} at {top['formatted_address']}!"
    except Exception as e:
        return f"⚠️ Error searching places: {str(e)}"

def process_chat(user_message, chat_history):
    """Process chat message and return AI response"""
    history = chat_history
    roles = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    # Check if all 15 questions have been answered
    if sum(1 for m in history if m["role"] == "user") >= 15:
        final_prompt = f""" You are a travel agent AI. Based on this user conversation, generate a personalized travel itinerary including:

- Destination recommendations
- Suggested duration
- Budget considerations
- Accommodation suggestions
- Key activities and experiences
- Travel tips

Conversation: {roles}

Itinerary: """
        reply = gemini_response(final_prompt)
        return reply
    
    # Else continue normal response flow
    prompt = roles + f"\nUser: {user_message}\nAssistant:"
    reply = gemini_response(prompt)
    
    # Add Google Places if needed
    if any(kw in user_message.lower() for kw in ["place", "travel to", "city", "location"]):
        place_info = search_places(user_message)
        if not place_info.startswith("⚠️"):  # Only add if there's no error
            reply += "\n\n" + place_info
    
    return reply

# Set page config
st.set_page_config(page_title="Travel Itinerary Planner", page_icon="🌍")
st.title("🌍 Travel Itinerary Planner Bot")

# Add a sidebar with information
with st.sidebar:
    st.image("https://www.svgrepo.com/show/261077/travel.svg", width=100)
    st.header("About")
    st.write("This travel bot helps you plan the perfect trip by asking relevant questions and creating a personalized itinerary based on your preferences.")
         
    st.markdown("---")
    st.markdown("### Contact the Developer")
    st.markdown("**Kavin N R**")
    st.markdown("AI Professional")
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/kavinnr/)")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

# Questions to ask the user
questions = [
    "Where would you like to travel?",
    "What are your travel dates?",
    "How many days do you plan to stay?",
    "What is your estimated budget?",
    "Are you traveling alone, with a partner, or family?",
    "What type of trip do you prefer: relaxation, adventure, culture, or luxury?",
    "Do you have specific destinations in mind?",
    "Do you need visa assistance?",
    "Preferred accommodation type (hotel, hostel, Airbnb, resort)?",
    "Flight class preference (economy, business)?",
    "Do you have any dietary restrictions?",
    "What kind of activities are you interested in?",
    "Any physical limitations we should consider?",
    "Are you open to guided tours?",
    "What's your ideal travel pace: relaxed, moderate, or packed?"
]

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ask next question
if st.session_state.question_index < len(questions):
    next_question = questions[st.session_state.question_index]
    with st.chat_message("assistant"):
        st.markdown(next_question)
elif st.session_state.question_index == len(questions) and not any(msg["role"] == "assistant" and "Itinerary" in msg["content"] for msg in st.session_state.chat_history[-3:]):
    with st.chat_message("assistant"):
        st.markdown("Thanks for all the info! I'm generating your personalized travel itinerary...")

# Handle user input
user_input = st.chat_input("Your answer", disabled=not (GEMINI_API_KEY and GOOGLE_PLACES_API_KEY))

if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Show typing indicator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Process the chat directly
            bot_reply = process_chat(user_input, st.session_state.chat_history)
    
    # Add the bot reply to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    
    # Move to next question
    if st.session_state.question_index < len(questions):
        st.session_state.question_index += 1
    
    # Rerun to update the UI
    st.rerun()
