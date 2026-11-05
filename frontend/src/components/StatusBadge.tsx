import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const st = (status || 'submitted').toLowerCase();

  let styles = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = st.replace('_', ' ');

  switch (st) {
    case 'submitted':
      styles = 'bg-blue-50 text-blue-700 border-blue-200';
      break;
    case 'under_review':
      styles = 'bg-sky-50 text-sky-800 border-sky-200';
      break;
    case 'verified':
      styles = 'bg-cyan-50 text-cyan-800 border-cyan-200';
      break;
    case 'assigned':
      styles = 'bg-indigo-50 text-indigo-700 border-indigo-200';
      break;
    case 'in_progress':
      styles = 'bg-purple-50 text-purple-700 border-purple-200 ring-1 ring-purple-200';
      break;
    case 'resolved':
      styles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      break;
    case 'closed':
      styles = 'bg-slate-100 text-slate-600 border-slate-200';
      break;
    case 'duplicate':
      styles = 'bg-zinc-100 text-zinc-600 border-zinc-200 border-dashed';
      break;
    case 'rejected':
      styles = 'bg-rose-50 text-rose-700 border-rose-200';
      break;
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-0.5 text-xs';

  return (
    <span className={`inline-flex items-center font-medium capitalize rounded-md border ${styles} ${sizeClasses}`}>
      {label}
    </span>
  );
};
