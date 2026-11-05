import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import { HotspotDashboardData } from '../types';
import { CampusMapSchematic } from '../components/CampusMapSchematic';
import {
  MapPin,
  Building2,
  AlertTriangle,
  Clock,
  ArrowRight,
  BarChart2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export const HotspotAnalysis: React.FC = () => {
  const [data, setData] = useState<HotspotDashboardData | null>(null);
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsService
      .getHotspots()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div className="py-24 text-center text-xs text-slate-500">Compiling hotspot density metrics...</div>;
  }

  const topLocations = [...data.locations].sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <MapPin className="w-5 h-5 text-blue-600" />
            <span>Campus Incident Hotspot Analysis</span>
          </h1>
          <p className="text-xs text-slate-500">
            Spatial density mapping and infrastructure risk concentration across university facilities.
          </p>
        </div>
      </div>

      {/* Campus Map Schematic */}
      <CampusMapSchematic
        locations={data.locations}
        selectedBuilding={selectedBuilding}
        onSelectBuilding={setSelectedBuilding}
      />

      {/* Chart: Incidents by Campus Facility */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-blue-600" />
              <span>Incident Volume by Campus Facility</span>
            </h3>
            <p className="text-xs text-slate-500">Distribution of all logged reports across major buildings</p>
          </div>
        </div>

        <div className="h-72 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topLocations.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="building"
                stroke="#94a3b8"
                fontSize={10}
                interval={0}
                angle={-20}
                textAnchor="end"
                height={50}
              />
              <YAxis stroke="#94a3b8" fontSize={11} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar dataKey="count" name="Total Reports" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="critical_count" name="Critical Severity" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="unresolved_count" name="Unresolved" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ranking Hotspots Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Highest Frequency Campus Hotspots</h3>
            <p className="text-xs text-slate-500">Ranked by total reports and hazard urgency</p>
          </div>
        </div>

        <div className="overflow-x-auto mt-2">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
                <th className="py-3 px-3">Rank</th>
                <th className="py-3 px-3">Building / Location</th>
                <th className="py-3 px-3">Total Reports</th>
                <th className="py-3 px-3">Critical / High</th>
                <th className="py-3 px-3">Unresolved Backlog</th>
                <th className="py-3 px-3">Primary Category</th>
                <th className="py-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {topLocations.map((loc, idx) => (
                <tr key={loc.building} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-3 font-bold text-slate-400">#{idx + 1}</td>
                  <td className="py-3 px-3 font-bold text-slate-900">
                    {loc.building}
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-800">{loc.count}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      loc.critical_count > 0 ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {loc.critical_count + loc.high_count} Severe
                    </span>
                  </td>
                  <td className="py-3 px-3 font-semibold text-amber-700">
                    {loc.unresolved_count} open
                  </td>
                  <td className="py-3 px-3 text-blue-700 font-medium">
                    {loc.primary_category}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <Link
                      to={`/incidents?building=${encodeURIComponent(loc.building)}`}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                    >
                      <span>Filter</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
