from typing import TypedDict, List, Optional, Dict, Any
class AgentState(TypedDict):
    raw_resume_text: Optional[str]
    user_query: Optional[str]
    parsed_profile: Optional[Dict[str, Any]]
    search_query: str
    raw_search_results: List[Dict[str, Any]]
    filters: Dict[str, Any]
    # The final output
    final_jobs: List[Dict[str, Any]]

    