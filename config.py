"""
config.py — App-wide constants, CSS loader, and data loading.
"""

import streamlit as st
import pandas as pd

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

# Icon from their website window icon
ICON_LINK: str = (
    "https://encrypted-tbn2.gstatic.com/faviconV2?"
    "url=https://reelvendornetwork.com"
    "&client=VFE&size=64&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2"
)

LOGO_LINK: str = (
    "https://reelvendornetwork.com/wp-content/uploads/2024/09/Gradient-Logo2.png"
)

# If True, the Gemini bot isn't activated to not waste any credits.
DEMO_MODE: bool = False


# ── CSS LOADER ─────────────────────────────────────────────────────────────────

def load_css(file_name: str = "style.css") -> None:
    """Inject a local CSS file into the Streamlit app."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── DATA LOADING ───────────────────────────────────────────────────────────────

@st.cache_data
def load_vendor_data(csv_path: str = "links.csv") -> pd.DataFrame:
    """Load the CSV of vendor links as a DataFrame. Falls back to a single Venue row."""
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame(
            {"Category": ["Venue"], "URL": ["https://reelvendornetwork.com/venues/"]}
        )
