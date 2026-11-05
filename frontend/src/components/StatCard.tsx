import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  colorScheme?: 'blue' | 'purple' | 'red' | 'amber' | 'emerald' | 'slate';
  badge?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  colorScheme = 'blue',
  badge,
}) => {
  const schemeClasses = {
    blue: {
      iconBg: 'bg-blue-100 text-blue-700',
      border: 'hover:border-blue-300',
    },
    purple: {
      iconBg: 'bg-purple-100 text-purple-700',
      border: 'hover:border-purple-300',
    },
    red: {
      iconBg: 'bg-red-100 text-red-700',
      border: 'hover:border-red-300',
    },
    amber: {
      iconBg: 'bg-amber-100 text-amber-700',
      border: 'hover:border-amber-300',
    },
    emerald: {
      iconBg: 'bg-emerald-100 text-emerald-700',
      border: 'hover:border-emerald-300',
    },
    slate: {
      iconBg: 'bg-slate-100 text-slate-700',
      border: 'hover:border-slate-300',
    },
  }[colorScheme];

  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-xs transition-all duration-200 hover:shadow-md ${schemeClasses.border}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${schemeClasses.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
        {badge && (
          <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
};
