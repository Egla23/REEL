'''
FRONTEND
streamlit run app.py
'''

import streamlit as st
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response

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

# --- TITLE ---
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

# --- PROCESSING ---
if submit_button:
    # Constructing the complex query
    query = f"""
    site:reelvendornetwork.com 
    Using the information from the Reel Vendor Network website (site:reelvendornetwork.com), 
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
            # Initialize chat with Google Search grounding
            response = generate_response(query)
            show_parts(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Fill out the wedding details in the sidebar and click 'Find My Vendors' to begin.")
