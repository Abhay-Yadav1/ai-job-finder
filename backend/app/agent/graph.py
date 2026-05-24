from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    parse_resume_node,
    build_query_node,
    web_search_node,
    parse_results_node
)

def create_agent_graph():
    # 1. Initialize the StateGraph with our specific TypedDict
    workflow = StateGraph(AgentState)
    
    # 2. Add our specific nodes
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("build_query", build_query_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("parse_results", parse_results_node)
    
    # 3. Connect the nodes in a straight line (Linear flow)
    workflow.set_entry_point("parse_resume")
    workflow.add_edge("parse_resume", "build_query")
    workflow.add_edge("build_query", "web_search")
    workflow.add_edge("web_search", "parse_results")
    workflow.add_edge("parse_results", END)
    
    # 4. Compile the graph into an executable application
    return workflow.compile()

# We instantiate it here so we can import 'agent_app' directly into our FastAPI routes later
agent_app = create_agent_graph()