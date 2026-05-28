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
  

    
    

def web_search_node(state: AgentState) -> dict:
    """Executes the search using Tavily API."""
    query = state["search_query"]
    # FIX: Reduced max_results from 10 to 5 to prevent LLM overload
    response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
    return {"raw_search_results": response["results"]}
    

def build_query_node(state: AgentState) -> dict:
    """Builds a highly optimized search query for Tavily."""
    user_query = state.get("user_query", "")
    parsed_profile = state.get("parsed_profile", {})
    filters = state.get("filters", {})
    
    # FIX: Force the LLM to search for "jobs" and stop it from using too many skills
    prompt = f"""You are an expert recruiter. Create a concise search query to find active job listings on search engines.
    Candidate Profile: {parsed_profile}
    User Query: {user_query}
    Active Filters: {filters}
    
    CRITICAL RULES:
    1. Return ONLY the raw search query string. No quotes, no explanations.
    2. You MUST include the word "jobs" or "hiring" (e.g., "AI Engineer remote jobs").
    3. If relying on the Candidate Profile, pick ONLY the top preferred role. DO NOT list all their skills in the query.
    4. Keep the query under 80 characters.
    """
    response = llm.invoke([SystemMessage(content=prompt)])
    
    raw_query = response.content.strip().strip('"').strip("'")
    safe_query = raw_query[:100]
    
    # Print it to the backend terminal so you can see what it's searching!
    print(f"\n[DEBUG] Search Query Built: {safe_query}\n")
    
    return {"search_query": safe_query}
    

def parse_results_node(state: AgentState) -> dict:
    """Cleans up messy search results into uniform Job Cards."""
    raw_results = str(state["raw_search_results"])
    structured_llm = llm.with_structured_output(JobResults)
    
    # FIX: Force the LLM to extract MULTIPLE items and prevent summarization
    prompt = """You are a precise data extraction assistant. I am giving you raw search results from the web.
    
    CRITICAL RULES:
    1. DO NOT summarize the results into a single generic job.
    2. You MUST extract EACH individual job posting you find into a SEPARATE job card in the list.
    3. Extract at least 3 to 5 distinct jobs if they exist in the text.
    4. Use the exact company name from the text. Never use words like "Various" or "Multiple".
    5. If the salary is missing, explicitly write "Not Disclosed".
    """
    
    result = structured_llm.invoke([
        SystemMessage(content=prompt), 
        HumanMessage(content=raw_results)
    ])
    
    return {"final_jobs": result.model_dump()["jobs"]}