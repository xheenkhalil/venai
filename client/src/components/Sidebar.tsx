"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { MessageSquarePlus, Settings, BarChart2, Briefcase, Users, MessageSquare } from "lucide-react";

type ChatSession = {
  id: string;
  title: string;
  created_at: string;
};

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { getToken } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/chat/sessions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {
      console.error("Failed to load chat sessions");
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/chat/sessions`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: "New Conversation" }),
      });
      if (res.ok) {
        const data = await res.json();
        router.push(`/dashboard/chat/${data.id}`);
        fetchSessions(); // refresh list
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <aside className="w-64 bg-slate-50 border-r flex flex-col text-slate-800">
      <div className="p-4 border-b flex items-center gap-2">
        <MessageSquare className="w-6 h-6 text-indigo-600" />
        <h2 className="text-xl font-bold">VenAI Copilot</h2>
      </div>

      <div className="p-4">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-2 px-4 py-2 bg-white border rounded shadow-sm hover:bg-slate-50 transition-colors text-sm font-medium"
        >
          <MessageSquarePlus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-4 pb-4 space-y-6">
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Main</h3>
          <div className="space-y-1">
            <Link
              href="/dashboard"
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors ${
                pathname === "/dashboard" ? "bg-slate-200 text-slate-900 font-medium" : "text-slate-600 hover:bg-slate-200"
              }`}
            >
              <Briefcase className="w-4 h-4" />
              Requests
            </Link>
            <Link
              href="/dashboard/vendors"
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors ${
                pathname.includes("/vendors") ? "bg-slate-200 text-slate-900 font-medium" : "text-slate-600 hover:bg-slate-200"
              }`}
            >
              <Users className="w-4 h-4" />
              Vendors
            </Link>
          </div>
        </div>

        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Recents</h3>
          <div className="space-y-1">
            {loading ? (
              <div className="px-2 text-sm text-slate-400 animate-pulse">Loading...</div>
            ) : sessions.length === 0 ? (
              <div className="px-2 text-sm text-slate-400">No recent chats</div>
            ) : (
              sessions.map((s) => (
                <Link
                  key={s.id}
                  href={`/dashboard/chat/${s.id}`}
                  className={`block truncate px-2 py-1.5 rounded text-sm transition-colors ${
                    pathname === `/dashboard/chat/${s.id}` ? "bg-slate-200 text-slate-900 font-medium" : "text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {s.title}
                </Link>
              ))
            )}
          </div>
        </div>
      </nav>

      <div className="p-4 border-t space-y-1">
        <Link
          href="/dashboard/analytics"
          className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors ${
            pathname.includes("/analytics") ? "bg-slate-200 text-slate-900 font-medium" : "text-slate-600 hover:bg-slate-200"
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          Analytics
        </Link>
        <Link
          href="/dashboard/settings"
          className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm transition-colors ${
            pathname.includes("/settings") ? "bg-slate-200 text-slate-900 font-medium" : "text-slate-600 hover:bg-slate-200"
          }`}
        >
          <Settings className="w-4 h-4" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
