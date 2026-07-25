import os
from tavily import TavilyClient

from app.core.config import settings

tavily_client = None

def get_tavily_client():
    global tavily_client
    if tavily_client is None:
        api_key = settings.TAVILY_API_KEY
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set")
        tavily_client = TavilyClient(api_key=api_key)
    return tavily_client

def search_for_vendors(query: str, limit: int = 5):
    """
    Search for vendors matching the given query using Tavily API.
    Returns a list of dictionaries with vendor details.
    """
    client = get_tavily_client()
    
    # We use a detailed search to get maximum context
    response = client.search(
        query=f"B2B vendors suppliers companies for {query}",
        search_depth="advanced",
        max_results=limit
    )
    
    vendors = []
    # Use Gemini to extract structured data including phone, email, and whatsapp
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from pydantic import BaseModel, Field
        from typing import List
        
        class ExtractedVendor(BaseModel):
            company_name: str
            description: str
            website: str = Field(default="")
            email: str = Field(default="")
            phone: str = Field(default="")
            whatsapp: str = Field(default="")
            
        class VendorList(BaseModel):
            vendors: List[ExtractedVendor]
            
        api_key = settings.GEMINI_API_KEY
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=api_key)
        structured_llm = llm.with_structured_output(VendorList)
        
        raw_results = ""
        for i, res in enumerate(response.get("results", [])):
            raw_results += f"Result {i+1}:\nTitle: {res.get('title')}\nContent: {res.get('content')}\nURL: {res.get('url')}\n\n"
            
        prompt = f"""Extract a list of vendors from the following search results. 
Make sure to carefully extract any mentioned phone numbers, email addresses, and whatsapp numbers. If a phone number is the only contact, assume it can be used for WhatsApp unless specified otherwise.
Search Results:
{raw_results}
"""
        extracted_data: VendorList = structured_llm.invoke(prompt)
        
        for v in extracted_data.vendors:
            vendors.append({
                "company_name": v.company_name,
                "description": v.description,
                "website": v.website or "",
                "email": v.email or "",
                "phone": v.phone or "",
                "whatsapp": v.whatsapp or "",
                "source": "tavily_search"
            })
            
    except Exception as e:
        print(f"Error extracting with Gemini: {e}")
        # Fallback to simple extraction
        for result in response.get("results", []):
            vendors.append({
                "company_name": result.get("title", "Unknown Company").split("|")[0].strip(),
                "description": result.get("content", ""),
                "website": result.get("url", ""),
                "email": "",
                "phone": "",
                "whatsapp": "",
                "source": "tavily_search"
            })
        
    return vendors
