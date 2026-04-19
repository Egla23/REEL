"""
components.py — Reusable Streamlit UI elements (sidebar form, chat display).
"""

import streamlit as st
import streamlit_antd_components as sac
from datetime import date
from streamlit_drawable_canvas import st_canvas

from config import ICON_LINK, LOGO_LINK
from utils import convert_canvas, uploaded_file_png, format_conversation


# ── SIDEBAR FORM ──────────────────────────────────────────────────────────────

def render_sidebar(vendor_df):
    """
    Render the full sidebar form.
    Returns a dict with all collected form values plus submit status.
    """
    with st.sidebar:
        st.image(LOGO_LINK)

        # "Make Me a Wedding" toggle
        make_wedding = sac.switch(
            label="Make Me a Wedding",
            size="lg",
            on_color="#da9982",
            align="center",
        )
        if make_wedding:
            st.info(
                "We'll plan your wedding for you based on your form! "
                "No need to select a vendor."
            )

        with st.form("wedding_criteria"):
            st.subheader("Vendor Selection")

            selected_category = st.selectbox(
                label="Select",
                options=vendor_df["Category"].tolist(),
                index=None,
                placeholder="Select a Vendor",
                label_visibility="collapsed",
                disabled=make_wedding,
            )

            st.subheader("Basics")

            wedding_date = st.date_input("Wedding Date", min_value=date.today())
            location = st.text_input(
                "Location or Venue", placeholder="e.g. Newport, RI", value="New England"
            )
            guest_range = st.selectbox(
                "Estimated Guest Count",
                ["N/A", "0-50", "50-100", "100-150", "150+"],
            )
            setting = st.selectbox("Setting", ["N/A", "Indoor", "Outdoor", "Both"])

            st.subheader("Style & Vision")

            style = st.text_input(
                "Style/Theme", placeholder="e.g. Coastal, Vintage, Cultural"
            )
            vibe_tags = st.multiselect(
                "Overall Vibe",
                ["Modern", "Romantic", "Cinematic", "Fun", "Luxury", "Classic", "Edgy"],
            )

            uploaded_files = st.file_uploader(
                "Inspiration Photos",
                type=["png", "jpg", "jpeg", "webp"],
                accept_multiple_files=True,
                help="Upload wedding inspiration photos to help guide the vendor search.",
            )

            preview_images = []
            model_images = []

            if uploaded_files:
                for uploaded_file in uploaded_files:
                    preview_images.append(uploaded_file)
                    model_images.append(uploaded_file_png(uploaded_file))

            st.write("Or sketch an idea:")
            canvas_result = st_canvas(
                stroke_width=3,
                stroke_color="#000000",
                background_color="#EEEEEE",
                height=250,
                width=250,
                drawing_mode="freedraw",
                key="canvas",
            )

            if (
                canvas_result.json_data is not None
                and len(canvas_result.json_data.get("objects", [])) > 0
            ):
                canvas_png_bytes = convert_canvas(canvas_result)
                if canvas_png_bytes is not None:
                    preview_images.append(canvas_png_bytes)
                    model_images.append(canvas_png_bytes)

            if preview_images:
                st.write("Preview:")
                for img in preview_images:
                    st.image(img, caption=None, use_container_width=True)

            st.subheader("Budget & Priorities")

            budget = st.text_input("Budget range for this vendor")
            notes = st.text_area("Special Requests / Deal Breakers")

            submit_button = st.form_submit_button("Find My Vendor")

            # Download button (inside sidebar, outside form would need rework)
            if st.session_state.search_clicked:
                chat_log = format_conversation(
                    st.session_state.response, st.session_state.messages
                )
                st.sidebar.download_button(
                    label="💾 Save Conversation",
                    data=chat_log,
                    file_name=f"wedding_vendors_{selected_category}_{date.today()}.md",
                    mime="text/markdown",
                )

    return {
        "submit_button": submit_button,
        "make_wedding": make_wedding,
        "selected_category": selected_category,
        "wedding_date": wedding_date,
        "location": location,
        "guest_range": guest_range,
        "setting": setting,
        "style": style,
        "vibe_tags": vibe_tags,
        "budget": budget,
        "notes": notes,
        "model_images": model_images,
    }


# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────

def render_initial_results(response, demo: bool = False):
    """Display the initial vendor search results as chat messages."""
    from utils import build_parts

    text_sections = build_parts(response, demo=demo)
    for section in text_sections:
        with st.chat_message("ai", avatar=ICON_LINK):
            st.markdown(section)


def render_chat_history(messages):
    """Replay previous follow-up chat messages."""
    for message in messages:
        avatar = ICON_LINK if message["role"] == "ai" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
