import streamlit as st
import asyncio

async def main():
    st.set_page_config(page_title="REEL Vendor", layout="wide")
    st.title("🎬 REEL Vendor")

    # --- session state ---
    if "selection" not in st.session_state:
        st.session_state.selection = None

    left, right = st.columns([1, 1.4], gap="large")

    # ---------------------------
    # LEFT: Forum
    # ---------------------------
    with left:
        st.subheader("Forum")

        with st.container(border=True):
            vendor_type = st.selectbox(
                "1) What vendor are you looking for?",
                ["Catering", "Photography", "Videography", "DJ", "Florist", "Venue", "Hair & Makeup", "Planner", "Other"],
                index=0
            )

            guest_count = st.number_input(
                "2) How many guests?",
                min_value=1,
                value=100,
                step=5
            )

            st.markdown("### Preferences (3 checkboxes)")
            cb_value = st.checkbox("3) Budget-friendly / best value")
            cb_quality = st.checkbox("4) High quality / premium")
            cb_fast = st.checkbox("5) Fast availability")

            run = st.button("▶ Run", type="primary", use_container_width=True)

            if run:
                st.session_state.selection = {
                    "vendor_type": vendor_type,
                    "guest_count": guest_count,
                    "pref_value": cb_value,
                    "pref_quality": cb_quality,
                    "pref_fast": cb_fast,
                }

    # ---------------------------
    # RIGHT: Results (updates after Run)
    # ---------------------------
    with right:
        st.subheader("Results")

        if st.session_state.selection:
            s = st.session_state.selection

            st.markdown("### Your Selection")
            st.markdown(f"**Vendor:** {s['vendor_type']}")
            st.markdown(f"**Guest count:** {s['guest_count']}")

            st.markdown("### Preferences")
            prefs = []
            if s["pref_value"]:
                prefs.append("Budget-friendly / best value")
            if s["pref_quality"]:
                prefs.append("High quality / premium")
            if s["pref_fast"]:
                prefs.append("Fast availability")

            if prefs:
                for p in prefs:
                    st.write(f"✅ {p}")
            else:
                st.write("None selected")

        else:
            st.info("Pick options on the left and click **Run**.")

if __name__ == "__main__":
    asyncio.run(main())