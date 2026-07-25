"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useParams } from "next/navigation";
import { Send, Phone, Info } from "lucide-react";
import ReactMarkdown from "react-markdown";

type Message = {
  id: string;
  role: "user" | "ai" | "system" | "tool";
  content: string;
  created_at: string;
};

export default function ChatPage() {
  const { getToken } = useAuth();
  const params = useParams();
  const id = params.id as string;
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    
    fetchSession();
    
    const interval = setInterval(() => {
      fetchSession(false);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const fetchSession = async (showLoading = true) => {
    if (showLoading) setLoading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/chat/sessions/${id}`, {

        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages);
      }
    } catch (e) {
      console.error(e);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/chat/sessions/${id}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ role: "user", content: userMessage.content }),
      });
      if (res.ok) {
        const aiMessage = await res.json();
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (e) {
      console.error("Failed to send message", e);
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500 animate-pulse">Loading chat...</div>;
  }

  return (
    <div className="flex flex-col h-full bg-slate-50/50 relative">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-4">
            <Phone className="w-12 h-12 text-slate-300" />
            <p>Start a conversation to extract vendor requirements and trigger phone calls.</p>
          </div>
        ) : (
          messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-2xl px-5 py-3.5 rounded-2xl ${
                  m.role === "user"
                    ? "bg-slate-800 text-white shadow-sm"
                    : m.role === "tool"
                    ? "bg-amber-50 text-amber-900 border border-amber-200 text-sm font-mono"
                    : "bg-white text-slate-800 border shadow-sm"
                }`}
              >
                {m.role === "ai" ? (
                  <div className="prose prose-sm prose-slate max-w-none">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap">{m.content}</div>
                )}
              </div>
            </div>
          ))
        )}
        {sending && (
          <div className="flex justify-start">
            <div className="max-w-2xl px-5 py-3.5 rounded-2xl bg-white text-slate-500 border shadow-sm flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0.2s" }}></span>
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0.4s" }}></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-white border-t">
        <div className="max-w-3xl mx-auto relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="E.g. I need 500 office chairs for a budget of $50k..."
            className="w-full resize-none rounded-xl border-slate-300 bg-slate-50 text-slate-900 pr-12 pl-4 py-3 focus:border-indigo-500 focus:ring-indigo-500 min-h-[60px] max-h-32"
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="absolute right-2 bottom-2 p-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="text-center mt-2 flex justify-center items-center gap-1 text-xs text-slate-400">
          <Info className="w-3 h-3" />
          VenAI Copilot can make real phone calls on your behalf.
        </div>
      </div>
    </div>
  );
}
