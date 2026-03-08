import streamlit as st
from datetime import date
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response # Keeping your imports

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
        
        # 1. Date Limitation: Set min_value to today
        wedding_date = st.date_input("Wedding Date", min_value=date.today())
        
        location = st.text_input("Location or Venue", placeholder="e.g. Newport, RI")
        
        # 2. Guest Range Dropdown
        guest_range = st.selectbox("Estimated Guest Count", [
            "Micro (Under 20)", 
            "Small (20-75)", 
            "Medium (75-150)", 
            "Large (150-300)", 
            "Grand (300+)"
        ])
        
        setting = st.selectbox("Setting", ["Indoor", "Outdoor", "Both"])

        st.subheader("Vendor Needs")
        # 3. Expanded Vendor List
        vendor_options = [
            "Venue", "Video", "Photo", "DJ", "Band", "Florist", 
            "Planner", "Catering", "Hair/Makeup", "Transportation", 
            "Officiant", "Rentals", "Cake/Dessert"
        ]
        vendors_needed = st.multiselect("Vendors Needed", vendor_options)
        
        # 4. Number of Vendors (Refined)
        vendor_count_pref = st.select_slider(
            "Searching for:", 
            options=["Single Vendor", "Small Team", "Full Vendor Squad"]
        )

        st.subheader("Style & Vision")
        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage")
        
        # 5. More Effective Vibe Selection (Multiselect allows for nuance)
        vibe_tags = st.multiselect(
            "Overall Vibe (Select all that apply)",
            ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Boho", "Classic", "Edgy"]
        )

        st.subheader("Budget & Priorities")
        budget = st.text_input("Budget range per vendor")
        priority = st.text_input("Top priority vendors")

        # ... (rest of your existing fields)
        notes = st.text_area("Special Requests / Deal Breakers")

        submit_button = st.form_submit_button("Find My Vendors")

# --- PROCESSING ---
if submit_button:
    # 6. Formatting the Output (The "Anti-Essay" Prompt)
    query = f"""
    SEARCH SITE: reelvendornetwork.com 
    
    USER WEDDING PROFILE:
    - Date: {wedding_date}
    - Location: {location}
    - Guest Size: {guest_range}
    - Vendors Needed: {', '.join(vendors_needed)}
    - Style/Vibe: {style} ({', '.join(vibe_tags)})
    - Priorities: {priority} (Budget: {budget})
    - Notes: {notes}

    INSTRUCTIONS:
    1. Provide a Bulleted List of recommended vendors found on reelvendornetwork.com.
    2. For each vendor, include: **Vendor Name**, **Category**, and a **1-sentence 'Why they fit'**.
    3. DO NOT write a long introduction or a concluding essay. 
    4. If no specific match is found, list one 'Featured Vendor' from the site that most closely aligns with the {style} style.
    5. Use Markdown tables or bold headers for readability.
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
