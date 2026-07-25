"use client"

import { useAuth } from "@clerk/nextjs";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NewRequestPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData(e.currentTarget);
    const data = {
      title: formData.get("title") as string,
      product_name: formData.get("product_name") as string,
      category: formData.get("category") as string,
      quantity: parseInt(formData.get("quantity") as string) || null,
      budget: formData.get("budget") as string,
      currency: formData.get("currency") as string,
      location: formData.get("location") as string,
      requirements: formData.get("requirements") as string,
      description: formData.get("description") as string,
    };

    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/procurement-requests/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(data)
      });

      if (!res.ok) {
        throw new Error("Failed to create request");
      }

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded border shadow-sm">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Create Procurement Request</h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 text-red-700 rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
          <input required name="title" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="e.g., Office Furniture Procurement" />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Product Name *</label>
            <input required name="product_name" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="e.g., Ergonomic Office Chairs" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
            <input name="category" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="e.g., Furniture" />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Quantity</label>
            <input name="quantity" type="number" min="1" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="10" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Budget</label>
            <input name="budget" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="5000" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Currency</label>
            <input name="currency" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="USD" defaultValue="USD" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
          <input name="location" type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="e.g., New York, NY" />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Specific Requirements</label>
          <textarea name="requirements" rows={3} className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="List any specific requirements or criteria for this product..." />
        </div>

        <div className="flex justify-end pt-4">
          <button 
            type="button" 
            onClick={() => router.back()}
            className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded mr-2 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            disabled={loading}
            className="px-6 py-2 bg-slate-900 text-white rounded hover:bg-slate-800 disabled:opacity-50 transition-colors"
          >
            {loading ? "Creating..." : "Create Request"}
          </button>
        </div>
      </form>
    </div>
  );
}
