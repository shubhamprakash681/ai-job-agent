'use client';

import DashboardLayout from '@/components/layout/DashboardLayout';
import { BarChart3 } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center mt-8">
        <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-medium text-gray-900 mb-2">Analytics coming soon</h3>
        <p className="text-gray-500 max-w-md mx-auto">
          Analytics will be available once you start tracking applications and gathering data on your job search performance.
        </p>
      </div>
    </DashboardLayout>
  );
}
