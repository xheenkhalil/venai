import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState

from app.core.config import settings

def report_node(state: AgentState):
    api_key = settings.GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
    
    import urllib.parse
    
    # Pre-generate fallback markdown links
    fallback_links = ""
    for cr in state.get("call_results", []):
        if not cr.get("available", True) and (cr.get("fallback_whatsapp") or cr.get("fallback_email_body")):
            vendor_name = cr.get("company_name")
            wa_text = urllib.parse.quote(cr.get("fallback_whatsapp", ""))
            email_sub = urllib.parse.quote(cr.get("fallback_email_subject", ""))
            email_body = urllib.parse.quote(cr.get("fallback_email_body", ""))
            
            wa_number = cr.get("vendor_whatsapp") or ""
            wa_number = "".join(filter(str.isdigit, wa_number)) # Clean to digits
            email_address = cr.get("vendor_email") or ""
            
            wa_link = f"https://wa.me/{wa_number}?text={wa_text}"
            email_link = f"mailto:{email_address}?subject={email_sub}&body={email_body}"
            
            fallback_links += f"\n### Fallback Options for {vendor_name}\n"
            if wa_number:
                fallback_links += f"- [Send WhatsApp Message to {vendor_name}]({wa_link})\n"
            if email_address:
                fallback_links += f"- [Send Email to {vendor_name}]({email_link})\n"

    prompt = f"""
    You are the Report Agent. Based on the analysis, write a final executive summary and procurement recommendation.
    
    Analysis Report:
    {state.get('analysis_report')}
    
    If there are fallback links provided below for vendors we couldn't reach, you MUST include a "Communication Fallbacks" section at the very end of your report and print these markdown links exactly as provided:
    {fallback_links}
    
    Format the entire output as a professional markdown document.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "final_report": response.content,
            "messages": [SystemMessage(content="Report Agent generated the final recommendation.")]
        }
    except Exception as e:
        print(f"Report error: {e}")
        return {
            "final_report": f"Report generation failed due to error: {str(e)}",
            "messages": [SystemMessage(content=f"Report Agent encountered an error: {str(e)}")]
        }
