import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState

from app.core.config import settings

def analysis_node(state: AgentState):
    api_key = settings.GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=api_key)
    
    prompt = f"""
    You are the Analysis Agent. Compare the following vendors and their quotes based on the product requirements.
    
    Product: {state.get('product_name')}
    Budget: {state.get('budget')}
    Requirements: {state.get('requirements')}
    
    Call Results (Quotes):
    {state.get('call_results')}
    
    Provide a detailed comparison and score them.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "analysis_report": response.content,
            "messages": [SystemMessage(content="Analysis Agent completed its comparison.")]
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        return {
            "analysis_report": f"Analysis failed due to error: {str(e)}",
            "messages": [SystemMessage(content=f"Analysis Agent encountered an error: {str(e)}")]
        }
