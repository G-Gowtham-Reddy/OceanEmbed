import React from 'react';
import { MapPin, Calendar, Layers, ArrowDownUp, RefreshCw } from 'lucide-react';
import { FilterState } from '../types';

interface FilterBarProps {
  filters: FilterState;
  onChangeFilters: (filters: FilterState) => void;
  onReset?: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onChangeFilters,
  onReset,
}) => {
  const regions = [
    'Equatorial Indian Ocean (0°N - 10°S, 60°E - 90°E)',
    'Bay of Bengal (10°N - 22°N, 80°E - 95°E)',
    'Arabian Sea (10°N - 25°N, 55°E - 75°E)',
    'Southern Tropical Indian Ocean (10°S - 25°S, 50°E - 100°E)',
  ];

  const variables = [
    'Temperature (°C)',
    'Salinity (PSU)',
    'Potential Density (kg/m³)',
    'Sound Velocity (m/s)',
  ];

  return (
    <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-4 shadow-xl backdrop-blur-md">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* Region Selector */}
        <div className="space-y-1.5">
          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-300">
            <MapPin className="h-3.5 w-3.5 text-cyan-400" />
            <span>Target Region</span>
          </label>
          <select
            value={filters.region}
            onChange={(e) => onChangeFilters({ ...filters, region: e.target.value })}
            className="w-full rounded-lg border border-slate-700/80 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          >
            {regions.map((reg) => (
              <option key={reg} value={reg} className="bg-slate-900 text-slate-200">
                {reg}
              </option>
            ))}
          </select>
        </div>

        {/* Date Selector */}
        <div className="space-y-1.5">
          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-300">
            <Calendar className="h-3.5 w-3.5 text-cyan-400" />
            <span>Observation Date</span>
          </label>
          <input
            type="date"
            value={filters.date}
            onChange={(e) => onChangeFilters({ ...filters, date: e.target.value })}
            className="w-full rounded-lg border border-slate-700/80 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </div>

        {/* Variable Selector */}
        <div className="space-y-1.5">
          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-300">
            <Layers className="h-3.5 w-3.5 text-cyan-400" />
            <span>Oceanographic Parameter</span>
          </label>
          <select
            value={filters.variable}
            onChange={(e) => onChangeFilters({ ...filters, variable: e.target.value })}
            className="w-full rounded-lg border border-slate-700/80 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          >
            {variables.map((v) => (
              <option key={v} value={v} className="bg-slate-900 text-slate-200">
                {v}
              </option>
            ))}
          </select>
        </div>

        {/* Depth Range Selector */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-medium text-slate-300">
            <span className="flex items-center gap-1.5">
              <ArrowDownUp className="h-3.5 w-3.5 text-cyan-400" />
              <span>Depth Range</span>
            </span>
            <span className="font-mono text-cyan-400 text-[11px]">
              {filters.depthRange[0]}m – {filters.depthRange[1]}m
            </span>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="200"
              max="1000"
              step="50"
              value={filters.depthRange[1]}
              onChange={(e) =>
                onChangeFilters({
                  ...filters,
                  depthRange: [filters.depthRange[0], parseInt(e.target.value, 10)],
                })
              }
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-800 accent-cyan-400"
            />
            {onReset && (
              <button
                onClick={onReset}
                title="Reset Filters"
                className="flex items-center justify-center rounded-lg border border-slate-700/80 bg-slate-900 p-2 text-slate-400 hover:text-white transition"
              >
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default FilterBar;
