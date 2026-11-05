import React, { useState, useEffect } from 'react';
import { metadataService, analyticsService } from '../services/api';
import { Department, TeamWorkload } from '../types';
import { Users2, Mail, UserCheck, ShieldCheck, Activity } from 'lucide-react';

export const TeamsManagement: React.FC = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [workloads, setWorkloads] = useState<TeamWorkload[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([metadataService.getDepartments(), analyticsService.getHotspots()])
      .then(([deptRes, hotspotRes]) => {
        setDepartments(deptRes);
        setWorkloads(hotspotRes.team_workloads);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const getTeamStats = (deptName: string) => {
    const w = workloads.find((wl) => wl.department.toLowerCase() === deptName.toLowerCase());
    return {
      pending: w ? w.pending_count : 0,
      inProgress: w ? w.in_progress_count : 0,
      resolved: w ? w.resolved_count : 0,
      totalActive: w ? w.pending_count + w.in_progress_count : 0,
    };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Users2 className="w-5 h-5 text-blue-600" />
            <span>Response Teams & Maintenance Workloads</span>
          </h1>
          <p className="text-xs text-slate-500">
            Operational capacity and active incident dispatch distribution across campus response units.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-xs text-slate-500">Loading department telemetry...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {departments.map((dept) => {
            const stats = getTeamStats(dept.name);
            const loadPercent = Math.min(100, (stats.totalActive / 15) * 100);

            return (
              <div
                key={dept.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {dept.code}
                      </span>
                      <h3 className="text-base font-bold text-slate-900 mt-1">{dept.name}</h3>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                      Active
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-600 pt-1">
                    <div className="flex items-center space-x-2">
                      <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                      <span>Head: <strong className="text-slate-800">{dept.head_person || 'Supervisor'}</strong></span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Mail className="w-3.5 h-3.5 text-slate-400" />
                      <span>Email: <span className="font-mono text-slate-500">{dept.contact_email}</span></span>
                    </div>
                  </div>

                  {/* Workload Metric Bar */}
                  <div className="pt-3 border-t border-slate-100 space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-[11px] font-semibold text-slate-500">Operational Load</span>
                      <span className="font-bold text-slate-800">{stats.totalActive} active tickets</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          loadPercent > 75 ? 'bg-rose-500' : loadPercent > 45 ? 'bg-amber-500' : 'bg-blue-600'
                        }`}
                        style={{ width: `${Math.max(8, loadPercent)}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-slate-50 p-2 rounded-lg">
                    <span className="block text-[10px] uppercase font-bold text-slate-400">Pending</span>
                    <span className="font-bold text-amber-700">{stats.pending}</span>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg">
                    <span className="block text-[10px] uppercase font-bold text-slate-400">In Prog</span>
                    <span className="font-bold text-purple-700">{stats.inProgress}</span>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg">
                    <span className="block text-[10px] uppercase font-bold text-slate-400">Done</span>
                    <span className="font-bold text-emerald-700">{stats.resolved}</span>
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
