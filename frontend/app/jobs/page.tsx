'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { Job, JobScore, JobSource, ManualJobCreate, CoverLetterResponse } from '@/types';
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
  SlidersHorizontal,
  ChevronRight,
  FileCheck,
  FileText,
  Download,
  Copy,
  Check,
  Edit3,
  Send,
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
  const [minScoreFilter, setMinScoreFilter] = useState('');

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Cover Letter Studio State
  const [coverLetterModalOpen, setCoverLetterModalOpen] = useState(false);
  const [coverLetterJob, setCoverLetterJob] = useState<Job | null>(null);
  const [coverLetterData, setCoverLetterData] = useState<CoverLetterResponse | null>(null);
  const [coverLetterTone, setCoverLetterTone] = useState<string>('technical');
  const [coverLetterDraft, setCoverLetterDraft] = useState<string>('');
  const [coverLetterLoading, setCoverLetterLoading] = useState(false);
  const [coverLetterSaving, setCoverLetterSaving] = useState(false);
  const [coverLetterCopied, setCoverLetterCopied] = useState(false);
  const [coverLetterTab, setCoverLetterTab] = useState<'editor' | 'preview'>('editor');
  const [coverLetterMessage, setCoverLetterMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);
  const [tailoringId, setTailoringId] = useState<number | null>(null);
  const [preparingAppId, setPreparingAppId] = useState<number | null>(null);
  const [alertMessage, setAlertMessage] = useState<{ type: 'info' | 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSources();
    fetchJobsList();
  }, [sourceFilter, statusFilter, minScoreFilter]);

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
      if (minScoreFilter) params.min_score = minScoreFilter;
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

  const handleAnalyzeJob = async (jobId: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setAnalyzingId(jobId);
    try {
      const updatedScore = await api.analyzeJob(jobId);
      setJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, score: updatedScore } : j))
      );
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob({ ...selectedJob, score: updatedScore });
      }
      setAlertMessage({
        type: 'success',
        text: `Multi-dimensional analysis complete: Match score ${updatedScore.total_score}/100 (${updatedScore.fit_category}).`,
      });
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Analysis failed: ${err.message || 'Error'}` });
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleTailorResume = async (jobId: number, variantId?: string) => {
    setTailoringId(jobId);
    try {
      const res = await api.tailorResume(jobId, variantId);
      setAlertMessage({
        type: 'success',
        text: `ATS Resume tailored for Job #${jobId} (v${res.version_number})! Validation: ${res.validation_status?.toUpperCase()} (${Math.round((res.confidence_score || 1) * 100)}% confidence). View in Resumes tab.`,
      });
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Resume tailoring failed: ${err.message || 'Error'}` });
    } finally {
      setTailoringId(null);
    }
  };

  const handleOpenCoverLetter = async (job: Job) => {
    setCoverLetterJob(job);
    setCoverLetterModalOpen(true);
    setCoverLetterLoading(true);
    setCoverLetterMessage(null);
    setCoverLetterTone('technical');
    try {
      const res = await api.getCoverLetter(job.id);
      setCoverLetterData(res);
      setCoverLetterDraft(res.content_markdown);
    } catch (err: any) {
      try {
        const genRes = await api.generateCoverLetter(job.id, 'technical');
        setCoverLetterData(genRes);
        setCoverLetterDraft(genRes.content_markdown);
      } catch (genErr: any) {
        setCoverLetterMessage({ type: 'error', text: genErr.message || 'Failed to load cover letter' });
      }
    } finally {
      setCoverLetterLoading(false);
    }
  };

  const handleRegenerateCoverLetter = async (tone?: string) => {
    if (!coverLetterJob) return;
    const targetTone = tone || coverLetterTone;
    setCoverLetterLoading(true);
    setCoverLetterMessage(null);
    try {
      const res = await api.generateCoverLetter(coverLetterJob.id, targetTone);
      setCoverLetterData(res);
      setCoverLetterDraft(res.content_markdown);
      setCoverLetterTone(targetTone);
      setCoverLetterMessage({ type: 'success', text: `Cover letter regenerated with ${targetTone} tone!` });
    } catch (err: any) {
      setCoverLetterMessage({ type: 'error', text: err.message || 'Failed to generate cover letter' });
    } finally {
      setCoverLetterLoading(false);
    }
  };

  const handleSaveCoverLetter = async () => {
    if (!coverLetterJob || !coverLetterDraft.trim()) return;
    setCoverLetterSaving(true);
    setCoverLetterMessage(null);
    try {
      const res = await api.updateCoverLetter(coverLetterJob.id, coverLetterDraft);
      setCoverLetterData(res);
      setCoverLetterMessage({ type: 'success', text: 'Cover letter saved & PDF updated successfully!' });
    } catch (err: any) {
      setCoverLetterMessage({ type: 'error', text: err.message || 'Failed to save cover letter' });
    } finally {
      setCoverLetterSaving(false);
    }
  };

  const handleCopyCoverLetter = () => {
    if (!coverLetterDraft) return;
    navigator.clipboard.writeText(coverLetterDraft);
    setCoverLetterCopied(true);
    setTimeout(() => setCoverLetterCopied(false), 2000);
  };

  const handlePrepareApplication = async (jobId: number) => {
    setPreparingAppId(jobId);
    try {
      const detail = await api.prepareApplication(jobId);
      setAlertMessage({
        type: 'success',
        text: `Application packet prepared for ${detail.job_company || 'Job'}! Resume, cover letter, and screening questions bundled (Status: ${detail.status}). Navigate to Applications tab to review and authorize.`,
      });
      if (selectedJob && selectedJob.id === jobId) {
        setSelectedJob(null);
      }
    } catch (err: any) {
      setAlertMessage({ type: 'error', text: `Failed to prepare application: ${err.message || 'Error'}` });
    } finally {
      setPreparingAppId(null);
    }
  };

  const handleProcessPending = async () => {
    setProcessingBatch(true);
    setAlertMessage(null);
    try {
      const res = await api.processPendingJobs(50);
      setAlertMessage({
        type: 'success',
        text: `Processing complete: ${res.total_processed} jobs evaluated (${res.passed} passed, ${res.rejected} rejected).`,
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
    if (cat === 'AUTO_PREPARE' || (score.total_score >= 85 && cat === 'HIGH_FIT')) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <Sparkles className="w-3 h-3 mr-1 text-emerald-600" />
          Auto-Prepare ({score.total_score}%)
        </span>
      );
    }
    if (cat === 'HIGH_PRIORITY' || (score.total_score >= 70 && cat === 'HIGH_FIT')) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
          <Award className="w-3 h-3 mr-1 text-indigo-600" />
          High Priority ({score.total_score}%)
        </span>
      );
    }
    if (cat === 'GOOD' || cat === 'MODERATE_FIT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
          Good Fit ({score.total_score}%)
        </span>
      );
    }
    if (cat === 'OPTIONAL' || cat === 'LOW_FIT') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
          Optional ({score.total_score}%)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
        Ignore ({score.total_score}%)
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
              {processingBatch ? 'Processing...' : 'Process Unclassified'}
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

        {/* Search and Multi-Dimensional Filters Bar */}
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

            <div className="flex flex-wrap gap-2">
              <select
                value={minScoreFilter}
                onChange={(e) => setMinScoreFilter(e.target.value)}
                aria-label="Filter by Match Score"
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-700 outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any Match Score</option>
                <option value="85">85%+ (Auto-Prepare)</option>
                <option value="70">70%+ (High Priority)</option>
                <option value="50">50%+ (Good Fit)</option>
                <option value="30">30%+ (Viable)</option>
              </select>

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
              <h4 className="text-base font-medium text-gray-800">No jobs found</h4>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                Try adjusting your filters or click &quot;Discover Jobs&quot; to fetch fresh opportunities.
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
                            <>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleOpenCoverLetter(job);
                                }}
                                className="text-indigo-600 hover:text-indigo-800 font-medium mr-2"
                              >
                                Cover Letter
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedJob(job);
                                }}
                                className="text-blue-600 hover:text-blue-800 font-medium mr-2"
                              >
                                Details
                              </button>
                            </>
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

        {/* Modal: Job Details & Multi-Dimensional Scoring Breakdown */}
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

              {/* Multi-Dimensional Match Breakdown Card */}
              {selectedJob.score ? (
                <div className="bg-gradient-to-br from-slate-50 to-indigo-50/40 border border-indigo-100 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-5 h-5 text-indigo-600" />
                      <span className="font-bold text-sm text-indigo-950">100-Point Candidate Fit Analysis</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {renderFitBadge(selectedJob.score)}
                      <button
                        onClick={() => handleAnalyzeJob(selectedJob.id)}
                        disabled={analyzingId === selectedJob.id}
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-medium underline disabled:opacity-50"
                      >
                        {analyzingId === selectedJob.id ? 'Analyzing...' : 'Deep Re-Score'}
                      </button>
                    </div>
                  </div>

                  {/* 6-Dimension Progress Breakdown */}
                  <div className="bg-white p-3.5 rounded-lg border border-slate-200 space-y-2.5 text-xs">
                    <div className="font-semibold text-slate-700 flex justify-between items-center">
                      <span>Multi-Dimensional Score Breakdown</span>
                      <span className="text-indigo-600 font-bold text-sm">{selectedJob.score.total_score} / 100 pts</span>
                    </div>

                    {/* Dim 1: Role Relevance (25) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>1. Role Relevance (Java / Fullstack)</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.role_relevance} / 25 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.role_relevance / 25) * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Dim 2: Core Skills (25) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>2. Core Tech Stack (Java, Spring Boot, React, SQL)</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.core_skills} / 25 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-emerald-600 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.core_skills / 25) * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Dim 3: Distributed Systems (15) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>3. Distributed Systems & Scale (Kafka, Redis, WebSockets)</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.distributed_systems} / 15 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-purple-600 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.distributed_systems / 15) * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Dim 4: Experience Fit (15) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>4. Experience Level (~3.2 yrs candidate profile)</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.experience_fit} / 15 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-amber-500 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.experience_fit / 15) * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Dim 5: Location Fit (10) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>5. Location & Remote Work Mode</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.location_score} / 10 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-teal-600 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.location_score / 10) * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Dim 6: Quality & Recency (10) */}
                    <div>
                      <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                        <span>6. Job Quality & Recency (ATS Board, Salary, Clear JD)</span>
                        <span className="font-semibold text-gray-900">{selectedJob.score.job_quality} / 10 pts</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all"
                          style={{ width: `${(selectedJob.score.job_quality / 10) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs bg-white p-3 rounded-lg border border-slate-200">
                    <div>
                      <span className="text-gray-500 block">Recommended Variant:</span>
                      <span className="font-semibold text-gray-900 font-mono">
                        {selectedJob.score.recommended_variant || 'java-backend'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block">Fit Category:</span>
                      <span className="font-bold text-gray-900">
                        {selectedJob.score.fit_category || 'EVALUATED'}
                      </span>
                    </div>
                  </div>

                  {/* Reasoning */}
                  {selectedJob.score.reasoning && (
                    <div className="text-xs bg-white p-3 rounded-lg border border-slate-200">
                      <span className="font-semibold text-slate-700 block mb-1">Score Breakdown Rationale:</span>
                      <p className="text-slate-600 italic">&ldquo;{selectedJob.score.reasoning}&rdquo;</p>
                    </div>
                  )}

                  {/* Strengths and Gaps */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    {selectedJob.score.strengths && (
                      <div className="bg-emerald-50/80 border border-emerald-200 p-2.5 rounded-lg">
                        <span className="font-semibold text-emerald-900 block mb-1">Matched Strengths:</span>
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
                        <span className="font-semibold text-amber-900 block mb-1">Skill Gaps:</span>
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
                      <Sparkles className="w-4 h-4 mr-1.5 text-indigo-600" /> Scoring Analysis Pending
                    </h4>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Evaluate this opportunity across the 6-dimension scoring rubric.
                    </p>
                  </div>
                  <button
                    onClick={() => handleAnalyzeJob(selectedJob.id)}
                    disabled={analyzingId === selectedJob.id}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors flex items-center shrink-0 disabled:opacity-50"
                  >
                    <Zap className={`w-3.5 h-3.5 mr-1.5 ${analyzingId === selectedJob.id ? 'animate-spin' : ''}`} />
                    {analyzingId === selectedJob.id ? 'Analyzing...' : 'Analyze Match Score'}
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
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => setSelectedJob(null)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => handleTailorResume(selectedJob.id, selectedJob.score?.recommended_variant || undefined)}
                    disabled={tailoringId === selectedJob.id}
                    className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
                  >
                    <FileCheck className={`w-3.5 h-3.5 mr-1.5 ${tailoringId === selectedJob.id ? 'animate-spin' : ''}`} />
                    {tailoringId === selectedJob.id ? 'Tailoring Resume...' : 'Tailor ATS Resume'}
                  </button>
                  <button
                    onClick={() => {
                      const job = selectedJob;
                      setSelectedJob(null);
                      handleOpenCoverLetter(job);
                    }}
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
                  >
                    <FileText className="w-3.5 h-3.5 mr-1.5" />
                    Cover Letter Studio
                  </button>
                  <button
                    onClick={() => handlePrepareApplication(selectedJob.id)}
                    disabled={preparingAppId === selectedJob.id}
                    className="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors disabled:opacity-50"
                  >
                    <Send className={`w-3.5 h-3.5 mr-1.5 ${preparingAppId === selectedJob.id ? 'animate-spin' : ''}`} />
                    {preparingAppId === selectedJob.id ? 'Preparing Packet...' : 'Prepare Application'}
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

        {/* Modal: Cover Letter Studio */}
        {coverLetterModalOpen && coverLetterJob && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full flex flex-col max-h-[92vh] overflow-hidden border border-slate-200">
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-slate-200 bg-slate-900 text-white flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg">
                    <FileText className="w-5 h-5" />
                  </span>
                  <div>
                    <h3 className="text-lg font-bold">Cover Letter Studio</h3>
                    <p className="text-xs text-slate-400">
                      {coverLetterJob.company || 'Company'} &bull; {coverLetterJob.title}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {coverLetterData && (
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        coverLetterData.validation_passed
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}>
                        {Math.round(coverLetterData.confidence_score * 100)}% Grounded
                      </span>
                      <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-full">
                        {coverLetterData.word_count} words
                      </span>
                    </div>
                  )}
                  <button
                    onClick={() => setCoverLetterModalOpen(false)}
                    className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Tone Toolbar & Tab bar */}
              <div className="px-6 py-3 bg-slate-50 border-b border-slate-200 flex flex-wrap justify-between items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Style / Tone:</span>
                  {(['technical', 'executive', 'startup'] as const).map((t) => (
                    <button
                      key={t}
                      onClick={() => handleRegenerateCoverLetter(t)}
                      disabled={coverLetterLoading}
                      className={`px-3 py-1 text-xs font-medium rounded-lg transition-all capitalize ${
                        coverLetterTone === t
                          ? 'bg-indigo-600 text-white shadow-xs font-semibold'
                          : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-2">
                  <div className="bg-slate-200 p-0.5 rounded-lg flex text-xs">
                    <button
                      onClick={() => setCoverLetterTab('editor')}
                      className={`px-3 py-1 rounded-md font-medium transition-colors ${
                        coverLetterTab === 'editor' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Editor
                    </button>
                    <button
                      onClick={() => setCoverLetterTab('preview')}
                      className={`px-3 py-1 rounded-md font-medium transition-colors ${
                        coverLetterTab === 'preview' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      Document Preview
                    </button>
                  </div>
                </div>
              </div>

              {/* Alert Messages */}
              {coverLetterMessage && (
                <div className={`mx-6 mt-3 p-3 rounded-lg text-xs font-medium ${
                  coverLetterMessage.type === 'success'
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    : 'bg-rose-50 text-rose-800 border border-rose-200'
                }`}>
                  {coverLetterMessage.text}
                </div>
              )}

              {/* Modal Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {coverLetterLoading ? (
                  <div className="h-72 flex flex-col items-center justify-center space-y-3">
                    <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" />
                    <p className="text-sm font-medium text-slate-600">
                      Drafting personalized cover letter for {coverLetterJob.company || 'the role'}...
                    </p>
                  </div>
                ) : coverLetterTab === 'editor' ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <label className="text-xs font-bold text-slate-700 uppercase tracking-wide flex items-center gap-1.5">
                        <Edit3 className="w-3.5 h-3.5 text-indigo-600" /> Cover Letter Text (Markdown)
                      </label>
                      <span className="text-xs text-slate-500 font-mono">
                        {coverLetterDraft.split(/\s+/).filter(Boolean).length} words
                      </span>
                    </div>
                    <textarea
                      rows={14}
                      value={coverLetterDraft}
                      onChange={(e) => setCoverLetterDraft(e.target.value)}
                      className="w-full text-sm font-sans leading-relaxed border border-slate-300 rounded-xl p-4 outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 bg-slate-50/50 shadow-inner"
                      placeholder="Write or edit your cover letter content..."
                    />
                  </div>
                ) : (
                  /* Document Preview Mode */
                  <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm space-y-6 max-w-2xl mx-auto font-sans text-slate-900">
                    {/* Letterhead */}
                    <div className="border-b border-slate-200 pb-4">
                      <h2 className="text-xl font-bold text-slate-900 tracking-tight">SHUBHAM PRAKASH</h2>
                      <p className="text-xs text-slate-500 mt-1">
                        Mumbai, India &bull; +91 9934305886 &bull; shubhamprakash230@gmail.com
                      </p>
                      <p className="text-xs text-slate-500">
                        Portfolio: https://www.shubhamprakash681.in/ &bull; LinkedIn: linkedin.com/in/shubhamprakash681
                      </p>
                    </div>

                    {/* Recipient info */}
                    <div className="text-xs text-slate-600 space-y-0.5">
                      <p className="font-semibold text-slate-800">Hiring Team / Engineering Leadership</p>
                      <p className="font-semibold text-slate-900">{coverLetterJob.company || 'Target Organization'}</p>
                      <p className="text-indigo-700 font-semibold pt-1">RE: Application for {coverLetterJob.title}</p>
                    </div>

                    {/* Body */}
                    <div className="space-y-4 text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
                      {coverLetterDraft}
                    </div>

                    {/* Sign-off */}
                    <div className="pt-4 border-t border-slate-100 text-sm text-slate-800 space-y-1">
                      <p>Sincerely,</p>
                      <p className="font-bold text-slate-900 pt-2">Shubham Prakash</p>
                      <p className="text-xs text-slate-500">Full Stack &amp; Backend Software Engineer</p>
                    </div>
                  </div>
                )}

                {/* Evidence & Grounding Audit Footnote */}
                {coverLetterData && (
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>
                        <strong>Verified Grounding:</strong> Accenture, TCS Digital (10k+ users), TradeX (Kafka, Redis), ~3.2 yrs exp.
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {coverLetterData.verified_skills.slice(0, 6).map((skill) => (
                        <span key={skill} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer Actions */}
              <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex flex-wrap justify-between items-center gap-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopyCoverLetter}
                    className="inline-flex items-center px-3 py-2 border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold shadow-2xs transition-colors"
                  >
                    {coverLetterCopied ? <Check className="w-3.5 h-3.5 mr-1.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 mr-1.5" />}
                    {coverLetterCopied ? 'Copied!' : 'Copy Text'}
                  </button>
                  <a
                    href={`/api/jobs/${coverLetterJob.id}/cover-letter/download/pdf`}
                    download
                    className="inline-flex items-center px-3 py-2 border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold shadow-2xs transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1.5 text-indigo-600" /> Download ATS PDF
                  </a>
                  <a
                    href={`/api/jobs/${coverLetterJob.id}/cover-letter/download/md`}
                    download
                    className="inline-flex items-center px-3 py-2 border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold shadow-2xs transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1.5 text-slate-600" /> Download Markdown
                  </a>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCoverLetterModalOpen(false)}
                    className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Done
                  </button>
                  <button
                    onClick={handleSaveCoverLetter}
                    disabled={coverLetterSaving}
                    className="inline-flex items-center px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
                  >
                    <Check className={`w-3.5 h-3.5 mr-1.5 ${coverLetterSaving ? 'animate-spin' : ''}`} />
                    {coverLetterSaving ? 'Saving...' : 'Save & Re-render PDF'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

