import React, { useState, useEffect } from 'react';
import { Cpu, BarChart2, CheckCircle2, RefreshCw, AlertCircle, Layers, ShieldCheck } from 'lucide-react';
import { ModelMetricsApiResponse, ModelMetricItem } from '../types';
import { API_BASE_URL } from '../config/api';

export const ModelAnalysisPage: React.FC = () => {
  const [metricsData, setMetricsData] = useState<ModelMetricsApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDepth, setSelectedDepth] = useState<number>(100);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE_URL}/api/model/metrics`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch validation metrics`);
        return res.json();
      })
      .then((data: ModelMetricsApiResponse) => {
        setMetricsData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Unable to connect to backend metrics API');
        setLoading(false);
      });
  }, []);

  const metrics: ModelMetricItem[] = metricsData?.metrics_by_depth || [];
  const selectedMetric = metrics.find((m) => m.depth === selectedDepth) || metrics[0];

  // Key highlight depths
  const highlightDepths = [0, 10, 50, 75, 100, 150, 300, 500, 1000, 1500];
  const displayMetrics = metrics.filter((m) => highlightDepths.includes(m.depth));

  return (
    <div className="space-y-6 font-sans">
      {/* 1. TOP ARCHITECTURE OVERVIEW BANNER */}
      <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-zinc-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-cyan-400" />
              <h2 className="text-base font-bold text-zinc-100">
                OceanEmbed Model Architecture & Out-of-Fold Validation
              </h2>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Phase 6 Optimized Multi-Model Voting Ensembles & Tuned Forest Regressors evaluated with 5-fold Float-Grouped Cross-Validation.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-950/40 px-3 py-1 text-xs font-mono text-emerald-300">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
              Zero Float-Level Leakage (GroupKFold)
            </span>
          </div>
        </div>

        {/* High-Level Benchmark Cards */}
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 text-xs">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
            <span className="text-zinc-400 text-[11px]">Evaluated Depths:</span>
            <div className="font-mono text-base font-bold text-zinc-100 mt-1">20 Levels</div>
            <span className="text-[10px] text-zinc-400">0m – 1500m (2000m excluded)</span>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
            <span className="text-zinc-400 text-[11px]">Surface Layer (10m) OOF:</span>
            <div className="font-mono text-base font-bold text-cyan-400 mt-1">0.416 °C RMSE</div>
            <span className="text-[10px] text-zinc-400">R² = 0.867 (Mixed Layer)</span>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
            <span className="text-zinc-400 text-[11px]">Thermocline (100m) OOF:</span>
            <div className="font-mono text-base font-bold text-amber-400 mt-1">1.496 °C RMSE</div>
            <span className="text-[10px] text-zinc-400">ΔRMSE = -0.132°C vs Phase 5</span>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
            <span className="text-zinc-400 text-[11px]">Deep Ocean (500m) OOF:</span>
            <div className="font-mono text-base font-bold text-emerald-400 mt-1">0.247 °C RMSE</div>
            <span className="text-[10px] text-zinc-400">R² = 0.956 (Climatology)</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex h-64 items-center justify-center rounded-xl border border-zinc-800 bg-[#0c0d12] text-zinc-400 gap-2">
          <RefreshCw className="h-5 w-5 animate-spin text-cyan-400" />
          <span>Loading genuine validation metrics from FastAPI backend...</span>
        </div>
      ) : error ? (
        <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-rose-900/50 bg-rose-950/20 p-6 text-rose-300 gap-2">
          <AlertCircle className="h-8 w-8 text-rose-400" />
          <span className="font-semibold text-sm">{error}</span>
          <span className="text-xs text-zinc-400">Ensure the FastAPI backend server is accessible.</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* 2. RECONSTRUCTION ERROR BY DEPTH CHART */}
          <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg lg:col-span-2 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Out-of-Fold Error by Depth (Phase 6 vs Phase 5 Baseline)
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Real cross-validation benchmarks evaluated strictly on unseen Argo floats
                  </p>
                </div>
                <BarChart2 className="h-4 w-4 text-cyan-400" />
              </div>

              {/* Depth Bars */}
              <div className="mt-5 space-y-2.5">
                {displayMetrics.map((row) => {
                  const isSelected = row.depth === selectedDepth;
                  return (
                    <div
                      key={row.depth}
                      onClick={() => setSelectedDepth(row.depth)}
                      className={`cursor-pointer rounded-lg p-2 transition ${
                        isSelected ? 'bg-cyan-950/30 border border-cyan-500/50' : 'hover:bg-zinc-900/60'
                      }`}
                    >
                      <div className="flex justify-between font-mono text-xs text-zinc-300 mb-1">
                        <span className="font-bold flex items-center gap-2">
                          <span className="text-cyan-400">{row.depth}m</span>
                          <span className="text-[10px] text-zinc-400 font-normal">({row.architecture.replace('_', ' ')})</span>
                        </span>
                        <span className="text-emerald-400 font-bold">
                          {row.rmse.toFixed(3)} °C{' '}
                          <span className="text-zinc-500 font-normal">vs {row.baseline_rmse.toFixed(3)} °C (Baseline)</span>
                        </span>
                      </div>
                      
                      {/* Bar Visualization */}
                      <div className="h-2.5 w-full bg-zinc-800 rounded-full overflow-hidden flex relative">
                        {/* Baseline Shadow Bar */}
                        <div
                          className="bg-zinc-600/40 absolute top-0 bottom-0 left-0 rounded-full"
                          style={{ width: `${Math.min(100, (row.baseline_rmse / 1.8) * 100)}%` }}
                        />
                        {/* Phase 6 Model Bar */}
                        <div
                          className={`rounded-full z-10 transition-all ${
                            row.depth >= 75 && row.depth <= 125 ? 'bg-amber-400' : 'bg-cyan-400'
                          }`}
                          style={{ width: `${Math.min(100, (row.rmse / 1.8) * 100)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between pt-3 border-t border-zinc-800/80 text-[11px] text-zinc-400">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
                  <span>Phase 6 Optimized Model</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-zinc-600" />
                  <span>Phase 5 Baseline</span>
                </span>
              </div>
              <span>Click any depth to inspect layer metrics</span>
            </div>
          </div>

          {/* 3. SELECTED DEPTH METRICS & SHAP ATTRIBUTION */}
          <div className="space-y-4">
            {/* Detailed Sounding Card */}
            <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg space-y-4">
              <div className="border-b border-zinc-800/80 pb-3 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Depth Benchmark: {selectedMetric.depth}m
                  </h3>
                  <p className="text-xs text-zinc-400">Architecture: {selectedMetric.architecture.replace('_', ' ')}</p>
                </div>
                <Layers className="h-4 w-4 text-cyan-400" />
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <span className="text-[10px] text-zinc-400">Out-of-Fold R²</span>
                  <div className="text-base font-bold text-cyan-300 mt-0.5">{selectedMetric.r2_score.toFixed(4)}</div>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <span className="text-[10px] text-zinc-400">OOF RMSE</span>
                  <div className="text-base font-bold text-emerald-400 mt-0.5">{selectedMetric.rmse.toFixed(4)} °C</div>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <span className="text-[10px] text-zinc-400">OOF MAE</span>
                  <div className="text-base font-bold text-zinc-100 mt-0.5">{selectedMetric.mae.toFixed(4)} °C</div>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                  <span className="text-[10px] text-zinc-400">Mean Bias (MBE)</span>
                  <div className="text-base font-bold text-zinc-300 mt-0.5">{selectedMetric.bias.toFixed(4)} °C</div>
                </div>
              </div>

              <div className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-3 text-xs text-zinc-300 space-y-1.5">
                <div className="font-semibold text-zinc-100 flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Physical Oceanography Dynamics</span>
                </div>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  {selectedMetric.depth <= 30
                    ? 'Surface mixed layer temperature is governed by solar radiation and turbulent heat exchange, coupled directly to Sea Surface Temperature (SST).'
                    : selectedMetric.depth <= 150
                    ? 'Thermocline layer experiences maximum vertical isotherm heave, governed by Sea Level Anomaly (SLA) capturing planetary waves and mesoscale eddies.'
                    : 'Intermediate and deep ocean temperatures are decoupled from synoptic surface weather, governed by basin climatology and water mass distributions.'}
                </p>
              </div>
            </div>

            {/* SHAP Attribution Card */}
            <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg space-y-3">
              <h4 className="text-xs font-bold text-zinc-200 uppercase tracking-wider">
                Phase 7 SHAP Feature Attribution
              </h4>
              <div className="space-y-2 text-xs">
                <div className="rounded bg-zinc-900/70 p-2 border border-zinc-800">
                  <div className="flex justify-between font-semibold text-zinc-200 text-[11px]">
                    <span>Surface Mixed Layer (0-30m)</span>
                    <span className="text-cyan-400">sat_sst (&gt;75%)</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-0.5">Direct radiative air-sea heat flux control.</p>
                </div>

                <div className="rounded bg-zinc-900/70 p-2 border border-zinc-800">
                  <div className="flex justify-between font-semibold text-zinc-200 text-[11px]">
                    <span>Thermocline (75-125m)</span>
                    <span className="text-amber-400">sat_sla (38-56%)</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-0.5">Sea Level Anomaly captures vertical thermocline heave.</p>
                </div>

                <div className="rounded bg-zinc-900/70 p-2 border border-zinc-800">
                  <div className="flex justify-between font-semibold text-zinc-200 text-[11px]">
                    <span>Deep Ocean (300-1500m)</span>
                    <span className="text-emerald-400">Coordinates (&gt;85%)</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 mt-0.5">Basin-scale hydrographic climatology (Arabian Sea vs Bay of Bengal).</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelAnalysisPage;
