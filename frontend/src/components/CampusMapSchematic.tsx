import React from 'react';
import { LocationHotspot } from '../types';
import { Building2, AlertTriangle, CheckCircle2, ChevronRight, Zap, Droplet, Wifi } from 'lucide-react';

interface CampusMapSchematicProps {
  locations: LocationHotspot[];
  selectedBuilding?: string | null;
  onSelectBuilding: (building: string | null) => void;
}

export const CampusMapSchematic: React.FC<CampusMapSchematicProps> = ({
  locations,
  selectedBuilding,
  onSelectBuilding,
}) => {
  // Mapping campus zones with layout coordinates and visual themes
  const buildingsConfig = [
    { key: 'Block C', name: 'Block C (Civil & Architecture)', zone: 'North Quad', color: 'from-blue-600 to-indigo-700', icon: Droplet },
    { key: 'Central Library', name: 'Central Library & Digital Centre', zone: 'Academic Core', color: 'from-amber-600 to-orange-700', icon: Wifi },
    { key: 'Block A', name: 'Computer Science & IT Block', zone: 'West Wing', color: 'from-emerald-600 to-teal-700', icon: Zap },
    { key: 'Block B', name: 'Block B (Basic Sciences & Physics)', zone: 'West Wing', color: 'from-violet-600 to-purple-700', icon: Zap },
    { key: 'Block E', name: 'Mechanical & Heavy Labs', zone: 'South Sector', color: 'from-slate-700 to-zinc-800', icon: Building2 },
    { key: 'Cafeteria', name: 'Student Dining & Food Court', zone: 'Central Plaza', color: 'from-rose-600 to-pink-700', icon: Building2 },
    { key: 'Hostel 1', name: 'Boys Hostel 1 Complex', zone: 'Residential East', color: 'from-cyan-600 to-blue-700', icon: Building2 },
    { key: 'Hostel 2', name: 'Girls Hostel 2 Complex', zone: 'Residential East', color: 'from-fuchsia-600 to-purple-700', icon: Building2 },
    { key: 'Auditorium', name: 'University Main Auditorium', zone: 'South Sector', color: 'from-indigo-600 to-blue-800', icon: Building2 },
    { key: 'Sports Complex', name: 'Indoor Sports & Gymnasium', zone: 'Recreation Zone', color: 'from-lime-600 to-emerald-700', icon: Building2 },
    { key: 'Admin Block', name: 'Administrative & Registrar Office', zone: 'Main Entrance', color: 'from-slate-600 to-slate-800', icon: Building2 },
  ];

  const getStats = (buildingKey: string) => {
    const loc = locations.find(
      (l) => l.building.toLowerCase() === buildingKey.toLowerCase() || l.location.toLowerCase().includes(buildingKey.toLowerCase())
    );
    return {
      count: loc ? loc.count : 0,
      critical: loc ? loc.critical_count : 0,
      high: loc ? loc.high_count : 0,
      unresolved: loc ? loc.unresolved_count : 0,
      category: loc ? loc.primary_category : 'None',
    };
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-blue-600" />
            <span>Interactive Campus Building Grid & Hotspot Schematic</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time visual density of campus reports. Click any building block to filter associated incidents.
          </p>
        </div>

        {selectedBuilding && (
          <button
            onClick={() => onSelectBuilding(null)}
            className="self-start text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors flex items-center space-x-1"
          >
            <span>Clear Filter ({selectedBuilding})</span>
            <span>×</span>
          </button>
        )}
      </div>

      {/* Grid of campus facilities */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-5">
        {buildingsConfig.map((b) => {
          const stats = getStats(b.key);
          const isSelected = selectedBuilding === b.key;
          const hasCritical = stats.critical > 0;
          const hasHigh = stats.high > 0;
          const Icon = b.icon;

          return (
            <div
              key={b.key}
              onClick={() => onSelectBuilding(isSelected ? null : b.key)}
              className={`relative rounded-xl border p-4 cursor-pointer transition-all duration-200 text-left ${
                isSelected
                  ? 'border-blue-600 ring-2 ring-blue-500/30 bg-blue-50/40 shadow-sm'
                  : 'border-slate-200 hover:border-blue-300 hover:shadow-md bg-white'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${b.color} text-white flex items-center justify-center shadow-xs`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 leading-tight">{b.key}</h4>
                    <span className="text-[10px] text-slate-400 block">{b.zone}</span>
                  </div>
                </div>

                {hasCritical ? (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 border border-red-200 animate-pulse">
                    {stats.critical} Critical
                  </span>
                ) : hasHigh ? (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-700 border border-orange-200">
                    {stats.high} High
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600">
                    {stats.count} Reports
                  </span>
                )}
              </div>

              {/* Sub details */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <div>
                  <span className="block text-[10px] uppercase font-semibold text-slate-400">Unresolved</span>
                  <span className="font-bold text-slate-800">{stats.unresolved} open</span>
                </div>
                <div className="text-right">
                  <span className="block text-[10px] uppercase font-semibold text-slate-400">Primary Domain</span>
                  <span className="font-semibold text-blue-700 truncate max-w-[110px] block">
                    {stats.category}
                  </span>
                </div>
              </div>

              {/* Select Indicator */}
              <div className="mt-3 flex items-center justify-end text-[11px] font-semibold text-blue-600">
                <span>{isSelected ? 'Filtered' : 'Filter incidents'}</span>
                <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
