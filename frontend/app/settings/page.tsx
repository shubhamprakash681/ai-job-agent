'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getSettings()
      .then(setSettings)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateSettings(settings);
      alert('Settings saved successfully');
    } catch (err) {
      console.error(err);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <DashboardLayout><div className="p-8 text-center text-gray-500">Loading...</div></DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">System Settings</h2>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg font-medium text-gray-900">Application Preferences</h3>
          </div>
          <div className="px-6 py-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Dry Run Mode</label>
                <p className="text-sm text-gray-500">Don't actually submit applications, just record them.</p>
              </div>
              <input
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={settings.DRY_RUN !== false}
                onChange={e => handleChange('DRY_RUN', e.target.checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Human Approval Required</label>
                <p className="text-sm text-gray-500">Require manual approval before submitting an application.</p>
              </div>
              <input
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={settings.HUMAN_APPROVAL_REQUIRED !== false}
                onChange={e => handleChange('HUMAN_APPROVAL_REQUIRED', e.target.checked)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Daily Application Limit</label>
              <input
                type="number"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black"
                value={settings.DAILY_APPLICATION_LIMIT || 5}
                onChange={e => handleChange('DAILY_APPLICATION_LIMIT', parseInt(e.target.value))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Minimum Job Score (0-100)</label>
              <input
                type="number"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black"
                value={settings.MINIMUM_JOB_SCORE || 70}
                onChange={e => handleChange('MINIMUM_JOB_SCORE', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg font-medium text-gray-900">AI Provider Config</h3>
          </div>
          <div className="px-6 py-5 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Gemini API Key</label>
              <input
                type="password"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border text-black"
                value={settings.GEMINI_API_KEY || ''}
                placeholder="AIzaSy..."
                onChange={e => handleChange('GEMINI_API_KEY', e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
