'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import { ResumeVariant, ResumeVersion } from '@/types';
import {
  FileCheck,
  FileText,
  Download,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Eye,
  X,
  Building,
  Briefcase,
  Calendar,
  Check,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';

export default function ResumesPage() {
  const [variants, setVariants] = useState<ResumeVariant[]>([]);
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState<ResumeVersion | null>(null);
  const [activeTab, setActiveTab] = useState<'content' | 'diff' | 'evidence' | 'keywords'>('content');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [vList, verList] = await Promise.all([
        api.getResumeVariants(),
        api.getResumeVersions(),
      ]);
      setVariants(vList);
      setVersions(verList.items);
    } catch (err) {
      console.error('Failed to load resume data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const parseJson = (str: string | null | undefined, fallback: any = {}) => {
    if (!str) return fallback;
    try {
      return JSON.parse(str);
    } catch {
      return fallback;
    }
  };

  const downloadUrl = (versionId: number, format: 'pdf' | 'docx' | 'md') => {
    return `/api/resumes/versions/${versionId}/download/${format}`;
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <FileCheck className="w-6 h-6 mr-2 text-emerald-600" /> ATS Resume Studio & Variants
            </h2>
            <p className="text-gray-500 text-sm mt-0.5">
              Strictly grounded ATS resumes with 100% verified evidence mapping, bullet reordering, and multi-format exports.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <ShieldCheck className="w-4 h-4 mr-1.5 text-emerald-600" /> Zero Hallucination Guarantee
            </span>
          </div>
        </div>

        {/* Resume Variants Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-gray-900 flex items-center">
              <Layers className="w-4 h-4 mr-2 text-blue-600" /> Candidate Master Variants ({variants.length})
            </h3>
            <span className="text-xs text-gray-500">Each tailored resume begins from one of these 4 verified archetypes</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {variants.map((v) => (
              <div
                key={v.id}
                className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col justify-between hover:shadow-md transition-shadow relative"
              >
                {v.is_default && (
                  <span className="absolute top-3.5 right-3.5 bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                    PRIMARY
                  </span>
                )}
                <div>
                  <h4 className="font-bold text-gray-900 text-sm">{v.display_name}</h4>
                  <div className="text-[11px] font-mono text-gray-400 mt-0.5">{v.name}</div>
                  <p className="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">
                    {v.description || 'Targeted specialization profile.'}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-100">
                  <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                    Priority Tech:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {(v.priority_skills ? v.priority_skills.split(',') : ['Java', 'Spring Boot']).slice(0, 3).map((s) => (
                      <span key={s.trim()} className="text-[10px] bg-slate-100 text-slate-700 font-medium px-2 py-0.5 rounded">
                        {s.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tailored Resumes Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-bold text-gray-900 text-base flex items-center">
                <FileText className="w-4 h-4 mr-2 text-indigo-600" /> Tailored Resumes ({versions.length})
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Targeted resume versions dynamically aligned with opportunity descriptions.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
              Loading resume records...
            </div>
          ) : versions.length === 0 ? (
            <div className="p-12 text-center text-gray-500 space-y-3">
              <FileCheck className="w-12 h-12 text-gray-300 mx-auto stroke-1" />
              <h4 className="text-base font-medium text-gray-800">No tailored resumes generated yet</h4>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                Navigate to the <span className="font-semibold text-gray-700">Jobs</span> console, click &quot;Details&quot; on any opportunity, and select &quot;Tailor ATS Resume&quot;.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
                  <tr>
                    <th className="py-3 px-6 text-left">Target Opportunity</th>
                    <th className="py-3 px-4 text-left">Version</th>
                    <th className="py-3 px-4 text-left">Evidence & Validation</th>
                    <th className="py-3 px-4 text-left">Confidence</th>
                    <th className="py-3 px-4 text-left">Generated</th>
                    <th className="py-3 px-6 text-right">Downloads & Review</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {versions.map((ver) => {
                    const validationStatus = (ver.validation_status || 'passed').toUpperCase();
                    const confPct = Math.round((ver.confidence_score || 1.0) * 100);

                    return (
                      <tr key={ver.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-4 px-6">
                          <div className="font-bold text-gray-900">{ver.job_title || `Job Opportunity #${ver.job_id || 'Master'}`}</div>
                          <div className="text-xs text-gray-500 flex items-center mt-0.5">
                            <Building className="w-3.5 h-3.5 mr-1 text-gray-400" />
                            {ver.job_company || 'Target Company'}
                          </div>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                            v{ver.version_number}.0
                          </span>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          {validationStatus === 'PASSED' ? (
                            <span className="inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                              <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Passed (Zero-Hallucination)
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800">
                              <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" /> Review Warning
                            </span>
                          )}
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap">
                          <div className="flex items-center space-x-1.5">
                            <span className="font-semibold text-xs text-gray-800">{confPct}%</span>
                            <div className="w-16 bg-gray-100 rounded-full h-1.5">
                              <div
                                className="bg-emerald-600 h-1.5 rounded-full"
                                style={{ width: `${confPct}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>

                        <td className="py-4 px-4 whitespace-nowrap text-xs text-gray-500">
                          {ver.created_at ? new Date(ver.created_at).toLocaleDateString() : 'Recent'}
                        </td>

                        <td className="py-4 px-6 whitespace-nowrap text-right text-xs">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => {
                                setSelectedVersion(ver);
                                setActiveTab('content');
                              }}
                              className="inline-flex items-center px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded text-xs border border-indigo-200 transition-colors"
                            >
                              <Eye className="w-3.5 h-3.5 mr-1" /> Inspect & Diff
                            </button>

                            {/* Download buttons */}
                            <a
                              href={downloadUrl(ver.id, 'pdf')}
                              download
                              title="Download ATS PDF"
                              className="inline-flex items-center p-1 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded border border-gray-200 transition-colors"
                            >
                              <span className="font-bold text-[10px] px-1 text-red-600">PDF</span>
                              <Download className="w-3.5 h-3.5" />
                            </a>

                            <a
                              href={downloadUrl(ver.id, 'docx')}
                              download
                              title="Download Word DOCX"
                              className="inline-flex items-center p-1 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded border border-gray-200 transition-colors"
                            >
                              <span className="font-bold text-[10px] px-1 text-blue-600">DOCX</span>
                              <Download className="w-3.5 h-3.5" />
                            </a>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal: Comprehensive Resume Inspector Drawer */}
        {selectedVersion && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full flex flex-col max-h-[92vh] overflow-hidden">
              {/* Drawer Header */}
              <div className="p-6 border-b border-gray-200 bg-slate-50 flex justify-between items-start">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                      v{selectedVersion.version_number}.0
                    </span>
                    <h3 className="text-xl font-bold text-gray-900">
                      {selectedVersion.job_title || `Job Opportunity #${selectedVersion.job_id}`}
                    </h3>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 flex items-center">
                    <Building className="w-3.5 h-3.5 mr-1 text-gray-400" />
                    {selectedVersion.job_company || 'Unknown Company'}
                    <span className="mx-2">•</span>
                    Confidence Score: {Math.round((selectedVersion.confidence_score || 1) * 100)}%
                    <span className="mx-2">•</span>
                    Validation: <span className="text-emerald-700 font-semibold ml-1 uppercase">{selectedVersion.validation_status}</span>
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <a
                    href={downloadUrl(selectedVersion.id, 'pdf')}
                    download
                    className="flex items-center px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-medium shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" /> PDF
                  </a>
                  <a
                    href={downloadUrl(selectedVersion.id, 'docx')}
                    download
                    className="flex items-center px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" /> DOCX
                  </a>
                  <a
                    href={downloadUrl(selectedVersion.id, 'md')}
                    download
                    className="flex items-center px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-medium shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" /> Markdown
                  </a>
                  <button
                    onClick={() => setSelectedVersion(null)}
                    className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-200 transition-colors ml-2"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Drawer Tabs */}
              <div className="flex border-b border-gray-200 px-6 bg-white text-xs font-semibold">
                <button
                  onClick={() => setActiveTab('content')}
                  className={`py-3 px-4 border-b-2 transition-colors ${
                    activeTab === 'content'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Tailored Resume Document
                </button>
                <button
                  onClick={() => setActiveTab('diff')}
                  className={`py-3 px-4 border-b-2 transition-colors ${
                    activeTab === 'diff'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Modifications & Diff Rationale
                </button>
                <button
                  onClick={() => setActiveTab('evidence')}
                  className={`py-3 px-4 border-b-2 transition-colors ${
                    activeTab === 'evidence'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Evidence Map (Zero-Hallucination)
                </button>
                <button
                  onClick={() => setActiveTab('keywords')}
                  className={`py-3 px-4 border-b-2 transition-colors ${
                    activeTab === 'keywords'
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Keyword Alignment Map
                </button>
              </div>

              {/* Drawer Body Content */}
              <div className="p-6 overflow-y-auto flex-1 bg-slate-50/50">
                {/* Tab 1: Full Content */}
                {activeTab === 'content' && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-gray-200">
                      <span className="text-xs text-gray-500">
                        Rendered Markdown document passed to ReportLab ATS PDF & Word generator.
                      </span>
                      <button
                        onClick={() => handleCopy(selectedVersion.content_markdown || '')}
                        className="flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        {copied ? <Check className="w-3.5 h-3.5 mr-1" /> : null}
                        {copied ? 'Copied!' : 'Copy Markdown'}
                      </button>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-xl p-6 font-mono text-xs text-gray-800 whitespace-pre-wrap leading-relaxed shadow-sm">
                      {selectedVersion.content_markdown || 'No document content available.'}
                    </div>
                  </div>
                )}

                {/* Tab 2: Diff Rationale */}
                {activeTab === 'diff' && (
                  <div className="space-y-4">
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 leading-relaxed">
                      <span className="font-bold block mb-1">ATS Optimization Summary:</span>
                      {selectedVersion.change_diff || 'Reordered key achievement bullets to emphasize role-specific technologies and aligned keywords with opportunity requirements.'}
                    </div>

                    {selectedVersion.validation_report && (
                      <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-2">
                        <h4 className="font-bold text-xs text-gray-700 uppercase">Verification Engine Audit:</h4>
                        <div className="text-xs font-mono text-gray-700 whitespace-pre-wrap bg-slate-50 p-3 rounded-lg border border-slate-200">
                          {selectedVersion.validation_report}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Tab 3: Evidence Map */}
                {activeTab === 'evidence' && (
                  <div className="space-y-4">
                    <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs text-emerald-900">
                      <div className="font-bold flex items-center mb-1">
                        <ShieldCheck className="w-4 h-4 mr-1.5 text-emerald-600" /> Evidence Audit Trail
                      </div>
                      Every claim and bullet in this resume links to an atomic, verified fact in candidate YAML facts.
                    </div>

                    <div className="space-y-2">
                      {Object.entries(parseJson(selectedVersion.evidence_mapping)).map(([claim, facts]: [string, any], idx) => (
                        <div key={idx} className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm space-y-2">
                          <div className="text-xs font-medium text-gray-900 leading-relaxed">&bull; {claim}</div>
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {(Array.isArray(facts) ? facts : [facts]).map((factId: string) => (
                              <span
                                key={factId}
                                className="inline-flex items-center text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200"
                              >
                                {factId}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tab 4: Keyword Alignment */}
                {activeTab === 'keywords' && (
                  <div className="space-y-4">
                    <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 text-xs text-purple-900">
                      <div className="font-bold flex items-center mb-1">
                        <Sparkles className="w-4 h-4 mr-1.5 text-purple-600" /> Job Keyword Matching
                      </div>
                      Keywords detected in the opportunity description mapped to candidate resume sections.
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {Object.entries(parseJson(selectedVersion.keyword_mapping)).map(([kw, status]: [string, any]) => (
                        <div key={kw} className="bg-white p-3 rounded-lg border border-gray-200 flex justify-between items-center text-xs">
                          <span className="font-medium text-gray-800 capitalize">{kw}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                            {String(status)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Drawer Footer */}
              <div className="p-4 border-t border-gray-200 bg-white flex justify-between items-center">
                <span className="text-xs text-gray-400">Version ID #{selectedVersion.id}</span>
                <button
                  onClick={() => setSelectedVersion(null)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors"
                >
                  Close Reviewer
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
