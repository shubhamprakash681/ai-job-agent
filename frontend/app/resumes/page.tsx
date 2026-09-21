'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { ResumeVariant } from '@/types';
import { FileCheck } from 'lucide-react';

export default function ResumesPage() {
  const [variants, setVariants] = useState<ResumeVariant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getResumeVariants()
      .then(setVariants)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <DashboardLayout><div className="p-8 text-center text-gray-500">Loading...</div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Resume Variants</h2>
      </div>

      {variants.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <FileCheck className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes yet</h3>
          <p className="text-gray-500">Upload your base resume and configure settings to generate targeted variants.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {variants.map(variant => (
            <div key={variant.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 relative">
              {variant.is_default && (
                <span className="absolute top-4 right-4 bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">Default</span>
              )}
              <h3 className="text-lg font-bold text-gray-900 mb-2">{variant.display_name}</h3>
              <p className="text-sm text-gray-500 mb-4">{variant.description || 'No description provided.'}</p>
              <div className="pt-4 border-t border-gray-100 flex space-x-3">
                <button className="text-sm font-medium text-blue-600 hover:text-blue-800">View Details</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
