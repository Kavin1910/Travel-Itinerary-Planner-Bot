from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

class Message(BaseModel):
    message: str
    chat_history: List[Dict[str, str]]

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

@app.post("/chat")
async def chat(data: Message):
    user_message = data.message
    history = data.chat_history
    roles = "\n".join([f"{m['role']}: {m['content']}" for m in history])

    # Check if all 15 questions have been answered
    if sum(1 for m in history if m["role"] == "user") >= 15:
        final_prompt = f"""
You are a travel agent AI. Based on this user conversation, generate a personalized travel itinerary including:

- Destination recommendations
- Suggested duration
- Budget considerations
- Accommodation suggestions
- Key activities and experiences
- Travel tips

Conversation:
{roles}

Itinerary:
"""
        reply = gemini_response(final_prompt)
        return { "reply": reply }

    # Else continue normal response flow
    prompt = roles + f"\nUser: {user_message}\nAssistant:"
    reply = gemini_response(prompt)

    # Add Google Places if needed
    if any(kw in user_message.lower() for kw in ["place", "travel to", "city", "location"]):
        reply += "\n\n" + search_places(user_message)

    return {"reply": reply}

