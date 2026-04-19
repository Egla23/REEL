"""
prompts.py — Prompt templates for vendor search and full wedding planning.
"""

import pandas as pd


def build_wedding_plan_prompt(
    vendor_df: pd.DataFrame,
    wedding_date,
    location: str,
    guest_range: str,
    style: str,
    vibe_tags: list[str],
    budget: str,
    notes: str,
) -> str:
    """Build the 'Make Me a Wedding' prompt using all vendor links."""
    target_links = ", ".join(vendor_df["URL"].astype(str))

    return f"""\
You are a wedding planner.

Create a full wedding plan using Reel Vendor Network vendors.
with the following links {target_links}

STEP 1: Use the links to find the best vendors.
STEP 2: Once you find names, search Google for more details on those specific vendors.

USER WEDDING PROFILE:
- Date: {wedding_date}
- Location: {location}
- Guest Size: {guest_range}
- Style/Vibe: {style} ({', '.join(vibe_tags)})
- Budget: {budget}
- Notes: {notes}

INSTRUCTIONS:
1. Recommend one vendor per multiple relevant categories based on user requirments \
(venue, catering, photography, DJ, etc.) with a maximum of 5 vendors total, one per each category.
2. Filter results from the Reel link to only include vendors relevant to the specified location. \
    2a. If no matches exist, state: "I could not find any Reel vendors serving {location}." \
    and list the available locations for the vendors on that page.
3. For each, include: **Vendor Name**, **Summary**, and a **'Why they fit'** section.
4. Keep it concise. Use Markdown headers for each vendor.
5. Only provide links to the actual vendor's website, not on Reel vendor network's website.
6. Use markdown text only. You may use math to rationalize a budget but do not use Latex or code snippets.
7. If the user adds any image or sketch input, make sure to acknowledge, and comment positivley.
"""


def build_vendor_search_prompt(
    selected_category: str,
    target_link: str,
    wedding_date,
    location: str,
    guest_range: str,
    style: str,
    vibe_tags: list[str],
    budget: str,
    notes: str,
) -> str:
    """Build the single-category vendor search prompt."""
    return f"""\
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
1. Provide 3 reccomended vendors from {selected_category}s found at {target_link}. \
    1a. If there are less than 3 available vendors, only list those. Do not search the web for more.
2. Filter results from the Reel link to only include vendors relevant to the specified location. \
    2a. If no matches exist, state: "I could not find any Reel vendors serving {location}." \
    and list the available locations for the vendors on that page.
3. For each, include: **Vendor Name**, **Summary**, and a **'Why they fit'** section.
4. Keep it concise. Use Markdown headers for each vendor.
5. Only provide links to the actual vendor's website, not on Reel vendor network's website.
6. Use markdown text only. You may use math to rationalize a budget but do not use Latex or code snippets.
7. If the user adds any image or sketch input, make sure to acknowledge, and comment positivley.
"""
