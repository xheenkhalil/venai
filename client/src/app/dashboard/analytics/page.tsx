"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { Activity, Phone, ShoppingBag, Users } from "lucide-react";

type AnalyticsData = {
  total_requests: number;
  total_vendors: number;
  total_calls: number;
  total_budget: number;
};

export default function AnalyticsPage() {
  const { getToken } = useAuth();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const d = await res.json();
        setData(d);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className=`p-8 text-slate-500 animate-pulse">Loading analytics...</div>;
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h1>
          <p className="text-slate-500">Overview of your procurement operations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between pb-4">
            <h3 className="font-semibold text-slate-600">Total Requests</h3>
            <ShoppingBag className="w-5 h-5 text-indigo-500" />
          </div>
          <p className="text-3xl font-bold text-slate-900">{data?.total_requests || 0}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between pb-4">
            <h3 className="font-semibold text-slate-600">Vendors Discovered</h3>
            <Users className="w-5 h-5 text-emerald-500" />
          </div>
          <p className="text-3xl font-bold text-slate-900">{data?.total_vendors || 0}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between pb-4">
            <h3 className="font-semibold text-slate-600">AI Phone Calls</h3>
            <Phone className="w-5 h-5 text-amber-500" />
          </div>
          <p className="text-3xl font-bold text-slate-900">{data?.total_calls || 0}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <div className="flex items-center justify-between pb-4">
            <h3 className="font-semibold text-slate-600">Budget Managed</h3>
            <Activity className="w-5 h-5 text-rose-500" />
          </div>
          <p className="text-3xl font-bold text-slate-900">{formatCurrency(data?.total_budget || 0)}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">System Activity</h3>
        <div className="h-64 flex items-center justify-center bg-slate-50 rounded border border-dashed">
          <p className="text-slate-400">Activity charts will appear here as you accumulate more data.</p>
        </div>
      </div>
    </div>
  );
}
