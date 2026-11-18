import React, { useState } from 'react';
import { OceanStation } from '../types';
import { Search, Download, Filter, MapPin, ChevronRight } from 'lucide-react';

const SAMPLE_STATIONS: OceanStation[] = [
  {
    id: 'STN-101',
    wmoId: '2903341',
    lat: 4.25,
    lon: 72.80,
    date: '2026-11-08',
    surfaceTemp: 29.6,
    bottomTemp: 3.4,
    mld: 38.0,
    profilesCount: 84,
    qualityFlag: 'Good',
  },
  {
    id: 'STN-102',
    wmoId: '2903348',
    lat: 0.12,
    lon: 80.50,
    date: '2026-11-09',
    surfaceTemp: 29.1,
    bottomTemp: 3.1,
    mld: 44.5,
    profilesCount: 92,
    qualityFlag: 'Good',
  },
  {
    id: 'STN-103',
    wmoId: '2903352',
    lat: -5.40,
    lon: 68.20,
    date: '2026-11-07',
    surfaceTemp: 28.7,
    bottomTemp: 3.8,
    mld: 52.0,
    profilesCount: 76,
    qualityFlag: 'Adjusted',
  },
  {
    id: 'STN-104',
    wmoId: '2903360',
    lat: 12.30,
    lon: 86.40,
    date: '2026-11-09',
    surfaceTemp: 29.8,
    bottomTemp: 2.9,
    mld: 32.0,
    profilesCount: 110,
    qualityFlag: 'Good',
  },
  {
    id: 'STN-105',
    wmoId: '2903365',
    lat: 15.80,
    lon: 65.10,
    date: '2026-11-06',
    surfaceTemp: 28.2,
    bottomTemp: 3.6,
    mld: 48.0,
    profilesCount: 64,
    qualityFlag: 'Suspect',
  },
  {
    id: 'STN-106',
    wmoId: '2903371',
    lat: -2.10,
    lon: 88.90,
    date: '2026-11-10',
    surfaceTemp: 29.3,
    bottomTemp: 3.2,
    mld: 41.0,
    profilesCount: 58,
    qualityFlag: 'Good',
  },
];

export const DataExplorerPage: React.FC = () => {
  const [selectedStation, setSelectedStation] = useState<OceanStation>(SAMPLE_STATIONS[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterQuality, setFilterQuality] = useState<string>('All');

  const filteredStations = SAMPLE_STATIONS.filter((stn) => {
    const matchesSearch =
      stn.wmoId.includes(searchTerm) ||
      stn.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesQuality = filterQuality === 'All' || stn.qualityFlag === filterQuality;
    return matchesSearch && matchesQuality;
  });

  // Calculate synthetic vertical profile for selected station
  const depthProfilePoints = [
    { depth: 0, temp: selectedStation.surfaceTemp },
    { depth: 50, temp: selectedStation.surfaceTemp - 0.3 },
    { depth: 100, temp: selectedStation.surfaceTemp - 2.8 },
    { depth: 150, temp: 21.4 },
    { depth: 200, temp: 18.2 },
    { depth: 300, temp: 14.8 },
    { depth: 400, temp: 12.1 },
    { depth: 600, temp: 8.4 },
    { depth: 800, temp: 5.2 },
    { depth: 1000, temp: selectedStation.bottomTemp },
  ];

  return (
    <div className="space-y-6">
      {/* Search & Actions Toolbar */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-[#091122]/90 p-4 shadow-lg sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by WMO ID (e.g. 2903341)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/90 pl-9 pr-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={filterQuality}
              onChange={(e) => setFilterQuality(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500"
            >
              <option value="All">All Quality Flags</option>
              <option value="Good">Good (QC 1)</option>
              <option value="Adjusted">Adjusted (QC 2)</option>
              <option value="Suspect">Suspect (QC 3)</option>
            </select>
          </div>
        </div>

        <button
          onClick={() => alert('Exporting hydrographic data matrix as NetCDF/CSV...')}
          className="flex items-center justify-center gap-2 rounded-lg border border-cyan-800/80 bg-cyan-950/60 px-4 py-2 text-xs font-medium text-cyan-300 hover:bg-cyan-900/80 transition"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export Profile Data</span>
        </button>
      </div>

      {/* Main Grid: Station Table Left + Vertical Sounding Profile Right */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Table of Stations */}
        <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#091122]/90 shadow-lg lg:col-span-2">
          <div className="border-b border-slate-800 px-5 py-3">
            <h3 className="text-sm font-semibold text-white">ARGO & Hydrographic Profiling Stations</h3>
            <p className="text-xs text-slate-400">Showing {filteredStations.length} illustrative sample stations</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-4 py-3">WMO ID</th>
                  <th className="px-4 py-3">Coordinates</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">SST</th>
                  <th className="px-4 py-3">MLD</th>
                  <th className="px-4 py-3">QC Status</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                {filteredStations.map((stn) => {
                  const isSelected = selectedStation.id === stn.id;
                  return (
                    <tr
                      key={stn.id}
                      onClick={() => setSelectedStation(stn)}
                      className={`cursor-pointer transition hover:bg-slate-800/50 ${
                        isSelected ? 'bg-cyan-950/40 text-cyan-200' : ''
                      }`}
                    >
                      <td className="px-4 py-3 font-semibold text-white">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="h-3.5 w-3.5 text-cyan-400" />
                          <span>{stn.wmoId}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-400 font-sans">
                        {stn.lat >= 0 ? `${stn.lat}°N` : `${Math.abs(stn.lat)}°S`},{' '}
                        {stn.lon}°E
                      </td>
                      <td className="px-4 py-3 text-slate-400">{stn.date}</td>
                      <td className="px-4 py-3 text-rose-400 font-bold">{stn.surfaceTemp}°C</td>
                      <td className="px-4 py-3 text-amber-400">{stn.mld} m</td>
                      <td className="px-4 py-3 font-sans">
                        <span
                          className={`rounded px-2 py-0.5 text-[10px] font-semibold ${
                            stn.qualityFlag === 'Good'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : stn.qualityFlag === 'Adjusted'
                              ? 'bg-amber-950 text-amber-300 border border-amber-800'
                              : 'bg-rose-950 text-rose-300 border border-rose-800'
                          }`}
                        >
                          {stn.qualityFlag}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <ChevronRight className="h-4 w-4 text-slate-500" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Vertical Sounding Profile Plot for Selected Float */}
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg flex flex-col">
          <div className="border-b border-slate-800 pb-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                Vertical Sounding Curve
              </span>
              <span className="font-mono text-xs text-slate-400">
                WMO #{selectedStation.wmoId}
              </span>
            </div>
            <h4 className="text-sm font-bold text-white mt-1">Temperature Profile vs Depth</h4>
            <p className="text-[11px] text-slate-400">0 – 1000m CTD Sensor Measurements</p>
          </div>

          {/* SVG Depth Curve Chart */}
          <div className="relative my-4 flex-1 min-h-[320px] rounded-lg border border-slate-800/80 bg-[#050a16] p-4 flex flex-col justify-between">
            <div className="flex justify-between text-[10px] font-mono text-slate-400 border-b border-slate-800 pb-1">
              <span>Depth (m)</span>
              <span>Temp: 0°C &rarr; 30°C</span>
            </div>

            <svg
              className="h-full w-full"
              viewBox="0 0 240 320"
              preserveAspectRatio="none"
            >
              {/* Depth horizontal grid lines */}
              {[0, 200, 400, 600, 800, 1000].map((d) => (
                <g key={d}>
                  <line
                    x1="30"
                    y1={(d / 1000) * 300 + 10}
                    x2="230"
                    y2={(d / 1000) * 300 + 10}
                    stroke="#1e293b"
                    strokeDasharray="2,2"
                  />
                  <text
                    x="25"
                    y={(d / 1000) * 300 + 14}
                    fill="#64748b"
                    fontSize="9"
                    textAnchor="end"
                    fontFamily="monospace"
                  >
                    {d}
                  </text>
                </g>
              ))}

              {/* Temperature curve line */}
              <polyline
                fill="none"
                stroke="#06b6d4"
                strokeWidth="2.5"
                points={depthProfilePoints
                  .map((p) => {
                    const x = 30 + (p.temp / 32) * 200;
                    const y = (p.depth / 1000) * 300 + 10;
                    return `${x},${y}`;
                  })
                  .join(' ')}
              />

              {/* Data points */}
              {depthProfilePoints.map((p, idx) => {
                const x = 30 + (p.temp / 32) * 200;
                const y = (p.depth / 1000) * 300 + 10;
                return (
                  <circle
                    key={idx}
                    cx={x}
                    cy={y}
                    r="3.5"
                    fill={p.temp > 24 ? '#ef4444' : p.temp > 16 ? '#eab308' : '#06b6d4'}
                    stroke="#0f172a"
                    strokeWidth="1.5"
                  />
                );
              })}
            </svg>

            <div className="flex justify-between text-[10px] font-mono text-slate-400 border-t border-slate-800 pt-1">
              <span>Surface: {selectedStation.surfaceTemp}°C</span>
              <span>1000m: {selectedStation.bottomTemp}°C</span>
            </div>
          </div>

          {/* Station Metadata Summary */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="rounded bg-slate-900/60 p-2 border border-slate-800">
              <span className="text-slate-400 text-[10px]">Location:</span>
              <div className="font-mono text-slate-200">
                {selectedStation.lat}°N, {selectedStation.lon}°E
              </div>
            </div>
            <div className="rounded bg-slate-900/60 p-2 border border-slate-800">
              <span className="text-slate-400 text-[10px]">MLD:</span>
              <div className="font-mono text-amber-400 font-bold">{selectedStation.mld} m</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default DataExplorerPage;
