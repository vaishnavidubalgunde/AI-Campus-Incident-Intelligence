import React, { useState, useEffect } from 'react';
import { systemService } from '../services/api';
import { AuditLogItem } from '../types';
import {
  Settings,
  ShieldCheck,
  Database,
  RefreshCw,
  CheckCircle2,
  Clock,
  User,
  Cpu,
  Layers,
  Sparkles
} from 'lucide-react';

export const SettingsAudit: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedNotice, setSeedNotice] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      const data = await systemService.getAuditLogs();
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleSeedDemo = async () => {
    if (!window.confirm('Re-seed demonstration database with over 220 synthetic incidents? Current temporary demo edits will be reset to standard synthetic demonstration dataset.')) {
      return;
    }
    setIsSeeding(true);
    try {
      const res = await systemService.seedDemo();
      setSeedNotice(res.message || 'Synthetic demonstration dataset re-seeded successfully.');
      await fetchLogs();
      setTimeout(() => setSeedNotice(null), 5000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Settings className="w-5 h-5 text-blue-600" />
            <span>Audit Trail & AI System Architecture</span>
          </h1>
          <p className="text-xs text-slate-500">
            Immutable administrative event logging and local AI machine learning configuration.
          </p>
        </div>

        <button
          onClick={handleSeedDemo}
          disabled={isSeeding}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs flex items-center space-x-2 transition-colors disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isSeeding ? 'animate-spin' : ''}`} />
          <span>{isSeeding ? 'Re-seeding Demo...' : 'Re-seed Demo Database (220+ Records)'}</span>
        </button>
      </div>

      {seedNotice && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-medium flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{seedNotice}</span>
        </div>
      )}

      {/* AI Engine Status Overview */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-sky-400" />
            <h3 className="text-sm font-bold tracking-tight">Active AI Core Modules</h3>
          </div>
          <span className="text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-400/30">
            Offline & Local Python ML Active
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          <div className="bg-white/5 p-3.5 rounded-xl border border-white/5 space-y-1">
            <span className="font-bold text-sky-300 block flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Hybrid NLP Classifier</span>
            </span>
            <p className="text-[11px] text-slate-300">
              Scikit-learn TF-IDF n-grams + Multinomial Naive Bayes with rule-assisted high confidence matching.
            </p>
          </div>

          <div className="bg-white/5 p-3.5 rounded-xl border border-white/5 space-y-1">
            <span className="font-bold text-amber-300 block flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Severity Scoring Engine</span>
            </span>
            <p className="text-[11px] text-slate-300">
              Multi-factor transparent priority scoring with compound hazard detection (water near electrics).
            </p>
          </div>

          <div className="bg-white/5 p-3.5 rounded-xl border border-white/5 space-y-1">
            <span className="font-bold text-purple-300 block flex items-center space-x-1">
              <Layers className="w-3.5 h-3.5" />
              <span>DBSCAN Density Clustering</span>
            </span>
            <p className="text-[11px] text-slate-300">
              Cosine distance matrix clustering identifying recurring problem hotspots across buildings.
            </p>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">Administrative Audit Trail</h3>
          <span className="text-xs text-slate-400">Past 100 System & Staff Actions</span>
        </div>

        {loading ? (
          <div className="py-20 text-center text-xs text-slate-500">Loading audit history...</div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center text-xs text-slate-500">No audit records logged yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Operator</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-800 whitespace-nowrap">
                      {log.user_name || 'System Auto'}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="font-mono text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 whitespace-nowrap">
                      {log.entity_type} {log.entity_id ? `#${log.entity_id}` : ''}
                    </td>
                    <td className="py-3 px-4 text-slate-700 max-w-md truncate">
                      {log.details || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
