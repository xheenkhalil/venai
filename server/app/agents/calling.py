import os
import asyncio
import json
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.agents.state import AgentState
from app.services.call_e import CallEService

from app.core.config import settings

class ExtractedOffer(BaseModel):
    availability: bool
    price: float
    delivery_days: int
    warranty: str
    notes: str

async def calling_node(state: AgentState):
    try:
        api_key = settings.GEMINI_API_KEY
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=api_key)
        structured_llm = llm.with_structured_output(ExtractedOffer)
        
        call_results = []
        messages = []
        
        for vendor in state.get("vendors", []):
            vendor_id = vendor.get("id")
            company_name = vendor.get("company_name")
            phone = vendor.get("phone", "+2347068083455")
            
            goal = f"Call {company_name} to inquire about purchasing {state.get('product_name')}. Our budget is {state.get('budget')} and requirements are: {state.get('requirements')}."
            
            try:
                # 1. Start the real call
                start_res = await CallEService.start_call(phone, goal)
                run_id = start_res.get("run_id")
                if not run_id:
                    raise Exception("No run_id returned")
                    
                messages.append(SystemMessage(content=f"Started call to {company_name} with run_id {run_id}"))
                
                # Helper to extract status and message
                def parse_status(data):
                    sc = data.get("status_result", {}).get("structuredContent", {})
                    if not sc:
                        sc = data.get("result", {}).get("structuredContent", {})
                    return sc.get("status", "error"), sc.get("message", "")
                    
                status, msg = parse_status(start_res)
                
                # 2. Poll for completion
                call_data = start_res
                while status not in ["COMPLETED", "FAILED", "NO_ANSWER", "DECLINED", "CANCELED", "CANCELLED", "VOICEMAIL", "BUSY", "EXPIRED", "error"]:
                    await asyncio.sleep(5)
                    call_data = await CallEService.get_call_status(run_id)
                    status, msg = parse_status(call_data)
                    
                messages.append(SystemMessage(content=f"Call to {company_name} finished with status {status}"))
                
                # 3. Handle gracefully
                if status == "COMPLETED":
                    raw_text = json.dumps(call_data)
                    extract_prompt = f"Extract the vendor offer from this call data:\n{raw_text}"
                    offer: ExtractedOffer = structured_llm.invoke(extract_prompt)
                    
                    call_results.append({
                        "vendor_id": vendor_id,
                        "company_name": company_name,
                        "available": offer.availability,
                        "price_quote": offer.price,
                        "delivery_time": f"{offer.delivery_days} days",
                        "notes": offer.notes,
                        "run_id": run_id
                    })
                else:
                    notes = f"Call failed with status {status}."
                    if "Region is not allowed" in msg:
                        notes = "Call Failed\n\nReason:\nDestination country is not currently supported by CALL-E.\n\nRecommendation:\nUse a supported phone number or contact the vendor through an alternative communication channel."
                    elif msg:
                        notes += f" Message: {msg}"
                        
                    # Draft Fallback Messages
                    draft_prompt = f"""
                    You are VenAI, a procurement assistant.
                    The automated phone call to {company_name} failed.
                    Draft a professional WhatsApp message and a professional Email inquiring about:
                    Product: {state.get('product_name')}
                    Requirements: {state.get('requirements')}
                    Budget: {state.get('budget')}
                    
                    Keep them very concise, polite, and directly ask for pricing and availability.
                    
                    Respond in exactly this JSON format:
                    {{"whatsapp": "message text", "email_subject": "subject", "email_body": "body"}}
                    """
                    
                    fallback_data = {"whatsapp": "", "email_subject": "", "email_body": ""}
                    try:
                        class FallbackDraft(BaseModel):
                            whatsapp: str
                            email_subject: str
                            email_body: str
                        
                        fallback_llm = llm.with_structured_output(FallbackDraft)
                        fallback_res = fallback_llm.invoke(draft_prompt)
                        fallback_data = {
                            "whatsapp": fallback_res.whatsapp,
                            "email_subject": fallback_res.email_subject,
                            "email_body": fallback_res.email_body
                        }
                    except Exception as e:
                        print(f"Fallback generation error: {e}")
                        
                    call_results.append({
                        "vendor_id": vendor_id,
                        "company_name": company_name,
                        "available": False,
                        "price_quote": 0,
                        "delivery_time": "N/A",
                        "notes": notes,
                        "run_id": run_id,
                        "fallback_whatsapp": fallback_data["whatsapp"],
                        "fallback_email_subject": fallback_data["email_subject"],
                        "fallback_email_body": fallback_data["email_body"],
                        "vendor_phone": vendor.get("phone", ""),
                        "vendor_whatsapp": vendor.get("whatsapp", "") or vendor.get("phone", ""),
                        "vendor_email": vendor.get("email", "")
                    })
                    
            except Exception as e:
                messages.append(SystemMessage(content=f"Error calling {company_name}: {str(e)}"))
                call_results.append({
                    "vendor_id": vendor_id,
                    "company_name": company_name,
                    "available": False,
                    "price_quote": 0,
                    "delivery_time": "N/A",
                    "notes": f"Error: {str(e)}"
                })
                
        return {
            "call_results": call_results,
            "messages": messages
        }
    except Exception as e:
        print(f"Calling node master error: {e}")
        return {
            "call_results": state.get("call_results", []),
            "messages": [SystemMessage(content=f"Calling node failed completely: {str(e)}")]
        }
