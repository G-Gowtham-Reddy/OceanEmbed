import React, { useState, useEffect } from 'react';
import {
  Thermometer,
  Layers,
  ArrowDownUp,
  Radio,
  Calendar,
  MapPin,
  RefreshCw,
  Sliders,
  Compass,
} from 'lucide-react';
import { OceanMap } from '../components/OceanMap';
import { DepthTemperatureChart } from '../components/DepthTemperatureChart';
import { ThreeDOceanModel } from '../components/ThreeDOceanModel';
import { OceanApiResponse, RegionInfo } from '../types';
import { API_BASE_URL } from '../config/api';

export const ThreeDOceanPage: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string>('equatorial-indian');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [depth, setDepth] = useState<number>(1500);

  const [oceanData, setOceanData] = useState<OceanApiResponse | null>(null);
  const [regions, setRegions] = useState<RegionInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch available ocean regions on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/ocean/regions`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load regions');
        return res.json();
      })
      .then((data: RegionInfo[]) => setRegions(data))
      .catch(() => {
        setRegions([
          {
            id: 'equatorial-indian',
            name: 'Equatorial Indian Ocean',
            coordinates: '0°N - 10°S, 60°E - 90°E',
            lat: -2.5,
            lon: 75.0,
            baseSst: 29.4,
            baseMld: 42.0,
            thermoclineDepth: 165,
            activeFloats: 142,
          },
          {
            id: 'bay-of-bengal',
            name: 'Bay of Bengal',
            coordinates: '10°N - 22°N, 80°E - 95°E',
            lat: 15.0,
            lon: 87.5,
            baseSst: 28.8,
            baseMld: 32.0,
            thermoclineDepth: 135,
            activeFloats: 88,
          },
          {
            id: 'arabian-sea',
            name: 'Arabian Sea',
            coordinates: '10°N - 25°N, 55°E - 75°E',
            lat: 16.5,
            lon: 65.0,
            baseSst: 27.9,
            baseMld: 48.0,
            thermoclineDepth: 150,
            activeFloats: 96,
          },
          {
            id: 'southern-tropical',
            name: 'Southern Tropical Indian Ocean',
            coordinates: '10°S - 25°S, 50°E - 100°E',
            lat: -18.0,
            lon: 75.0,
            baseSst: 25.4,
            baseMld: 65.0,
            thermoclineDepth: 190,
            activeFloats: 114,
          },
        ]);
      });
  }, []);

  // Fetch real temperature profile when region, date, or depth changes
  useEffect(() => {
    setLoading(true);
    setError(null);

    const url = `${API_BASE_URL}/api/ocean/temperature?region=${encodeURIComponent(
      selectedRegion
    )}&date=${encodeURIComponent(date)}&max_depth=${depth}`;

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`Backend returned HTTP ${res.status}`);
        return res.json();
      })
      .then((data: OceanApiResponse) => {
        setOceanData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Unable to load ocean temperature data');
        setLoading(false);
      });
  }, [selectedRegion, date, depth]);

  const kpis = oceanData?.kpis;

  return (
    <div className="space-y-5 font-sans">
      {/* 1. TOP CONTROLS & SELECTION BAR */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-lg">
        <div className="flex flex-wrap items-center gap-3">
          {/* Region Selector */}
          <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-1.5 text-xs">
            <MapPin className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-zinc-400 uppercase tracking-wider">Ocean Region</span>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="bg-transparent font-medium text-zinc-100 outline-none cursor-pointer"
              >
                {regions.map((reg) => (
                  <option key={reg.id} value={reg.id} className="bg-zinc-900 text-zinc-100">
                    {reg.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Date Selector */}
          <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-1.5 text-xs">
            <Calendar className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-zinc-400 uppercase tracking-wider">Date</span>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="bg-transparent font-mono text-zinc-100 outline-none cursor-pointer"
              />
            </div>
          </div>

          {/* Target Depth Slider */}
          <div className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3.5 py-1.5 text-xs min-w-[220px]">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-1 flex-col">
              <div className="flex justify-between items-center text-[9px] text-zinc-400 uppercase tracking-wider">
                <span>Vertical Sounding Depth</span>
                <span className="font-mono text-cyan-300 font-bold">{depth} m</span>
              </div>
              <input
                type="range"
                min="500"
                max="1500"
                step="50"
                value={depth}
                onChange={(e) => setDepth(parseInt(e.target.value, 10))}
                className="mt-1 h-1 w-full appearance-none rounded-lg bg-zinc-800 accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 text-xs font-mono">
          {loading ? (
            <span className="flex items-center gap-1.5 text-cyan-400">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Syncing 3D Model & Profile...</span>
            </span>
          ) : error ? (
            <span className="text-amber-400">{error}</span>
          ) : (
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>3D Model Live Synced</span>
            </span>
          )}
        </div>
      </div>

      {/* 2. KPI METRICS CARDS */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {/* Surface Temp */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Surface Temp (SST)</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-orange-400 border border-zinc-800">
              <Thermometer className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-orange-300 font-mono">
              {kpis?.surfaceTemp ?? '--'} °C
            </span>
            <span className="text-[10px] text-zinc-400">at 0m</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Mapped to 3D surface water</p>
        </div>

        {/* Mixed Layer Depth */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Mixed Layer Depth</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-cyan-400 border border-zinc-800">
              <Layers className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-zinc-100 font-mono">
              {kpis?.mld ?? '--'} m
            </span>
            <span className="text-[10px] text-zinc-400">MLD</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Upper turbulent layer boundary</p>
        </div>

        {/* Thermocline Depth */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Thermocline Depth</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-amber-400 border border-zinc-800">
              <ArrowDownUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-amber-300 font-mono">
              {kpis?.thermoclineDepth ?? '--'} m
            </span>
            <span className="text-[10px] text-zinc-400">Thermocline</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Max thermal gradient transition</p>
        </div>

        {/* Abyssal Temp */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Deep Water Temp</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-indigo-400 border border-zinc-800">
              <Radio className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-indigo-300 font-mono">
              {kpis?.targetDepthTemp ?? '--'} °C
            </span>
            <span className="text-[10px] text-zinc-400">at {depth}m</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Bottom deep-ocean boundary</p>
        </div>
      </div>

      {/* 3. CORE REALITY: 3D OCEAN WATER COLUMN MODEL (HERO DISPLAY) */}
      <div className="w-full">
        <ThreeDOceanModel
          profile={oceanData?.profile ?? []}
          regionName={oceanData?.region ?? 'Selected Ocean Region'}
          coordinates={oceanData?.coordinates ?? 'Lat/Lon Grid'}
          surfaceTemp={kpis?.surfaceTemp}
          mld={kpis?.mld}
          thermoclineDepth={kpis?.thermoclineDepth}
          targetDepthTemp={kpis?.targetDepthTemp}
          maxDepth={depth}
        />
      </div>

      {/* 4. SYNCED WORKSPACE: INTERACTIVE MAP + 2D DEPTH TEMPERATURE PROFILE */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 items-stretch">
        {/* Interactive Ocean Map */}
        <div className="min-h-[580px] h-full flex flex-col">
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-xs font-medium text-zinc-300 flex items-center gap-1.5">
              <Compass className="h-3.5 w-3.5 text-cyan-400" />
              Click any point on the map to update both Graph & 3D Ocean Model:
            </span>
            <span className="text-[11px] font-mono text-cyan-400">
              Live Map-to-3D Data Sync
            </span>
          </div>
          <div className="flex-1 min-h-[520px]">
            <OceanMap
              selectedRegionId={selectedRegion}
              onSelectRegion={setSelectedRegion}
              regions={regions}
              currentTemp={kpis?.surfaceTemp}
              date={date}
              targetDepth={depth}
              onSelectCustomProfile={(data) => setOceanData(data)}
            />
          </div>
        </div>

        {/* Depth Temperature Visualizer Graph */}
        <div className="min-h-[580px] h-full flex flex-col">
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-xs font-medium text-zinc-300 flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5 text-cyan-400" />
              Subsurface Temperature Depth Profile:
            </span>
            <span className="text-[11px] font-mono text-zinc-400">
              0m to {depth}m Depth
            </span>
          </div>
          <div className="flex-1 min-h-[520px]">
            <DepthTemperatureChart
              profile={oceanData?.profile ?? []}
              layers={oceanData?.layers ?? []}
              maxDepth={depth}
              regionName={oceanData?.region ?? 'Selected Region'}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreeDOceanPage;
