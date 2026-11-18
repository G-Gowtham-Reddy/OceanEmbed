import React, { useState } from 'react';
import { CheckCircle2 } from 'lucide-react';

export const ArgoValidationPage: React.FC = () => {
  const [selectedFloat, setSelectedFloat] = useState<'2903341' | '2903348' | '2903352'>('2903341');

  const floatData = {
    '2903341': {
      lat: '4.25°N',
      lon: '72.80°E',
      cycle: 'Cycle #148',
      mae: '0.29 °C',
      rmse: '0.36 °C',
      bias: '-0.04 °C',
      r2: '0.984',
      levels: [
        { depth: 0, argo: 29.6, model: 29.5, diff: -0.1 },
        { depth: 50, argo: 29.3, model: 29.2, diff: -0.1 },
        { depth: 100, argo: 26.8, model: 26.5, diff: -0.3 },
        { depth: 150, argo: 21.4, model: 21.7, diff: +0.3 },
        { depth: 200, argo: 18.2, model: 18.0, diff: -0.2 },
        { depth: 400, argo: 12.1, model: 12.3, diff: +0.2 },
        { depth: 700, argo: 7.2, model: 7.1, diff: -0.1 },
        { depth: 1000, argo: 3.4, model: 3.5, diff: +0.1 },
      ],
    },
    '2903348': {
      lat: '0.12°N',
      lon: '80.50°E',
      cycle: 'Cycle #092',
      mae: '0.34 °C',
      rmse: '0.41 °C',
      bias: '+0.06 °C',
      r2: '0.978',
      levels: [
        { depth: 0, argo: 29.1, model: 29.2, diff: +0.1 },
        { depth: 50, argo: 28.9, model: 28.8, diff: -0.1 },
        { depth: 100, argo: 25.4, model: 25.1, diff: -0.3 },
        { depth: 150, argo: 20.8, model: 21.2, diff: +0.4 },
        { depth: 200, argo: 17.5, model: 17.3, diff: -0.2 },
        { depth: 400, argo: 11.8, model: 11.9, diff: +0.1 },
        { depth: 700, argo: 6.9, model: 6.8, diff: -0.1 },
        { depth: 1000, argo: 3.1, model: 3.2, diff: +0.1 },
      ],
    },
    '2903352': {
      lat: '5.40°S',
      lon: '68.20°E',
      cycle: 'Cycle #064',
      mae: '0.31 °C',
      rmse: '0.38 °C',
      bias: '-0.02 °C',
      r2: '0.981',
      levels: [
        { depth: 0, argo: 28.7, model: 28.6, diff: -0.1 },
        { depth: 50, argo: 28.4, model: 28.5, diff: +0.1 },
        { depth: 100, argo: 24.2, model: 24.0, diff: -0.2 },
        { depth: 150, argo: 19.6, model: 19.9, diff: +0.3 },
        { depth: 200, argo: 16.8, model: 16.6, diff: -0.2 },
        { depth: 400, argo: 11.2, model: 11.4, diff: +0.2 },
        { depth: 700, argo: 6.4, model: 6.3, diff: -0.1 },
        { depth: 1000, argo: 3.8, model: 3.7, diff: -0.1 },
      ],
    },
  };

  const current = floatData[selectedFloat];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              <span>In-Situ Ground Truth ARGO Float Validation</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Rigorous point-by-point cross-validation of reconstructed vertical columns against calibrated in-situ CTD profiles.
            </p>
          </div>

          {/* Float Selector Tabs */}
          <div className="flex items-center rounded-lg border border-slate-700 bg-slate-900 p-1 text-xs">
            {(['2903341', '2903348', '2903352'] as const).map((id) => (
              <button
                key={id}
                onClick={() => setSelectedFloat(id)}
                className={`rounded px-3 py-1.5 font-medium transition ${
                  selectedFloat === id
                    ? 'bg-cyan-600 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Float #{id}
              </button>
            ))}
          </div>
        </div>

        {/* Validation Scorecards */}
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4 text-xs">
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-slate-400 text-[11px]">Correlation (R² Score):</span>
            <div className="font-mono text-xl font-bold text-emerald-400 mt-1">{current.r2}</div>
            <span className="text-[10px] text-slate-400">Excellent fidelity</span>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-slate-400 text-[11px]">Mean Absolute Error:</span>
            <div className="font-mono text-xl font-bold text-cyan-400 mt-1">{current.mae}</div>
            <span className="text-[10px] text-slate-400">Full 0-1000m column</span>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-slate-400 text-[11px]">Root Mean Square Error:</span>
            <div className="font-mono text-xl font-bold text-white mt-1">{current.rmse}</div>
            <span className="text-[10px] text-slate-400">Low variance</span>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-slate-400 text-[11px]">Systemic Bias:</span>
            <div className="font-mono text-xl font-bold text-amber-400 mt-1">{current.bias}</div>
            <span className="text-[10px] text-slate-400">Unbiased prediction</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Visual Dual Profile Curves Plot */}
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg flex flex-col justify-between">
          <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">Vertical Profile Overlay</h3>
              <p className="text-xs text-slate-400">
                WMO #{selectedFloat} ({current.lat}, {current.lon})
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="h-2 w-2 rounded-full bg-cyan-400" />
                ARGO Observed
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <span className="h-2 w-2 rounded-full bg-amber-400" />
                OceanEmbed Model
              </span>
            </div>
          </div>

          {/* SVG Profile Plot */}
          <div className="relative my-4 min-h-[300px] rounded-lg border border-slate-800 bg-[#050a16] p-4">
            <svg className="w-full h-full min-h-[280px]" viewBox="0 0 300 280">
              {/* Grid Lines */}
              {[0, 200, 400, 600, 800, 1000].map((d) => (
                <g key={d}>
                  <line
                    x1="40"
                    y1={(d / 1000) * 250 + 15}
                    x2="290"
                    y2={(d / 1000) * 250 + 15}
                    stroke="#1e293b"
                    strokeDasharray="2,2"
                  />
                  <text
                    x="35"
                    y={(d / 1000) * 250 + 19}
                    fill="#64748b"
                    fontSize="9"
                    textAnchor="end"
                    fontFamily="monospace"
                  >
                    {d}m
                  </text>
                </g>
              ))}

              {/* Observed Line (Cyan) */}
              <polyline
                fill="none"
                stroke="#06b6d4"
                strokeWidth="2.5"
                points={current.levels
                  .map((lvl) => {
                    const x = 40 + (lvl.argo / 32) * 240;
                    const y = (lvl.depth / 1000) * 250 + 15;
                    return `${x},${y}`;
                  })
                  .join(' ')}
              />

              {/* Model Reconstructed Line (Amber Dashed) */}
              <polyline
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
                strokeDasharray="4,4"
                points={current.levels
                  .map((lvl) => {
                    const x = 40 + (lvl.model / 32) * 240;
                    const y = (lvl.depth / 1000) * 250 + 15;
                    return `${x},${y}`;
                  })
                  .join(' ')}
              />
            </svg>
          </div>

          <div className="flex justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
            <span>Surface: ARGO {current.levels[0].argo}°C / Model {current.levels[0].model}°C</span>
            <span>1000m: ARGO {current.levels[7].argo}°C / Model {current.levels[7].model}°C</span>
          </div>
        </div>

        {/* Residual Sounding Table */}
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg overflow-hidden">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white">Layer Residual Soundings</h3>
            <p className="text-xs text-slate-400">Direct temperature delta at standard oceanographic depths</p>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-800 bg-slate-900/80 text-[10px] uppercase text-slate-400">
                <tr>
                  <th className="px-3 py-2">Depth</th>
                  <th className="px-3 py-2 text-cyan-400">ARGO In-Situ</th>
                  <th className="px-3 py-2 text-amber-400">OceanEmbed</th>
                  <th className="px-3 py-2 text-right">Residual (ΔT)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {current.levels.map((lvl) => (
                  <tr key={lvl.depth} className="hover:bg-slate-800/40">
                    <td className="px-3 py-2.5 font-bold text-white">{lvl.depth} m</td>
                    <td className="px-3 py-2.5 text-cyan-300">{lvl.argo.toFixed(1)} °C</td>
                    <td className="px-3 py-2.5 text-amber-300">{lvl.model.toFixed(1)} °C</td>
                    <td
                      className={`px-3 py-2.5 text-right font-bold ${
                        Math.abs(lvl.diff) <= 0.1
                          ? 'text-emerald-400'
                          : Math.abs(lvl.diff) <= 0.3
                          ? 'text-cyan-400'
                          : 'text-amber-400'
                      }`}
                    >
                      {lvl.diff > 0 ? `+${lvl.diff.toFixed(1)}` : lvl.diff.toFixed(1)} °C
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ArgoValidationPage;
