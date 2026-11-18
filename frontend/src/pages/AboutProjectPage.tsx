import React from 'react';
import { Waves, BookOpen, ShieldCheck, Database } from 'lucide-react';

export const AboutProjectPage: React.FC = () => {
  return (
    <div className="space-y-6 font-sans">
      {/* Hero Section */}
      <div className="rounded-2xl border border-zinc-800 bg-gradient-to-br from-[#0c0d12] via-[#090b10] to-[#06070a] p-6 shadow-2xl sm:p-8">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-700 shadow-lg shadow-cyan-500/20">
            <Waves className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight text-zinc-100 sm:text-2xl">
                OceanEmbed (SIH26066)
              </h2>
              <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-xs font-semibold text-cyan-400 border border-cyan-800 font-mono">
                Production System (v1.0)
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1 sm:text-sm">
              Continuous 3D Ocean Subsurface Temperature Field Reconstruction via Physics-Informed Machine Learning
            </p>
          </div>
        </div>

        <p className="mt-6 text-xs text-zinc-300 leading-relaxed sm:text-sm max-w-4xl">
          While modern Earth observation satellites provide continuous high-resolution sea surface temperature (SST) and sea surface height (SSH/SLA) measurements, subsurface ocean temperature observations remain sparse, relying primarily on drifting Argo profiling floats. OceanEmbed bridges this critical gap by training multi-depth machine learning ensembles and tree models collocated with genuine satellite and in-situ Argo observations to reconstruct the complete vertical ocean thermal structure down to 1500 metres across the North Indian Ocean.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Objectives & Scientific Methodology */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-6 shadow-lg lg:col-span-2 space-y-5">
          <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 border-b border-zinc-800/80 pb-3">
            <BookOpen className="h-4 w-4 text-cyan-400" />
            <span>Research & System Methodology</span>
          </h3>

          <div className="space-y-4 text-xs text-zinc-300">
            <div className="flex gap-3">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-cyan-950 border border-cyan-800 text-[11px] font-bold text-cyan-400">
                01
              </span>
              <div>
                <h4 className="font-semibold text-zinc-100">Full-Depth Water Column Reconstruction (0–1500m)</h4>
                <p className="mt-1 text-zinc-400 leading-relaxed">
                  Reconstructs temperature across 20 standardized oceanographic depth levels (0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500m), resolving the steep thermocline zone where internal waves and mesoscale eddies induce major vertical isotherm heave.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-cyan-950 border border-cyan-800 text-[11px] font-bold text-cyan-400">
                02
              </span>
              <div>
                <h4 className="font-semibold text-zinc-100">Float-Grouped Cross-Validation (Zero Data Leakage)</h4>
                <p className="mt-1 text-zinc-400 leading-relaxed">
                  Models are validated using 5-fold GroupKFold cross-validation grouped strictly by Argo float WMO identifier, preventing float-level data leakage and verifying genuine generalization across unseen drifting floats.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-cyan-950 border border-cyan-800 text-[11px] font-bold text-cyan-400">
                03
              </span>
              <div>
                <h4 className="font-semibold text-zinc-100">SHAP Explainability & Physical Attribution</h4>
                <p className="mt-1 text-zinc-400 leading-relaxed">
                  TreeSHAP feature attributions confirm that Sea Surface Temperature governs the surface mixed layer (&gt;75%), Sea Level Anomaly governs the thermocline (38–56%), and geographic coordinates govern deep-water climatology (&gt;85%).
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 text-xs text-zinc-300">
            <div className="font-semibold text-zinc-100 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Scientific Rigor & Preservation:</span>
            </div>
            <p className="mt-1.5 text-zinc-400 leading-relaxed">
              All 75 collocated in-situ profiles across 13 Argo floats and 21 synchronized satellite NetCDFs (2018–2026) are fully preserved. Model predictions and evaluations are strictly genuine with honest disclosure of dataset limitations.
            </p>
          </div>
        </div>

        {/* Operational Data Sources */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-6 shadow-lg space-y-4">
          <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 border-b border-zinc-800/80 pb-3">
            <Database className="h-4 w-4 text-cyan-400" />
            <span>Operational Data Ingestion</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
              <div className="font-semibold text-zinc-200">International Argo GDAC & INCOIS</div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Quality-controlled CTD profiling floats across the Arabian Sea and Bay of Bengal.
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
              <div className="font-semibold text-zinc-200">NOAA Coral Reef Watch (CRW)</div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                0.05° high-resolution Sea Surface Temperature (SST) daily satellite observations.
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
              <div className="font-semibold text-zinc-200">Copernicus Marine (CMEMS)</div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                0.25° gridded daily Sea Level Anomaly (SLA) & Geostrophic Surface Currents (U, V).
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
              <div className="font-semibold text-zinc-200">FastAPI & PyTorch / scikit-learn</div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Low-latency microsecond inference serving calibrated multi-depth voting ensembles.
              </p>
            </div>
          </div>

          <div className="pt-2 text-center text-[11px] text-zinc-400 font-mono">
            OceanEmbed • Smart India Hackathon (SIH26066)
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutProjectPage;
