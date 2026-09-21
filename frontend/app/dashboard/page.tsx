'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { DashboardSummary } from '@/types';
import { Briefcase, FileText, CheckCircle, Clock, Calendar, BarChart, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboardSummary()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <DashboardLayout><div className="flex h-64 items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div></DashboardLayout>;

  if (!data) return <DashboardLayout><div>Error loading dashboard data</div></DashboardLayout>;

  const isGettingStarted = data.total_jobs === 0;

  const statCards = [
    { label: 'Total Jobs', value: data.total_jobs, icon: Briefcase, color: 'bg-blue-500' },
    { label: 'New Jobs Today', value: data.new_jobs_today, icon: Calendar, color: 'bg-green-500' },
    { label: 'High Priority', value: data.high_priority_jobs, icon: AlertCircle, color: 'bg-red-500' },
    { label: 'Pending Apps', value: data.applications_pending, icon: Clock, color: 'bg-yellow-500' },
    { label: 'Submitted Apps', value: data.applications_submitted, icon: CheckCircle, color: 'bg-indigo-500' },
    { label: 'Interviews', value: data.interview_count, icon: FileText, color: 'bg-purple-500' },
    { label: 'Response Rate', value: `${(data.response_rate * 100).toFixed(1)}%`, icon: BarChart, color: 'bg-teal-500' },
  ];

  return (
    <DashboardLayout>
      {isGettingStarted && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-2">Getting Started</h3>
          <p>Welcome to AI Job Agent! It looks like you don't have any jobs yet. Make sure your Candidate Profile and Settings are configured, and wait for the job discovery agent to fetch new opportunities.</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {statCards.map((stat, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center space-x-4">
            <div className={`p-3 rounded-lg text-white ${stat.color}`}>
              <stat.icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{stat.label}</p>
              <h4 className="text-2xl font-bold text-gray-900">{stat.value}</h4>
            </div>
          </div>
        ))}
      </div>
    </DashboardLayout>
  );
}
