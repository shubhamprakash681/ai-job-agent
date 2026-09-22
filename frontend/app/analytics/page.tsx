'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import {
  FunnelResponse,
  BreakdownsResponse,
  TimelineResponse,
  LLMUsageResponse,
  LearningLoopResponse,
  DashboardSummary,
} from '@/types';
import {
  TrendingUp,
  Filter,
  Layers,
  FileCheck2,
  Globe2,
  Lightbulb,
  Coins,
  Calendar,
  ArrowRight,
  ArrowDownRight,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  Building2,
  MapPin,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Cpu,
} from 'lucide-react';

export default function AnalyticsPage() {
  const [funnel, setFunnel] = useState<FunnelResponse | null>(null);
  const [breakdowns, setBreakdowns] = useState<BreakdownsResponse | null>(null);
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [llmUsage, setLlmUsage] = useState<LLMUsageResponse | null>(null);
  const [insights, setInsights] = useState<LearningLoopResponse | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  const [timeframeDays, setTimeframeDays] = useState<number>(30);
  const [activeTab, setActiveTab] = useState<'funnel' | 'variants' | 'sources' | 'insights' | 'costs' | 'timeline'>('funnel');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async (days: number = timeframeDays) => {
    try {
      setRefreshing(true);
      const [fData, bData, tData, lData, iData, sData] = await Promise.all([
        api.getAnalyticsFunnel(),
        api.getAnalyticsBreakdowns(),
        api.getAnalyticsTimeline(days),
        api.getAnalyticsLLMUsage(),
        api.getAnalyticsInsights(),
        api.dashboardSummary(),
      ]);
      setFunnel(fData);
      setBreakdowns(bData);
      setTimeline(tData);
      setLlmUsage(lData);
      setInsights(iData);
      setSummary(sData);
    } catch (err) {
      console.error('Failed to load analytics data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData(timeframeDays);
  }, [timeframeDays]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex h-96 items-center justify-center">
          <div className="flex flex-col items-center space-y-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-500 font-medium">Loading platform analytics...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Derive metrics
  const discoveredCount = funnel?.stages.find(s => s.key === 'DISCOVERED')?.count || 0;
  const shortlistedCount = funnel?.stages.find(s => s.key === 'SHORTLISTED')?.count || 0;
  const appliedCount = funnel?.stages.find(s => s.key === 'APPLIED')?.count || 0;
  const interviewCount = funnel?.stages.find(s => s.key === 'INTERVIEW')?.count || 0;
  const offerCount = funnel?.stages.find(s => s.key === 'OFFER')?.count || 0;

  const interviewRate = appliedCount > 0 ? ((interviewCount / appliedCount) * 100).toFixed(1) : '0.0';
  const matchRate = shortlistedCount > 0 ? ((appliedCount / shortlistedCount) * 100).toFixed(1) : '0.0';

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Toolbar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold text-gray-900">Analytics & Conversion Funnel</h1>
              <span className="bg-blue-100 text-blue-700 text-xs px-2.5 py-0.5 rounded-full font-semibold">
                Phase 10 Hardened
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Multi-dimensional conversion tracking, resume variant yield, and outcome-driven learning loop.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
              {[
                { label: '7 Days', val: 7 },
                { label: '30 Days', val: 30 },
                { label: 'All Time', val: 90 },
              ].map(tf => (
                <button
                  key={tf.val}
                  onClick={() => setTimeframeDays(tf.val)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                    timeframeDays === tf.val
                      ? 'bg-white text-blue-600 shadow-xs font-semibold'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tf.label}
                </button>
              ))}
            </div>

            <button
              onClick={() => loadData(timeframeDays)}
              disabled={refreshing}
              className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600 transition-colors disabled:opacity-50"
              title="Refresh Data"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* Top KPI Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Discovered</span>
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <Briefcase className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 mt-2">{discoveredCount}</div>
            <span className="text-xs text-gray-400 mt-1 block">Active opportunities</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Shortlisted</span>
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                <Filter className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 mt-2">{shortlistedCount}</div>
            <span className="text-xs text-indigo-600 font-medium mt-1 block">Score ≥ 60 / Priority</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Submitted</span>
              <div className="p-2 bg-teal-50 text-teal-600 rounded-lg">
                <CheckCircle2 className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 mt-2">{appliedCount}</div>
            <span className="text-xs text-gray-500 mt-1 block">{matchRate}% match rate</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Interviews</span>
              <div className="p-2 bg-purple-50 text-purple-600 rounded-lg">
                <Calendar className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-purple-700 mt-2">{interviewCount}</div>
            <span className="text-xs text-purple-600 font-medium mt-1 block">{interviewRate}% interview rate</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Offers</span>
              <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                <Sparkles className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-emerald-700 mt-2">{offerCount}</div>
            <span className="text-xs text-emerald-600 font-medium mt-1 block">Conversion target</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">LLM Cost</span>
              <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
                <Coins className="h-4 w-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 mt-2">
              ${llmUsage?.estimated_total_cost_usd.toFixed(2) || '0.00'}
            </div>
            <span className="text-xs text-emerald-600 font-semibold mt-1 flex items-center">
              <ShieldCheck className="h-3 w-3 mr-1" /> Free Tier / 0 Spend
            </span>
          </div>
        </div>

        {/* Visual Application Funnel Bar Section */}
        {funnel && funnel.stages.length > 0 && (
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Layers className="h-5 w-5 text-blue-600" />
                  Application Conversion Funnel
                </h3>
                <p className="text-xs text-gray-500">
                  Progression and drop-off analysis across discovery, application, and interview stages.
                </p>
              </div>

              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <span className="inline-block w-2.5 h-2.5 bg-blue-500 rounded-full"></span>
                <span>Active Conversion</span>
              </div>
            </div>

            {/* Funnel Stage Cards Flow */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-3 pt-2">
              {funnel.stages.map((stage, idx) => {
                const colors = [
                  'border-blue-200 bg-blue-50/50 text-blue-900',
                  'border-indigo-200 bg-indigo-50/50 text-indigo-900',
                  'border-sky-200 bg-sky-50/50 text-sky-900',
                  'border-teal-200 bg-teal-50/50 text-teal-900',
                  'border-purple-200 bg-purple-50/50 text-purple-900',
                  'border-emerald-200 bg-emerald-50/50 text-emerald-900',
                ];
                const cardColor = colors[idx % colors.length];

                return (
                  <div
                    key={stage.key}
                    className={`relative p-4 rounded-xl border ${cardColor} flex flex-col justify-between transition-all hover:shadow-xs`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                          Step 0{idx + 1}
                        </span>
                        {idx > 0 && stage.drop_off_pct > 0 && (
                          <span className="text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded-full font-semibold flex items-center">
                            <ArrowDownRight className="h-2.5 w-2.5 mr-0.5" />
                            -{stage.drop_off_pct}%
                          </span>
                        )}
                      </div>
                      <h4 className="text-sm font-semibold text-gray-900 truncate" title={stage.name}>
                        {stage.name}
                      </h4>
                      <div className="text-2xl font-bold text-gray-900 mt-2">{stage.count}</div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-gray-200/60">
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <span>Step Yield:</span>
                        <span className="font-semibold text-gray-900">{stage.conversion_pct}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1.5 overflow-hidden">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, stage.conversion_pct)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tabbed Analytical Deep Dive */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
          {/* Tabs Navigation */}
          <div className="flex border-b border-gray-200 overflow-x-auto bg-gray-50/80 px-4">
            {[
              { id: 'funnel', label: 'Funnel & Conversion Matrix', icon: TrendingUp },
              { id: 'variants', label: 'Resume Variant Yield', icon: FileCheck2 },
              { id: 'sources', label: 'Source Effectiveness', icon: Globe2 },
              { id: 'insights', label: 'Learning Loop Advisor', icon: Lightbulb },
              { id: 'costs', label: 'AI Cost & Token Usage', icon: Cpu },
              { id: 'timeline', label: 'Activity Timeline', icon: Calendar },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-3.5 px-4 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600 bg-white shadow-xs'
                    : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-100/50'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          <div className="p-6">
            {/* Tab 1: Funnel & Conversion Matrix */}
            {activeTab === 'funnel' && funnel && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-gray-900 mb-1">Conversion Efficiency Matrix</h3>
                  <p className="text-xs text-gray-500">
                    Step-by-step conversion benchmarks calculated from historical job data.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Match → Application</span>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {(funnel.summary_rates.match_to_application_rate * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Shortlisted jobs converted to prepared submissions</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Application → Interview</span>
                    <div className="text-2xl font-bold text-purple-700 mt-1">
                      {(funnel.summary_rates.application_to_interview_rate * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Submissions yielding recruiter interview rounds</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Interview → Offer</span>
                    <div className="text-2xl font-bold text-emerald-700 mt-1">
                      {(funnel.summary_rates.interview_to_offer_rate * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Interviews advancing to final compensation offer</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Overall Application → Offer</span>
                    <div className="text-2xl font-bold text-blue-700 mt-1">
                      {(funnel.summary_rates.overall_conversion_rate * 100).toFixed(1)}%
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Total end-to-end yield per job application</p>
                  </div>
                </div>

                {/* Funnel Details Table */}
                <div className="overflow-x-auto border border-gray-200 rounded-xl">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-semibold border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3">Funnel Stage</th>
                        <th className="px-4 py-3 text-right">Volume</th>
                        <th className="px-4 py-3 text-right">Step Conversion</th>
                        <th className="px-4 py-3 text-right">Drop-off</th>
                        <th className="px-4 py-3 text-left">Funnel Diagnostic</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {funnel.stages.map((stage, idx) => (
                        <tr key={stage.key} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900 flex items-center space-x-2">
                            <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                            <span>{stage.name}</span>
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-gray-900">{stage.count}</td>
                          <td className="px-4 py-3 text-right text-gray-600 font-semibold">{stage.conversion_pct}%</td>
                          <td className="px-4 py-3 text-right text-red-600 font-medium">
                            {idx === 0 ? '—' : `-${stage.drop_off_pct}% (${stage.drop_off_count})`}
                          </td>
                          <td className="px-4 py-3 text-xs text-gray-500">
                            {stage.key === 'DISCOVERED' && 'Total opportunities fetched via crawlers and manual input.'}
                            {stage.key === 'SHORTLISTED' && 'Opportunities scoring 60+ points or classified HIGH_PRIORITY.'}
                            {stage.key === 'PREPARED' && 'ATS tailored resume and customized cover letter generated.'}
                            {stage.key === 'APPLIED' && 'Human-approved applications submitted (under dry-run or live mode).'}
                            {stage.key === 'INTERVIEW' && 'Recruiter screens, coding assessments, or technical rounds.'}
                            {stage.key === 'OFFER' && 'Formal offer proposal and package received.'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Tab 2: Resume Variant Yield */}
            {activeTab === 'variants' && breakdowns && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-gray-900 mb-1">Resume Variant Performance</h3>
                  <p className="text-xs text-gray-500">
                    A/B conversion comparison across the 4 specialized master resume variants.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {breakdowns.variants.map(variant => {
                    const isBest = insights?.top_variant === variant.variant_name;

                    return (
                      <div
                        key={variant.variant_name}
                        className={`p-5 rounded-xl border transition-all ${
                          isBest
                            ? 'border-blue-400 bg-blue-50/20 shadow-xs'
                            : 'border-gray-200 bg-white'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center space-x-2">
                              <h4 className="font-bold text-gray-900">{variant.display_name}</h4>
                              {isBest && (
                                <span className="bg-blue-600 text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                                  Top Converting
                                </span>
                              )}
                            </div>
                            <span className="text-xs font-mono text-gray-400 mt-0.5 block">
                              {variant.variant_name}
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs text-gray-500">Interview Rate</span>
                            <div className="text-xl font-bold text-purple-700">{variant.conversion_rate}%</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-gray-100 text-center">
                          <div className="bg-gray-50 p-2.5 rounded-lg">
                            <span className="text-[11px] text-gray-500 block">Submitted</span>
                            <span className="text-base font-bold text-gray-900">{variant.applications_count}</span>
                          </div>
                          <div className="bg-purple-50 p-2.5 rounded-lg">
                            <span className="text-[11px] text-purple-600 block">Interviews</span>
                            <span className="text-base font-bold text-purple-900">{variant.interviews_count}</span>
                          </div>
                          <div className="bg-emerald-50 p-2.5 rounded-lg">
                            <span className="text-[11px] text-emerald-600 block">Offers</span>
                            <span className="text-base font-bold text-emerald-900">{variant.offers_count}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Tab 3: Source Effectiveness */}
            {activeTab === 'sources' && breakdowns && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-gray-900 mb-1">Job Board & Source Effectiveness</h3>
                  <p className="text-xs text-gray-500">
                    Recruiter response rates and interview conversion across direct ATS vs board aggregators.
                  </p>
                </div>

                <div className="overflow-x-auto border border-gray-200 rounded-xl">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-semibold border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3">Source Channel</th>
                        <th className="px-4 py-3 text-right">Jobs Discovered</th>
                        <th className="px-4 py-3 text-right">Applied</th>
                        <th className="px-4 py-3 text-right">Interviews</th>
                        <th className="px-4 py-3 text-right">Response Rate</th>
                        <th className="px-4 py-3 text-right">Interview Rate</th>
                        <th className="px-4 py-3 text-center">Channel Type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {breakdowns.sources.map(src => {
                        const isDirect = ['greenhouse', 'lever', 'manual'].includes(src.source);

                        return (
                          <tr key={src.source} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-semibold text-gray-900 capitalize flex items-center space-x-2">
                              <Globe2 className="h-4 w-4 text-gray-400" />
                              <span>{src.source}</span>
                            </td>
                            <td className="px-4 py-3 text-right text-gray-700 font-medium">{src.jobs_count}</td>
                            <td className="px-4 py-3 text-right text-gray-700 font-medium">{src.applied_count}</td>
                            <td className="px-4 py-3 text-right text-purple-700 font-bold">{src.interviews_count}</td>
                            <td className="px-4 py-3 text-right font-semibold text-gray-900">{src.response_rate}%</td>
                            <td className="px-4 py-3 text-right font-bold text-purple-700">{src.interview_rate}%</td>
                            <td className="px-4 py-3 text-center">
                              {isDirect ? (
                                <span className="bg-emerald-100 text-emerald-800 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                                  Direct ATS
                                </span>
                              ) : (
                                <span className="bg-gray-100 text-gray-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                                  Aggregator
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Geographic & Employer Breakdown Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-100">
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-1.5">
                      <MapPin className="h-4 w-4 text-blue-600" />
                      Geographic Distribution
                    </h4>
                    <div className="space-y-2">
                      {breakdowns.locations.map(loc => (
                        <div key={loc.location} className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg text-xs">
                          <span className="font-medium text-gray-900">{loc.location}</span>
                          <div className="flex items-center space-x-4">
                            <span className="text-gray-500">{loc.jobs_count} jobs</span>
                            <span className="font-semibold text-blue-600">{loc.applications_count} applied</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-1.5">
                      <Building2 className="h-4 w-4 text-indigo-600" />
                      Active Company Pipeline
                    </h4>
                    <div className="space-y-2">
                      {breakdowns.companies.length > 0 ? (
                        breakdowns.companies.map(comp => (
                          <div key={comp.company} className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg text-xs">
                            <span className="font-medium text-gray-900">{comp.company}</span>
                            <div className="flex items-center space-x-3">
                              <span className="text-gray-500">{comp.total_jobs} total</span>
                              <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-semibold text-[10px]">
                                {comp.highest_stage}
                              </span>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-gray-400 py-4 text-center">No company applications logged yet.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 4: Learning Loop Advisor */}
            {activeTab === 'insights' && insights && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start space-x-3">
                  <ShieldCheck className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-blue-900">
                      Outcome-Driven Learning Loop (PROMPT.md Section 75)
                    </h4>
                    <p className="text-xs text-blue-700 mt-0.5">
                      The agent automatically optimizes ranking, source priorities, and resume variant preferences
                      based on recruiter responses. Candidate background facts remain strictly immutable.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {insights.insights.map((insight, idx) => (
                    <div key={idx} className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 bg-gray-100 text-gray-700 rounded-md">
                            {insight.type.replace('_', ' ')}
                          </span>
                          <span className="text-xs font-semibold text-emerald-600">{insight.impact}</span>
                        </div>
                        <h4 className="text-sm font-bold text-gray-900">{insight.title}</h4>
                        <p className="text-xs text-gray-700 mt-2 font-medium bg-gray-50 p-2.5 rounded-lg border border-gray-100">
                          {insight.recommendation}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          <strong className="text-gray-700">Rationale: </strong>
                          {insight.rationale}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 5: AI Cost & Token Usage */}
            {activeTab === 'costs' && llmUsage && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-gray-900 mb-1">AI Provider & Cost Control</h3>
                  <p className="text-xs text-gray-500">
                    Real-time auditing of input/output tokens, provider latency, and estimated cost (Section 78).
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Total LLM Requests</span>
                    <div className="text-2xl font-bold text-gray-900 mt-1">{llmUsage.total_requests}</div>
                    <p className="text-xs text-gray-500 mt-1">Logged in audit records</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Input Tokens Processed</span>
                    <div className="text-2xl font-bold text-indigo-700 mt-1">
                      {llmUsage.total_input_tokens.toLocaleString()}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">JD extraction & prompt tokens</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Output Tokens Generated</span>
                    <div className="text-2xl font-bold text-teal-700 mt-1">
                      {llmUsage.total_output_tokens.toLocaleString()}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Classification & resume bullets</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <span className="text-xs text-gray-500 font-medium">Estimated Expenditure</span>
                    <div className="text-2xl font-bold text-emerald-700 mt-1">
                      ${llmUsage.estimated_total_cost_usd.toFixed(4)}
                    </div>
                    <p className="text-xs text-emerald-600 font-medium mt-1">100% Free Tier Eligible</p>
                  </div>
                </div>

                {/* Providers Table */}
                <div className="overflow-x-auto border border-gray-200 rounded-xl">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-semibold border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3">AI Provider</th>
                        <th className="px-4 py-3 text-right">Invocations</th>
                        <th className="px-4 py-3 text-right">Input Tokens</th>
                        <th className="px-4 py-3 text-right">Output Tokens</th>
                        <th className="px-4 py-3 text-right">Average Latency</th>
                        <th className="px-4 py-3 text-right">Est. Cost (USD)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {Object.entries(llmUsage.by_provider).map(([prov, stats]) => (
                        <tr key={prov} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-semibold text-gray-900 capitalize flex items-center space-x-2">
                            <Cpu className="h-4 w-4 text-blue-600" />
                            <span>{prov}</span>
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-gray-900">{stats.requests}</td>
                          <td className="px-4 py-3 text-right text-gray-600">{stats.input_tokens.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right text-gray-600">{stats.output_tokens.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right text-gray-600">{stats.avg_duration_ms} ms</td>
                          <td className="px-4 py-3 text-right font-mono font-semibold text-emerald-700">
                            ${stats.estimated_cost_usd.toFixed(4)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Tab 6: Activity Timeline */}
            {activeTab === 'timeline' && timeline && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-gray-900 mb-1">Activity Volume Over Time</h3>
                  <p className="text-xs text-gray-500">
                    Daily trajectory of discovered jobs, submitted applications, and interviews ({timeframeDays} days).
                  </p>
                </div>

                <div className="space-y-2">
                  {timeline.points.slice(-14).map(point => {
                    const totalAct = point.discovered + point.applied + point.interviews;

                    return (
                      <div key={point.date} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-xs">
                        <span className="font-mono text-gray-700 font-semibold w-24">{point.date}</span>
                        <div className="flex-1 mx-4 flex items-center space-x-2">
                          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden flex">
                            {point.discovered > 0 && (
                              <div
                                style={{ width: `${Math.min(100, point.discovered * 25)}%` }}
                                className="bg-blue-500 h-full"
                                title={`${point.discovered} discovered`}
                              ></div>
                            )}
                            {point.applied > 0 && (
                              <div
                                style={{ width: `${Math.min(100, point.applied * 30)}%` }}
                                className="bg-teal-500 h-full"
                                title={`${point.applied} applied`}
                              ></div>
                            )}
                            {point.interviews > 0 && (
                              <div
                                style={{ width: `${Math.min(100, point.interviews * 50)}%` }}
                                className="bg-purple-600 h-full"
                                title={`${point.interviews} interviews`}
                              ></div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 text-gray-600 shrink-0">
                          <span className="text-blue-700 font-medium">{point.discovered} disc</span>
                          <span className="text-teal-700 font-medium">{point.applied} appl</span>
                          <span className="text-purple-700 font-bold">{point.interviews} intv</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
