import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  PlusCircle,
  FileText,
  ListOrdered,
  BrainCircuit,
  MapPin,
  Sparkles,
  MessageSquareCode,
  Users2,
  Settings,
  ShieldCheck,
  Building
} from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { role } = useAuth();
  const isAdmin = role === 'admin';

  interface NavLinkItem {
    to: string;
    label: string;
    icon: any;
    badge?: string;
  }

  const studentLinks: NavLinkItem[] = [
    { to: '/student', label: 'My Dashboard', icon: LayoutDashboard },
    { to: '/report', label: 'Report Incident', icon: PlusCircle },
    { to: '/my-incidents', label: 'My Incident History', icon: FileText },
  ];

  const adminLinks: NavLinkItem[] = [
    { to: '/admin', label: 'Executive Overview', icon: LayoutDashboard },
    { to: '/incidents', label: 'All Incidents', icon: ListOrdered },
    { to: '/intelligence', label: 'AI Pattern Discovery', icon: BrainCircuit, badge: 'AI' },
    { to: '/hotspots', label: 'Campus Hotspot Map', icon: MapPin },
    { to: '/recommendations', label: 'Smart Recommendations', icon: Sparkles, badge: 'Smart' },
    { to: '/assistant', label: 'Analytics Assistant', icon: MessageSquareCode, badge: 'NL' },
    { to: '/teams', label: 'Team Workload & Assign', icon: Users2 },
    { to: '/settings', label: 'Audit Trail & Demo Data', icon: Settings },
  ];

  const links: NavLinkItem[] = isAdmin ? adminLinks : studentLinks;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
        />
      )}

      <aside
        className={`fixed lg:sticky top-16 left-0 z-40 w-64 h-[calc(100vh-4rem)] bg-white border-r border-slate-200 transition-transform duration-300 flex flex-col justify-between overflow-y-auto ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 space-y-6">
          <div className="px-3 py-2 bg-slate-50 border border-slate-200/80 rounded-xl">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-600">
              <Building className="w-4 h-4 text-blue-600" />
              <span>Campus Workspace</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
              <span>Portal Mode:</span>
              <span className="font-bold text-slate-800 uppercase tracking-wider">
                {isAdmin ? 'Admin Console' : 'Student Portal'}
              </span>
            </div>
          </div>

          <nav className="space-y-1">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">
              Navigation
            </div>
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-xs font-semibold'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`
                  }
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{link.label}</span>
                  </div>
                  {link.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider bg-indigo-100 text-indigo-700">
                      {link.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-slate-100 text-xs text-slate-400 bg-slate-50/50">
          <div className="flex items-center space-x-1.5 text-slate-500 font-medium">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>AI Core: Scikit-learn + NLP</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            DBSCAN, TF-IDF & Severity Engine Active
          </p>
        </div>
      </aside>
    </>
  );
};
