'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Application } from '@/types';

export default function ApplicationsPage() {
  const [apps, setApps] = useState<Application[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getApplications()
      .then(res => {
        setApps(res.items);
        setTotal(res.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <DashboardLayout><div className="p-8 text-center text-gray-500">Loading applications...</div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
          <h3 className="font-semibold text-gray-800">Applications ({total})</h3>
        </div>
        
        {apps.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No applications yet. Applications will appear here as you apply to jobs.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-50 text-gray-700">
                <tr>
                  <th className="px-6 py-3">Job ID</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Score</th>
                  <th className="px-6 py-3">Applied Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {apps.map(app => (
                  <tr key={app.id} className="hover:bg-gray-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900">Job #{app.job_id}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        {app.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">{app.job_score || '-'}</td>
                    <td className="px-6 py-4">{app.applied_at ? new Date(app.applied_at).toLocaleDateString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
