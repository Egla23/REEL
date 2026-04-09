import streamlit as st
import pandas as pd # Added for CSV handling
from datetime import date
from bot import SYSTEM_INSTRUCTION, MODEL, generate_response 
import re
import time

# Define session state variables so streamlit remembers chat history
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

if "response" not in st.session_state:
    st.session_state.response = None

if "target_link" not in st.session_state:
    st.session_state.target_link = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Icon from their website window icon
ICON_LINK: str = "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://reelvendornetwork.com&client=VFE&size=64&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2"
LOGO_LINK: str = "https://reelvendornetwork.com/wp-content/uploads/2024/09/Gradient-Logo2.png"

# If True, the Gemini bot isn't activated to not waste any credits.
DEMO_MODE: bool = False 

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
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

def build_parts(response) -> list:

    # For demo purposes to not waste API credits
    if DEMO_MODE: # or if response is str as generate response in demo mode returns str      
        return [response]
    
    if not response.candidates:
        return ['No response generated.']
        
    # Combine all parts into one string
    full_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])

    # Avoids latex formatting issues by ignoring '$' cmd
    full_text.replace('$', '\$')  

    # Split by header while keeping the header
    raw_sections = re.split(r'(?m)^(?=#)', full_text)
    return [s.strip() for s in raw_sections if s.strip()]

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

        style = st.text_input("Style/Theme", placeholder="e.g. Coastal, Vintage, Cultural")
        vibe_tags = st.multiselect(
            "Overall Vibe",
            ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Classic", "Edgy"]
        )
        
        # st.subheader("Inspiration Photos")

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

        st.subheader("Budget & Priorities")

        budget = st.text_input("Budget range for this vendor")
        notes = st.text_area("Special Requests / Deal Breakers")
        submit_button = st.form_submit_button("Find My Vendor")

# QUERY  
if submit_button:
    st.session_state.search_clicked = True
    st.session_state.messages = []   # reset chat for new vendor search

    # LINK LOOKUP: Find the URL associated with the selection
    target_link = vendor_df[vendor_df["Category"] == selected_category]["URL"].values[0]

    # INJECTING THE VALUES TO QUERY: Updated query with specific requirements
    profile_text = f"""
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
        1a. If there are less than 3 available vendors, only list those. Do not search the web for more.
    2. Filter results from the Reel link to only include vendors relevant to the specified location. 
        2a. If no matches exist, state: "I could not find any Reel vendors serving {location}." 
        and list the available locations for the vendors on that page.
    3. For each, include: **Vendor Name**, **Summary**, and a **'Why they fit'** section.
    4. Keep it concise. Use Markdown headers for each vendor.
    5. Only provide links to the actual vendor's website, not on Reel vendor network's website.
    6. Use markdown text only. You may use math to rationalize a budget but do not use Latex or code snippets.
    """
    print("\n",profile_text)

    try:
        # can try st.status to recieve updates from gemin
        # and then             st.write(f"Analyzing {selected_category} based on your needs")
        with st.spinner(f"Searching {selected_category} options at Reel Vendor Network..."):
            response = generate_response(profile_text,images=uploaded_pictures,demo=DEMO_MODE) # TODO
            st.session_state.response = response
            st.session_state.target_link = target_link
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- show saved result after reruns ---
if st.session_state.search_clicked:
    st.markdown(f"See more {selected_category}s at {st.session_state.target_link}")

    # Vendor result
    text_sections = build_parts(st.session_state.response)
    for section in text_sections:
        with st.chat_message("ai", avatar=ICON_LINK):
            st.markdown(section)

    # show previous follow-up chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=ICON_LINK if message["role"] == "ai" else None):
            st.markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input("Say something")

    if prompt:
        # Save and show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate bot response
        response = generate_response(prompt, demo=DEMO_MODE)

        # Save and show bot response
        st.session_state.messages.append({"role": "ai", "content": response})
        with st.chat_message("ai", avatar=ICON_LINK):
            text_sections = build_parts(response)
            for section in text_sections:
                st.markdown(section)
