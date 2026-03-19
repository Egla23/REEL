### --------------
from google import genai
from google.genai.types import Tool, GenerateContentConfig

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Get the API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# System instruction to act as a URL Context guide
SYSTEM_INSTRUCTION = """
You are a specialized wedding planner assistant for the Reel Vendor Network. 
Your PRIMARY source of information is site:reelvendornetwork.com.
When the user provides wedding details, you must search site:reelvendornetwork.com first to find matching vendors.
"""

# Initialize the client
client = genai.Client(api_key=gemini_api_key, http_options={'api_version': 'v1alpha'})
client = genai.Client()
model_id = "gemini-3-flash-preview"

tools = [
    {"google_search": {}},
    {"url_context": {}},
]

url1 = "https://reelvendornetwork.com/"
# url2 = "https://reelvendornetwork.com/djs/"

response = client.models.generate_content(
    model=model_id,
    contents=f"Find 3 best florists from {url1}",
    config=GenerateContentConfig(
        tools=tools,
        system_instruction=SYSTEM_INSTRUCTION,
    )
)

for part in response.candidates[0].content.parts:
    if part.text:
        print(part.text)

# For verification, you can inspect the metadata to see which URLs the model retrieved
if response.candidates[0].grounding_metadata:
    print("\n--- Search Sources ---")
    print(response.candidates[0].grounding_metadata.search_entry_point)
### ----