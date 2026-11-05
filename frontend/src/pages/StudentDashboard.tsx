import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { incidentService, notificationService } from '../services/api';
import { Incident, NotificationItem } from '../types';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  PlusCircle,
  ArrowRight,
  Bell,
  Search,
  MapPin,
  Calendar
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [incRes, notifRes] = await Promise.all([
          incidentService.list({ mine_only: true, page_size: 10 }),
          notificationService.getAll(),
        ]);
        setIncidents(incRes.incidents);
        setNotifications(notifRes);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const total = incidents.length;
  const openCount = incidents.filter((i) => ['submitted', 'verified'].includes(i.status)).length;
  const inProgressCount = incidents.filter((i) => ['under_review', 'assigned', 'in_progress'].includes(i.status)).length;
  const resolvedCount = incidents.filter((i) => ['resolved', 'closed'].includes(i.status)).length;

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <span className="inline-block px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-blue-200 tracking-wide mb-3">
            Student Incident Reporting Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.full_name}
          </h1>
          <p className="mt-2 text-sm text-blue-100/90 leading-relaxed">
            Report infrastructure defects, safety hazards, and facility breakdowns using natural language.
            Our AI engine classifies issues and routes them instantly to response teams.
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/report"
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-blue-500 hover:bg-blue-400 text-white rounded-xl text-sm font-semibold shadow-md shadow-blue-500/20 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Report an Incident</span>
            </Link>
            <Link
              to="/my-incidents"
              className="inline-flex items-center space-x-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-semibold backdrop-blur-md transition-all"
            >
              <span>View All My Reports</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Reported"
          value={total}
          subtitle="Your submitted reports"
          icon={FileText}
          colorScheme="blue"
        />
        <StatCard
          title="Awaiting Review"
          value={openCount}
          subtitle="New submission queue"
          icon={Clock}
          colorScheme="amber"
        />
        <StatCard
          title="Under Investigation"
          value={inProgressCount}
          subtitle="Assigned to work crews"
          icon={AlertTriangle}
          colorScheme="purple"
        />
        <StatCard
          title="Resolved"
          value={resolvedCount}
          subtitle="Verified operational"
          icon={CheckCircle2}
          colorScheme="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Incidents Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h3 className="text-base font-bold text-slate-900">Recent Incident Submissions</h3>
              <p className="text-xs text-slate-500">Live operational status of your campus reports</p>
            </div>
            <Link
              to="/my-incidents"
              className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
            >
              <span>See full list</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-slate-500">Loading your reports...</div>
          ) : incidents.length === 0 ? (
            <div className="py-12 text-center">
              <FileText className="w-10 h-10 text-slate-300 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-700">No incident reports filed yet</p>
              <p className="text-xs text-slate-500 mt-1">
                Notice water leaks, damaged panels, or Wi-Fi drops? Report them in seconds.
              </p>
              <Link
                to="/report"
                className="mt-4 inline-flex items-center space-x-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Submit First Report</span>
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-slate-100 mt-2">
              {incidents.slice(0, 5).map((inc) => (
                <div key={inc.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-blue-700">
                        {inc.incident_number}
                      </span>
                      <SeverityBadge severity={inc.severity} size="sm" />
                      <StatusBadge status={inc.status} size="sm" />
                    </div>
                    <Link
                      to={`/incidents/${inc.id}`}
                      className="text-sm font-semibold text-slate-900 hover:text-blue-600 block line-clamp-1"
                    >
                      {inc.title}
                    </Link>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span>{inc.building} - {inc.location}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>{new Date(inc.created_at).toLocaleDateString()}</span>
                      </span>
                    </div>
                  </div>

                  <Link
                    to={`/incidents/${inc.id}`}
                    className="self-start sm:self-center px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    Details →
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notifications & System Updates */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <Bell className="w-4 h-4 text-blue-600" />
                <span>Status Notifications</span>
              </h3>
            </div>

            <div className="mt-3 space-y-3 max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <p className="text-xs text-slate-500 py-8 text-center italic">
                  No notifications yet. You will receive real-time updates when an administrator actions your report.
                </p>
              ) : (
                notifications.slice(0, 5).map((n) => (
                  <div
                    key={n.id}
                    className="p-3 rounded-xl bg-slate-50 border border-slate-200/70 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{n.title}</span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="text-slate-600 text-[11px] leading-relaxed">{n.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 bg-blue-50/50 rounded-xl p-3 text-xs text-blue-900">
            <span className="font-bold block text-[11px] uppercase tracking-wider text-blue-700">Campus Safety Helpline</span>
            <span className="text-xs font-medium">Emergency Control Desk: Ext. 4444 / (080) 2345-6789</span>
          </div>
        </div>
      </div>
    </div>
  );
};
