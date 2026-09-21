'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { api } from '@/lib/api';
import {
  CandidateProfile,
  CandidateFact,
  SkillCategory,
  ResumeValidationResponse,
} from '@/types';
import {
  User,
  Briefcase,
  Code2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ExternalLink,
  RefreshCw,
  Search,
  ShieldCheck,
  GraduationCap,
  Layers,
  Award,
} from 'lucide-react';

export default function CandidatePage() {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [facts, setFacts] = useState<CandidateFact[]>([]);
  const [skillsData, setSkillsData] = useState<{ categories: SkillCategory[]; total_skills: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Tabs: 'overview' | 'skills' | 'facts' | 'validator'
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'facts' | 'validator'>('overview');

  // Facts filtering
  const [factCategoryFilter, setFactCategoryFilter] = useState<string>('all');
  const [factSearch, setFactSearch] = useState<string>('');

  // Validator state
  const [testText, setTestText] = useState<string>(
    `# Shubham Prakash - Software Engineer\nSoftware Engineer with 3+ years experience building microservices with Java, Spring Boot, and React.\n- Developed enterprise applications using Java, Spring Boot, React, and Node.js.\n- Optimized caching supporting 10,000+ concurrent users with zero data conflicts.\n- Built TradeX paper trading platform using Kafka and WebSockets with Redis caching.`
  );
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ResumeValidationResponse | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [prof, factsRes, skillsRes] = await Promise.all([
        api.getCandidate(),
        api.getCandidateFacts(),
        api.getCandidateSkills(),
      ]);
      setProfile(prof);
      setFacts(factsRes);
      setSkillsData(skillsRes);
    } catch (err) {
      console.error('Failed to load candidate data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncKB = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const res = await api.syncCandidateKB();
      setSyncMessage(`Synced ${res.facts_count} atomic facts for ${res.candidate_name}!`);
      await loadData();
    } catch (err: any) {
      setSyncMessage(`Sync failed: ${err.message || 'Error'}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleValidate = async () => {
    if (!testText.trim()) return;
    setValidating(true);
    try {
      const report = await api.validateResumeText(testText);
      setValidationResult(report);
    } catch (err) {
      console.error('Validation failed', err);
    } finally {
      setValidating(false);
    }
  };

  const setPresetText = (type: 'clean' | 'hallucination' | 'metric') => {
    if (type === 'clean') {
      setTestText(
        `# Shubham Prakash - Full Stack Engineer\nSoftware Engineer with 3 years experience building scalable systems using Java, Spring Boot, React.\n- Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript.\n- Optimized caching and session management supporting 10,000+ concurrent users with 80% faster load times.\n- Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing.`
      );
    } else if (type === 'hallucination') {
      setTestText(
        `# Staff Distributed Systems Engineer\n10+ years experience architecting distributed systems using Kubernetes, Rust, and Go.\n- Deployed production GraphQL federation gateway using Rust and Solidity.\n- Led migration to Google Cloud Platform (GCP) with Terraform.`
      );
    } else if (type === 'metric') {
      setTestText(
        `# Shubham Prakash - Backend Engineer\nSoftware Engineer with 8 years of Java experience.\n- Scaled backend architecture to support 500,000+ concurrent users with zero latency.\n- Managed team of 45 engineers at Accenture.`
      );
    }
    setValidationResult(null);
  };

  const filteredFacts = facts.filter((f) => {
    const matchesCategory = factCategoryFilter === 'all' || f.category.toLowerCase() === factCategoryFilter.toLowerCase();
    const matchesSearch =
      !factSearch.trim() ||
      f.claim.toLowerCase().includes(factSearch.toLowerCase()) ||
      f.fact_id.toLowerCase().includes(factSearch.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex h-64 items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Top Header Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start space-x-4">
              <div className="h-14 w-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-xl font-bold">
                SP
              </div>
              <div>
                <div className="flex items-center space-x-3">
                  <h2 className="text-2xl font-bold text-gray-900">{profile?.full_name || 'Shubham Prakash'}</h2>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <ShieldCheck className="w-3.5 h-3.5 mr-1" /> KB Verified
                  </span>
                </div>
                <p className="text-gray-600 text-sm mt-0.5">
                  {profile?.current_role || 'Packaged App Development Analyst'} at{' '}
                  <span className="font-medium text-gray-800">{profile?.current_company || 'Accenture'}</span> •{' '}
                  {profile?.location || 'Mumbai, India'} • ~3.2 years experience
                </p>
                <div className="flex items-center space-x-4 mt-2 text-xs text-blue-600">
                  {profile?.portfolio_url && (
                    <a href={profile.portfolio_url} target="_blank" rel="noreferrer" className="flex items-center hover:underline">
                      <ExternalLink className="w-3 h-3 mr-1" /> Portfolio
                    </a>
                  )}
                  {profile?.github_url && (
                    <a href={profile.github_url} target="_blank" rel="noreferrer" className="flex items-center hover:underline">
                      <ExternalLink className="w-3 h-3 mr-1" /> GitHub
                    </a>
                  )}
                  {profile?.linkedin_url && (
                    <a href={profile.linkedin_url} target="_blank" rel="noreferrer" className="flex items-center hover:underline">
                      <ExternalLink className="w-3 h-3 mr-1" /> LinkedIn
                    </a>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleSyncKB}
                disabled={syncing}
                className="flex items-center px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg border border-slate-300 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${syncing ? 'animate-spin' : ''}`} />
                {syncing ? 'Syncing...' : 'Sync from YAML'}
              </button>
            </div>
          </div>

          {syncMessage && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-lg">
              {syncMessage}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Briefcase className="w-4 h-4 mr-2" /> Overview & Experience
            </button>
            <button
              onClick={() => setActiveTab('skills')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === 'skills'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Code2 className="w-4 h-4 mr-2" /> Skills Taxonomy ({skillsData?.total_skills || 0})
            </button>
            <button
              onClick={() => setActiveTab('facts')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === 'facts'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <ShieldCheck className="w-4 h-4 mr-2" /> Verified Facts ({facts.length})
            </button>
            <button
              onClick={() => setActiveTab('validator')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === 'validator'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <AlertTriangle className="w-4 h-4 mr-2" /> Anti-Hallucination Sandbox
            </button>
          </nav>
        </div>

        {/* Tab 1: Overview & Experience */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Work Experience */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Briefcase className="w-5 h-5 mr-2 text-blue-600" /> Work Experience
                </h3>
                <div className="space-y-6">
                  {/* Accenture */}
                  <div className="border-l-2 border-blue-500 pl-4 relative">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-gray-900">Packaged App Development Analyst</h4>
                        <p className="text-sm text-gray-600">Accenture • Mumbai, India</p>
                      </div>
                      <span className="text-xs bg-blue-50 text-blue-700 font-medium px-2.5 py-1 rounded">
                        Apr 2026 – Present
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">
                      Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards.
                    </p>
                  </div>

                  {/* TCS Digital */}
                  <div className="border-l-2 border-slate-300 pl-4 relative">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-gray-900">Software Developer</h4>
                        <p className="text-sm text-gray-600">Tata Consultancy Services (TCS Digital) • Mumbai, India</p>
                      </div>
                      <span className="text-xs bg-gray-100 text-gray-700 font-medium px-2.5 py-1 rounded">
                        Jun 2023 – Apr 2026
                      </span>
                    </div>
                    <ul className="text-sm text-gray-700 mt-2 space-y-1.5 list-disc list-inside">
                      <li>Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js.</li>
                      <li>Migrated ArcGIS authentication to backend; implemented JWT, OAuth2, and Auth0 SSO across 3 applications.</li>
                      <li>Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing.</li>
                      <li>Optimized caching supporting 10,000+ concurrent users with zero data conflicts; 80% faster load times.</li>
                    </ul>
                  </div>

                  {/* Sylvr */}
                  <div className="border-l-2 border-slate-200 pl-4 relative">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-gray-900">Software Engineer Intern</h4>
                        <p className="text-sm text-gray-600">Sylvr • Remote, India</p>
                      </div>
                      <span className="text-xs bg-gray-100 text-gray-700 font-medium px-2.5 py-1 rounded">
                        Mar 2023 – Jun 2023
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">
                      Developed MERN stack applications for financial data visualization serving 50+ organizations. Containerized with Docker and deployed with Nginx (98% uptime).
                    </p>
                  </div>

                  {/* IIT Patna */}
                  <div className="border-l-2 border-slate-200 pl-4 relative">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold text-gray-900">Research Intern</h4>
                        <p className="text-sm text-gray-600">IIT Patna • Remote, India</p>
                      </div>
                      <span className="text-xs bg-gray-100 text-gray-700 font-medium px-2.5 py-1 rounded">
                        Jan 2022 – May 2022
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">
                      Deep learning research involving emotion prediction and psychiatric disorder prediction from BCI signals.
                    </p>
                  </div>
                </div>
              </div>

              {/* Projects */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Layers className="w-5 h-5 mr-2 text-indigo-600" /> Featured Projects
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* TradeX */}
                  <div className="border border-gray-200 rounded-lg p-4 bg-slate-50">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-gray-900">TradeX</h4>
                      <span className="text-xs font-semibold text-green-700 bg-green-100 px-2 py-0.5 rounded">Live</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">Realtime Paper Trading Platform</p>
                    <p className="text-xs text-gray-700 mt-2">
                      Spring Boot microservices, Kafka streaming, WebSockets, Redis caching, PostgreSQL persistence, and 10 years of OHLCV historical data.
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {['Spring Boot', 'Kafka', 'WebSockets', 'Redis', 'PostgreSQL'].map((t) => (
                        <span key={t} className="text-xs bg-white border border-gray-300 px-2 py-0.5 rounded text-gray-700">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* VideoShare */}
                  <div className="border border-gray-200 rounded-lg p-4 bg-slate-50">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-gray-900">VideoShare</h4>
                      <span className="text-xs font-semibold text-green-700 bg-green-100 px-2 py-0.5 rounded">Live</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">Video Sharing & Streaming Platform</p>
                    <p className="text-xs text-gray-700 mt-2">
                      Full-featured YouTube-like platform with video streaming, MongoDB Atlas fuzzy search, NSFW classifier, deployed on AWS EC2 behind Nginx (99% uptime).
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {['Node.js', 'React', 'MongoDB Atlas', 'Docker', 'AWS EC2'].map((t) => (
                        <span key={t} className="text-xs bg-white border border-gray-300 px-2 py-0.5 rounded text-gray-700">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar info */}
            <div className="space-y-6">
              {/* Education Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-md font-bold text-gray-900 mb-3 flex items-center">
                  <GraduationCap className="w-5 h-5 mr-2 text-teal-600" /> Education
                </h3>
                <div>
                  <h4 className="font-semibold text-gray-900 text-sm">B.Tech - Electronics & Communication</h4>
                  <p className="text-xs text-gray-600">Cochin University of Science and Technology (CUSAT)</p>
                  <p className="text-xs text-gray-500 mt-1">2019 – 2023 • Kochi, Kerala</p>
                  <div className="mt-3 inline-block bg-teal-50 border border-teal-200 text-teal-800 text-xs px-2.5 py-1 rounded-md font-semibold">
                    CGPA: 8.91 / 10 (First Class with Distinction)
                  </div>
                </div>
              </div>

              {/* Preferences Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-md font-bold text-gray-900 mb-3 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-blue-600" /> Application Preferences
                </h3>
                <div className="space-y-3 text-xs text-gray-700">
                  <div>
                    <span className="font-semibold text-gray-900">Total Experience:</span> 3+ years (39 months)
                  </div>
                  <div>
                    <span className="font-semibold text-gray-900">Notice Period:</span> 30 days
                  </div>
                  <div>
                    <span className="font-semibold text-gray-900">Remote Preference:</span> Hybrid or Remote
                  </div>
                  <div>
                    <span className="font-semibold text-gray-900">Target Locations:</span> Mumbai, Bengaluru, Hyderabad, Pune, Remote
                  </div>
                  <div>
                    <span className="font-semibold text-gray-900">Target Roles:</span> Senior Software Engineer, Backend Engineer, Java Full Stack
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Skills Taxonomy */}
        {activeTab === 'skills' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {skillsData?.categories.map((cat) => (
                <div key={cat.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                  <h4 className="font-bold text-gray-900 text-md mb-3 pb-2 border-b border-gray-100 flex justify-between items-center">
                    <span>{cat.name}</span>
                    <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-normal">
                      {cat.skills.length} skills
                    </span>
                  </h4>
                  <div className="space-y-2.5">
                    {cat.skills.map((skill) => (
                      <div key={skill.name} className="flex items-center justify-between text-sm py-1 border-b border-gray-50">
                        <div className="flex items-center space-x-2">
                          <span className={`w-2 h-2 rounded-full ${skill.primary ? 'bg-blue-600' : 'bg-slate-300'}`}></span>
                          <span className="font-medium text-gray-800">{skill.name}</span>
                        </div>
                        <div className="flex items-center space-x-1.5">
                          <span className="text-xs text-gray-500 font-mono">{skill.years_experience}y</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded capitalize ${
                              skill.proficiency === 'expert'
                                ? 'bg-purple-100 text-purple-800 font-semibold'
                                : skill.proficiency === 'advanced'
                                ? 'bg-blue-100 text-blue-800 font-medium'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {skill.proficiency}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Verified Facts */}
        {activeTab === 'facts' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
            <div className="flex flex-col sm:flex-row justify-between gap-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Category:</span>
                <select
                  value={factCategoryFilter}
                  onChange={(e) => setFactCategoryFilter(e.target.value)}
                  className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-blue-500 text-black"
                >
                  <option value="all">All Categories</option>
                  <option value="experience">Experience</option>
                  <option value="skill">Skills</option>
                  <option value="project">Projects</option>
                  <option value="education">Education</option>
                </select>
              </div>

              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search facts or keywords..."
                  value={factSearch}
                  onChange={(e) => setFactSearch(e.target.value)}
                  className="pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 text-black w-full sm:w-64"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase">
                    <th className="py-3 px-4">Fact ID</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Verified Claim</th>
                    <th className="py-3 px-4">Source</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredFacts.map((fact) => (
                    <tr key={fact.id || fact.fact_id} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-mono text-xs text-blue-600">{fact.fact_id}</td>
                      <td className="py-3 px-4">
                        <span className="capitalize text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
                          {fact.category}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-900 max-w-xl">{fact.claim}</td>
                      <td className="py-3 px-4 text-xs text-gray-500">{fact.source}</td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded">
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Verified
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredFacts.length === 0 && (
                <div className="text-center py-8 text-gray-500">No facts matched your filters.</div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Anti-Hallucination Sandbox */}
        {activeTab === 'validator' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Box */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-gray-900 text-md flex items-center">
                  <ShieldCheck className="w-5 h-5 mr-2 text-blue-600" /> Resume / Claim Validator
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPresetText('clean')}
                    className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded"
                  >
                    Clean Preset
                  </button>
                  <button
                    onClick={() => setPresetText('hallucination')}
                    className="text-xs bg-red-50 hover:bg-red-100 text-red-700 px-2.5 py-1 rounded"
                  >
                    Hallucination Preset
                  </button>
                  <button
                    onClick={() => setPresetText('metric')}
                    className="text-xs bg-amber-50 hover:bg-amber-100 text-amber-700 px-2.5 py-1 rounded"
                  >
                    Metric Preset
                  </button>
                </div>
              </div>

              <p className="text-xs text-gray-600">
                Type or paste resume text to test the anti-hallucination engine. Every technical skill, metric, and bullet point will be checked against Shubham Prakash's verified knowledge base.
              </p>

              <textarea
                rows={10}
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
                className="w-full text-sm font-mono p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 text-black"
                placeholder="Paste resume markdown or claims here..."
              />

              <button
                onClick={handleValidate}
                disabled={validating}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                {validating ? 'Analyzing Against KB...' : 'Run Anti-Hallucination Validation'}
              </button>
            </div>

            {/* Validation Report */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
              <h3 className="font-bold text-gray-900 text-md">Validation Results</h3>

              {!validationResult ? (
                <div className="h-64 flex flex-col items-center justify-center text-gray-400 text-sm">
                  <ShieldCheck className="w-12 h-12 mb-2 stroke-1" />
                  Click &quot;Run Anti-Hallucination Validation&quot; to inspect text.
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Status Banner */}
                  <div
                    className={`p-4 rounded-lg border flex items-center justify-between ${
                      validationResult.passed
                        ? 'bg-green-50 border-green-200 text-green-800'
                        : 'bg-red-50 border-red-200 text-red-800'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {validationResult.passed ? (
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600" />
                      )}
                      <span className="font-bold">
                        {validationResult.passed ? 'PASSED: Verified Against Knowledge Base' : 'FAILED: Hallucinations / Discrepancies Detected'}
                      </span>
                    </div>
                    <span className="text-sm font-semibold">
                      Score: {(validationResult.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Errors / Hallucinations */}
                  {validationResult.errors.length > 0 && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg space-y-1">
                      <p className="text-xs font-bold text-red-800">Errors & Hallucinations:</p>
                      <ul className="text-xs text-red-700 list-disc list-inside space-y-1">
                        {validationResult.errors.map((e, idx) => (
                          <li key={idx}>{e}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Hallucinated Skills */}
                  {validationResult.hallucinated_skills.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-700 mb-1">Unverified Tech / Hallucinations:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {validationResult.hallucinated_skills.map((s) => (
                          <span key={s} className="text-xs bg-red-100 text-red-800 font-semibold px-2.5 py-0.5 rounded">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Verified Skills */}
                  {validationResult.verified_skills.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-700 mb-1">Verified Skills Found in Text:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {validationResult.verified_skills.map((s) => (
                          <span key={s} className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Supported Claims */}
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">
                      Supported Claims ({validationResult.supported_claims_count}):
                    </p>
                    <div className="max-h-48 overflow-y-auto space-y-1.5 border border-gray-100 p-2 rounded">
                      {validationResult.supported_claims.map((sc, idx) => (
                        <div key={idx} className="text-xs bg-gray-50 p-2 rounded border border-gray-200">
                          <p className="text-gray-900">{sc.claim}</p>
                          <p className="text-xs text-blue-600 font-mono mt-0.5">Source: {sc.source || 'Verified KB'}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
