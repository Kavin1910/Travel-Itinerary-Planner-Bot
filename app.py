import streamlit as st
import requests
import multiprocessing
import uvicorn
import os
import time
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Check if environment variables are set
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables")
if not GOOGLE_PLACES_API_KEY:
    print("Warning: GOOGLE_PLACES_API_KEY not found in environment variables")

# Define FastAPI models
class Message(BaseModel):
    message: str
    chat_history: List[Dict[str, str]]

# Configure API
api_app = FastAPI()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Error contacting Gemini: {str(e)}]"

def search_places(query: str):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_PLACES_API_KEY}
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    if not results:
        return "No places found."
    top = results[0]
    return f"I recommend {top['name']} at {top['formatted_address']}!"

@api_app.post("/chat")
async def chat(data: Message):
    user_message = data.message
    history = data.chat_history
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
        return {"reply": reply}
    
    # Else continue normal response flow
    prompt = roles + f"\nUser: {user_message}\nAssistant:"
    reply = gemini_response(prompt)
    
    # Add Google Places if needed
    if any(kw in user_message.lower() for kw in ["place", "travel to", "city", "location"]):
        reply += "\n\n" + search_places(user_message)
    
    return {"reply": reply}

def run_fastapi():
    """Run the FastAPI server"""
    uvicorn.run(api_app, host="127.0.0.1", port=8000)

def run_streamlit():
    """Define and run the Streamlit app"""
    # Set page config
    st.set_page_config(page_title="Travel Itinerary Planner")
    st.title("🌍 Travel Itinerary Planner Bot")

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
    else:
        with st.chat_message("assistant"):
            st.markdown("Thanks for all the info! I'm generating your itinerary...")

        # Display contact card at the end
        with st.container():
            st.markdown("---")
            st.markdown("### Contact the Developer")
            st.markdown("**Kavin N R**")
            st.markdown("AI Professional")
            st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/kavinnr/)")
            st.markdown("---")

    # Handle user input
    user_input = st.chat_input("Your answer")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        try:
            response = requests.post("http://localhost:8000/chat", json={
                "message": user_input,
                "chat_history": st.session_state.chat_history
            })
            bot_reply = response.json()["reply"]

            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

            if st.session_state.question_index < len(questions):
                st.session_state.question_index += 1
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the backend server. Please make sure it's running.")

if __name__ == "__main__":
    # Start the FastAPI server in a separate process
    api_process = multiprocessing.Process(target=run_fastapi)
    api_process.start()
    
    # Wait a moment for the API server to start
    time.sleep(2)
    
    # Start the Streamlit app
    run_streamlit()
