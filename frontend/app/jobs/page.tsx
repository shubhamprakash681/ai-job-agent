'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Job, JobScore, JobSource, ManualJobCreate } from '@/types';
import {
  Briefcase,
  Plus,
  RefreshCw,
  Search,
  ExternalLink,
  MapPin,
  Building,
  DollarSign,
  Clock,
  ShieldAlert,
  X,
  CheckCircle2,
  Sparkles,
  AlertTriangle,
  Award,
  Zap,
} from 'lucide-react';

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [sources, setSources] = useState<JobSource[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('active');

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Manual Job Form
  const [manualForm, setManualForm] = useState<ManualJobCreate>({
    title: '',
    company: '',
    description: '',
    url: '',
    location: 'Mumbai',
    salary: '',
    experience: '3-5 yrs',
  });
  const [savingManual, setSavingManual] = useState(false);
  const [formMessage, setFormMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Ingestion & Processing Trigger State
  const [fetchingJobs, setFetchingJobs] = useState(false);
  const [processingBatch, setProcessingBatch] = useState(false);
  const [classifyingId, setClassifyingId] = useState<number | null>(null);
  const [alertMessage, setAlertMessage] = useState<{ type: 'info' | 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSources();
    fetchJobsList();
  }, [sourceFilter, statusFilter]);

  const loadSources = async () => {
    try {
      const srcList = await api.getJobSources();
      setSources(srcList);
    } catch (e) {
      console.error('Failed to load sources', e);
    }
  };

  const fetchJobsList = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (sourceFilter) params.source = sourceFilter;
      if (statusFilter && statusFilter !== 'all') params.status = statusFilter;
      if (search.trim()) params.search = search.trim();

      const res = await api.getJobs(params);
      setJobs(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobsList();
  };

  const handleCreateManualJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualForm.title.trim()) return;

    setSavingManual(true);
    setFormMessage(null);
    try {
      const res = await api.createManualJob(manualForm);
      setFormMessage({
        type: res.is_new ? 'success' : 'error',
        text: res.message,
      });
      if (res.is_new) {
        setManualForm({
          title: '',
          company: '',
          description: '',
          url: '',
          location: 'Mumbai',
          salary: '',
          experience: '3-5 yrs',
        });
        await fetchJobsList();
        setTimeout(() => setShowAddModal(false), 1200);
      }
    } catch (err: any) {
      setFormMessage({ type: 'error', text: err.message || 'Failed to add job' });
    } finally {
      setSavingManual(false);
    }
  };

  const handleTriggerFetch = async () => {
    setFetchingJobs(true);
    setAlertMessage(null);
    try {
      const res = await api.fetchJobs({
        keyword: 'Java Spring Boot',
        location: 'Mumbai',
        limit: 15,
      });
      setAlertMessage({
        type: 'success',
        text: `Discovery complete: ${res.new_jobs_saved} new jobs added, ${res.duplicates_skipped} duplicates skipped.`,
      });
      await fetchJobsList();
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Error fetching jobs: ${err.message || 'Failed'}` });
    } finally {
      setFetchingJobs(false);
    }
  };

  const handleClassifyJob = async (jobId: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setClassifyingId(jobId);
    try {
      const res = await api.classifyJob(jobId);
      // Update jobs list state
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, status: res.job.status, score: res.score } : j))
      );
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob({ ...selectedJob, status: res.job.status, score: res.score });
      }
      setAlertMessage({
        type: 'success',
        text: `Job #${jobId} classified: ${res.score.fit_category} (${res.score.total_score}%) — Variant: ${res.score.recommended_variant}`,
      });
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Classification failed: ${err.message || 'Error'}` });
    } finally {
      setClassifyingId(null);
    }
  };

  const handleProcessPending = async () => {
    setProcessingBatch(true);
    setAlertMessage(null);
    try {
      const res = await api.processPendingJobs(50);
      setAlertMessage({
        type: 'success',
        text: `Processing complete: ${res.total_processed} jobs evaluated (${res.passed} passed prefilters, ${res.rejected} rejected).`,
      });
      await fetchJobsList();
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Batch processing failed: ${err.message || 'Error'}` });
    } finally {
      setProcessingBatch(false);
    }
  };

  const formatSalary = (min: number | null, max: number | null, currency: string) => {
    if (!min && !max) return 'Not Disclosed';
    if (currency === 'INR') {
      const minLpa = min ? (min / 100000).toFixed(0) : '';
      const maxLpa = max ? (max / 100000).toFixed(0) : '';
      if (minLpa && maxLpa && minLpa !== maxLpa) return `₹${minLpa} - ₹${maxLpa} LPA`;
      if (minLpa) return `₹${minLpa} LPA`;
    }
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    return `$${(min || max)?.toLocaleString()}`;
  };

  const parseJsonArray = (val: string | null | undefined): string[] => {
    if (!val) return [];
    try {
      const parsed = JSON.parse(val);
      return Array.isArray(parsed) ? parsed : [val];
    } catch {
      return [val];
    }
  };

  const renderFitBadge = (score?: JobScore | null) => {
    if (!score || score.fit_category === null) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
          Unclassified
        </span>
      );
    }
    const cat = score.fit_category.toUpperCase();
    if (cat === 'HIGH_FIT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <Sparkles className="w-3 h-3 mr-1 text-emerald-600" />
          High Fit ({score.total_score}%)
        </span>
      );
    }
    if (cat === 'MODERATE_FIT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
          Moderate ({score.total_score}%)
        </span>
      );
    }
    if (cat === 'LOW_FIT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
          Low Fit ({score.total_score}%)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
        Rejected ({score.total_score}%)
      </span>
    );
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Title and Action Buttons */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Briefcase className="w-6 h-6 mr-2 text-blue-600" /> Job Opportunities
            </h2>
            <p className="text-gray-500 text-sm mt-0.5">
              {total} opportunities ingested across verified boards and manual entries.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={handleProcessPending}
              disabled={processingBatch}
              className="flex items-center px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-sm font-medium rounded-lg border border-indigo-200 transition-colors disabled:opacity-50"
              title="Run prefilters and AI classification on unclassified jobs"
            >
              <Zap className={`w-4 h-4 mr-1.5 ${processingBatch ? 'animate-spin' : 'text-indigo-600'}`} />
              {processingBatch ? 'Classifying...' : 'Classify Unprocessed'}
            </button>

            <button
              onClick={handleTriggerFetch}
              disabled={fetchingJobs}
              className="flex items-center px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg border border-slate-300 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-1.5 ${fetchingJobs ? 'animate-spin' : ''}`} />
              {fetchingJobs ? 'Discovering...' : 'Discover Jobs'}
            </button>

            <button
              onClick={() => {
                setFormMessage(null);
                setShowAddModal(true);
              }}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
            >
              <Plus className="w-4 h-4 mr-1.5" /> Add Job Manually
            </button>
          </div>
        </div>

        {alertMessage && (
          <div
            className={`p-3 text-sm rounded-lg flex items-center justify-between border ${
              alertMessage.type === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : alertMessage.type === 'error'
                ? 'bg-rose-50 border-rose-200 text-rose-800'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}
          >
            <span>{alertMessage.text}</span>
            <button onClick={() => setAlertMessage(null)} className="text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Source Badges */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="font-semibold text-gray-500 mr-1">Active Adapters:</span>
          {sources.map((src) => (
            <span
              key={src.source}
              className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-700 font-medium"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
              {src.source.toUpperCase()}
            </span>
          ))}
          <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-amber-50 border border-amber-200 text-amber-700 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></span>
            LINKEDIN (MANUAL ONLY - SAFE)
          </span>
        </div>

        {/* Search and Filters Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search jobs by title, company, or skills..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 text-black"
              />
            </div>

            <div className="flex gap-2">
              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                aria-label="Filter by Source"
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Sources</option>
                {sources.map((s) => (
                  <option key={s.source} value={s.source}>
                    {s.source.toUpperCase()}
                  </option>
                ))}
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                aria-label="Filter by Status"
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">Active Only</option>
                <option value="all">All Statuses</option>
                <option value="rejected_fit">Rejected (Fit)</option>
                <option value="rejected_prefilter">Rejected (Prefilter)</option>
                <option value="closed">Closed</option>
              </select>

              <button
                type="submit"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-sm font-medium transition-colors"
              >
                Filter
              </button>
            </div>
          </form>
        </div>

        {/* Jobs List Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
              Loading opportunities...
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center text-gray-500 space-y-3">
              <Briefcase className="w-12 h-12 text-gray-300 mx-auto stroke-1" />
              <h4 className="text-base font-medium text-gray-800">No jobs discovered yet</h4>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                Use &quot;Add Job Manually&quot; to paste an opportunity, or click &quot;Discover Jobs&quot; to run the source adapters.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
                  <tr>
                    <th className="py-3 px-6 text-left">Role & Company</th>
                    <th className="py-3 px-4 text-left">Candidate Fit</th>
                    <th className="py-3 px-4 text-left">Location</th>
                    <th className="py-3 px-4 text-left">Experience</th>
                    <th className="py-3 px-4 text-left">Salary</th>
                    <th className="py-3 px-4 text-left">Skills</th>
                    <th className="py-3 px-4 text-left">Source</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {jobs.map((job) => {
                    const locationsList = parseJsonArray(job.locations);
                    const skillsList = parseJsonArray(job.skills);
                    const isClassifying = classifyingId === job.id;

                    return (
                      <tr
                        key={job.id}
                        onClick={() => setSelectedJob(job)}
                        className="hover:bg-slate-50 cursor-pointer transition-colors"
                      >
                        <td className="py-4 px-6">
                          <div className="font-bold text-gray-900">{job.title}</div>
                          <div className="text-xs text-gray-600 flex items-center mt-0.5">
                            <Building className="w-3.5 h-3.5 mr-1 text-gray-400" />
                            {job.company || 'Unknown Company'}
                          </div>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          {renderFitBadge(job.score)}
                          {job.score?.recommended_variant && (
                            <div className="text-[11px] text-slate-500 font-mono mt-1">
                              {job.score.recommended_variant}
                            </div>
                          )}
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          <div className="flex items-center text-xs text-gray-700">
                            <MapPin className="w-3.5 h-3.5 mr-1 text-gray-400" />
                            {locationsList.join(', ') || 'Mumbai'}
                          </div>
                          {job.remote && (
                            <span className="inline-block text-xs text-indigo-700 bg-indigo-50 font-medium px-2 py-0.5 rounded mt-1">
                              Remote
                            </span>
                          )}
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap text-xs text-gray-700">
                          {job.experience_min ? `${job.experience_min} - ${job.experience_max || '+'} yrs` : 'Not specified'}
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap text-xs font-medium text-gray-900">
                          {formatSalary(job.salary_min, job.salary_max, job.currency)}
                        </td>

                        <td className="py-4 px-4 max-w-xs">
                          <div className="flex flex-wrap gap-1">
                            {skillsList.slice(0, 3).map((s) => (
                              <span key={s} className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                                {s}
                              </span>
                            ))}
                            {skillsList.length > 3 && (
                              <span className="text-xs text-gray-400 font-mono">+{skillsList.length - 3}</span>
                            )}
                          </div>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          <span className="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 uppercase">
                            {job.source}
                          </span>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap text-right text-xs">
                          {!job.score ? (
                            <button
                              onClick={(e) => handleClassifyJob(job.id, e)}
                              disabled={isClassifying}
                              className="inline-flex items-center px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded text-xs border border-indigo-200 transition-colors mr-2 disabled:opacity-50"
                            >
                              <Zap className={`w-3 h-3 mr-1 ${isClassifying ? 'animate-spin' : ''}`} />
                              {isClassifying ? 'Classifying...' : 'Classify'}
                            </button>
                          ) : (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedJob(job);
                              }}
                              className="text-blue-600 hover:text-blue-800 font-medium mr-2"
                            >
                              Details
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal: Add Job Manually */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center pb-2 border-b border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <Plus className="w-5 h-5 mr-2 text-blue-600" /> Ingest Opportunity Manually
                </h3>
                <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {formMessage && (
                <div
                  className={`p-3 rounded-lg text-xs font-medium flex items-center ${
                    formMessage.type === 'success'
                      ? 'bg-green-50 text-green-800 border border-green-200'
                      : 'bg-red-50 text-red-800 border border-red-200'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4 mr-1.5 shrink-0" />
                  {formMessage.text}
                </div>
              )}

              <form onSubmit={handleCreateManualJob} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Job Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Senior Java Developer"
                    value={manualForm.title}
                    onChange={(e) => setManualForm({ ...manualForm, title: e.target.value })}
                    className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Company</label>
                    <input
                      type="text"
                      placeholder="e.g. Acme Corp"
                      value={manualForm.company || ''}
                      onChange={(e) => setManualForm({ ...manualForm, company: e.target.value })}
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Location</label>
                    <input
                      type="text"
                      placeholder="e.g. Mumbai or Remote"
                      value={manualForm.location || ''}
                      onChange={(e) => setManualForm({ ...manualForm, location: e.target.value })}
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Experience Requirement</label>
                    <input
                      type="text"
                      placeholder="e.g. 3-5 yrs"
                      value={manualForm.experience || ''}
                      onChange={(e) => setManualForm({ ...manualForm, experience: e.target.value })}
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Salary Range</label>
                    <input
                      type="text"
                      placeholder="e.g. ₹18L - ₹24L or $120k"
                      value={manualForm.salary || ''}
                      onChange={(e) => setManualForm({ ...manualForm, salary: e.target.value })}
                      className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Job or Apply URL</label>
                  <input
                    type="url"
                    placeholder="https://..."
                    value={manualForm.url || ''}
                    onChange={(e) =>
                      setManualForm({ ...manualForm, url: e.target.value, application_url: e.target.value })
                    }
                    className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Job Description / Requirements (Skills are auto-extracted)
                  </label>
                  <textarea
                    rows={5}
                    placeholder="Paste the full job description or requirements here..."
                    value={manualForm.description || ''}
                    onChange={(e) => setManualForm({ ...manualForm, description: e.target.value })}
                    className="w-full text-sm font-mono border border-gray-300 rounded-lg p-3 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={savingManual}
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {savingManual ? 'Saving & Deduplicating...' : 'Ingest Opportunity'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Job Details & AI Classification Breakdown */}
        {selectedJob && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 space-y-4 max-h-[88vh] overflow-y-auto">
              <div className="flex justify-between items-start pb-3 border-b border-gray-100">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{selectedJob.title}</h3>
                  <p className="text-sm font-medium text-gray-600 mt-0.5">{selectedJob.company || 'Unknown Company'}</p>
                </div>
                <button onClick={() => setSelectedJob(null)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* AI Classification & Match Breakdown Card */}
              {selectedJob.score ? (
                <div className="bg-gradient-to-br from-slate-50 to-indigo-50/40 border border-indigo-100 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-5 h-5 text-indigo-600" />
                      <span className="font-bold text-sm text-indigo-950">AI Fit Analysis</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {renderFitBadge(selectedJob.score)}
                      <button
                        onClick={() => handleClassifyJob(selectedJob.id)}
                        disabled={classifyingId === selectedJob.id}
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-medium underline"
                      >
                        {classifyingId === selectedJob.id ? 'Re-evaluating...' : 'Re-classify'}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs bg-white p-3 rounded-lg border border-slate-200">
                    <div>
                      <span className="text-gray-500 block">Recommended Variant:</span>
                      <span className="font-semibold text-gray-900 font-mono">
                        {selectedJob.score.recommended_variant || 'java-backend'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block">Match Score:</span>
                      <span className="font-bold text-gray-900 text-sm">
                        {selectedJob.score.total_score} / 100
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block">Role Relevance:</span>
                      <span className="font-semibold text-gray-900">
                        {selectedJob.score.role_relevance} / 25
                      </span>
                    </div>
                  </div>

                  {/* Reasoning */}
                  {selectedJob.score.reasoning && (
                    <div className="text-xs bg-white p-3 rounded-lg border border-slate-200">
                      <span className="font-semibold text-slate-700 block mb-1">Fit Assessment Rationale:</span>
                      <p className="text-slate-600 italic">&ldquo;{selectedJob.score.reasoning}&rdquo;</p>
                    </div>
                  )}

                  {/* Strengths and Gaps */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    {selectedJob.score.strengths && (
                      <div className="bg-emerald-50/80 border border-emerald-200 p-2.5 rounded-lg">
                        <span className="font-semibold text-emerald-900 block mb-1">Matched Skills:</span>
                        <div className="flex flex-wrap gap-1">
                          {parseJsonArray(selectedJob.score.strengths).map((s) => (
                            <span key={s} className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-[11px] font-medium">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedJob.score.gaps && (
                      <div className="bg-amber-50/80 border border-amber-200 p-2.5 rounded-lg">
                        <span className="font-semibold text-amber-900 block mb-1">Missing / Gap Skills:</span>
                        <div className="flex flex-wrap gap-1">
                          {parseJsonArray(selectedJob.score.gaps).map((s) => (
                            <span key={s} className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[11px] font-medium">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Risks */}
                  {selectedJob.score.risks && parseJsonArray(selectedJob.score.risks).length > 0 && (
                    <div className="bg-rose-50 border border-rose-200 p-2.5 rounded-lg text-xs">
                      <span className="font-semibold text-rose-900 flex items-center mb-1">
                        <AlertTriangle className="w-3.5 h-3.5 mr-1 text-rose-600" /> Flags & Risks:
                      </span>
                      <ul className="list-disc list-inside text-rose-800 space-y-0.5">
                        {parseJsonArray(selectedJob.score.risks).map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
                  <div>
                    <h4 className="text-sm font-bold text-gray-800 flex items-center">
                      <Sparkles className="w-4 h-4 mr-1.5 text-indigo-600" /> AI Classification Pending
                    </h4>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Evaluate this opportunity against Shubham&apos;s verified skills and experience.
                    </p>
                  </div>
                  <button
                    onClick={() => handleClassifyJob(selectedJob.id)}
                    disabled={classifyingId === selectedJob.id}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors flex items-center shrink-0 disabled:opacity-50"
                  >
                    <Zap className={`w-3.5 h-3.5 mr-1.5 ${classifyingId === selectedJob.id ? 'animate-spin' : ''}`} />
                    {classifyingId === selectedJob.id ? 'Classifying...' : 'Classify Fit Now'}
                  </button>
                </div>
              )}

              {/* Metadata pill bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3 rounded-lg text-xs">
                <div>
                  <span className="text-gray-500 block">Location:</span>
                  <span className="font-semibold text-gray-800">
                    {parseJsonArray(selectedJob.locations).join(', ') || 'Mumbai'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Salary:</span>
                  <span className="font-semibold text-gray-800">
                    {formatSalary(selectedJob.salary_min, selectedJob.salary_max, selectedJob.currency)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Experience:</span>
                  <span className="font-semibold text-gray-800">
                    {selectedJob.experience_min ? `${selectedJob.experience_min}+ yrs` : 'Not specified'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Source:</span>
                  <span className="font-semibold uppercase text-blue-700">{selectedJob.source}</span>
                </div>
              </div>

              {/* Skills */}
              <div>
                <h4 className="text-xs font-bold text-gray-700 uppercase mb-2">Detected Technologies & Skills</h4>
                <div className="flex flex-wrap gap-1.5">
                  {parseJsonArray(selectedJob.skills).map((skill) => (
                    <span
                      key={skill}
                      className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-md font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="text-xs font-bold text-gray-700 uppercase mb-2">Job Description</h4>
                <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg text-xs font-mono text-gray-800 whitespace-pre-wrap max-h-52 overflow-y-auto leading-relaxed">
                  {selectedJob.description || 'No description provided.'}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                <div className="text-xs text-gray-400">Job ID: #{selectedJob.id}</div>
                <div className="space-x-2">
                  <button
                    onClick={() => setSelectedJob(null)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Close
                  </button>
                  {selectedJob.application_url && (
                    <a
                      href={selectedJob.application_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium"
                    >
                      <ExternalLink className="w-3.5 h-3.5 mr-1.5" /> Open Application Link
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
