import React, { useRef, useEffect, useState, useMemo } from 'react';
import {
  Thermometer,
  Layers,
  Waves,
  Radio,
  MapPin,
  Calendar,
  Maximize2,
  Database,
  Satellite,
} from 'lucide-react';
import { FilterState } from '../types';

interface OceanCrossSectionProps {
  filters: FilterState;
  onChangeFilters: (filters: FilterState) => void;
}

interface ProbePoint {
  x: number;
  y: number;
  depth: number;
  longitude: number;
  temperature: number;
}

export const OceanCrossSection: React.FC<OceanCrossSectionProps> = ({
  filters,
  onChangeFilters,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [probe, setProbe] = useState<ProbePoint | null>(null);

  // Depth ticks (Left Y-axis)
  const depthTicks = useMemo(
    () => [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    []
  );

  // Longitude ticks (Bottom X-axis)
  const lonTicks = useMemo(
    () => ['65.0°E', '67.5°E', '70.0°E', '72.5°E', '75.0°E', '77.5°E', '80.0°E', '82.5°E', '85.0°E'],
    []
  );

  // Temperature scale (Right Y-axis)
  const tempScale = useMemo(
    () => [30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2],
    []
  );

  // Render Clean Scientific Oceanographic Thermal Cross-Section (Static, Zero Distracting Animation)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const cols = 200;
    const colWidth = width / cols;
    const surfaceY = 16; // Stable, crisp water surface line

    // 1. Draw smooth continuous scientific thermal stratification
    for (let c = 0; c < cols; c++) {
      const u = c / cols; // 0 to 1 across 65°E to 85°E

      // Natural oceanographic thermocline tilt matching real-world equatorial hydrography
      const thermoclineWave = Math.sin(u * Math.PI * 1.3 - 0.2) * 36;

      const grad = ctx.createLinearGradient(0, surfaceY, 0, height);

      // Depth layer boundaries mapped to 0..1 scale
      const rRed = Math.max(0.04, Math.min(0.14, (70 + thermoclineWave * 0.4) / 1000));
      const rOrange = Math.max(0.10, Math.min(0.24, (140 + thermoclineWave * 0.7) / 1000));
      const rYellow = Math.max(0.18, Math.min(0.36, (230 + thermoclineWave) / 1000));
      const rGreen = Math.max(0.32, Math.min(0.52, (380 + thermoclineWave * 0.9) / 1000));
      const rCyan = Math.max(0.50, Math.min(0.72, (560 + thermoclineWave * 0.6) / 1000));
      const rDeepBlue = Math.max(0.72, Math.min(0.90, (760 + thermoclineWave * 0.3) / 1000));

      // Scientific thermal colormap
      grad.addColorStop(0.0, '#b91c1c'); // Crimson Red (Warm Surface)
      grad.addColorStop(rRed * 0.8, '#dc2626');
      grad.addColorStop(rRed, '#ea580c'); // Orange
      grad.addColorStop(rOrange, '#f59e0b');
      grad.addColorStop(rYellow, '#eab308'); // Golden Yellow (20°C Thermocline Core)
      grad.addColorStop(rGreen * 0.8, '#22c55e'); // Green
      grad.addColorStop(rGreen, '#06b6d4'); // Cyan
      grad.addColorStop(rCyan, '#0284c7'); // Ocean Blue
      grad.addColorStop(rDeepBlue, '#1d4ed8'); // Royal Blue
      grad.addColorStop(1.0, '#021844'); // Deep Midnight Abyssal Navy

      ctx.fillStyle = grad;
      ctx.fillRect(c * colWidth, surfaceY, colWidth + 1.2, height - surfaceY);
    }

    // 2. Clean Water Surface Interface Line
    ctx.beginPath();
    ctx.moveTo(0, surfaceY);
    ctx.lineTo(width, surfaceY);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.stroke();

    // 3. Draw Crisp Scientific Isotherm Contours with Embedded Badges
    const contourDepths = [
      { d: 110, temp: '28 °C', showBadge: true, badgeU: 0.52 },
      { d: 230, temp: '20 °C', showBadge: true, badgeU: 0.50 },
      { d: 380, temp: '15 °C', showBadge: true, badgeU: 0.49 },
      { d: 560, temp: '10 °C', showBadge: true, badgeU: 0.46 },
      { d: 760, temp: '5 °C', showBadge: true, badgeU: 0.44 },
    ];

    contourDepths.forEach((layer) => {
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.lineWidth = 1.0;

      for (let x = 0; x <= width; x += 8) {
        const u = x / width;
        const thermoclineWave = Math.sin(u * Math.PI * 1.3 - 0.2) * 36;
        const y = ((layer.d + thermoclineWave) / 1000) * height;

        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Temperature badge along contour
      if (layer.showBadge) {
        const badgeX = layer.badgeU * width;
        const thermoclineWave = Math.sin(layer.badgeU * Math.PI * 1.3 - 0.2) * 36;
        const badgeY = ((layer.d + thermoclineWave) / 1000) * height;

        ctx.fillStyle = 'rgba(8, 18, 38, 0.90)';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 1;
        const bw = 38;
        const bh = 16;
        ctx.beginPath();
        ctx.roundRect(badgeX - bw / 2, badgeY - bh / 2, bw, bh, 3);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 9px monospace';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(layer.temp, badgeX, badgeY);
      }
      ctx.restore();
    });

    // 4. Draw Deep Bathymetric Seabed Mountains Terrain (GEBCO Elevation)
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(0, height);

    for (let x = 0; x <= width; x += 4) {
      const u = x / width;
      const leftRidge = Math.exp(-u * 6.5) * 380;
      const rightRidge = Math.exp(-(1 - u) * 6.0) * 390;
      const cragNoise =
        Math.sin(u * 55) * 14 +
        Math.cos(u * 110) * 8 +
        Math.sin(u * 220) * 4;

      const bathyMeters = 930 - leftRidge - rightRidge + cragNoise;
      const y = Math.min(height, (bathyMeters / 1000) * height);

      if (x === 0) ctx.lineTo(0, y);
      else ctx.lineTo(x, y);
    }

    ctx.lineTo(width, height);
    ctx.closePath();

    // Deep ocean rock illumination
    const rockGrad = ctx.createLinearGradient(0, height * 0.5, 0, height);
    rockGrad.addColorStop(0.0, '#0a2e5c'); // Deep illuminated crest
    rockGrad.addColorStop(0.25, '#061c3b');
    rockGrad.addColorStop(0.7, '#020b18');
    rockGrad.addColorStop(1.0, '#00040a'); // Basalt crust
    ctx.fillStyle = rockGrad;
    ctx.fill();

    // Mountain ridge highlight
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 1.3;
    ctx.stroke();
    ctx.restore();
  }, [filters.depthRange]);

  // Handle probe on mouse move
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
    const y = Math.max(0, Math.min(rect.height, e.clientY - rect.top));

    const depthFraction = y / rect.height;
    const depth = Math.round(depthFraction * filters.depthRange[1]);
    const u = x / rect.width;
    const longitude = parseFloat((65.0 + u * 20.0).toFixed(2));

    // Thermodynamic formula
    const sst = 29.4;
    const deepTemp = 2.4;
    const thermoclineCenter = 180;
    const t =
      deepTemp +
      (sst - deepTemp) / (1 + Math.exp((depth - thermoclineCenter) / 95));
    const temperature = parseFloat(t.toFixed(1));

    setProbe({ x, y, depth, longitude, temperature });
  };

  const handleMouseLeave = () => {
    setProbe(null);
  };

  return (
    <div className="flex flex-col w-full rounded-2xl border border-cyan-950/80 bg-[#001026] text-white shadow-2xl overflow-hidden font-sans">
      {/* 1. HERO HEADER WITH KPI METRICS CARD */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between px-6 pt-5 pb-3 gap-4">
        {/* Left: Ocean Explorer Title */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-1.5 rounded-full bg-cyan-400 shadow-md shadow-cyan-400/50" />
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white drop-shadow">
              Ocean Explorer
            </h1>
            <p className="text-xs text-slate-300">
              Integrated surface and subsurface temperature analysis • Equatorial Indian Ocean
            </p>
          </div>
        </div>

        {/* Right: Glassmorphic Combined KPI Stats Card */}
        <div className="flex items-center rounded-xl border border-cyan-900/60 bg-[#041a38]/80 px-4 py-2.5 backdrop-blur-md shadow-lg divide-x divide-cyan-900/50 text-xs">
          {/* SST */}
          <div className="flex items-center gap-2.5 px-3 first:pl-1">
            <div className="rounded-lg bg-cyan-950/70 p-1.5 text-cyan-400 border border-cyan-800/40">
              <Thermometer className="h-4 w-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-medium">SST</span>
              <div className="font-bold text-white text-sm font-mono">29.4 °C</div>
            </div>
          </div>

          {/* MLD */}
          <div className="flex items-center gap-2.5 px-3">
            <div className="rounded-lg bg-cyan-950/70 p-1.5 text-cyan-400 border border-cyan-800/40">
              <Layers className="h-4 w-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-medium">MLD</span>
              <div className="font-bold text-white text-sm font-mono">42.8 m</div>
            </div>
          </div>

          {/* Thermocline */}
          <div className="flex items-center gap-2.5 px-3">
            <div className="rounded-lg bg-cyan-950/70 p-1.5 text-cyan-400 border border-cyan-800/40">
              <Waves className="h-4 w-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-medium">Thermocline</span>
              <div className="font-bold text-white text-sm font-mono">164.0 m</div>
            </div>
          </div>

          {/* ARGO */}
          <div className="flex items-center gap-2.5 px-3 last:pr-1">
            <div className="rounded-lg bg-cyan-950/70 p-1.5 text-cyan-400 border border-cyan-800/40">
              <Radio className="h-4 w-4" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-medium">ARGO</span>
              <div className="font-bold text-emerald-400 text-sm font-mono">142 Active</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. CONTROLS TOOLBAR */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-2.5 bg-[#00142f] border-y border-cyan-950/90 text-xs">
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Target Region */}
          <div className="flex items-center gap-2 rounded-xl border border-cyan-900/70 bg-[#03152d]/90 px-3.5 py-1.5 text-xs shadow">
            <MapPin className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-400 leading-none">Target Region</span>
              <span className="text-white font-medium text-[11px] leading-tight mt-0.5">
                {filters.region}
              </span>
            </div>
          </div>

          {/* Date */}
          <div className="flex items-center gap-2 rounded-xl border border-cyan-900/70 bg-[#03152d]/90 px-3.5 py-1.5 text-xs shadow">
            <Calendar className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-400 leading-none">Date</span>
              <span className="text-white font-mono font-medium text-[11px] leading-tight mt-0.5">
                {filters.date}
              </span>
            </div>
          </div>

          {/* Parameter */}
          <div className="flex items-center gap-2 rounded-xl border border-cyan-900/70 bg-[#03152d]/90 px-3.5 py-1.5 text-xs shadow">
            <Layers className="h-3.5 w-3.5 text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-400 leading-none">Parameter</span>
              <span className="text-white font-medium text-[11px] leading-tight mt-0.5">
                {filters.parameter}
              </span>
            </div>
          </div>
        </div>

        {/* Right Controls: Depth Slider + Fullscreen */}
        <div className="flex items-center gap-3">
          {/* Depth Slider */}
          <div className="flex flex-col justify-center rounded-xl border border-cyan-900/70 bg-[#03152d]/90 px-3.5 py-1 text-xs shadow min-w-[210px]">
            <div className="flex justify-between items-center text-[10px] text-slate-300 font-mono mb-0.5">
              <span>Depth Range:</span>
              <span className="text-cyan-300 font-bold">
                {filters.depthRange[0]} – {filters.depthRange[1]} m
              </span>
            </div>
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
              className="h-1.5 w-full appearance-none rounded-lg bg-cyan-950 accent-cyan-400 cursor-pointer"
            />
          </div>

          {/* Fullscreen Button */}
          <button
            onClick={() => {
              if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
              } else {
                document.exitFullscreen();
              }
            }}
            className="flex h-8 w-8 items-center justify-center rounded-xl border border-cyan-800 bg-[#041a38] text-cyan-300 shadow hover:border-cyan-400 hover:text-white transition"
            title="Toggle Fullscreen"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* 3. TEMPERATURE CROSS-SECTION (Depth Scale + Static Canvas + Temp Scale) */}
      <div className="relative flex flex-1 min-h-[520px] bg-[#000a1a]">
        {/* Left Y-Axis: Depth Scale (0 to 1,000 m) */}
        <div className="w-16 sm:w-20 flex-shrink-0 flex flex-col justify-between py-2 pl-3 pr-2 border-r border-cyan-950/60 bg-[#000c1e] select-none text-[11px] font-mono text-slate-300">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-tight pb-1">
            Depth (m)
          </div>
          {depthTicks.map((d) => (
            <div key={d} className="flex items-center justify-between group">
              <span className="text-slate-300 text-[10px]">
                {d === 1000 ? '1,000' : d}
              </span>
              <span className="h-[1px] w-2 bg-slate-700" />
            </div>
          ))}
        </div>

        {/* Center: Oceanographic Temperature Field Canvas */}
        <div
          ref={containerRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="relative flex-1 cursor-crosshair overflow-hidden select-none"
        >
          {/* Main static temperature field canvas */}
          <canvas
            ref={canvasRef}
            width={1000}
            height={520}
            className="h-full w-full object-cover"
          />

          {/* Depth Grid Lines */}
          <div className="absolute inset-0 pointer-events-none flex flex-col justify-between py-2">
            {depthTicks.map((d) => (
              <div
                key={d}
                className="w-full border-b border-slate-700/15"
                style={{ top: `${(d / 1000) * 100}%` }}
              />
            ))}
          </div>

          {/* Interactive Mouse Probe & Tooltip */}
          {probe && (
            <>
              {/* Crosshair */}
              <div
                className="absolute top-0 bottom-0 pointer-events-none w-[1px] border-l border-dashed border-cyan-300"
                style={{ left: `${probe.x}px` }}
              />
              <div
                className="absolute left-0 right-0 pointer-events-none h-[1px] border-t border-dashed border-cyan-300"
                style={{ top: `${probe.y}px` }}
              />
              <div
                className="absolute pointer-events-none -translate-x-1/2 -translate-y-1/2 h-3.5 w-3.5 rounded-full border-2 border-white bg-cyan-400 shadow-lg shadow-cyan-400"
                style={{ left: `${probe.x}px`, top: `${probe.y}px` }}
              />

              {/* Floating Tooltip */}
              <div
                className="absolute z-30 pointer-events-none w-56 rounded-xl border border-cyan-500/80 bg-[#03152d]/95 p-3 text-xs text-white shadow-2xl backdrop-blur-md font-mono"
                style={{
                  left: `${Math.min(probe.x + 16, (containerRef.current?.clientWidth || 700) - 240)}px`,
                  top: `${Math.min(probe.y + 16, (containerRef.current?.clientHeight || 450) - 130)}px`,
                }}
              >
                <div className="flex items-center justify-between border-b border-cyan-900 pb-1 mb-1.5 text-cyan-300 text-[10px]">
                  <span>Sounding Probe</span>
                  <span>{probe.longitude}°E</span>
                </div>
                <div className="flex justify-between items-center text-slate-300 text-[11px]">
                  <span>Depth:</span>
                  <span className="font-bold text-white">{probe.depth} m</span>
                </div>
                <div className="flex justify-between items-center text-slate-300 text-[11px]">
                  <span>Temperature:</span>
                  <span className="font-bold text-amber-400">{probe.temperature} °C</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Right Y-Axis: Temperature Scale Legend (°C) */}
        <div className="w-16 sm:w-20 flex-shrink-0 flex flex-col justify-between py-2 pl-2 pr-3 border-l border-cyan-950/60 bg-[#000c1e] select-none text-[11px] font-mono text-slate-300">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-tight pb-1 text-right">
            Temperature (°C)
          </div>

          <div className="flex-1 flex gap-2 items-stretch my-1">
            {/* Color Gradient Bar */}
            <div
              className="w-3 rounded-full border border-slate-700/80 shadow-inner"
              style={{
                background:
                  'linear-gradient(to bottom, #b91c1c 0%, #dc2626 12%, #ea580c 24%, #f59e0b 36%, #eab308 48%, #22c55e 60%, #06b6d4 72%, #0284c7 84%, #1d4ed8 92%, #021844 100%)',
              }}
            />

            {/* Scale numbers (30 down to 2) */}
            <div className="flex-1 flex flex-col justify-between text-right text-[10px] text-slate-300 font-mono">
              {tempScale.map((t) => (
                <span
                  key={t}
                  className={t >= 28 ? 'text-rose-400 font-bold' : t <= 4 ? 'text-blue-400' : ''}
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4. BOTTOM X-AXIS: LONGITUDE TICKS */}
      <div className="flex items-center justify-between px-16 sm:px-24 py-1.5 border-t border-cyan-950/80 bg-[#000d20] text-[11px] font-mono text-slate-400">
        <div className="flex items-center justify-between w-full">
          {lonTicks.map((lon) => (
            <span key={lon} className="hover:text-cyan-300 transition">
              {lon}
            </span>
          ))}
        </div>
      </div>
      <div className="text-center text-[10px] font-mono text-slate-500 pb-2 bg-[#000d20]">
        Longitude (°E)
      </div>

      {/* 5. BOTTOM FOOTER METADATA PILLS */}
      <div className="flex flex-wrap items-center gap-3 px-6 py-3 border-t border-cyan-950/80 bg-[#000814] text-xs">
        {/* Bathymetry Pill */}
        <div className="flex items-center gap-2 rounded-full border border-cyan-900/60 bg-[#03152d]/80 px-3.5 py-1 text-[11px] text-slate-300">
          <Database className="h-3.5 w-3.5 text-cyan-400" />
          <span>Bathymetry: GEBCO 2024 (15 arc-sec)</span>
        </div>

        {/* SST Pill */}
        <div className="flex items-center gap-2 rounded-full border border-cyan-900/60 bg-[#03152d]/80 px-3.5 py-1 text-[11px] text-slate-300">
          <Satellite className="h-3.5 w-3.5 text-cyan-400" />
          <span>SST: GHRSST (L4)</span>
        </div>

        {/* Coverage Pill */}
        <div className="flex items-center gap-2 rounded-full border border-cyan-900/60 bg-[#03152d]/80 px-3.5 py-1 text-[11px] text-slate-300">
          <Layers className="h-3.5 w-3.5 text-cyan-400" />
          <span>Coverage: 0 – 1,000 m</span>
        </div>
      </div>
    </div>
  );
};
export default OceanCrossSection;
