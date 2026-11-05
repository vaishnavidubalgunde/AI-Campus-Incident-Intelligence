import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsService, incidentService } from '../services/api';
import { StatsOverview, HotspotDashboardData, Incident } from '../types';
import { StatCard } from '../components/StatCard';
import { CampusMapSchematic } from '../components/CampusMapSchematic';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import {
  FileText,
  Clock,
  AlertTriangle,
  Users2,
  CheckCircle2,
  Activity,
  BrainCircuit,
  ArrowRight,
  TrendingUp,
  MapPin,
  Sparkles,
  BarChart3
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
  Legend
} from 'recharts';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [hotspotData, setHotspotData] = useState<HotspotDashboardData | null>(null);
  const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      const [overviewRes, hotspotsRes, incRes] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getHotspots(),
        incidentService.list({
          building: selectedBuilding || undefined,
          page_size: 6,
        }),
      ]);
      setStats(overviewRes);
      setHotspotData(hotspotsRes);
      setRecentIncidents(incRes.incidents);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [selectedBuilding]);

  const COLORS = ['#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626', '#0891b2', '#475569'];
  const SEVERITY_COLORS: Record<string, string> = {
    Critical: '#dc2626',
    High: '#ea580c',
    Medium: '#eab308',
    Low: '#16a34a',
  };

  if (loading || !stats || !hotspotData) {
    return <div className="py-24 text-center text-xs text-slate-500">Loading campus operations intelligence...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Executive Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 rounded-2xl p-6 sm:p-8 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-blue-200 tracking-wide mb-3">
            <Activity className="w-3.5 h-3.5 text-sky-400" />
            <span>Campus Incident Intelligence Operations Center</span>
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Campus Operations & AI Decision Engine
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Real-time multi-category incident monitoring, automatic clustering with DBSCAN,
            severity prioritization, and actionable facilities dispatch.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          <Link
            to="/intelligence"
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 flex items-center space-x-2 transition-all"
          >
            <BrainCircuit className="w-4 h-4" />
            <span>AI Pattern Discovery</span>
          </Link>
          <Link
            to="/recommendations"
            className="px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold backdrop-blur-md flex items-center space-x-2 transition-all"
          >
            <Sparkles className="w-4 h-4 text-sky-300" />
            <span>Action Recommendations</span>
          </Link>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          title="Total Reports"
          value={stats.total_incidents}
          subtitle="All recorded incidents"
          icon={FileText}
          colorScheme="blue"
        />
        <StatCard
          title="New Triage"
          value={stats.new_incidents}
          subtitle="Awaiting initial review"
          icon={Clock}
          colorScheme="slate"
        />
        <StatCard
          title="Critical / High"
          value={stats.critical_high_count}
          subtitle="Priority hazards"
          icon={AlertTriangle}
          colorScheme="red"
        />
        <StatCard
          title="In Progress"
          value={stats.in_progress_count}
          subtitle="Work crew active"
          icon={Activity}
          colorScheme="purple"
        />
        <StatCard
          title="Overdue (> 4d)"
          value={stats.overdue_count}
          subtitle="Breaching response SLA"
          icon={AlertTriangle}
          colorScheme="amber"
        />
        <StatCard
          title="Resolved"
          value={stats.resolved_count}
          subtitle={`Avg ${stats.avg_resolution_hours}h resolve`}
          icon={CheckCircle2}
          colorScheme="emerald"
        />
      </div>

      {/* Interactive Campus Building Schematic Grid */}
      <CampusMapSchematic
        locations={hotspotData.locations}
        selectedBuilding={selectedBuilding}
        onSelectBuilding={setSelectedBuilding}
      />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 14-day Trend Line Chart */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span>14-Day Incident Volume vs. Resolution Rate</span>
              </h3>
              <p className="text-xs text-slate-500">Daily intake velocity tracked against team completions</p>
            </div>
          </div>
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hotspotData.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Reports Filed"
                  stroke="#2563eb"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="resolved"
                  name="Resolved"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Pie Chart */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="pb-4 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Severity Distribution</h3>
            <p className="text-xs text-slate-500">AI-computed hazard risk tiers</p>
          </div>
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={hotspotData.severities}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  innerRadius={45}
                  paddingAngle={4}
                >
                  {hotspotData.severities.map((entry) => (
                    <Cell
                      key={entry.severity}
                      fill={SEVERITY_COLORS[entry.severity] || '#64748b'}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Category Breakdown Bar Chart */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="pb-4 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Incidents by Domain Category</h3>
            <p className="text-xs text-slate-500">Breakdown of reported facility disciplines</p>
          </div>
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hotspotData.categories.slice(0, 6)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                <YAxis
                  dataKey="category"
                  type="category"
                  stroke="#94a3b8"
                  fontSize={10}
                  width={140}
                  tickFormatter={(val) => (val.length > 20 ? `${val.slice(0, 18)}...` : val)}
                />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Team Workload Distribution */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Response Team Workload</h3>
              <p className="text-xs text-slate-500">Active tickets queued per department</p>
            </div>
            <Link to="/teams" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
              Manage Teams →
            </Link>
          </div>
          <div className="divide-y divide-slate-100 mt-3 max-h-64 overflow-y-auto">
            {hotspotData.team_workloads.map((team) => (
              <div key={team.department} className="py-2.5 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-slate-900 block">{team.department}</span>
                  <span className="text-[10px] text-slate-400">
                    {team.resolved_count} completed this term
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-amber-50 text-amber-700 border border-amber-200">
                    {team.pending_count} pending
                  </span>
                  <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-purple-50 text-purple-700 border border-purple-200">
                    {team.in_progress_count} in-progress
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filtered Incidents Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              {selectedBuilding ? `Incidents in ${selectedBuilding}` : 'Recent Campus Incidents'}
            </h3>
            <p className="text-xs text-slate-500">Live operational feed from across the institution</p>
          </div>
          <Link to="/incidents" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
            View All Incidents Table →
          </Link>
        </div>

        <div className="divide-y divide-slate-100 mt-2">
          {recentIncidents.map((inc) => (
            <div key={inc.id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-blue-700">{inc.incident_number}</span>
                  <SeverityBadge severity={inc.severity} size="sm" />
                  <StatusBadge status={inc.status} size="sm" />
                </div>
                <Link
                  to={`/incidents/${inc.id}`}
                  className="text-sm font-semibold text-slate-900 hover:text-blue-600 block line-clamp-1"
                >
                  {inc.title}
                </Link>
                <div className="text-[11px] text-slate-400 flex items-center space-x-3">
                  <span>{inc.building} — {inc.location}</span>
                  <span>{new Date(inc.created_at).toLocaleDateString()}</span>
                  <span className="text-blue-600 font-medium">{inc.category_name}</span>
                </div>
              </div>

              <Link
                to={`/incidents/${inc.id}`}
                className="self-start sm:self-center px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-blue-600 hover:text-white text-xs font-semibold text-slate-700 transition-colors"
              >
                Inspect →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
