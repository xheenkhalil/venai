import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from typing import Literal

from app.agents.state import AgentState

from app.core.config import settings

class Route(BaseModel):
    next_agent: Literal["research", "calling", "analysis", "report", "FINISH"]

def supervisor_node(state: AgentState):
    api_key = settings.GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=api_key)
    structured_llm = llm.with_structured_output(Route)
    
    system_prompt = (
        "You are the Supervisor Agent for VenAI, a procurement orchestration system. "
        "Your job is to manage the workflow of fulfilling a procurement request.\n"
        "You have the following agents at your disposal:\n"
        "- 'research': To gather information on vendors if we don't have enough data.\n"
        "- 'calling': To call vendors and get quotes if we have vendors but no pricing/availability yet.\n"
        "- 'analysis': To compare vendors once we have call results (quotes).\n"
        "- 'report': To generate a final recommendation report once analysis is complete.\n\n"
        "Review the current state of the request and route to the appropriate next agent. "
        "If the final report is completed, route to 'FINISH'."
    )
    
    state_summary = f"""
    Product: {state.get('product_name')}
    Budget: {state.get('budget')}
    Vendors Found: {len(state.get('vendors', []))}
    Call Results Gathered: {len(state.get('call_results', []))}
    Analysis Done: {bool(state.get('analysis_report'))}
    Final Report Done: {bool(state.get('final_report'))}
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Current State:\n{state_summary}\n\nWhat is the next step?")
    ]
    
    try:
        response = structured_llm.invoke(messages)
        return {"next_agent": response.next_agent}
    except Exception as e:
        print(f"Supervisor error: {e}")
        return {"next_agent": "FINISH", "final_report": f"Workflow failed at supervisor node due to error: {str(e)}"}
