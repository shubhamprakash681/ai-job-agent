'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { CandidateProfile } from '@/types';

export default function CandidatePage() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<CandidateProfile>>({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = () => {
    setLoading(true);
    api.getCandidate()
      .then(res => {
        setProfile(res);
        setFormData(res);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleSave = async () => {
    try {
      const updated = await api.updateCandidate(formData);
      setProfile(updated);
      setEditing(false);
    } catch (err) {
      console.error(err);
      alert('Failed to update profile');
    }
  };

  if (loading) return <DashboardLayout><div className="p-8 text-center text-gray-500">Loading...</div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden max-w-4xl">
        <div className="px-6 py-5 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Candidate Profile</h3>
          {!editing ? (
            <button onClick={() => setEditing(true)} className="px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
              Edit Profile
            </button>
          ) : (
            <div className="space-x-3">
              <button onClick={() => { setEditing(false); setFormData(profile || {}); }} className="px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button onClick={handleSave} className="px-4 py-2 bg-blue-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700">
                Save
              </button>
            </div>
          )}
        </div>
        
        <div className="px-6 py-5 space-y-6">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.full_name || ''} onChange={e => setFormData({...formData, full_name: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.full_name || '-'}</div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              {editing ? (
                <input type="email" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.email || ''} onChange={e => setFormData({...formData, email: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.email || '-'}</div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.phone || ''} onChange={e => setFormData({...formData, phone: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.phone || '-'}</div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.location || ''} onChange={e => setFormData({...formData, location: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.location || '-'}</div>
              )}
            </div>
            
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Portfolio / LinkedIn URL</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.portfolio_url || ''} onChange={e => setFormData({...formData, portfolio_url: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-blue-600 hover:underline"><a href={profile?.portfolio_url || '#'} target="_blank" rel="noreferrer">{profile?.portfolio_url || '-'}</a></div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Current Company</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.current_company || ''} onChange={e => setFormData({...formData, current_company: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.current_company || '-'}</div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Current Role</label>
              {editing ? (
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.current_role || ''} onChange={e => setFormData({...formData, current_role: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.current_role || '-'}</div>
              )}
            </div>
            
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Target Roles (comma separated)</label>
              {editing ? (
                <textarea rows={2} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black" value={formData.target_roles || ''} onChange={e => setFormData({...formData, target_roles: e.target.value})} />
              ) : (
                <div className="mt-1 text-sm text-gray-900">{profile?.target_roles || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
