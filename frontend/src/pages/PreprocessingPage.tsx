import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, Database, ShieldCheck } from 'lucide-react';

export const PreprocessingPage: React.FC = () => {
  const [activeStage, setActiveStage] = useState<number>(2);

  const stages = [
    {
      id: 1,
      title: 'NetCDF Telemetry Ingestion',
      subtitle: 'ARGO GDAC & Copernicus GHRSST',
      status: 'Completed',
      recordsProcessed: '18,420 profiles',
      rejectionRate: '0.4%',
      details:
        'Parse multi-sensor NetCDF trajectories, extract CTD salinity, pressure, and in-situ temperature variables. Synchronize timestamps to UTC 00:00.',
    },
    {
      id: 2,
      title: 'Sensor Despiking & Outlier Filter',
      subtitle: '3-sigma sliding median window',
      status: 'Active',
      recordsProcessed: '18,346 profiles',
      rejectionRate: '1.2%',
      details:
        'Identify transient electronic sensor spikes along the vertical pressure coordinate. Profiles containing consecutive spike anomalies (>3 standard deviations) are filtered.',
    },
    {
      id: 3,
      title: 'Density Inversion Check',
      subtitle: 'Thermodynamic buoyancy validation (∂ρ/∂z ≥ 0)',
      status: 'Pending',
      recordsProcessed: '18,125 profiles',
      rejectionRate: '0.8%',
      details:
        'Enforce ocean physical stability according to TEOS-10. Soundings displaying unstable density inversions due to salinity sensor drift are flagged with QC flag 3.',
    },
    {
      id: 4,
      title: 'Vertical Akima Spline Interpolation',
      subtitle: 'Standard hydrographic levels (0 to 1000m)',
      status: 'Pending',
      recordsProcessed: '17,980 profiles',
      rejectionRate: '0.0%',
      details:
        'Interpolate irregular CTD sampling depths onto 58 standard oceanographic depth levels preserving thermocline gradients without spurious cubic oscillations.',
    },
    {
      id: 5,
      title: 'Spatial Grid Binning & Latent Alignment',
      subtitle: '0.25° × 0.25° domain rasterization',
      status: 'Pending',
      recordsProcessed: '17,980 profiles',
      rejectionRate: '0.0%',
      details:
        'Map interpolated vertical profiles to corresponding SST and Sea Surface Height (SSH) satellite pixels for model training pair assembly.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Database className="h-5 w-5 text-cyan-400" />
              <span>Hydrographic Data Preprocessing & Quality Control Pipeline</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Multi-stage automated pipeline translating raw satellite SST & in-situ ARGO profiles into analysis-ready tensors.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-3 py-1.5 rounded-lg">
            <ShieldCheck className="h-4 w-4" />
            <span>TEOS-10 Standards Compliant</span>
          </div>
        </div>
      </div>

      {/* Stage Flow Stepper */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {stages.map((stg) => {
          const isSelected = activeStage === stg.id;
          return (
            <div
              key={stg.id}
              onClick={() => setActiveStage(stg.id)}
              className={`cursor-pointer rounded-xl border p-4 transition shadow-md ${
                isSelected
                  ? 'border-cyan-500 bg-cyan-950/40 text-white'
                  : 'border-slate-800 bg-[#091122]/80 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="font-bold text-cyan-400">STAGE 0{stg.id}</span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[9px] font-semibold ${
                    stg.status === 'Completed'
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : stg.status === 'Active'
                      ? 'bg-cyan-950 text-cyan-400 border border-cyan-800'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {stg.status}
                </span>
              </div>
              <h4 className="mt-2 text-xs font-semibold text-white">{stg.title}</h4>
              <p className="mt-1 text-[10px] text-slate-400">{stg.subtitle}</p>
            </div>
          );
        })}
      </div>

      {/* Active Stage Deep Dive */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg lg:col-span-2">
          <div className="border-b border-slate-800 pb-3">
            <div className="text-xs font-mono text-cyan-400 uppercase">Stage 0{activeStage} Inspection</div>
            <h3 className="text-base font-bold text-white mt-1">
              {stages[activeStage - 1].title}
            </h3>
            <p className="text-xs text-slate-400 mt-1">{stages[activeStage - 1].details}</p>
          </div>

          <div className="mt-5 grid grid-cols-2 gap-4 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
              <span className="text-slate-400 text-[11px]">Soundings Validated:</span>
              <div className="font-mono text-xl font-bold text-white mt-1">
                {stages[activeStage - 1].recordsProcessed}
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Passed initial QC flags (WMO 1 & 2)</p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
              <span className="text-slate-400 text-[11px]">Rejection / Filter Rate:</span>
              <div className="font-mono text-xl font-bold text-amber-400 mt-1">
                {stages[activeStage - 1].rejectionRate}
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Flagged for automated correction</p>
            </div>
          </div>

          {/* Code / Algorithm Snippet Preview */}
          <div className="mt-5 rounded-lg border border-slate-800 bg-[#050a16] p-4 text-xs font-mono text-slate-300">
            <div className="text-[10px] text-cyan-400 uppercase tracking-widest mb-2 border-b border-slate-800 pb-1">
              Processing Routine (Python / NumPy / Scipy)
            </div>
            <pre className="text-[11px] leading-relaxed text-slate-300 overflow-x-auto">
{`def despike_vertical_profile(pressure, temperature, window=5, threshold=3.0):
    """Applies rolling median deviation filter along water column."""
    rolling_med = scipy.ndimage.median_filter(temperature, size=window)
    residuals = np.abs(temperature - rolling_med)
    mad = np.median(residuals) + 1e-6
    mask = residuals < (threshold * 1.4826 * mad)
    return pressure[mask], temperature[mask]`}
            </pre>
          </div>
        </div>

        {/* Quality Audit Log */}
        <div className="rounded-xl border border-slate-800 bg-[#091122]/90 p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-sm font-semibold text-white">Automated Audit Log</h3>
              <p className="text-xs text-slate-400">Live filter outputs & diagnostics</p>
            </div>

            <div className="mt-4 space-y-2.5 text-xs font-mono">
              <div className="rounded bg-slate-900/60 p-2.5 border border-slate-800 flex items-start gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-slate-300 text-[11px]">Float #2903341: Despike OK</div>
                  <div className="text-[10px] text-slate-500">104 depth soundings processed</div>
                </div>
              </div>

              <div className="rounded bg-slate-900/60 p-2.5 border border-slate-800 flex items-start gap-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-slate-300 text-[11px]">Float #2903348: Vertical Spline OK</div>
                  <div className="text-[10px] text-slate-500">Akima interpolation mapped to 58 levels</div>
                </div>
              </div>

              <div className="rounded bg-slate-900/60 p-2.5 border border-slate-800 flex items-start gap-2">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-amber-300 text-[11px]">Float #2903365: Inversion Warning</div>
                  <div className="text-[10px] text-slate-500">drho/dz = -0.004 kg/m4 at depth 85m</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            Pipeline engine: OceanEmbed Python Preprocessor v0.2
          </div>
        </div>
      </div>
    </div>
  );
};
export default PreprocessingPage;
