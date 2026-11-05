import React, { useState, useEffect } from 'react';
import { intelligenceService } from '../services/api';
import { Recommendation } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  Building2,
  ShieldCheck,
  ArrowRight,
  Check,
  AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    try {
      const data = await intelligenceService.getRecommendations();
      setRecommendations(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleAction = async (id: number, status: 'actioned' | 'dismissed') => {
    try {
      await intelligenceService.actionRecommendation(id, status);
      setActionNotice(`Recommendation status updated to ${status}.`);
      setRecommendations(recommendations.filter((r) => r.id !== id));
      setTimeout(() => setActionNotice(null), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-md">
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-sky-300 tracking-wide mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Decision Support Intelligence</span>
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Smart Administrative Recommendations
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-blue-100 max-w-2xl leading-relaxed">
          Rule-assisted algorithmic recommendations generated directly from campus incident frequencies,
          recurring faults, and crew backlog distributions.
        </p>
      </div>

      {actionNotice && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-medium flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{actionNotice}</span>
        </div>
      )}

      {loading ? (
        <div className="py-24 text-center text-xs text-slate-500">Synthesizing recommendations...</div>
      ) : recommendations.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-xs text-slate-500 space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
          <p className="text-sm font-bold text-slate-800">All current recommendations actioned</p>
          <p className="text-slate-400">Campus operational risk indicators are currently within normal baseline.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center space-x-2">
                    <SeverityBadge severity={rec.priority} />
                    <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                      Target: {rec.suggested_department}
                    </span>
                  </div>
                  <span className="text-[11px] font-semibold text-slate-400">
                    {(rec.confidence * 100).toFixed(0)}% Confidence
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {rec.title}
                </h3>

                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                  {rec.reason}
                </p>

                <div className="text-xs text-slate-500 flex items-center space-x-2 pt-1">
                  <ShieldCheck className="w-4 h-4 text-blue-600" />
                  <span>
                    Backed by {rec.supporting_incident_count} empirical database reports (
                    {rec.supporting_incident_ids.slice(0, 4).map((id) => `#${id}`).join(', ')}...)
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                <Link
                  to="/incidents"
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                >
                  <span>Review tickets</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleAction(rec.id, 'dismissed')}
                    className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 text-xs font-semibold transition-colors flex items-center space-x-1"
                  >
                    <XCircle className="w-3.5 h-3.5 text-slate-400" />
                    <span>Dismiss</span>
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, 'actioned')}
                    className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-colors flex items-center space-x-1"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Action Policy</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
