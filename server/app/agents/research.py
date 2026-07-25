import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState

from app.core.config import settings

def research_node(state: AgentState):
    api_key = settings.GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
    
    # In a fully realized system, this agent would use tools to search the web.
    # Since we already ran the Tavily search in Phase 4 and populated the DB/State,
    # this agent can just validate or format the vendor data.
    
    prompt = f"""
    You are the Research Agent. We have discovered the following vendors for the product: {state.get('product_name')}.
    Vendors: {state.get('vendors')}
    
    Please provide a brief summary of our research findings.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [SystemMessage(content=f"Research Agent completed: {response.content}")]}
    except Exception as e:
        print(f"Research error: {e}")
        return {"messages": [SystemMessage(content=f"Research Agent encountered an error: {str(e)}")]}
