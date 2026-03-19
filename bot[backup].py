"""
To run this code, open the terminal and do the following cmd:
streamlit run app.py
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Get the API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("Gemini API key is missing. Add it to your .env file.")

MODEL = 'gemini-2.5-flash' # Adjusted to a standard available flash model

# System instruction to act as a URL Context guide
SYSTEM_INSTRUCTION = """
You are a specialized wedding planner assistant for the Reel Vendor Network. 
Your PRIMARY source of information is site:reelvendornetwork.com.
When the user provides wedding details, you must search site:reelvendornetwork.com first to find matching vendors.
"""

# Initialize the client
client = genai.Client(api_key=gemini_api_key, http_options={'api_version': 'v1alpha'})

# Note: Ensure your SDK version matches the 'google-genai' package structure
# Define your tools
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

# Initialize the config correctly using = instead of :
config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=[grounding_tool]
)

def generate_response(query: str):
    chat = client.chats.create(
        model=MODEL, 
        config={
            'system_instruction': SYSTEM_INSTRUCTION,
            'tools': [{'google_search': {}}]
        }
    )            
    response = chat.send_message(query)
    return response

