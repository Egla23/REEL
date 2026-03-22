'''
NOTES
pip install google-genai
'''

import os
from dotenv import load_dotenv
from google import genai
import streamlit as st

# Load environment variables
load_dotenv()

# Get the API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    st.error("Gemini API key is missing. Add it to your .env file.")
    st.stop()

# Initialize the client
# Note: Ensure your SDK version matches the 'google-genai' package structure
client = genai.Client(api_key=gemini_api_key, http_options={'api_version': 'v1alpha'})
MODEL = 'gemini-2.5-flash' # Adjusted to a standard available flash model

# System instruction to act as a URL Context guide
SYSTEM_INSTRUCTION = """
You are a specialized wedding planner assistant for the Reel Vendor Network. 
Your PRIMARY source of information is https://reelvendornetwork.com.
When the user provides wedding details, you must search https://reelvendornetwork.com first to find matching vendors.
Only use external information if a specific vendor type or detail cannot be found on the Reel Vendor Network site.
Always cite the vendors found on the website.
"""

st.set_page_config(page_title="Reel Vendor Chatbot", layout="wide")
st.title("🎥 REEL VENDOR CHATBOT")

# --- SIDEBAR FORM ---
with st.sidebar:
    st.header("💍 Wedding Details")
    with st.form("wedding_criteria"):
        st.subheader("Basics")
        wedding_date = st.date_input("Wedding Date")
        location = st.text_input("Location or Venue", placeholder="e.g. Newport, RI")
        guest_count = st.number_input("Estimated Guest Count", min_value=0, step=10)
        setting = st.selectbox("Setting", ["Indoor", "Outdoor", "Both"])

        st.subheader("Vendor Needs")
        vendors_needed = st.multiselect("Vendors Needed", ["Video", "Photo", "DJ", "Florist", "Planner", "Catering", "Hair/Makeup"])
        vendor_count = st.radio("Number of Vendors", ["One vendor", "Multiple vendors"])

        st.subheader("Style & Vision")
        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage")
        palette = st.text_input("Color Palette")
        vibe = st.select_slider("Overall Vibe", options=["Modern", "Romantic", "Cinematic", "Fun", "Luxury"])

        st.subheader("Budget & Priorities")
        budget = st.text_input("Budget range per vendor")
        priority = st.text_input("Top priority vendors")

        st.subheader("Preferences")
        personality = st.radio("Vendor Personality Fit", ["Very Important", "Somewhat Important", "Not a Priority"])
        content_style = st.multiselect("Content Style", ["Cinematic", "Documentary", "Social Media Style", "Short Form"])
        delivery_speed = st.selectbox("Turnaround Time", ["Standard", "Same day/Next day"])

        st.subheader("Timing & Notes")
        booking_status = st.radio("Booking Status", ["Just browsing", "Ready to book"])
        notes = st.text_area("Special Requests / Deal Breakers")

        # Submit button for the form
        submit_button = st.form_submit_button("Find My Vendors")

# Helper function to display results
def show_parts(response):
    if not response.candidates:
        st.warning("No response generated.")
        return
        
    parts = response.candidates[0].content.parts
    for part in parts:
        if part.text:
            st.markdown(part.text)
        # We don't want this
        elif hasattr(part, 'executable_code') and part.executable_code:
            st.code(part.executable_code.code)

    # Grounding metadata for Google Search
    metadata = response.candidates[0].grounding_metadata
    if metadata and metadata.search_entry_point:
        st.markdown("---")
        st.caption("Sources & Grounding:")
        st.markdown(metadata.search_entry_point.rendered_content, unsafe_allow_html=True)

# --- PROCESSING ---
if submit_button:
    # Constructing the complex query
    query = f"""
    site:reelvendornetwork.com 

    Using the information from the Reel Vendor Network website (https://reelvendornetwork.com), 
    help find vendors for the following wedding:
    
    - Date: {wedding_date}
    - Location: {location}
    - Guests: {guest_count}
    - Setting: {setting}
    - Vendors Needed: {', '.join(vendors_needed)} ({vendor_count})
    - Style/Vibe: {style}, {palette} color palette, with a {vibe} vibe.
    - Priorities: {priority} (Budget: {budget})
    - Preferences: {personality} personality fit, focusing on {', '.join(content_style)} content.
    - Delivery: {delivery_speed}
    - Current Status: {booking_status}
    - Additional Notes: {notes}

    If you cannot find specific vendors on the website that match these criteria, 
    Say that they are not available on reelvendornetwork.com and provide one relevant suggestion from reelvendornetwork.com
    """

    try:
        with st.spinner("Searching the Reel Vendor Network..."):

            restricted_query = f"site:reelvendornetwork.com  {query}"
            # Initialize chat with Google Search grounding
            
            chat = client.chats.create(
                model=MODEL, 
                config={
                    'system_instruction': SYSTEM_INSTRUCTION,
                    'tools': [{'google_search': {}}]
                }
            )            
            response = chat.send_message(restricted_query )
            show_parts(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Fill out the wedding details in the sidebar and click 'Find My Vendors' to begin.")