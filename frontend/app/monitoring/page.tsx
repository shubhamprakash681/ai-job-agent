'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import {
  FollowupItem,
  FollowupListResponse,
  FollowupDraftResponse,
  EmailParseResponse,
  InAppNotification,
  Application,
} from '@/types';
import {
  Clock,
  Mail,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Copy,
  Check,
  Send,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  Bell,
  Inbox,
  Video,
  Code,
  FileCheck,
  X,
} from 'lucide-react';
import clsx from 'clsx';

function MonitoringContent() {
  const searchParams = useSearchParams();
  const initialTab = searchParams.get('tab') || 'radar';
  const [activeTab, setActiveTab] = useState<'radar' | 'email' | 'notifications'>(
    initialTab === 'notifications' ? 'notifications' : initialTab === 'email' ? 'email' : 'radar'
  );

  const [loading, setLoading] = useState(true);
  const [followupsData, setFollowupsData] = useState<FollowupListResponse | null>(null);
  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);

  // Follow-up Email Modal State
  const [selectedFollowup, setSelectedFollowup] = useState<FollowupItem | null>(null);
  const [draftTone, setDraftTone] = useState<'professional' | 'courteous' | 'concise'>('professional');
  const [recipientName, setRecipientName] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [draftLoading, setDraftLoading] = useState(false);
  const [draftResponse, setDraftResponse] = useState<FollowupDraftResponse | null>(null);
  const [copiedDraft, setCopiedDraft] = useState(false);

  // Email Parser State
  const [rawEmailText, setRawEmailText] = useState('');
  const [emailSender, setEmailSender] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [parseLoading, setParseLoading] = useState(false);
  const [parseResult, setParseResult] = useState<EmailParseResponse | null>(null);
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const [targetStatus, setTargetStatus] = useState<string>('INTERVIEW');
  const [applyingMatch, setApplyingMatch] = useState(false);
  const [matchSuccessMsg, setMatchSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    loadAllData();
  }, []);

  async function loadAllData() {
    setLoading(true);
    try {
      const [fRes, nRes, appRes] = await Promise.all([
        api.getFollowups().catch(() => null),
        api.getNotifications().catch(() => ({ items: [], unread_count: 0, total: 0 })),
        api.getApplications({ per_page: '100' }).catch(() => ({ items: [] })),
      ]);

      if (fRes) setFollowupsData(fRes);
      if (nRes) setNotifications(nRes.items || []);
      if (appRes) setApplications(appRes.items || []);
    } catch (err) {
      console.error('Error loading monitoring data:', err);
    } finally {
      setLoading(false);
    }
  }

  // Generate Followup Email Draft
  async function handleGenerateDraft(item: FollowupItem, tone = draftTone) {
    setSelectedFollowup(item);
    setDraftTone(tone);
    setDraftLoading(true);
    setCopiedDraft(false);
    try {
      const draft = await api.draftFollowup(item.application_id, {
        tone,
        recipient_name: recipientName || undefined,
        recipient_email: recipientEmail || undefined,
      });
      setDraftResponse(draft);
    } catch (err: any) {
      alert(err.message || 'Failed to generate draft');
    } finally {
      setDraftLoading(false);
    }
  }

  // Copy Draft Body to Clipboard
  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    setCopiedDraft(true);
    setTimeout(() => setCopiedDraft(false), 2500);
  }

  // Parse Raw Recruiter Email
  async function handleAnalyzeEmail() {
    if (!rawEmailText.trim()) return;
    setParseLoading(true);
    setMatchSuccessMsg(null);
    try {
      const result = await api.parseEmail({
        raw_email_text: rawEmailText,
        sender: emailSender || undefined,
        subject: emailSubject || undefined,
      });
      setParseResult(result);
      if (result.suggested_application_id) {
        setSelectedAppId(result.suggested_application_id);
      }
      if (result.suggested_status) {
        setTargetStatus(result.suggested_status);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to parse email');
    } finally {
      setParseLoading(false);
    }
  }

  // Apply Email Match
  async function handleApplyMatch() {
    if (!parseResult || !selectedAppId) return;
    setApplyingMatch(true);
    try {
      const res = await api.applyEmailMatch({
        application_id: selectedAppId,
        classification: parseResult.classification,
        new_status: targetStatus,
        notes: `Extracted via Email Ingestion. Intent: ${parseResult.classification}. Platform: ${parseResult.key_details.assessment_platform || 'N/A'}`,
        event_metadata: parseResult.key_details,
      });
      setMatchSuccessMsg(`Application #${selectedAppId} successfully updated to ${res.status}!`);
      loadAllData();
    } catch (err: any) {
      alert(err.message || 'Failed to apply email match');
    } finally {
      setApplyingMatch(false);
    }
  }

  // Mark Notification Read
  async function handleMarkRead(id: number) {
    try {
      await api.markNotificationRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    } catch (err) {
      console.error(err);
    }
  }

  // Mark All Notifications Read
  async function handleMarkAllRead() {
    try {
      await api.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Monitoring & Follow-Up Center</h1>
            <p className="text-sm text-gray-500">
              Track application aging, generate grounded follow-up outreach, and classify inbound recruiter emails.
            </p>
          </div>
          <button
            onClick={loadAllData}
            className="flex items-center self-start md:self-auto px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition shadow-sm"
          >
            <RefreshCw className={clsx('w-4 h-4 mr-2', loading && 'animate-spin')} />
            Refresh Radar
          </button>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Needs Follow-Up
              </span>
              <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
                <Clock className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-gray-900">
                {followupsData?.total_needing_followup || 0}
              </span>
              <span className="text-xs text-amber-700 font-medium">applications</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">7-day & 14-day check-in windows</p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                7-Day Window
              </span>
              <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                <Mail className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-blue-700">
                {followupsData?.seven_day_count || 0}
              </span>
              <span className="text-xs text-blue-600 font-medium">ready to check</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">Courteous initial follow-up</p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                14-Day Window
              </span>
              <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
                <Calendar className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-purple-700">
                {followupsData?.fourteen_day_count || 0}
              </span>
              <span className="text-xs text-purple-600 font-medium">second check-in</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">Polite status inquiry</p>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Stale (&gt;30d)
              </span>
              <div className="p-2 bg-gray-50 rounded-lg text-gray-500">
                <AlertTriangle className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-gray-600">
                {followupsData?.stale_count || 0}
              </span>
              <span className="text-xs text-gray-500 font-medium">inactive</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">Consider archiving or closing</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="border-b border-gray-200 flex space-x-8">
          <button
            onClick={() => setActiveTab('radar')}
            className={clsx(
              'pb-4 px-1 text-sm font-semibold border-b-2 transition flex items-center gap-2',
              activeTab === 'radar'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <Clock className="w-4 h-4" />
            Follow-Up Radar
            {(followupsData?.total_needing_followup || 0) > 0 && (
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-amber-100 text-amber-800">
                {followupsData?.total_needing_followup}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('email')}
            className={clsx(
              'pb-4 px-1 text-sm font-semibold border-b-2 transition flex items-center gap-2',
              activeTab === 'email'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <Inbox className="w-4 h-4" />
            Recruiter Email Analyzer
          </button>

          <button
            onClick={() => setActiveTab('notifications')}
            className={clsx(
              'pb-4 px-1 text-sm font-semibold border-b-2 transition flex items-center gap-2',
              activeTab === 'notifications'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <Bell className="w-4 h-4" />
            Alerts & Notifications
            {notifications.filter((n) => !n.read).length > 0 && (
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-red-100 text-red-800">
                {notifications.filter((n) => !n.read).length}
              </span>
            )}
          </button>
        </div>

        {/* TAB 1: Follow-Up Radar */}
        {activeTab === 'radar' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-gray-900">Application Lifecycle Radar</h3>
                <p className="text-xs text-gray-500">
                  Real-time aging monitoring for all submitted and interviewing positions.
                </p>
              </div>
              <div className="flex items-center text-xs text-gray-500 bg-white border border-gray-200 px-3 py-1.5 rounded-lg">
                <ShieldCheck className="w-4 h-4 text-emerald-600 mr-1.5" />
                Zero Spam Guard: Human review required before outreach
              </div>
            </div>

            {loading ? (
              <div className="py-16 text-center text-gray-500">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
                Scanning application aging...
              </div>
            ) : !followupsData?.items.length ? (
              <div className="py-16 text-center text-gray-500">
                <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                <p className="font-semibold text-gray-800">All applications are fresh!</p>
                <p className="text-xs text-gray-400 mt-1">
                  Applications will appear here once submitted and will alert you at the 7-day and 14-day mark.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase">
                    <tr>
                      <th className="px-6 py-3">Company & Role</th>
                      <th className="px-6 py-3">Submission Date</th>
                      <th className="px-6 py-3">Aging Status</th>
                      <th className="px-6 py-3">Recommended Next Step</th>
                      <th className="px-6 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {followupsData.items.map((item) => (
                      <tr key={item.application_id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">{item.company}</div>
                          <div className="text-xs text-gray-500">{item.job_title}</div>
                        </td>
                        <td className="px-6 py-4 text-gray-600 text-xs">
                          {item.applied_at
                            ? new Date(item.applied_at).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })
                            : 'Recently'}
                          <div className="text-gray-400">{item.days_since_applied} day(s) ago</div>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={clsx(
                              'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold',
                              item.followup_type === '7_DAY' && 'bg-blue-100 text-blue-800',
                              item.followup_type === '14_DAY' && 'bg-purple-100 text-purple-800',
                              item.followup_type === '30_DAY_STALE' && 'bg-gray-100 text-gray-700',
                              item.followup_type === 'RECENT' && 'bg-emerald-100 text-emerald-800'
                            )}
                          >
                            {item.followup_type === '7_DAY' && '7-Day Follow-Up'}
                            {item.followup_type === '14_DAY' && '14-Day Check-In'}
                            {item.followup_type === '30_DAY_STALE' && '30+ Days Stale'}
                            {item.followup_type === 'RECENT' && 'Fresh (<7d)'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-600 max-w-xs">
                          {item.suggested_action}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleGenerateDraft(item)}
                            className="inline-flex items-center px-3 py-1.5 border border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg text-xs font-medium transition shadow-sm"
                          >
                            <Mail className="w-3.5 h-3.5 mr-1.5" />
                            Draft Follow-Up
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Recruiter Email Analyzer */}
        {activeTab === 'email' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
              <div>
                <h3 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                  <Inbox className="w-5 h-5 text-blue-600" />
                  Inbound Recruiter Email Ingestion
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Paste incoming recruiter emails, interview requests, coding assessments, or rejections.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Sender Email (Optional)
                  </label>
                  <input
                    type="text"
                    value={emailSender}
                    onChange={(e) => setEmailSender(e.target.value)}
                    placeholder="e.g. recruiter@swiggy.in"
                    className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Email Subject (Optional)
                  </label>
                  <input
                    type="text"
                    value={emailSubject}
                    onChange={(e) => setEmailSubject(e.target.value)}
                    placeholder="e.g. Invitation to Interview"
                    className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Raw Email Body
                </label>
                <textarea
                  rows={8}
                  value={rawEmailText}
                  onChange={(e) => setRawEmailText(e.target.value)}
                  placeholder="Paste the recruiter's email message here..."
                  className="w-full text-xs px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono"
                />
              </div>

              <button
                onClick={handleAnalyzeEmail}
                disabled={parseLoading || !rawEmailText.trim()}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-xs font-semibold rounded-lg flex items-center justify-center transition shadow-sm"
              >
                <Sparkles className={clsx('w-4 h-4 mr-2', parseLoading && 'animate-spin')} />
                {parseLoading ? 'Analyzing Email Intent...' : 'Analyze & Classify Email'}
              </button>
            </div>

            {/* Classification & Action Output */}
            <div className="lg:col-span-6 bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
              <h3 className="text-base font-semibold text-gray-900">Analysis & Status Progression</h3>

              {matchSuccessMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-xs flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 flex-shrink-0 text-emerald-600" />
                  {matchSuccessMsg}
                </div>
              )}

              {!parseResult ? (
                <div className="py-16 text-center text-gray-400">
                  <Inbox className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                  <p className="text-xs">Paste an email on the left and click Analyze to classify.</p>
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  {/* Intent Header */}
                  <div className="p-3.5 bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-gray-500 uppercase tracking-wider text-[11px]">
                        Detected Intent
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <span
                          className={clsx(
                            'px-2.5 py-1 rounded-full font-bold text-xs',
                            parseResult.classification === 'INTERVIEW_INVITATION' && 'bg-emerald-100 text-emerald-800',
                            parseResult.classification === 'ASSESSMENT_REQUEST' && 'bg-purple-100 text-purple-800',
                            parseResult.classification === 'OFFER' && 'bg-green-100 text-green-800',
                            parseResult.classification === 'REJECTION' && 'bg-rose-100 text-rose-800',
                            parseResult.classification === 'APPLICATION_RECEIVED' && 'bg-blue-100 text-blue-800'
                          )}
                        >
                          {parseResult.classification.replace('_', ' ')}
                        </span>
                        <span className="text-gray-400">
                          ({Math.round(parseResult.confidence * 100)}% confidence)
                        </span>
                      </div>
                    </div>
                    {parseResult.company_extracted && (
                      <div className="text-right">
                        <div className="font-semibold text-gray-500 uppercase tracking-wider text-[11px]">
                          Target Company
                        </div>
                        <div className="font-bold text-gray-900 mt-1">{parseResult.company_extracted}</div>
                      </div>
                    )}
                  </div>

                  {/* Extracted Details */}
                  {parseResult.key_details.meeting_links && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="font-semibold text-blue-900 flex items-center gap-1.5 mb-1.5">
                        <Video className="w-4 h-4 text-blue-600" />
                        Meeting & Scheduling Links
                      </div>
                      <div className="space-y-1">
                        {parseResult.key_details.meeting_links.map((link: string, idx: number) => (
                          <a
                            key={idx}
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block text-blue-600 underline truncate hover:text-blue-800"
                          >
                            {link}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {parseResult.key_details.assessment_platform && (
                    <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="font-semibold text-purple-900 flex items-center gap-1.5 mb-1">
                        <Code className="w-4 h-4 text-purple-600" />
                        Online Assessment Platform
                      </div>
                      <div>Platform: <strong>{parseResult.key_details.assessment_platform}</strong></div>
                      {parseResult.key_details.deadline && (
                        <div className="mt-0.5 text-purple-700">Deadline hint: {parseResult.key_details.deadline}</div>
                      )}
                    </div>
                  )}

                  {/* Application Correlation */}
                  <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
                    <label className="block font-semibold text-gray-700">
                      Match to Active Application
                    </label>
                    <select
                      value={selectedAppId || ''}
                      onChange={(e) => setSelectedAppId(Number(e.target.value) || null)}
                      className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg bg-white"
                    >
                      <option value="">-- Select matching application --</option>
                      {applications.map((app) => (
                        <option key={app.id} value={app.id}>
                          #{app.id} — {app.job_company || 'Company'} ({app.job_title || 'Role'}) [{app.status}]
                        </option>
                      ))}
                    </select>
                    {parseResult.match_rationale && (
                      <p className="text-[11px] text-gray-500">{parseResult.match_rationale}</p>
                    )}
                  </div>

                  {/* Lifecycle State Transition */}
                  <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
                    <label className="block font-semibold text-gray-700">
                      Target Lifecycle State
                    </label>
                    <select
                      value={targetStatus}
                      onChange={(e) => setTargetStatus(e.target.value)}
                      className="w-full text-xs px-3 py-2 border border-gray-300 rounded-lg bg-white"
                    >
                      <option value="INTERVIEW">INTERVIEW (Schedule Screen / Technical Round)</option>
                      <option value="OFFER">OFFER (Offer Received)</option>
                      <option value="REJECTED">REJECTED (Candidate Not Moving Forward)</option>
                      <option value="APPLIED">APPLIED (Application Acknowledged)</option>
                    </select>
                  </div>

                  <button
                    onClick={handleApplyMatch}
                    disabled={applyingMatch || !selectedAppId}
                    className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-semibold rounded-lg flex items-center justify-center transition shadow-sm"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {applyingMatch ? 'Applying Update...' : 'Apply Status Update & Record Event'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: Notifications */}
        {activeTab === 'notifications' && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-gray-900">In-App Alerts & Follow-Up Reminders</h3>
                <p className="text-xs text-gray-500">
                  System alerts for aging applications, scheduled interviews, and recruiter communication.
                </p>
              </div>
              <button
                onClick={handleMarkAllRead}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
              >
                Mark All as Read
              </button>
            </div>

            {!notifications.length ? (
              <div className="py-16 text-center text-gray-400">
                <Bell className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                <p className="text-xs">No notifications yet. Alerts will appear here automatically.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 text-xs">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={clsx(
                      'p-4 flex items-start justify-between transition',
                      !n.read ? 'bg-blue-50/40' : 'hover:bg-gray-50'
                    )}
                  >
                    <div className="space-y-1 max-w-xl">
                      <div className="flex items-center gap-2">
                        {!n.read && (
                          <span className="w-2 h-2 rounded-full bg-blue-600 flex-shrink-0" />
                        )}
                        <span className="font-semibold text-gray-900">{n.title}</span>
                        <span className="text-gray-400 text-[11px]">
                          {new Date(n.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-600">{n.message}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      {!n.read && (
                        <button
                          onClick={() => handleMarkRead(n.id)}
                          className="px-2.5 py-1 text-gray-500 hover:text-gray-800 border border-gray-200 rounded text-[11px] bg-white"
                        >
                          Mark Read
                        </button>
                      )}
                      {n.action_url && (
                        <a
                          href={n.action_url}
                          className="px-2.5 py-1 bg-blue-600 text-white rounded text-[11px] hover:bg-blue-700"
                        >
                          View
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* FOLLOW-UP DRAFT MODAL */}
      {selectedFollowup && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div>
                <h3 className="font-semibold text-gray-900">
                  Follow-Up Email Draft — {selectedFollowup.company}
                </h3>
                <p className="text-xs text-gray-500">
                  {selectedFollowup.job_title} ({selectedFollowup.days_since_applied} days since application)
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedFollowup(null);
                  setDraftResponse(null);
                }}
                className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-4">
              {/* Tone Selection Pills */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-500">Tone:</span>
                {(['professional', 'courteous', 'concise'] as const).map((tone) => (
                  <button
                    key={tone}
                    onClick={() => handleGenerateDraft(selectedFollowup, tone)}
                    className={clsx(
                      'px-3 py-1 rounded-full text-xs font-medium capitalize transition',
                      draftTone === tone
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    )}
                  >
                    {tone}
                  </button>
                ))}
              </div>

              {/* Recipient Details */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-gray-700 font-medium mb-1">Recipient Name</label>
                  <input
                    type="text"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    placeholder="e.g. Hiring Team or Priya"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 font-medium mb-1">Recipient Email</label>
                  <input
                    type="email"
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    placeholder="e.g. talent@company.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>

              {draftLoading ? (
                <div className="py-12 text-center text-gray-500">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
                  Generating grounded follow-up draft...
                </div>
              ) : draftResponse ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Subject</label>
                    <input
                      type="text"
                      readOnly
                      value={draftResponse.subject}
                      className="w-full text-xs px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-800 font-medium"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      Email Body (Edit or Copy)
                    </label>
                    <textarea
                      rows={10}
                      value={draftResponse.body}
                      onChange={(e) =>
                        setDraftResponse({ ...draftResponse, body: e.target.value })
                      }
                      className="w-full text-xs p-3 border border-gray-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>

                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-[11px] text-emerald-800 flex items-start">
                    <ShieldCheck className="w-4 h-4 mr-2 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong>Strict Candidate Ground Truth verified</strong>: Shubham Prakash (~3.2 years
                      experience at TCS Digital & Accenture, Java/Spring Boot/Kafka/React, 30-day notice).
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
              <span className="text-xs text-gray-400">
                Draft will never be sent automatically without your explicit action.
              </span>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    setSelectedFollowup(null);
                    setDraftResponse(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Close
                </button>
                {draftResponse && (
                  <button
                    onClick={() => copyToClipboard(draftResponse.body)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center transition shadow-sm"
                  >
                    {copiedDraft ? (
                      <>
                        <Check className="w-4 h-4 mr-1.5" />
                        Copied to Clipboard!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-1.5" />
                        Copy Email Draft
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default function MonitoringPage() {
  return (
    <Suspense
      fallback={
        <DashboardLayout>
          <div className="py-24 text-center text-gray-500">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
            <p className="text-sm font-medium">Loading Monitoring Center...</p>
          </div>
        </DashboardLayout>
      }
    >
      <MonitoringContent />
    </Suspense>
  );
}


