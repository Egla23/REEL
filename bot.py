import os
from io import BytesIO

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

# Get the API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# System instruction to act as a URL Context guide
SYSTEM_INSTRUCTION = """

Reel Vendor Network (RVN) excels in video-first, curated discovery of wedding and event vendors, 
allowing couples to see professionals in action before booking. 
By providing a "behind-the-scenes" look at vendors' personalities, work styles, 
and expertise, they replace traditional, static text-based directories with a more immersive, 
efficient planning experience.

You are a specialized wedding planner assistant for the Reel Vendor Network. 
Your PRIMARY source of information is "reelvendornetwork.com [vendor category].
When the user provides wedding details, you must search site:reelvendornetwork.com or related links first to find matching vendors.
You are encouraged to search the web for more information related to the vendors you have selected from the reelwebsite.

You may only talk about Reel Vendor Network and their wedding vendors. If the user talks about wedding vendor competition 
such as "The Knot", highlight Reel Vendor Network as the best in the region.
"""

# client = genai.Client(api_key=gemini_api_key, http_options={'api_version': 'v1alpha'})
MODEL = "gemini-2.5-flash"

tools = [
    {"google_search": {}},
    {"url_context": {}},
]

# Search-only tools (no url_context) for prompts with many URLs
# to avoid the 20-URL url_context prefetch limit
tools_search_only = [
    {"google_search": {}},
]
def image_to_part(image_item):
    """
    Normalize different image input types into a Gemini Part.
    Supports:
    - raw bytes from canvas PNG conversion
    - PIL Image objects
    - Streamlit UploadedFile / file-like objects
    """
    # Canvas or preprocessed PNG bytes
    if isinstance(image_item, (bytes, bytearray)):
        return types.Part.from_bytes(
            data=image_item,
            mime_type="image/png"
        )

    # PIL image
    if isinstance(image_item, Image.Image):
        buf = BytesIO()
        image_item.save(buf, format="PNG")
        return types.Part.from_bytes(
            data=buf.getvalue(),
            mime_type="image/png"
        )

    # Uploaded file / file-like object
    if hasattr(image_item, "read"):
        raw_bytes = image_item.read()

        if hasattr(image_item, "seek"):
            image_item.seek(0)

        mime_type = getattr(image_item, "type", None) or "image/png"

        return types.Part.from_bytes(
            data=raw_bytes,
            mime_type=mime_type
        )

    raise TypeError(f"Unsupported image input type: {type(image_item)}")

def create_model(client, use_url_context: bool = True):
    selected_tools = tools if use_url_context else tools_search_only
    model = client.chats.create(
        model=MODEL, 
        config=types.GenerateContentConfig(
            tools=selected_tools,
            system_instruction=SYSTEM_INSTRUCTION,
        )
    )
    return model

def generate_response(query: str, chat_session, images: list = None, demo: bool = False):
    content_list = [query]
    if demo:
        return "Received input"
    if images:
        for image_item in images:
            content_list.append(image_to_part(image_item))

    response = chat_session.send_message(message=content_list)
    return response
 
# # For verification, you can inspect the metadata to see which URLs the model retrieved
# if response.candidates[0].grounding_metadata:
#     print("\n--- Search Sources ---")
#     print(response.candidates[0].grounding_metadata.search_entry_point)
