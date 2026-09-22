'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Application, ApplicationDetail, ApplicationQuestion } from '@/types';
import {
  FileCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  X,
  Search,
  ExternalLink,
  ShieldCheck,
  Send,
  HelpCircle,
  FileText,
  RefreshCw,
  Building,
  MapPin,
  ChevronRight,
  Download,
  Eye,
  Check,
  Edit3,
} from 'lucide-react';

export default function ApplicationsPage() {
  const [apps, setApps] = useState<Application[]>([]);
  const [total, setTotal] = useState(0);
  const [dailyCount, setDailyCount] = useState(0);
  const [dailyLimit, setDailyLimit] = useState(10);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  // Selected application for detail review drawer
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const [appDetail, setAppDetail] = useState<ApplicationDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'questions' | 'cover_letter' | 'evidence'>('overview');

  // Question editing state
  const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
  const [editedAnswer, setEditedAnswer] = useState('');
  const [savingQuestion, setSavingQuestion] = useState(false);

  // Action states
  const [actionLoading, setActionLoading] = useState(false);
  const [alertMessage, setAlertMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter !== 'all') params.status = statusFilter;
      if (search.trim()) params.search = search.trim();

      const res = await api.getApplications(params);
      setApps(res.items);
      setTotal(res.total);
      setDailyCount(res.daily_count);
      setDailyLimit(res.daily_limit);
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [statusFilter]);

  const handleOpenDetail = async (appId: number) => {
    setSelectedAppId(appId);
    setDetailLoading(true);
    setAlertMessage(null);
    try {
      const detail = await api.getApplication(appId);
      setAppDetail(detail);
      setActiveTab(detail.status === 'AWAITING_APPROVAL' ? 'questions' : 'overview');
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: err.message || 'Failed to load application details' });
    } finally {
      setDetailLoading(false);
    }
  };

  const handleApproveApplication = async (appId: number) => {
    setActionLoading(true);
    setAlertMessage(null);
    try {
      const res = await api.approveApplication(appId, { user_approved: true, dry_run: true });
      setAlertMessage({
        type: 'success',
        text: `Application #${appId} successfully approved and submitted (Dry Run)! Code: ${res.evidence?.confirmation_code || 'OK'}`,
      });
      setShowConfirmModal(false);
      await fetchApplications();
      if (selectedAppId === appId) {
        const updated = await api.getApplication(appId);
        setAppDetail(updated);
      }
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: err.message || 'Failed to approve application' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleRejectApplication = async (appId: number) => {
    setActionLoading(true);
    setAlertMessage(null);
    try {
      await api.rejectApplication(appId, 'Rejected from Applications Hub');
      setAlertMessage({ type: 'success', text: `Application #${appId} marked as REJECTED.` });
      await fetchApplications();
      if (selectedAppId === appId) {
        const updated = await api.getApplication(appId);
        setAppDetail(updated);
      }
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: err.message || 'Failed to reject application' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSaveQuestion = async (questionId: number) => {
    if (!appDetail) return;
    setSavingQuestion(true);
    try {
      const updatedQ = await api.updateQuestion(appDetail.id, questionId, editedAnswer, true);
      setAppDetail({
        ...appDetail,
        questions: appDetail.questions.map((q) => (q.id === questionId ? updatedQ : q)),
      });
      setEditingQuestionId(null);
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: err.message || 'Failed to save question answer' });
    } finally {
      setSavingQuestion(false);
    }
  };

  const awaitingCount = apps.filter((a) => a.status === 'AWAITING_APPROVAL').length;
  const appliedCount = apps.filter((a) => a.status === 'APPLIED').length;
  const manualCount = apps.filter((a) => a.status === 'MANUAL_REQUIRED').length;

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'AWAITING_APPROVAL':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            Awaiting Approval
          </span>
        );
      case 'APPLIED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            Applied (Dry-Run)
          </span>
        );
      case 'APPLYING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">
            <RefreshCw className="w-3 h-3 text-blue-600 animate-spin" />
            Submitting...
          </span>
        );
      case 'MANUAL_REQUIRED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-50 text-purple-800 border border-purple-200">
            <ExternalLink className="w-3 h-3 text-purple-600" />
            Manual Review
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            Rejected
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200">
            {status}
          </span>
        );
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Title & Safety Summary */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Application Approval Hub</h2>
            <p className="text-sm text-slate-500">
              Orchestrate job applications, inspect screening questions, and authorize submissions.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchApplications}
              disabled={loading}
              className="inline-flex items-center px-3.5 py-2 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Daily Limit Card */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-2xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Daily Application Limit
                </span>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">
                  {dailyCount} <span className="text-sm font-normal text-slate-400">/ {dailyLimit} today</span>
                </h3>
              </div>
              <span className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                <ShieldCheck className="w-5 h-5" />
              </span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 mt-3 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all ${
                  dailyCount >= dailyLimit ? 'bg-rose-500' : 'bg-indigo-600'
                }`}
                style={{ width: `${Math.min((dailyCount / dailyLimit) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500" /> DRY_RUN active (mock submissions)
            </p>
          </div>

          {/* Awaiting Approval */}
          <div className="bg-white rounded-xl p-5 border border-amber-200 shadow-2xs bg-gradient-to-br from-amber-50/40 to-white">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-amber-800 uppercase tracking-wider">
                  Awaiting Human Approval
                </span>
                <h3 className="text-2xl font-bold text-amber-900 mt-1">{awaitingCount}</h3>
              </div>
              <span className="p-2 bg-amber-100 text-amber-700 rounded-lg">
                <Clock className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-amber-700 mt-3 font-medium">Packets ready for final authorization</p>
          </div>

          {/* Total Applied */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-2xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Submitted / Applied</span>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">{appliedCount}</h3>
              </div>
              <span className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                <CheckCircle2 className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-3">Evidence logged with proof code</p>
          </div>

          {/* Manual Portal Redirect */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-2xs">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">External Manual</span>
                <h3 className="text-2xl font-bold text-slate-900 mt-1">{manualCount}</h3>
              </div>
              <span className="p-2 bg-purple-50 text-purple-600 rounded-lg">
                <ExternalLink className="w-5 h-5" />
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-3">Requires portal login or CAPTCHA</p>
          </div>
        </div>

        {/* Global Notification Banner */}
        {alertMessage && (
          <div
            className={`p-4 rounded-xl text-xs font-medium flex items-center justify-between ${
              alertMessage.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                : 'bg-rose-50 text-rose-800 border border-rose-200'
            }`}
          >
            <span>{alertMessage.text}</span>
            <button onClick={() => setAlertMessage(null)} className="text-slate-400 hover:text-slate-700">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Filter Toolbar */}
        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-2xs flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
            {[
              { id: 'all', label: 'All Applications' },
              { id: 'AWAITING_APPROVAL', label: `Awaiting Approval (${awaitingCount})` },
              { id: 'APPLIED', label: `Applied (${appliedCount})` },
              { id: 'MANUAL_REQUIRED', label: `Manual (${manualCount})` },
              { id: 'REJECTED', label: 'Rejected' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-colors whitespace-nowrap ${
                  statusFilter === tab.id
                    ? 'bg-indigo-600 text-white font-semibold shadow-2xs'
                    : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search company or role..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchApplications()}
              className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900"
            />
          </div>
        </div>

        {/* Applications List Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center space-y-3">
              <RefreshCw className="w-6 h-6 animate-spin text-indigo-600" />
              <p className="text-xs font-medium">Loading applications...</p>
            </div>
          ) : apps.length === 0 ? (
            <div className="p-12 text-center text-slate-500 space-y-2">
              <FileCheck className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="font-semibold text-slate-700">No applications found.</p>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Applications are prepared when you tailor resumes and cover letters in the Jobs Console.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-3.5 px-4">Role & Company</th>
                    <th className="py-3.5 px-4">Fit Score</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Tailored Resume</th>
                    <th className="py-3.5 px-4">Cover Letter</th>
                    <th className="py-3.5 px-4">Submitted Date</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {apps.map((app) => (
                    <tr
                      key={app.id}
                      onClick={() => handleOpenDetail(app.id)}
                      className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                    >
                      <td className="py-4 px-4 font-medium text-slate-900">
                        <div className="flex items-center gap-2">
                          <div>
                            <p className="font-bold text-slate-900">{app.job_title || `Job #${app.job_id}`}</p>
                            <p className="text-xs text-slate-500">{app.job_company || 'Target Organization'}</p>
                          </div>
                        </div>
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                          {app.job_score || 70} / 100
                        </span>
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">{renderStatusBadge(app.status)}</td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        {app.resume_version_id ? (
                          <span className="inline-flex items-center gap-1 text-xs text-emerald-700 font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Tailored (v{app.resume_version_id})
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">Master template</span>
                        )}
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap">
                        {app.cover_letter ? (
                          <span className="inline-flex items-center gap-1 text-xs text-indigo-700 font-medium">
                            <FileText className="w-3.5 h-3.5" /> Ready ({app.cover_letter.split(/\s+/).length} words)
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">Not drafted</span>
                        )}
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap text-slate-500">
                        {app.applied_at
                          ? new Date(app.applied_at).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : 'Pending'}
                      </td>

                      <td className="py-4 px-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleOpenDetail(app.id)}
                            className="inline-flex items-center px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 shadow-2xs"
                          >
                            <Eye className="w-3 h-3 mr-1 text-slate-500" /> Review Packet
                          </button>
                          {app.status === 'AWAITING_APPROVAL' && (
                            <button
                              onClick={() => {
                                setSelectedAppId(app.id);
                                setShowConfirmModal(true);
                              }}
                              className="inline-flex items-center px-3 py-1 text-xs font-bold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 shadow-2xs transition-colors"
                            >
                              <Send className="w-3 h-3 mr-1" /> Approve
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Slide-over Application Packet Review Drawer */}
        {selectedAppId && appDetail && (
          <div className="fixed inset-0 bg-black/50 z-50 flex justify-end backdrop-blur-2xs">
            <div className="bg-white w-full max-w-2xl h-full shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-right duration-200 border-l border-slate-200">
              {/* Drawer Header */}
              <div className="px-6 py-4 bg-slate-900 text-white flex justify-between items-center border-b border-slate-800">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white">{appDetail.job_title}</h3>
                    <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md">
                      App #{appDetail.id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    {appDetail.job_company} &bull; {appDetail.job_location || 'Mumbai / Remote'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {renderStatusBadge(appDetail.status)}
                  <button
                    onClick={() => setSelectedAppId(null)}
                    className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Drawer Tabs */}
              <div className="px-6 bg-slate-50 border-b border-slate-200 flex gap-4 text-xs font-semibold">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`py-3 border-b-2 transition-colors ${
                    activeTab === 'overview'
                      ? 'border-indigo-600 text-indigo-600 font-bold'
                      : 'border-transparent text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Packet Overview
                </button>
                <button
                  onClick={() => setActiveTab('questions')}
                  className={`py-3 border-b-2 transition-colors flex items-center gap-1.5 ${
                    activeTab === 'questions'
                      ? 'border-indigo-600 text-indigo-600 font-bold'
                      : 'border-transparent text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Screening Questions ({appDetail.questions.length})
                </button>
                <button
                  onClick={() => setActiveTab('cover_letter')}
                  className={`py-3 border-b-2 transition-colors ${
                    activeTab === 'cover_letter'
                      ? 'border-indigo-600 text-indigo-600 font-bold'
                      : 'border-transparent text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Cover Letter
                </button>
                <button
                  onClick={() => setActiveTab('evidence')}
                  className={`py-3 border-b-2 transition-colors ${
                    activeTab === 'evidence'
                      ? 'border-indigo-600 text-indigo-600 font-bold'
                      : 'border-transparent text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Audit &amp; Evidence
                </button>
              </div>

              {/* Drawer Body Content */}
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                {activeTab === 'overview' && (
                  <div className="space-y-4 text-xs">
                    {/* Opportunity Summary */}
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                      <h4 className="font-bold text-slate-800 uppercase tracking-wider text-xs">Target Opportunity</h4>
                      <div className="grid grid-cols-2 gap-2 text-slate-700">
                        <p>
                          <span className="text-slate-400">Company:</span> {appDetail.job_company}
                        </p>
                        <p>
                          <span className="text-slate-400">Role:</span> {appDetail.job_title}
                        </p>
                        <p>
                          <span className="text-slate-400">Match Score:</span> {appDetail.job_score} / 100
                        </p>
                        <p>
                          <span className="text-slate-400">Portal URL:</span>{' '}
                          {appDetail.application_url ? (
                            <a
                              href={appDetail.application_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-blue-600 underline inline-flex items-center gap-0.5"
                            >
                              Open Portal <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          ) : (
                            'N/A'
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Candidate Identity */}
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                      <h4 className="font-bold text-slate-800 uppercase tracking-wider text-xs">Candidate Ground Truth</h4>
                      <div className="grid grid-cols-2 gap-2 text-slate-700">
                        <p>
                          <span className="text-slate-400">Applicant:</span> Shubham Prakash
                        </p>
                        <p>
                          <span className="text-slate-400">Experience:</span> ~3.2 years (TCS 3 yrs, Accenture)
                        </p>
                        <p>
                          <span className="text-slate-400">Notice Period:</span> 30 days
                        </p>
                        <p>
                          <span className="text-slate-400">Location:</span> Mumbai, India
                        </p>
                      </div>
                    </div>

                    {/* Packaged Documents */}
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
                      <h4 className="font-bold text-slate-800 uppercase tracking-wider text-xs">Attached Documents</h4>
                      <div className="flex flex-wrap gap-2">
                        {appDetail.resume_version_id && (
                          <a
                            href={`/api/resumes/versions/${appDetail.resume_version_id}/download/pdf`}
                            download
                            className="inline-flex items-center px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-100 font-medium gap-1.5 shadow-2xs"
                          >
                            <Download className="w-3.5 h-3.5 text-indigo-600" /> ATS Resume PDF (v
                            {appDetail.resume_version_number || appDetail.resume_version_id})
                          </a>
                        )}
                        {appDetail.cover_letter && (
                          <a
                            href={`/api/jobs/${appDetail.job_id}/cover-letter/download/pdf`}
                            download
                            className="inline-flex items-center px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-100 font-medium gap-1.5 shadow-2xs"
                          >
                            <Download className="w-3.5 h-3.5 text-indigo-600" /> Cover Letter PDF
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'questions' && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <p className="text-xs text-slate-500 font-medium">
                        Screening questions answered using verified candidate ground truth:
                      </p>
                    </div>

                    {appDetail.questions.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">No screening questions logged for this application.</p>
                    ) : (
                      <div className="space-y-3">
                        {appDetail.questions.map((q) => (
                          <div key={q.id} className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2.5">
                            <div className="flex justify-between items-start gap-2">
                              <h5 className="font-bold text-slate-900 text-xs">{q.question}</h5>
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold shrink-0 ${
                                  q.confidence >= 0.95
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : 'bg-amber-100 text-amber-800'
                                }`}
                              >
                                {Math.round(q.confidence * 100)}% Match
                              </span>
                            </div>

                            {editingQuestionId === q.id ? (
                              <div className="space-y-2">
                                <textarea
                                  rows={3}
                                  value={editedAnswer}
                                  onChange={(e) => setEditedAnswer(e.target.value)}
                                  className="w-full text-xs font-sans p-2.5 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                                />
                                <div className="flex justify-end gap-2">
                                  <button
                                    onClick={() => setEditingQuestionId(null)}
                                    className="px-2.5 py-1 text-slate-600 hover:bg-slate-200 rounded-md text-xs"
                                  >
                                    Cancel
                                  </button>
                                  <button
                                    onClick={() => handleSaveQuestion(q.id)}
                                    disabled={savingQuestion}
                                    className="px-3 py-1 bg-indigo-600 text-white font-semibold rounded-md text-xs hover:bg-indigo-700 disabled:opacity-50"
                                  >
                                    {savingQuestion ? 'Saving...' : 'Save Answer'}
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <div className="space-y-1.5">
                                <p className="text-xs text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200/80 leading-relaxed font-sans">
                                  {q.final_answer || q.proposed_answer}
                                </p>
                                <div className="flex justify-between items-center pt-1 text-[11px] text-slate-400">
                                  <span>Source: {q.answer_source || 'Verified Facts'}</span>
                                  <button
                                    onClick={() => {
                                      setEditingQuestionId(q.id);
                                      setEditedAnswer(q.final_answer || q.proposed_answer || '');
                                    }}
                                    className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center gap-1"
                                  >
                                    <Edit3 className="w-3 h-3" /> Edit Answer
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'cover_letter' && (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="text-xs font-bold text-slate-700 uppercase">Cover Letter Text</h4>
                      <a
                        href={`/api/jobs/${appDetail.job_id}/cover-letter/download/pdf`}
                        download
                        className="inline-flex items-center text-xs text-indigo-600 font-semibold hover:text-indigo-800 gap-1"
                      >
                        <Download className="w-3.5 h-3.5" /> Download PDF
                      </a>
                    </div>
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
                      {appDetail.cover_letter || 'No cover letter attached.'}
                    </div>
                  </div>
                )}

                {activeTab === 'evidence' && (
                  <div className="space-y-4 text-xs">
                    {appDetail.submission_evidence_parsed ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                            Mode: {appDetail.submission_evidence_parsed.mode || 'DRY_RUN'}
                          </span>
                          <span className="font-mono text-slate-700 text-xs">
                            Code: {appDetail.submission_evidence_parsed.confirmation_code}
                          </span>
                        </div>
                        <div className="bg-slate-900 text-emerald-400 p-4 rounded-xl font-mono text-[11px] overflow-x-auto max-h-72">
                          <pre>{JSON.stringify(appDetail.submission_evidence_parsed, null, 2)}</pre>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 text-center">
                        Application not submitted yet. Submission evidence will be recorded upon human approval.
                      </div>
                    )}

                    {/* Events Timeline */}
                    <div className="space-y-2 pt-2">
                      <h5 className="font-bold text-slate-800 text-xs uppercase tracking-wider">Lifecycle Event Log</h5>
                      <div className="space-y-2">
                        {appDetail.events.map((ev) => (
                          <div key={ev.id} className="p-3 bg-white border border-slate-200 rounded-lg text-xs space-y-1">
                            <div className="flex justify-between text-slate-400 text-[11px]">
                              <span className="font-bold text-slate-700">{ev.event_type}</span>
                              <span>{new Date(ev.created_at).toLocaleTimeString()}</span>
                            </div>
                            {ev.event_data && (
                              <p className="text-slate-600 font-mono text-[10px] bg-slate-50 p-1.5 rounded">
                                {ev.event_data}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Drawer Footer Actions */}
              <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-between items-center gap-3">
                <div>
                  {appDetail.status === 'AWAITING_APPROVAL' && (
                    <button
                      onClick={() => handleRejectApplication(appDetail.id)}
                      disabled={actionLoading}
                      className="px-3.5 py-2 text-xs font-semibold text-rose-600 hover:text-rose-800 hover:bg-rose-50 rounded-lg transition-colors"
                    >
                      Reject Application
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedAppId(null)}
                    className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg text-xs font-medium hover:bg-slate-100"
                  >
                    Close
                  </button>

                  {appDetail.status === 'AWAITING_APPROVAL' && (
                    <button
                      onClick={() => setShowConfirmModal(true)}
                      disabled={actionLoading}
                      className="inline-flex items-center px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
                    >
                      <Send className="w-3.5 h-3.5 mr-1.5" />
                      Approve &amp; Submit (Dry Run)
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Confirmation Modal */}
        {showConfirmModal && selectedAppId && (
          <div className="fixed inset-0 bg-black/60 z-60 flex items-center justify-center p-4 backdrop-blur-2xs">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 border border-slate-200">
              <div className="flex items-center gap-3">
                <span className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl">
                  <ShieldCheck className="w-6 h-6" />
                </span>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Authorize Submission</h3>
                  <p className="text-xs text-slate-500">Human Approval Gate Verification</p>
                </div>
              </div>

              <div className="text-xs text-slate-600 space-y-2 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <p>
                  You are about to authorize submission for <strong>Application #{selectedAppId}</strong>.
                </p>
                <p>
                  <strong>Safety Status:</strong> <code className="text-indigo-600 font-bold">DRY_RUN=true</code> is
                  active. The application packet will be validated, simulated, and logged with full audit evidence.
                </p>
                <p>
                  <strong>Daily Throttle:</strong> {dailyCount} of {dailyLimit} applications processed today.
                </p>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleApproveApplication(selectedAppId)}
                  disabled={actionLoading}
                  className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-xs transition-colors disabled:opacity-50"
                >
                  <Check className={`w-3.5 h-3.5 mr-1.5 ${actionLoading ? 'animate-spin' : ''}`} />
                  {actionLoading ? 'Submitting...' : 'Confirm & Submit'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
