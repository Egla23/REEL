### --------------
from google import genai
from google.genai.types import Tool, GenerateContentConfig
from google.genai import types
import os
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
You are a specialized wedding planner assistant for the Reel Vendor Network. 
Your PRIMARY source of information is "site:reelvendornetwork.com [vendor category].
When the user provides wedding details, you must search site:reelvendornetwork.com or related links first to find matching vendors.
You are encouraged to search the web for more information related to the vendors you have selected from the reelwebsite.
"""

# Initialize the client
client = genai.Client(api_key=gemini_api_key, http_options={'api_version': 'v1alpha'})
MODEL = "gemini-2.5-flash"

tools = [
    {"google_search": {}},
    {"url_context": {}},
]

chat = client.chats.create(
    model=MODEL, 
    config=types.GenerateContentConfig(
        tools=tools,
        system_instruction=SYSTEM_INSTRUCTION,
    )
)

def generate_response(query: str, images: list = None, demo: bool = False):

    # Start with the text query
    content_list = [query]

    if demo == False:
        if images:
            for uploaded_file in images:
                # Open the Byte stream as a PIL Image object
                img = Image.open(uploaded_file)
                content_list.append(img)

        # Send the list (contains 1 string and N images)
        response = chat.send_message(message=content_list)
        return response
    else:
        return "Received input"
 
# # For verification, you can inspect the metadata to see which URLs the model retrieved
# if response.candidates[0].grounding_metadata:
#     print("\n--- Search Sources ---")
#     print(response.candidates[0].grounding_metadata.search_entry_point)
