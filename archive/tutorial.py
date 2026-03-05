'''
NOTES:
    pip install google-genai
'''

from dotenv import load_dotenv
import os
from google import genai
import streamlit as st

# Load environment variables
load_dotenv()

# Get the API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Gemini API key is missing. Add it to your .env file.")

# Initialize the client
client = genai.Client(http_options={'api_version': 'v1alpha'})
MODEL = 'gemini-2.5-flash'

# Input for the query
'''
Like input() in Python, the below line stores input text into a query.
When users fill out a form, we will construct the query and put it in the model for the user. 
'''
query = st.text_input("[VALUES OF FORM]") 

# App title and settings
st.title("REEL CHATBOT")
st.sidebar.title("[FORM HERE]")

# Helper function to display results
def show_parts(response):
    parts = response.candidates[0].content.parts
    for part in parts:
        if part.text:
            st.markdown(part.text)
        elif part.executable_code:
            st.code(part.executable_code.code)
        else:
            st.json(part)

    metadata = response.candidates[0].grounding_metadata
    if metadata and metadata.search_entry_point:
        st.markdown(metadata.search_entry_point.rendered_content)

# Process the query
if query:
    try:
        st.spinner("Processing...")

        # Gemini search with Google Search
        chat = client.chats.create(model=MODEL, config={'tools': 'google_search'})
        response = chat.send_message(query)
        show_parts(response)
    except Exception as e:
        st.error(f"Error: {e}")