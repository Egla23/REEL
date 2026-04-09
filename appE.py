import streamlit as st
import pandas as pd # Added for CSV handling
from datetime import date
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response 
import re
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np

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

def build_parts(response) -> list:
    if not response.candidates:
        return ['No response generated.']
        
    # Combine all parts into one string
    full_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])

    # Avoids latex formatting issues by ignoring '$' cmd
    full_text.replace('$', '\$')  

    # Split by header while keeping the header
    raw_sections = re.split(r'(?m)^(?=#)', full_text)
    return [s.strip() for s in raw_sections if s.strip()]

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

        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage, Cultural")
        vibe_tags = st.multiselect(
            "Overall Vibe",
            ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Classic", "Edgy"]
        )
        
        uploaded_pictures = st.file_uploader(
            "Inspiration Photos",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            help="Upload wedding inspiration photos to help guide the vendor search."
        )

        if uploaded_pictures:
            st.write("Preview:")
            for img in uploaded_pictures:
                st.image(img, caption=img.name, use_container_width=True)

        # --- CANVAS INTEGRATION ---
        st.write("Or sketch an idea:")
        canvas_result = st_canvas(
            stroke_width=3,
            stroke_color="#000000",
            background_color="#EEEEEE",
            height=250, # Scaled down for the sidebar
            width=250,  # Scaled down for the sidebar
            drawing_mode="freedraw",
            key="canvas"
        )
        # --------------------------

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
        If there are less than 3 available vendors, only list those. Do not search the web for more.
    2. For each, include: **Vendor Name**, **Summary**, and a **'Why they fit'** section.
    3. Keep it concise. Use Markdown headers for readability.
    4. Only provide links to the actual vendor's website, not on Reel vendor network's website.
    5. Use markdown text only. You may use math to rationalize a budget but do not use Latex or code snippets.
    """
    print("\n",query)

    # --- IMAGE PROCESSING COMBINATION ---
    all_visuals = []
    
    # Add uploaded files
    if uploaded_pictures:
        all_visuals.extend(uploaded_pictures)
        
    # Add canvas drawing DIRECTLY as a PIL Image
    if canvas_result.json_data is not None and len(canvas_result.json_data.get("objects", [])) > 0:
        img_array = canvas_result.image_data
        pil_image = Image.fromarray(img_array.astype('uint8'), 'RGBA').convert('RGB')
        
        # Just append the raw image! Your bot.py will now handle it perfectly.
        all_visuals.append(pil_image)
    # -----------------------------------

    try:
        with st.spinner(f"Searching {selected_category} options at Reel Vendor Network..."):
            
            # Pass the combined 'all_visuals' list to the bot
            response = generate_response(query, all_visuals)
            
            st.markdown(f"See more {selected_category}s at {target_link}")

            text_sections = build_parts(response) # builds part so headers are split into list.

            for section in text_sections:
                with st.chat_message("ai", avatar=ICON_LINK): # Gives message a chat bubble
                    st.markdown(section)
                
    except Exception as e:
        st.error(f"An error occurred: {e}")