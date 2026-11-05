import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { incidentService, metadataService } from '../services/api';
import { Incident, Department, IncidentCategory } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import { Timeline } from '../components/Timeline';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  User,
  Sparkles,
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  Link2,
  Send,
  Users2,
  FileCheck
} from 'lucide-react';

export const IncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  const [incident, setIncident] = useState<Incident | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [categories, setCategories] = useState<IncidentCategory[]>([]);
  const [loading, setLoading] = useState(true);

  // Admin form state
  const [selectedStatus, setSelectedStatus] = useState('');
  const [statusNotes, setStatusNotes] = useState('');
  const [selectedDeptId, setSelectedDeptId] = useState<number | undefined>(undefined);
  const [assignNotes, setAssignNotes] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchDetails = async () => {
    if (!id) return;
    try {
      const inc = await incidentService.getById(Number(id));
      setIncident(inc);
      setSelectedStatus(inc.status);
      setSelectedDeptId(inc.assigned_department_id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
    if (isAdmin) {
      metadataService.getDepartments().then(setDepartments);
      metadataService.getCategories().then(setCategories);
    }
  }, [id, isAdmin]);

  const handleStatusChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incident) return;
    setIsUpdating(true);
    try {
      await incidentService.updateStatus(incident.id, selectedStatus, statusNotes);
      setActionSuccess(`Status successfully updated to ${selectedStatus}`);
      setStatusNotes('');
      fetchDetails();
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAssignDepartment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incident || !selectedDeptId) return;
    setIsUpdating(true);
    try {
      await incidentService.assign(incident.id, selectedDeptId, assignNotes);
      setActionSuccess('Department assignment updated successfully');
      setAssignNotes('');
      fetchDetails();
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleLinkDuplicate = async (targetId: number, simScore: number) => {
    if (!incident) return;
    try {
      await incidentService.linkDuplicate(incident.id, targetId, simScore, 'Confirmed duplicate by administrator');
      setActionSuccess(`Linked as duplicate of incident #${targetId}`);
      fetchDetails();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return <div className="py-20 text-center text-xs text-slate-500">Loading incident intelligence...</div>;
  }

  if (!incident) {
    return (
      <div className="py-20 text-center space-y-3">
        <p className="text-base font-bold text-slate-800">Incident record not found</p>
        <Link to="/incidents" className="text-xs text-blue-600 font-semibold">
          Return to list
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to={isAdmin ? '/incidents' : '/my-incidents'}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isAdmin ? 'Back to All Incidents' : 'Back to My Reports'}</span>
        </Link>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono font-bold text-slate-500">{incident.incident_number}</span>
          <StatusBadge status={incident.status} />
          <SeverityBadge severity={incident.severity} />
        </div>
      </div>

      {actionSuccess && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-medium flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Incident Details & AI Deep Dive */}
        <div className="lg:col-span-7 space-y-6">
          {/* Core Info */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                {incident.category_name}
              </span>
              <h1 className="text-xl font-extrabold text-slate-900 mt-0.5">{incident.title}</h1>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl text-slate-800 text-sm leading-relaxed">
              {incident.description}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-slate-400">Campus Zone</span>
                <span className="font-semibold text-slate-800 block flex items-center space-x-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>{incident.building}</span>
                </span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-slate-400">Room / Floor</span>
                <span className="font-semibold text-slate-800 block flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>{incident.floor_room || 'General Vicinity'}</span>
                </span>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-slate-400">Reporter</span>
                <span className="font-semibold text-slate-800 block flex items-center space-x-1">
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  <span>{incident.reporter_name}</span>
                </span>
              </div>
            </div>

            {incident.resolution_notes && (
              <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-xl text-xs space-y-1">
                <span className="font-bold text-emerald-900 flex items-center space-x-1">
                  <FileCheck className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Resolution Details</span>
                </span>
                <p className="text-emerald-800 text-[11px]">{incident.resolution_notes}</p>
              </div>
            )}
          </div>

          {/* AI Intelligence Deep Dive Card */}
          {incident.ai_analysis && (
            <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-sky-400" />
                  <h3 className="text-sm font-bold tracking-tight">AI Diagnostic Intelligence</h3>
                </div>
                <span className="text-[10px] font-semibold bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded-full border border-sky-400/30">
                  Scikit-Learn NLP Pipeline
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Predicted Category</span>
                  <span className="font-bold text-white text-sm">{incident.ai_analysis.predicted_category}</span>
                  <span className="text-[10px] text-sky-300 block mt-0.5">
                    Confidence: {(incident.ai_analysis.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Priority Score</span>
                  <span className="font-bold text-amber-300 text-sm">{incident.ai_analysis.priority_score} / 100</span>
                  <span className="text-[10px] text-slate-300 block mt-0.5 capitalize">
                    Tier: {incident.ai_analysis.severity_level}
                  </span>
                </div>
              </div>

              {/* Factors */}
              <div className="bg-white/5 p-3.5 rounded-xl border border-white/5 text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">
                  Score Contribution Audit
                </span>
                <ul className="space-y-1 text-[11px] text-slate-300">
                  {incident.ai_analysis.score_factors.map((factor, i) => (
                    <li key={i} className="flex items-start space-x-1.5">
                      <span className="text-sky-400">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action recommendations */}
              <div className="bg-white/5 p-3.5 rounded-xl border border-white/5 text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1.5">
                  Recommended Protocol
                </span>
                <ul className="space-y-1 text-[11px] text-slate-300">
                  {incident.ai_analysis.recommended_actions.map((act, i) => (
                    <li key={i} className="flex items-start space-x-1.5">
                      <span className="text-emerald-400">✓</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Similar Reports */}
              {incident.ai_analysis.similar_incidents && incident.ai_analysis.similar_incidents.length > 0 && (
                <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3.5 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs">
                    <Link2 className="w-4 h-4" />
                    <span>Similar & Duplicate Candidate Records</span>
                  </div>
                  <div className="space-y-2">
                    {incident.ai_analysis.similar_incidents.map((s) => (
                      <div
                        key={s.incident_id}
                        className="bg-black/30 p-2.5 rounded-lg flex items-center justify-between text-xs"
                      >
                        <div className="space-y-0.5 max-w-[280px]">
                          <span className="font-mono text-[10px] text-amber-300">{s.incident_number}</span>
                          <p className="text-[11px] text-slate-200 truncate">{s.title}</p>
                          <span className="text-[10px] text-slate-400">{s.location}</span>
                        </div>
                        <div className="text-right flex items-center space-x-2">
                          <span className="text-xs font-bold text-amber-300">
                            {(s.similarity_score * 100).toFixed(0)}%
                          </span>
                          {isAdmin && !incident.is_duplicate && (
                            <button
                              onClick={() => handleLinkDuplicate(s.incident_id, s.similarity_score)}
                              className="px-2 py-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 rounded text-[10px] font-bold"
                            >
                              Merge
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Col: Timeline & Admin Actions */}
        <div className="lg:col-span-5 space-y-6">
          {/* Admin Operations Control */}
          {isAdmin && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
              <h3 className="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center space-x-2">
                <Users2 className="w-4 h-4 text-blue-600" />
                <span>Administrator Triage Controls</span>
              </h3>

              {/* Status Update Form */}
              <form onSubmit={handleStatusChange} className="space-y-3">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Update Lifecycle Status
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500 outline-hidden"
                >
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="verified">Verified</option>
                  <option value="assigned">Assigned</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                  <option value="rejected">Rejected</option>
                </select>

                <textarea
                  rows={2}
                  placeholder="Audit note or resolution comments..."
                  value={statusNotes}
                  onChange={(e) => setStatusNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500 outline-hidden"
                />

                <button
                  type="submit"
                  disabled={isUpdating}
                  className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors"
                >
                  Confirm Status Change
                </button>
              </form>

              {/* Department Assignment Form */}
              <form onSubmit={handleAssignDepartment} className="space-y-3 pt-3 border-t border-slate-100">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Assign Maintenance / Crew
                </label>
                <select
                  value={selectedDeptId || ''}
                  onChange={(e) => setSelectedDeptId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500 outline-hidden"
                >
                  <option value="">Select Response Team</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.head_person || 'Supervisor'})
                    </option>
                  ))}
                </select>

                <input
                  type="text"
                  placeholder="Assignment dispatch notes..."
                  value={assignNotes}
                  onChange={(e) => setAssignNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500 outline-hidden"
                />

                <button
                  type="submit"
                  disabled={isUpdating || !selectedDeptId}
                  className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
                >
                  Dispatch to Crew
                </button>
              </form>
            </div>
          )}

          {/* Progress Timeline */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 pb-3 border-b border-slate-100">
              Incident Lifecycle Progress
            </h3>
            <div className="mt-4">
              <Timeline history={incident.status_history} currentStatus={incident.status} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
