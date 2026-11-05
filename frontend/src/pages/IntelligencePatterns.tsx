import React, { useState, useEffect } from 'react';
import { intelligenceService } from '../services/api';
import { DiscoveredPattern } from '../types';
import {
  BrainCircuit,
  RefreshCw,
  Sparkles,
  MapPin,
  Tag,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldCheck,
  Layers
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const IntelligencePatterns: React.FC = () => {
  const [patterns, setPatterns] = useState<DiscoveredPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');
  const [notification, setNotification] = useState<string | null>(null);

  const fetchPatterns = async () => {
    try {
      const data = await intelligenceService.getPatterns();
      setPatterns(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatterns();
  }, []);

  const handleRefreshPatterns = async () => {
    setIsRefreshing(true);
    try {
      const res: any = await intelligenceService.refreshPatterns();
      setNotification(res.message || 'Pattern analysis re-computed across all database incidents.');
      await fetchPatterns();
      setTimeout(() => setNotification(null), 4000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRefreshing(false);
    }
  };

  const filteredPatterns = patterns.filter((p) => {
    if (filterType === 'all') return true;
    return p.pattern_type === filterType;
  });

  const getPatternTypeBadge = (type: string) => {
    switch (type) {
      case 'location_hotspot':
        return { label: 'Location Hotspot', color: 'bg-blue-100 text-blue-800 border-blue-200' };
      case 'recurring_issue':
        return { label: 'Semantic DBSCAN Cluster', color: 'bg-purple-100 text-purple-800 border-purple-200' };
      case 'category_spike':
        return { label: 'Multi-Building Anomaly', color: 'bg-amber-100 text-amber-800 border-amber-200' };
      case 'unresolved_cluster':
        return { label: 'Overdue Backlog Bottleneck', color: 'bg-rose-100 text-rose-800 border-rose-200' };
      default:
        return { label: type, color: 'bg-slate-100 text-slate-800 border-slate-200' };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-sky-300 tracking-wide mb-3">
            <BrainCircuit className="w-3.5 h-3.5" />
            <span>Campus Intelligence Engine</span>
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            AI Incident Pattern Discovery
          </h1>
          <p className="mt-2 text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Unsupervised density clustering (DBSCAN), TF-IDF vector similarity, and spatial aggregation
            transform raw individual complaint reports into actionable campus infrastructure intelligence.
          </p>
        </div>

        <button
          onClick={handleRefreshPatterns}
          disabled={isRefreshing}
          className="self-start md:self-center px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 flex items-center space-x-2 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>{isRefreshing ? 'Re-running Algorithms...' : 'Re-Run Pattern Discovery'}</span>
        </button>
      </div>

      {notification && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-medium flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200 p-3 shadow-xs flex flex-wrap gap-2 text-xs">
        {[
          { key: 'all', label: `All Patterns (${patterns.length})` },
          { key: 'location_hotspot', label: 'Building Hotspots' },
          { key: 'recurring_issue', label: 'Semantic Text Clusters' },
          { key: 'category_spike', label: 'Cross-Campus Spikes' },
          { key: 'unresolved_cluster', label: 'SLA Backlogs' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilterType(tab.key)}
            className={`px-3.5 py-1.5 rounded-lg font-semibold transition-colors ${
              filterType === tab.key
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Pattern Cards List */}
      {loading ? (
        <div className="py-24 text-center text-xs text-slate-500">Discovering clusters and trends...</div>
      ) : filteredPatterns.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-xs text-slate-500">
          No patterns found matching this category filter.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredPatterns.map((pat) => {
            const badge = getPatternTypeBadge(pat.pattern_type);

            return (
              <div
                key={pat.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border ${badge.color}`}
                    >
                      {badge.label}
                    </span>
                    <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                      {(pat.confidence_score * 100).toFixed(0)}% Evidence Confidence
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 leading-snug">
                    {pat.pattern_title}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {pat.explanation}
                  </p>

                  <div className="space-y-2 pt-1 text-xs">
                    <div className="flex items-center space-x-2 text-slate-500">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="font-medium text-slate-700">Affected Zones:</span>
                      <span className="truncate">{pat.affected_locations.join(', ')}</span>
                    </div>

                    <div className="flex items-center space-x-2 text-slate-500">
                      <Tag className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="font-medium text-slate-700">Category:</span>
                      <span>{pat.categories.join(', ')}</span>
                    </div>

                    <div className="flex items-center space-x-2 text-slate-500">
                      <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="font-medium text-slate-700">Time Horizon:</span>
                      <span>{pat.time_period}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 space-y-3">
                  {/* Suggested Action Box */}
                  <div className="p-3 bg-blue-50/70 border border-blue-200/80 rounded-xl text-xs space-y-1">
                    <span className="font-bold text-blue-900 flex items-center space-x-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                      <span>Recommended Administrator Action</span>
                    </span>
                    <p className="text-blue-800 text-[11px] leading-relaxed">
                      {pat.suggested_action}
                    </p>
                  </div>

                  {/* Supporting incidents & links */}
                  <div className="flex items-center justify-between text-xs pt-1">
                    <span className="text-[11px] font-semibold text-slate-500">
                      Evidence: {pat.incident_count} reports ({pat.supporting_incident_ids.slice(0, 4).map((id) => `#${id}`).join(', ')}...)
                    </span>
                    <Link
                      to={`/incidents?building=${encodeURIComponent(pat.affected_locations[0] || '')}`}
                      className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <span>Filter related</span>
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
