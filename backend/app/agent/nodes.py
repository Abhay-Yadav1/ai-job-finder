import os
from langchain_core.messages import SystemMessage, HumanMessage # type: ignore
from tavily import TavilyClient # type: ignore
from langchain_groq import ChatGroq # type: ignore
from .state import AgentState
from .models import ExtractedProfile, JobResults
from dotenv import load_dotenv # type: ignore

# Load environment variables (TAVILY_API_KEY, GROQ_API_KEY)
load_dotenv()

# Initialize your AI and Search clients
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0 # Keep temperature at 0 for strict formatting
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) 

def parse_resume_node(state: AgentState) -> dict:
    """Extracts structured data from the raw resume text."""
    if not state.get("raw_resume_text"):
        return {"parsed_profile": None}
    
    structured_llm = llm.with_structured_output(ExtractedProfile)
    prompt = "Extract the candidate's skills, experience level, and preferred job roles from the following resume text."
    
    result = structured_llm.invoke([
        SystemMessage(content=prompt), 
        HumanMessage(content=state["raw_resume_text"])
    ])
    return {"parsed_profile": result.model_dump()}
  

def build_query_node(state: AgentState) -> dict:
    """Builds a highly optimized search query for Tavily."""
    user_query = state.get("user_query", "")
    parsed_profile = state.get("parsed_profile", {})
    filters = state.get("filters", {}) # FIX 1: Extracted the filters from state
    
    # FIX 2: Added strict instructions to prevent conversational text
    prompt = f"""You are a job search assistant. Based on the following data, create a concise search query optimized for a job search engine. 
    Candidate Profile: {parsed_profile}
    User Query: {user_query}
    Active Filters: {filters}
    
    IMPORTANT: Return ONLY the raw search query string. Do not include quotes, explanations, or any conversational preamble.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"search_query": response.content.strip()}
    

def web_search_node(state: AgentState) -> dict:
    """Executes the search using Tavily API."""
    query = state["search_query"]
    response = tavily_client.search(query=query, search_depth="advanced", max_results=10)
    return {"raw_search_results": response["results"]}
    

def parse_results_node(state: AgentState) -> dict:
    """Cleans up messy search results into uniform Job Cards."""
    raw_results = str(state["raw_search_results"])
    structured_llm = llm.with_structured_output(JobResults)
    
    # FIX 3: Removed hardcoded field names. We let Pydantic handle the schema enforcement.
    prompt = """You are a data extraction assistant. Convert the following raw search results into the required structured job card format.
    IMPORTANT: Output ONLY pure, valid JSON. Do not include any <function> tags, markdown, or conversational text."""
    
    result = structured_llm.invoke([
        SystemMessage(content=prompt), 
        HumanMessage(content=raw_results)
    ])
    return {"final_jobs": result.model_dump()["jobs"]}