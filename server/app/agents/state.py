from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    request_id: str
    organization_id: str
    product_name: str
    requirements: str
    location: str
    budget: str
    
    vendors: List[Dict[str, Any]] # Vendors to evaluate
    call_results: List[Dict[str, Any]] # Results from calling agent
    analysis_report: str # Output from analysis agent
    final_report: str # Output from report agent
    
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str # Used by supervisor to route
