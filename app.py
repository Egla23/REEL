import streamlit as st
import pandas as pd # Added for CSV handling
from datetime import date
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response 

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- TITLE ---
# Icon from their website window icon
ICON_LINK = "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://reelvendornetwork.com&client=VFE&size=64&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2"
LOGO_LINK = "https://reelvendornetwork.com/wp-content/uploads/2024/09/Gradient-Logo2.png"

st.set_page_config(page_title="Reel Vendor Network", page_icon=ICON_LINK, layout="wide")
# Set style
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
st.title("Reel Vendor Assistant")

# st.image("https://reelvendornetwork.com/wp-content/uploads/2024/09/Gradient-Logo2.png",width=100)

# --- DATA LOADING ---
@st.cache_data
def load_vendor_data():
    # Load the CSV of vendor links as a dataframe. If it doesn't exist, provide a fallback
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

    # Grounding metadata (hidden for now)
    # metadata = response.candidates[0].grounding_metadata
    # if metadata and metadata.search_entry_point:
    #     st.markdown("---")
        # st.caption("Sources & Grounding:")
        # st.markdown(metadata.search_entry_point.rendered_content, unsafe_allow_html=True)

# --- SIDEBAR FORM ---
with st.sidebar:
    st.logo(LOGO_LINK)

    with st.form("wedding_criteria"):

        st.subheader("Vendor Selection")
    
        selected_category = st.selectbox(
            label="Select",
            options=vendor_df["Category"].tolist(),
            index=None, # Is a required selection
            placeholder="Select a Vendor",
            label_visibility="collapsed"
        )

        st.subheader("Basics")

        wedding_date = st.date_input("Wedding Date", min_value=date.today())
        location = st.text_input("Location or Venue", placeholder="e.g. Newport, RI",value="New England")
        guest_range = st.selectbox("Estimated Guest Count", ["N/A","0-50", "50-100", "100-150", "150+"])
        setting = st.selectbox("Setting", ["N/A","Indoor", "Outdoor", "Both"])

        st.subheader("Style & Vision")

        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage")
        vibe_tags = st.multiselect(
            "Overall Vibe",
            ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Classic", "Edgy"]
        )

        st.subheader("Budget & Priorities")

        budget = st.text_input("Budget range for this vendor")
        notes = st.text_area("Special Requests / Deal Breakers")
        submit_button = st.form_submit_button("Find My Vendor")

# QUERY  
if submit_button:
    # LINK LOOKUP: Find the URL associated with the selection
    target_link = vendor_df[vendor_df["Category"] == selected_category]["URL"].values[0]

    # INJECTING THE VALUES TO QUERY: Updated query with specific requirements
    query = f"""
    You are searching specifically for a {selected_category}.
    
    Quietly follow these steps without writing the output:
    STEP 1: Use the link {target_link} to find the best {selected_category} vendors.
    STEP 2: Once you find names, search Google for more details on those specific vendors.

    Use the following wedding profile, if applicable, for more context:

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
    4. Only provide links to the actual vendor's website, not on Reel vendor network's website.
    """
    print("\n",query)
    try:
        with st.spinner(f"Searching {selected_category} options at Reel Vendor Network..."):
            response = generate_response(query)
            print(f"See more {selected_category}s at {target_link}")
            show_parts(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")