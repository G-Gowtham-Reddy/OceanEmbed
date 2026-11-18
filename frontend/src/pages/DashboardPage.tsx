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
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { OceanMap } from '../components/OceanMap';
import { DepthTemperatureChart } from '../components/DepthTemperatureChart';
import { ThreeDOceanModel } from '../components/ThreeDOceanModel';
import { OceanApiResponse, RegionInfo } from '../types';
import { API_BASE_URL } from '../config/api';

export const DashboardPage: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string>('equatorial-indian');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [depth, setDepth] = useState<number>(1000);
  const [visualizerMode, setVisualizerMode] = useState<'chart' | '3d'>('chart');

  const [oceanData, setOceanData] = useState<OceanApiResponse | null>(null);
  const [regions, setRegions] = useState<RegionInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch available regions on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/ocean/regions`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load regions');
        return res.json();
      })
      .then((data: RegionInfo[]) => setRegions(data))
      .catch(() => {
        // Fallback default regions if offline
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

  // Fetch real temperature profile whenever region, date, or depth changes
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
      {/* 1. TOP CONTROLS BAR (Region, Date, Depth) */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-lg">
        {/* Controls selectors */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Region Selector */}
          <div className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-1.5 text-xs">
            <MapPin className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-zinc-400 uppercase tracking-wider">Region</span>
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

          {/* Depth Range Slider */}
          <div className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900/80 px-3.5 py-1.5 text-xs min-w-[220px]">
            <Sliders className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-1 flex-col">
              <div className="flex justify-between items-center text-[9px] text-zinc-400 uppercase tracking-wider">
                <span>Target Depth</span>
                <span className="font-mono text-cyan-300 font-bold">{depth} m</span>
              </div>
              <input
                type="range"
                min="100"
                max="1500"
                step="50"
                value={depth}
                onChange={(e) => setDepth(parseInt(e.target.value, 10))}
                className="mt-1 h-1 w-full appearance-none rounded-lg bg-zinc-800 accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Status & Live Update indicator */}
        <div className="flex items-center gap-2 text-xs font-mono">
          {loading ? (
            <span className="flex items-center gap-1.5 text-cyan-400">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Updating from Backend...</span>
            </span>
          ) : error ? (
            <span className="flex items-center gap-1.5 text-rose-400">
              <AlertCircle className="h-3.5 w-3.5" />
              <span>{error}</span>
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-zinc-400">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>Backend Synced</span>
            </span>
          )}
        </div>
      </div>

      {/* 2. FOUR CLEAN KPI CARDS (Charcoal Black, Soft Silver & Subtle Cyan) */}
      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Surface Temperature */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Surface Temperature</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-cyan-400 border border-zinc-800">
              <Thermometer className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-zinc-100 font-mono">
              {kpis?.surfaceTemp ?? '--'} °C
            </span>
            <span className="text-[10px] text-zinc-400">Sea surface</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Upper warm layer</p>
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
            <span className="text-[10px] text-zinc-400">Wind-mixed zone</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Uniform temperature boundary</p>
        </div>

        {/* Transition Zone (Thermocline) */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Transition Depth</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-cyan-400 border border-zinc-800">
              <ArrowDownUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-zinc-100 font-mono">
              {kpis?.thermoclineDepth ?? '--'} m
            </span>
            <span className="text-[10px] text-zinc-400">Thermocline</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">Rapid cooling boundary</p>
        </div>

        {/* Target Depth Temperature */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-md">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-medium">Deep Water Temp</span>
            <div className="rounded-md bg-zinc-900 p-1.5 text-cyan-400 border border-zinc-800">
              <Radio className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-cyan-300 font-mono">
              {kpis?.targetDepthTemp ?? '--'} °C
            </span>
            <span className="text-[10px] text-zinc-400">at {depth}m</span>
          </div>
          <p className="mt-1 text-[11px] text-zinc-400">
            {kpis?.activeFloats ?? 142} monitoring floats active
          </p>
        </div>
      </div>

      {/* 3. TWO-COLUMN CORE WORKSPACE: INTERACTIVE MAP + DEPTH TEMPERATURE VISUALIZER (EXPANDED HEIGHT) */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 items-stretch">
        {/* Left Column: Interactive Map */}
        <div className="min-h-[640px] h-full flex flex-col">
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

        {/* Right Column: Depth Temperature Visualizer (2D Chart or 3D Ocean Model) */}
        <div className="min-h-[640px] h-full flex flex-col">
          {/* Header Mode Switcher */}
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-xs font-medium text-zinc-300">
              {visualizerMode === 'chart' ? '2D Subsurface Temperature Profile' : '3D Realistic Ocean Water Column'}
            </span>
            <div className="flex items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900/80 p-0.5">
              <button
                onClick={() => setVisualizerMode('chart')}
                className={`rounded px-2.5 py-1 text-[11px] font-medium transition-all ${
                  visualizerMode === 'chart'
                    ? 'bg-cyan-950/70 text-cyan-300 border border-cyan-500/30'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                2D Depth Chart
              </button>
              <button
                onClick={() => setVisualizerMode('3d')}
                className={`rounded px-2.5 py-1 text-[11px] font-medium transition-all ${
                  visualizerMode === '3d'
                    ? 'bg-cyan-950/70 text-cyan-300 border border-cyan-500/30'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                3D Ocean Model
              </button>
            </div>
          </div>

          <div className="flex-1 min-h-[580px]">
            {visualizerMode === 'chart' ? (
              <DepthTemperatureChart
                profile={oceanData?.profile ?? []}
                layers={oceanData?.layers ?? []}
                maxDepth={depth}
                regionName={oceanData?.region ?? 'Selected Region'}
              />
            ) : (
              <ThreeDOceanModel
                profile={oceanData?.profile ?? []}
                regionName={oceanData?.region ?? 'Selected Region'}
                coordinates={oceanData?.coordinates ?? 'Lat/Lon Grid'}
                surfaceTemp={kpis?.surfaceTemp}
                mld={kpis?.mld}
                thermoclineDepth={kpis?.thermoclineDepth}
                targetDepthTemp={kpis?.targetDepthTemp}
                maxDepth={depth}
              />
            )}
          </div>
        </div>
      </div>

      {/* 4. CLEAN FOOTER ATTRIBUTION */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-zinc-800/80 bg-[#0a0a0e] px-4 py-2.5 text-xs text-zinc-400">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-cyan-400" />
          <span>
            Connected to OceanEmbed Core Backend at{' '}
            <code className="rounded bg-zinc-900 px-1.5 py-0.5 font-mono text-zinc-300">
              {API_BASE_URL}
            </code>
          </span>
        </div>
        <div className="text-[11px] text-zinc-400">
          Temperature layers computed dynamically based on TEOS-10 physical oceanography standards.
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
