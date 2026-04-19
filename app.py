"""
app.py — Main entry point: layout, session state, and control flow.
All heavy logic lives in config, utils, prompts, components, and bot.
"""

import streamlit as st
from google import genai

from config import ICON_LINK, DEMO_MODE, load_css, load_vendor_data
from bot import generate_response, create_model
from utils import build_parts
from prompts import build_wedding_plan_prompt, build_vendor_search_prompt
from components import render_sidebar, render_initial_results, render_chat_history


# ── PAGE CONFIG & STYLING ─────────────────────────────────────────────────────

st.set_page_config(page_title="Reel Vendor Network", page_icon=ICON_LINK, layout="wide")
load_css("style.css")
st.title("Reel Vendor Assistant")


# ── AI CLIENT (cached) ────────────────────────────────────────────────────────

@st.cache_resource
def get_client():
    from bot import gemini_api_key
    return genai.Client(api_key=gemini_api_key, http_options={"api_version": "v1alpha"})


# ── SESSION STATE ──────────────────────────────────────────────────────────────

if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

if "response" not in st.session_state:
    st.session_state.response = None

if "target_link" not in st.session_state:
    st.session_state.target_link = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    client = get_client()
    st.session_state.chat_session = create_model(client)

MODEL_SESSION = st.session_state.chat_session


# ── DATA ───────────────────────────────────────────────────────────────────────

vendor_df = load_vendor_data()


# ── SIDEBAR ────────────────────────────────────────────────────────────────────

form = render_sidebar(vendor_df)


# ── QUERY HANDLING ─────────────────────────────────────────────────────────────

if form["submit_button"]:
    if not form["selected_category"] and not form["make_wedding"]:
        st.error(
            'Please select a vendor category, or select "Make Me a Wedding" before searching.'
        )
        st.stop()

    st.session_state.search_clicked = True
    st.session_state.messages = []  # reset chat for new vendor search

    selected_category = form["selected_category"]

    if form["make_wedding"]:
        selected_category = "vendor"  # label for the spinner
        st.session_state.target_link = "https://reelvendornetwork.com/"

        # Use search-only session (no url_context) to avoid the 20-URL prefetch limit
        MODEL_SESSION = create_model(get_client(), use_url_context=False)

        profile_text = build_wedding_plan_prompt(
            vendor_df=vendor_df,
            wedding_date=form["wedding_date"],
            location=form["location"],
            guest_range=form["guest_range"],
            style=form["style"],
            vibe_tags=form["vibe_tags"],
            budget=form["budget"],
            notes=form["notes"],
        )
    else:
        target_link = vendor_df[vendor_df["Category"] == selected_category]["URL"].values[0]
        st.session_state.target_link = target_link

        profile_text = build_vendor_search_prompt(
            selected_category=selected_category,
            target_link=target_link,
            wedding_date=form["wedding_date"],
            location=form["location"],
            guest_range=form["guest_range"],
            style=form["style"],
            vibe_tags=form["vibe_tags"],
            budget=form["budget"],
            notes=form["notes"],
        )

    # --- VENDOR RESULT ---
    try:
        with st.spinner(f"Searching {selected_category} options at Reel Vendor Network..."):
            st.session_state.response = generate_response(
                profile_text,
                MODEL_SESSION,
                images=form["model_images"],
                demo=DEMO_MODE,
            )
    except Exception as e:
        st.error(f"An error occurred: {e}")


# ── DISPLAY RESULTS & FOLLOW-UP CHAT ──────────────────────────────────────────

if st.session_state.search_clicked:
    st.markdown(
        f"See more {form['selected_category'] or 'vendor'}s at {st.session_state.target_link}"
    )

    render_initial_results(st.session_state.response, demo=DEMO_MODE)
    render_chat_history(st.session_state.messages)

    # --- CHAT INPUT ---
    prompt = st.chat_input("Say something")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        response = generate_response(prompt, MODEL_SESSION, demo=DEMO_MODE)
        text_sections = build_parts(response, demo=DEMO_MODE)
        full_response_text = "\n\n".join(text_sections)

        st.session_state.messages.append({"role": "ai", "content": full_response_text})

        with st.chat_message("ai", avatar=ICON_LINK):
            for section in text_sections:
                st.markdown(section)
        st.rerun()
