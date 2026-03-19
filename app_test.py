import streamlit as st
import pandas as pd # Added for CSV handling
from datetime import date
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response 

# --- TITLE ---
st.set_page_config(page_title="Reel Vendor Chatbot", layout="wide")
st.title("🎥 REEL VENDOR CHATBOT")

# --- DATA LOADING ---
@st.cache_data
def load_vendor_data():
    # Load the CSV. If it doesn't exist, provide a fallback
    try:
        df = pd.read_csv("links.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame({"Category": ["Venue"], "URL": ["https://reelvendornetwork.com/venues/"]})

vendor_df = load_vendor_data()

# Helper function to display results
def show_parts(response):
    if not response.candidates:
        st.warning("No response generated.")
        return
        
    parts = response.candidates[0].content.parts
    for part in parts:
        if part.text:
            st.markdown(part.text)

    metadata = response.candidates[0].grounding_metadata
    if metadata and metadata.search_entry_point:
        st.markdown("---")
        st.caption("Sources & Grounding:")
        st.markdown(metadata.search_entry_point.rendered_content, unsafe_allow_html=True)

# --- SIDEBAR FORM ---
with st.sidebar:
    st.header("💍 Wedding Details")
    with st.form("wedding_criteria"):
        st.subheader("Basics")
        wedding_date = st.date_input("Wedding Date", min_value=date.today())
        location = st.text_input("Location or Venue", placeholder="e.g. Newport, RI")
        
        guest_range = st.selectbox("Estimated Guest Count", ["0-50", "50-100", "100-150", "150+"])
        setting = st.selectbox("Setting", ["Indoor", "Outdoor", "Both"])

        st.subheader("Vendor Selection")
        
        # 1. DYNAMIC DROPDOWN: Populated from CSV categories
        # 2. LIMITATION: Using selectbox ensures only ONE vendor is picked
        selected_category = st.selectbox(
            "What type of vendor are you looking for?", 
            options=vendor_df["Category"].tolist()
        )

        st.subheader("Style & Vision")
        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage")
        vibe_tags = st.multiselect(
            "Overall Vibe",
            ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Boho", "Classic", "Edgy"]
        )

        st.subheader("Budget & Priorities")
        budget = st.text_input("Budget range for this vendor")
        
        notes = st.text_area("Special Requests / Deal Breakers")

        submit_button = st.form_submit_button("Find My Vendor")

# --- PROCESSING ---
if submit_button:
    # 3. LINK LOOKUP: Find the URL associated with the selection
    target_link = vendor_df[vendor_df["Category"] == selected_category]["URL"].values[0]

    # 4. INJECTING THE LINK: Updated query with your specific requirement
    query = f"""
    You are searching specifically for a {selected_category}.
    
    STEP 1: Use the link {target_link} to find the best {selected_category} vendors.
    STEP 2: Once you find names, search Google for more details on those specific vendors.

    USER WEDDING PROFILE:
    - Date: {wedding_date}
    - Location: {location}
    - Guest Size: {guest_range}
    - Style/Vibe: {style} ({', '.join(vibe_tags)})
    - Budget: {budget}
    - Notes: {notes}

    INSTRUCTIONS:
    1. Provide 3 reccomended vendors from {selected_category}s found at {target_link}.
    2. For each, include: **Vendor Name**, **Summary**, and a **'Why they fit'** section.
    3. Keep it concise. Use Markdown headers for readability.
    """

    try:
        with st.spinner(f"Searching {selected_category} options at Reel Vendor Network..."):
            response = generate_response(query)
            show_parts(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")