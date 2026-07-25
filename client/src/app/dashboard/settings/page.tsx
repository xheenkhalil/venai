"use client";

import { useUser } from "@clerk/nextjs";
import { Building, Mail, User as UserIcon, Lock, Globe } from "lucide-react";

export default function SettingsPage() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div className="p-8 text-slate-500 animate-pulse">Loading settings...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Organization Settings</h1>
        <p className="text-slate-500">Manage your account and integration preferences</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-1">
          <h3 className="text-lg font-medium text-slate-900">Profile</h3>
          <p className="text-sm text-slate-500">Your personal information and email address.</p>
        </div>
        
        <div className="md:col-span-2 bg-white shadow-sm rounded-xl border p-6 space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-xl font-bold">
              {user?.firstName?.[0] || <UserIcon />}
            </div>
            <div>
              <p className="font-medium text-slate-900">{user?.fullName}</p>
              <p className="text-sm text-slate-500">{user?.primaryEmailAddress?.emailAddress}</p>
            </div>
          </div>
          
          <div className="pt-4 border-t">
            <button className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 text-sm font-medium transition-colors">
              Manage in Clerk
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-6 border-t">
        <div className="md:col-span-1 space-y-1">
          <h3 className="text-lg font-medium text-slate-900">Integrations</h3>
          <p className="text-sm text-slate-500">Configure your CALL-E and external API keys.</p>
        </div>
        
        <div className="md:col-span-2 bg-white shadow-sm rounded-xl border p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">CALL-E API Key</label>
            <div className="flex relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Lock className="w-4 h-4" />
              </span>
              <input 
                type="password" 
                placeholder="ce_live_**********************"
                className="w-full pl-10 pr-4 py-2 border rounded-lg bg-slate-50 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-slate-500 cursor-not-allowed"
                disabled
              />
            </div>
            <p className="mt-1 text-xs text-slate-500">Managed via environment variables in VenAI Core.</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Default Region</label>
            <div className="flex relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Globe className="w-4 h-4" />
              </span>
              <select className="w-full pl-10 pr-4 py-2 border rounded-lg bg-white focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                <option>United States (+1)</option>
                <option>United Kingdom (+44)</option>
                <option>Global Routing</option>
              </select>
            </div>
          </div>
          
          <div className="pt-2">
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium transition-colors">
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
