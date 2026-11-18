import React, { useState } from 'react';
import { ArrowDownUp } from 'lucide-react';

interface DepthPoint {
  depth: number;
  temperature: number;
  label: string;
}

interface LayerSummary {
  name: string;
  depthRange: string;
  tempRange: string;
  description: string;
}

interface DepthTemperatureChartProps {
  profile: DepthPoint[];
  layers: LayerSummary[];
  maxDepth: number;
  regionName: string;
}

export const DepthTemperatureChart: React.FC<DepthTemperatureChartProps> = ({
  profile,
  layers,
  maxDepth,
  regionName,
}) => {
  const [hoveredPoint, setHoveredPoint] = useState<DepthPoint | null>(null);

  if (!profile || profile.length === 0) {
    return (
      <div className="flex h-full min-h-[640px] items-center justify-center rounded-xl border border-zinc-800 bg-[#0c0d12] p-8 text-zinc-400">
        Loading temperature soundings...
      </div>
    );
  }

  // Expanded chart dimensions in SVG coordinates for full vertical immersion
  const svgWidth = 520;
  const svgHeight = 380;
  const padLeft = 52;
  const padRight = 35;
  const padTop = 26;
  const padBottom = 34;

  const chartW = svgWidth - padLeft - padRight;
  const chartH = svgHeight - padTop - padBottom;

  // Temperature domain: 0°C to 32°C
  const minTemp = 0;
  const maxTemp = 32;

  const tempToX = (t: number) => padLeft + ((t - minTemp) / (maxTemp - minTemp)) * chartW;
  const depthToY = (d: number) => padTop + (d / maxDepth) * chartH;

  // Build SVG path
  const pathD = profile
    .map((pt, idx) => {
      const x = tempToX(pt.temperature);
      const y = depthToY(pt.depth);
      return `${idx === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(' ');

  // Gradient area path
  const areaD = `${pathD} L ${padLeft} ${depthToY(profile[profile.length - 1].depth).toFixed(1)} L ${padLeft} ${padTop} Z`;

  // Representative depth ticks (supporting depths up to 1500m)
  const allTicks = [0, 100, 250, 500, 750, 1000, 1250, 1500];
  const ticks = allTicks.filter((d) => d <= maxDepth);
  if (!ticks.includes(maxDepth)) ticks.push(maxDepth);

  return (
    <div className="flex flex-col h-full rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-xl select-none">
      {/* Chart Header */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <ArrowDownUp className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-zinc-100">
            Vertical Temperature Profile Sounding
          </h3>
          <span className="text-[10px] bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 px-2 py-0.5 rounded font-mono">
            T(z) Continuous Curve
          </span>
        </div>
        <span className="text-xs font-mono text-zinc-400">
          0 – {maxDepth} Metres • {regionName}
        </span>
      </div>

      {/* SVG Depth-Temperature Curve with expanded vertical space */}
      <div className="relative flex-1 min-h-[380px] w-full rounded-lg bg-[#08090d] border border-zinc-800/80 p-2 flex items-center justify-center">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-full"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Soft Cyan Area Gradient */}
            <linearGradient id="tempAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.28" />
              <stop offset="50%" stopColor="#0891b2" stopOpacity="0.10" />
              <stop offset="100%" stopColor="#0284c7" stopOpacity="0.02" />
            </linearGradient>

            {/* Depth Line Gradient: Warm Red/Orange near surface -> Green -> Cyan -> Deep Blue */}
            <linearGradient id="tempStrokeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" />
              <stop offset="15%" stopColor="#f97316" />
              <stop offset="35%" stopColor="#10b981" />
              <stop offset="65%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
          </defs>

          {/* Depth Grid Lines (Horizontal) */}
          {ticks.map((d) => {
            const y = depthToY(d);
            return (
              <g key={d}>
                <line
                  x1={padLeft}
                  y1={y}
                  x2={padLeft + chartW}
                  y2={y}
                  stroke="#1c1d24"
                  strokeDasharray="3 3"
                />
                <text
                  x={padLeft - 8}
                  y={y + 3.5}
                  fill="#71717a"
                  fontSize="9"
                  fontFamily="monospace"
                  textAnchor="end"
                >
                  {d}m
                </text>
              </g>
            );
          })}

          {/* Temperature Axis Ticks (Top & Bottom) */}
          {[0, 5, 10, 15, 20, 25, 30].map((t) => {
            const x = tempToX(t);
            return (
              <g key={t}>
                <line
                  x1={x}
                  y1={padTop}
                  x2={x}
                  y2={padTop + chartH}
                  stroke="#16171f"
                />
                <text
                  x={x}
                  y={padTop - 8}
                  fill="#71717a"
                  fontSize="8.5"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {t}°C
                </text>
              </g>
            );
          })}

          {/* Axis Labels */}
          <text
            x={padLeft + chartW / 2}
            y={svgHeight - 10}
            fill="#52525b"
            fontSize="9"
            fontFamily="sans-serif"
            textAnchor="middle"
          >
            Water Temperature (°C) →
          </text>

          {/* Area Fill */}
          <path d={areaD} fill="url(#tempAreaGrad)" />

          {/* Main Temperature Curve */}
          <path
            d={pathD}
            fill="none"
            stroke="url(#tempStrokeGrad)"
            strokeWidth="2.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Interactive Profile Data Points */}
          {profile.map((pt) => {
            const x = tempToX(pt.temperature);
            const y = depthToY(pt.depth);
            const isHovered = hoveredPoint?.depth === pt.depth;

            return (
              <g
                key={pt.depth}
                onMouseEnter={() => setHoveredPoint(pt)}
                onMouseLeave={() => setHoveredPoint(null)}
                className="cursor-pointer"
              >
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered ? 6 : 3.5}
                  fill={isHovered ? '#22d3ee' : '#e4e4e7'}
                  stroke="#09090b"
                  strokeWidth="1.5"
                  className="transition-all"
                />
              </g>
            );
          })}
        </svg>

        {/* Hover Readout Tooltip */}
        {hoveredPoint && (
          <div className="absolute top-4 right-4 rounded-lg border border-cyan-500/60 bg-zinc-950/95 px-3.5 py-2 text-xs font-mono text-zinc-200 shadow-2xl backdrop-blur-md z-10">
            <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider">Depth Sounding</div>
            <div className="mt-1 flex items-center gap-3">
              <div>
                <span className="text-zinc-400">Depth: </span>
                <span className="font-bold text-white">{hoveredPoint.depth}m</span>
              </div>
              <div className="text-zinc-600">|</div>
              <div>
                <span className="text-zinc-400">Temp: </span>
                <span className="font-bold text-cyan-300">{hoveredPoint.temperature}°C</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Simplified Layer Descriptions (Spacious & Clean at Bottom) */}
      <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
        {layers.map((layer) => (
          <div
            key={layer.name}
            className="rounded-lg border border-zinc-800/80 bg-zinc-900/60 p-3 flex flex-col justify-between"
          >
            <div>
              <div className="text-[11px] font-semibold text-zinc-200">
                {layer.name}
              </div>
              <div className="mt-1 flex items-center justify-between font-mono text-[10px]">
                <span className="text-cyan-400 font-medium">{layer.tempRange}</span>
                <span className="text-zinc-400">{layer.depthRange}</span>
              </div>
            </div>
            <p className="mt-1.5 text-[10.5px] text-zinc-400 leading-snug">
              {layer.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DepthTemperatureChart;
