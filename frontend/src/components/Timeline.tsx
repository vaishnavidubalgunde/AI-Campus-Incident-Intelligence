import React from 'react';
import { StatusHistoryItem } from '../types';
import { CheckCircle2, Clock, User, AlertCircle } from 'lucide-react';

interface TimelineProps {
  history: StatusHistoryItem[];
  currentStatus: string;
}

export const Timeline: React.FC<TimelineProps> = ({ history, currentStatus }) => {
  const steps = [
    { key: 'submitted', label: 'Submitted' },
    { key: 'under_review', label: 'Under Review' },
    { key: 'verified', label: 'Verified' },
    { key: 'assigned', label: 'Assigned' },
    { key: 'in_progress', label: 'In Progress' },
    { key: 'resolved', label: 'Resolved' },
    { key: 'closed', label: 'Closed' },
  ];

  const currentIdx = steps.findIndex((s) => s.key === currentStatus);

  return (
    <div className="space-y-6">
      {/* Horizontal milestone bar */}
      <div className="hidden sm:flex items-center justify-between relative px-2">
        <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-1 bg-slate-200 z-0" />
        {steps.map((s, idx) => {
          const isDone = currentIdx >= idx;
          const isCurrent = currentIdx === idx;

          return (
            <div key={s.key} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-colors ${
                  isCurrent
                    ? 'bg-blue-600 text-white ring-4 ring-blue-100 shadow-sm'
                    : isDone
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white border-2 border-slate-300 text-slate-400'
                }`}
              >
                {isDone ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
              </div>
              <span
                className={`mt-2 text-[11px] font-medium tracking-tight ${
                  isCurrent ? 'font-bold text-blue-700' : isDone ? 'text-slate-800' : 'text-slate-400'
                }`}
              >
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Vertical Detailed History Log */}
      <div className="mt-6 border-t border-slate-100 pt-5">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Status Audit Trail
        </h4>
        <div className="relative pl-6 space-y-4 before:content-[''] before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {history.length === 0 ? (
            <p className="text-xs text-slate-500 italic">Initial submission awaiting review.</p>
          ) : (
            history.map((item) => (
              <div key={item.id} className="relative group text-left">
                <div className="absolute -left-6 top-1.5 w-3.5 h-3.5 rounded-full border-2 border-white bg-blue-600 ring-2 ring-blue-100" />
                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-slate-900 capitalize">
                      Status changed to: <span className="text-blue-700">{item.new_status.replace('_', ' ')}</span>
                    </span>
                    <span className="text-[10px] text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(item.created_at).toLocaleString()}</span>
                    </span>
                  </div>
                  {item.notes && <p className="text-xs text-slate-600 mt-1">{item.notes}</p>}
                  <div className="mt-1 flex items-center text-[10px] text-slate-400 space-x-1">
                    <User className="w-3 h-3" />
                    <span>Actor: {item.changed_by_name || 'System Auto-Triage'}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
