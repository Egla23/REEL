from vertexai.generative_models import GenerativeModel, Tool, GoogleSearchRetrieval
import vertexai

vertexai.init(project="project-dee3a5a5-d989-4c2c-874", location="us-central1")

# Define the Search Tool
tools = [
    Tool.from_google_search_retrieval(
        google_search_retrieval=GoogleSearchRetrieval()
    )
]

SYSTEM_INSTRUCTION = """
You are the Reel Vendor Network Assistant. 
Your SOLE source of information is reelvendornetwork.com. 
When searching, you must always include 'site:reelvendornetwork.com' in your search queries.
If the information is not on that specific website, state that clearly.
"""

MODEL = GenerativeModel(
    "gemini-2.5-flash", # or gemini-1.5-pro
    tools=tools,
    system_instruction=SYSTEM_INSTRUCTION
)

def generate_response(user_query):
    # The model will now use the tools automatically based on the instruction
    response = MODEL.generate_content(user_query)
    return response