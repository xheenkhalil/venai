"use client"

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function VendorsPage() {
  const { getToken } = useAuth();
  const [vendors, setVendors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtering & Pagination State
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // CRUD Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVendor, setEditingVendor] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  const fetchVendors = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/vendors/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setVendors(data);
      }
    } catch (err) {
      console.error("Failed to load vendors", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, [getToken]);

  // Derived State (Filtering & Pagination)
  const filteredVendors = vendors.filter((v) => {
    const term = searchTerm.toLowerCase();
    return (
      (v.company_name || "").toLowerCase().includes(term) ||
      (v.email || "").toLowerCase().includes(term) ||
      (v.phone || "").toLowerCase().includes(term) ||
      (v.whatsapp || "").toLowerCase().includes(term)
    );
  });

  const totalPages = Math.ceil(filteredVendors.length / itemsPerPage);
  const paginatedVendors = filteredVendors.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Handlers
  const handleOpenCreateModal = () => {
    setEditingVendor(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (vendor: any) => {
    setEditingVendor(vendor);
    setIsModalOpen(true);
  };

  const handleDelete = async (vendorId: string) => {
    if (!confirm("Are you sure you want to delete this vendor?")) return;
    try {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/vendors/${vendorId}`, {
        method: `DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        toast.success("Vendor deleted successfully");
        fetchVendors();
      } else {
        toast.error("Failed to delete vendor");
      }
    } catch (err) {
      console.error(err);
      toast.error("Error deleting vendor");
    }
  };

  const handleSaveVendor = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSaving(true);
    
    const formData = new FormData(e.currentTarget);
    const data = {
      company_name: formData.get("company_name") as string,
      website: formData.get("website") as string,
      phone: formData.get("phone") as string,
      email: formData.get("email") as string,
      whatsapp: formData.get("whatsapp") as string,
      source: editingVendor ? editingVendor.source : "Manual",
    };

    try {
      const token = await getToken();
      const url = editingVendor 
        ? `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/vendors/${editingVendor.id}` 
        : `${process.env.NEXT_PUBLIC_API_URL || `http://localhost:8000"}/api/v1/vendors/`;
      const method = editingVendor ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        toast.success(editingVendor ? "Vendor updated" : "Vendor created");
        setIsModalOpen(false);
        fetchVendors();
      } else {
        toast.error("Failed to save vendor");
      }
    } catch (err) {
      console.error(err);
      toast.error("Error saving vendor");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Vendors Directory</h2>
        <button 
          onClick={handleOpenCreateModal}
          className="px-4 py-2 bg-slate-900 text-white rounded hover:bg-slate-800 transition-colors"
        >
          + New Vendor
        </button>
      </div>

      <div className="mb-4 flex items-center gap-4">
        <input 
          type="text"
          placeholder="Search by name, email, or phone..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1); // Reset to first page on search
          }}
          className="w-full max-w-md px-4 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900"
        />
        <div className="text-sm text-slate-500">
          Showing {filteredVendors.length} vendors
        </div>
      </div>
      
      {loading ? (
        <p className="text-slate-500">Loading vendors...</p>
      ) : filteredVendors.length === 0 ? (
        <div className="bg-white p-12 rounded border text-center text-slate-500 shadow-sm">
          No vendors found matching your criteria.
        </div>
      ) : (
        <div className="bg-white rounded border overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">WhatsApp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedVendors.map((vendor: any) => (
                <tr key={vendor.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{vendor.company_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 hover:underline">
                    {vendor.website ? (
                      <a href={vendor.website.startsWith('http') ? vendor.website : `https://${vendor.website}`} target="_blank" rel="noreferrer">
                        Link
                      </a>
                    ) : (
                      <span className="text-slate-400 no-underline">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{vendor.phone || <span className="text-slate-400">N/A</span>}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{vendor.email || <span className="text-slate-400">N/A</span>}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{vendor.whatsapp || <span className="text-slate-400">N/A</span>}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      {vendor.verification_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-right space-x-3">
                    <button onClick={() => handleOpenEditModal(vendor)} className="text-indigo-600 hover:text-indigo-900">Edit</button>
                    <button onClick={() => handleDelete(vendor.id)} className="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="px-6 py-3 border-t bg-gray-50 flex items-center justify-between">
              <button 
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => p - 1)}
                className="px-3 py-1 border rounded bg-white text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                &larr; Prev
              </button>
              <span className="text-sm text-slate-600">
                Page {currentPage} of {totalPages}
              </span>
              <button 
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(p => p + 1)}
                className="px-3 py-1 border rounded bg-white text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50"
              >
                Next &rarr;
              </button>
            </div>
          )}
        </div>
      )}

      {/* CRUD Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md shadow-xl border">
            <h3 className="text-xl font-bold text-slate-800 mb-4">
              {editingVendor ? "Edit Vendor" : "New Vendor"}
            </h3>
            <form onSubmit={handleSaveVendor} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Company Name *</label>
                <input required name="company_name" defaultValue={editingVendor?.company_name} type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Website</label>
                <input name="website" defaultValue={editingVendor?.website} type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <input name="phone" defaultValue={editingVendor?.phone} type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">WhatsApp</label>
                <input name="whatsapp" defaultValue={editingVendor?.whatsapp} type="text" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input name="email" defaultValue={editingVendor?.email} type="email" className="w-full px-3 py-2 border rounded text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900" />
              </div>
              
              <div className="flex justify-end pt-4 space-x-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded">
                  Cancel
                </button>
                <button type="submit" disabled={saving} className="px-6 py-2 bg-slate-900 text-white rounded hover:bg-slate-800 disabled:opacity-50">
                  {saving ? "Saving..." : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
