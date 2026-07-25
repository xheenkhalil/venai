"use client"

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";

import ReactMarkdown from 'react-markdown';
import { Search, Bot, Smartphone, Mail, MessageCircle, Globe, PhoneCall, CheckCircle2, XCircle } from "lucide-react";

export default function RequestDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const { getToken } = useAuth();
  const router = useRouter();
  
  const [request, setRequest] = useState<any>(null);
  const [vendors, setVendors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [runningAgents, setRunningAgents] = useState(false);
  const [error, setError] = useState("");
  
  const [callingVendor, setCallingVendor] = useState<{[key: string]: boolean}>({});
  const [callResults, setCallResults] = useState<{[key: string]: any}>({});

  const fetchRequest = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/procurement-requests/${unwrappedParams.id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setRequest(data);
        
        // Populate callResults if bulk workflow was completed
        if (data.call_results_json) {
          try {
            const results = JSON.parse(data.call_results_json);
            const mappedResults: {[key: string]: any} = {};
            results.forEach((r: any) => {
              mappedResults[r.vendor_id] = {
                status: r.available ? 'COMPLETED' : (r.notes?.includes(`Error") || r.notes?.includes("Failed") ? 'FAILED' : 'COMPLETED'),
                available: r.available,
                price: r.price_quote,
                delivery: r.delivery_time,
                notes: r.notes
              };
            });
            // Merge with existing callResults so we don't overwrite manual calls made just now
            setCallResults(prev => ({...mappedResults, ...prev}));
          } catch (e) {
            console.error("Failed to parse call_results_json", e);
          }
        }
      } else {
        setError("Failed to load request");
      }
    } catch (err: any) {
      setError(err.message || "Failed to load request");
    } finally {
      setLoading(false);
    }
  };

  const fetchVendors = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/procurement-requests/${unwrappedParams.id}/vendors`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setVendors(data);
      }
    } catch (err) {
      console.error(`Failed to fetch vendors", err);
    }
  };

  useEffect(() => {
    fetchRequest();
    fetchVendors();
  }, [unwrappedParams.id]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (request && (request.status === "searching" || request.status === "analyzing" || request.status === "calling")) {
      interval = setInterval(() => {
        fetchRequest();
        fetchVendors();
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [request?.status, unwrappedParams.id]);

  const handleFindVendors = async () => {
    setSearching(true);
    setError("");
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/vendors/search?request_id=${unwrappedParams.id}`, {
        method: `POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        toast.success(`Successfully found ${data.vendors_found} vendors!`);
        fetchRequest();
      } else {
        const errData = await res.json();
        throw new Error(errData.detail || "Search failed");
      }
    } catch (err: any) {
      setError(err.message || "Failed to search for vendors");
    } finally {
      setSearching(false);
    }
  };

  const handleCallVendor = async (vendorId: string) => {
    setCallingVendor(prev => ({...prev, [vendorId]: true}));
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/agents/call/${unwrappedParams.id}/${vendorId}`, {
        method: `POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCallResults(prev => ({...prev, [vendorId]: data}));
      } else {
        const err = await res.json();
        setCallResults(prev => ({...prev, [vendorId]: {status: "FAILED", notes: err.detail || "Unknown error"}}));
      }
    } catch (err: any) {
      setCallResults(prev => ({...prev, [vendorId]: {status: "FAILED", notes: err.message || "Network error"}}));
    } finally {
      setCallingVendor(prev => ({...prev, [vendorId]: false}));
    }
  };

  const handleRunAgents = async () => {
    setRunningAgents(true);
    setError("");
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/agents/start/${unwrappedParams.id}`, {
        method: `POST",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (res.ok) {
        toast.success("Agent workflow completed successfully!");
        fetchRequest();
      } else {
        const errData = await res.json();
        throw new Error(errData.detail || "Workflow failed");
      }
    } catch (err: any) {
      setError(err.message || "Failed to run agent workflow");
    } finally {
      setRunningAgents(false);
    }
  };

  if (loading) return <div className="text-slate-500">Loading request details...</div>;
  if (error || !request) return <div className="text-red-500">{error || "Not found"}</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/dashboard" className="text-slate-500 hover:text-slate-800 transition-colors">
          &larr; Back to Requests
        </Link>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-full">
          {request.status}
        </span>
      </div>

      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <div className="p-6 border-b flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-slate-800">{request.title}</h2>
            <p className="text-slate-500 mt-1">Created on {new Date(request.created_at).toLocaleDateString()}</p>
          </div>
          
          <div className="space-x-3 flex">
            <button 
              onClick={handleFindVendors}
              disabled={searching || request.status !== "draft"}
              className="px-4 py-2 bg-slate-100 text-slate-700 font-medium rounded hover:bg-slate-200 disabled:opacity-50 transition-colors shadow-sm flex items-center border gap-2"
            >
              {searching ? (
                <>
                  <Search className="w-4 h-4 animate-pulse" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Find Vendors
                </>
              )}
            </button>
            <button 
              onClick={handleRunAgents}
              disabled={runningAgents || request.status === "draft"}
              className="px-6 py-2 bg-indigo-600 text-white font-medium rounded hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm flex items-center gap-2"
            >
              {runningAgents ? (
                <>
                  <Bot className="w-4 h-4 animate-pulse" />
                  Agents Working...
                </>
              ) : (
                <>
                  <Bot className="w-4 h-4" />
                  Run Agent Workflow
                </>
              )}
            </button>
          </div>
        </div>

        <div className="p-6 grid grid-cols-2 gap-8">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Product Information</h3>
              <div className="mt-2 text-slate-900">
                <p><span className="font-medium">Product:</span> {request.product_name}</p>
                <p><span className="font-medium">Category:</span> {request.category || "N/A"}</p>
                <p><span className="font-medium">Quantity:</span> {request.quantity || "N/A"}</p>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Financials & Logistics</h3>
              <div className="mt-2 text-slate-900">
                <p><span className="font-medium">Budget:</span> {request.budget ? `${request.budget} ${request.currency || ''}` : "N/A"}</p>
                <p><span className="font-medium">Location:</span> {request.location || "N/A"}</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider">Requirements</h3>
            <p className="mt-2 text-slate-700 whitespace-pre-wrap bg-slate-50 p-4 rounded border">
              {request.requirements || "No specific requirements provided."}
            </p>
          </div>
        </div>
        
        {vendors.length > 0 && (
          <div className="p-6 border-t bg-slate-50">
            <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-4">Discovered Vendors ({vendors.length})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {vendors.map((v) => (
                <div key={v.id} className="bg-white p-4 rounded border shadow-sm">
                  <h4 className="font-bold text-slate-800">{v.company_name}</h4>
                  <div className="text-sm text-slate-600 mt-2 space-y-2">
                    {v.phone && <p className="flex items-center gap-2"><Smartphone className="w-4 h-4 text-slate-400" /> {v.phone}</p>}
                    {v.email && <p className="flex items-center gap-2"><Mail className="w-4 h-4 text-slate-400" /> {v.email}</p>}
                    {v.whatsapp && <p className="flex items-center gap-2"><MessageCircle className="w-4 h-4 text-slate-400" /> {v.whatsapp}</p>}
                    {v.website && <p className="flex items-center gap-2"><Globe className="w-4 h-4 text-slate-400" /> <a href={v.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Website</a></p>}
                  </div>
                  
                  <div className="mt-4 flex flex-wrap gap-2">
                    {v.phone && (
                      <button 
                        onClick={() => handleCallVendor(v.id)}
                        disabled={callingVendor[v.id]}
                        className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center gap-1.5"
                      >
                        {callingVendor[v.id] ? (
                          <><PhoneCall className="w-3.5 h-3.5 animate-pulse" /> Calling...</>
                        ) : (
                          <><PhoneCall className="w-3.5 h-3.5" /> AI Call</>
                        )}
                      </button>
                    )}
                    {v.whatsapp && (
                      <a 
                        href={`https://wa.me/${v.whatsapp.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(`Hello ${v.company_name},\n\nI am interested in purchasing ${request?.product_name}. Our budget is ${request?.budget || 'flexible'}. Please let me know your availability.\n\nThank you.`)}`}
                        target="_blank" rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-teal-600 text-white text-xs font-medium rounded hover:bg-teal-700 transition-colors inline-flex items-center gap-1.5"
                      >
                        <MessageCircle className="w-3.5 h-3.5" /> WhatsApp
                      </a>
                    )}
                    {v.email && (
                      <a 
                        href={`mailto:${v.email}?subject=Procurement Inquiry: ${request?.product_name}&body=${encodeURIComponent(`Hello ${v.company_name},\n\nI am reaching out to inquire about purchasing ${request?.product_name}. Our budget is ${request?.budget || 'flexible'} and our requirements are: ${request?.requirements || 'standard'}.\n\nPlease let me know if you can fulfill this request.\n\nThank you.`)}`}
                        target="_blank" rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors inline-flex items-center gap-1.5"
                      >
                        <Mail className="w-3.5 h-3.5" /> Email
                      </a>
                    )}
                  </div>
                  
                  {callResults[v.id] && (
                    <div className={`mt-3 p-3 rounded text-sm border ${callResults[v.id].status === 'COMPLETED' ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                      {callResults[v.id].status === 'COMPLETED' ? (
                        <>
                          <div className="font-bold mb-2 flex items-center gap-1.5">
                            <CheckCircle2 className="w-4 h-4 text-green-600" /> 
                            Call Completed
                          </div>
                          <p><strong>Available:</strong> {callResults[v.id].available ? 'Yes' : 'No'}</p>
                          <p><strong>Price:</strong> ${callResults[v.id].price}</p>
                          <p><strong>Delivery:</strong> {callResults[v.id].delivery}</p>
                          <p className="mt-1"><strong>Notes:</strong> {callResults[v.id].notes}</p>
                        </>
                      ) : (
                        <>
                          <div className="font-bold mb-2 flex items-center gap-1.5">
                            <XCircle className="w-4 h-4 text-red-600" /> 
                            Call Failed
                          </div>
                          <p>{callResults[v.id].notes}</p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {request.analysis_result && (
          <div className="p-6 border-t bg-indigo-50/30">
            <h3 className="text-lg font-bold text-indigo-900 mb-4 flex items-center gap-2">
              <Bot className="w-5 h-5" /> 
              AI Recommendation Report
            </h3>
            <div className="prose prose-slate max-w-none text-slate-800 bg-white p-6 rounded border shadow-sm text-sm">
              <ReactMarkdown 
                components={{
                  a: ({node, ...props}) => <a {...props} className="text-blue-600 hover:underline font-semibold" target="_blank" rel="noopener noreferrer" />
                }}
              >
                {request.analysis_result}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
