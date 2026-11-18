import React, { useState, useEffect, useMemo } from 'react';
import {
  Play,
  CheckCircle2,
  Sliders,
  RefreshCw,
  Thermometer,
  AlertCircle,
} from 'lucide-react';
import { PredictionResponseData, ArgoProfileItem } from '../types';
import { checkIsOcean } from '../components/OceanMap';
import { API_BASE_URL } from '../config/api';

export const PredictionPage: React.FC = () => {
  // Input parameters
  const [sst, setSst] = useState<string>('29.2');
  const [sla, setSla] = useState<string>('0.05');
  const [currentU, setCurrentU] = useState<string>('0.12');
  const [currentV, setCurrentV] = useState<string>('-0.08');
  const [latitude, setLatitude] = useState<string>('15.0');
  const [longitude, setLongitude] = useState<string>('87.5');
  const [date, setDate] = useState<string>('2025-07-15');

  // Preset profiles from genuine collocated dataset
  const [presetProfiles, setPresetProfiles] = useState<ArgoProfileItem[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('');

  // Inference state
  const [isInferring, setIsInferring] = useState<boolean>(false);
  const [predictionResult, setPredictionResult] = useState<PredictionResponseData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleBlur = () => {
    if (sst === '') return;
    const num = parseFloat(sst);
    if (num < 26) setSst('26');
    if (num > 32) setSst('32');
  };

  // Fetch preset Argo profiles on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/ocean/profiles?limit=12`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.profiles) {
          setPresetProfiles(data.profiles);
        }
      })
      .catch(() => {
        // Preset fetch failure non-blocking
      });
  }, []);

  // Track dirty state (whether user modified parameters since last prediction)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);

  // Auto-predict toggle (instant prediction on change vs manual button)
  const [autoPredict, setAutoPredict] = useState<boolean>(true);

  // Real-time Land-Sea Masking Validation
  const isLocationOcean = useMemo(() => {
    const latNum = parseFloat(latitude);
    const lonNum = parseFloat(longitude);
    if (isNaN(latNum) || isNaN(lonNum)) return true;
    return checkIsOcean(latNum, lonNum).isOcean;
  }, [latitude, longitude]);

  // Execute Live Inference
  const executePrediction = async (customParams?: {
    sstVal?: string;
    slaVal?: string;
    uVal?: string;
    vVal?: string;
    latVal?: string;
    lonVal?: string;
    dateVal?: string;
  }) => {
    const targetSst = customParams?.sstVal ?? sst;
    const targetSla = customParams?.slaVal ?? sla;
    const targetU = customParams?.uVal ?? currentU;
    const targetV = customParams?.vVal ?? currentV;
    const targetLat = customParams?.latVal ?? latitude;
    const targetLon = customParams?.lonVal ?? longitude;
    const targetDate = customParams?.dateVal ?? date;

    const latNum = parseFloat(targetLat);
    const lonNum = parseFloat(targetLon);
    const sstNum = parseFloat(targetSst);
    const slaNum = parseFloat(targetSla);

    // Guard against incomplete typing
    if (isNaN(latNum) || isNaN(lonNum) || isNaN(sstNum) || isNaN(slaNum)) {
      return;
    }

    // Enforce Authoritative Land-Sea Mask
    const landCheck = checkIsOcean(latNum, lonNum);
    if (!landCheck.isOcean) {
      setError(landCheck.message);
      setPredictionResult(null);
      setIsInferring(false);
      return;
    }

    setIsInferring(true);
    setError(null);

    const payload = {
      sat_sst: sstNum,
      sat_sla: slaNum,
      sat_current_u: parseFloat(targetU) || 0.0,
      sat_current_v: parseFloat(targetV) || 0.0,
      latitude: latNum,
      longitude: lonNum,
      date: targetDate,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        let errorMsg = `Inference execution failed (HTTP ${res.status})`;
        if (errJson && errJson.detail) {
          if (Array.isArray(errJson.detail)) {
            errorMsg = errJson.detail.map((d: any) => `${d.loc ? d.loc.slice(-1)[0] + ': ' : ''}${d.msg}`).join(', ');
          } else if (typeof errJson.detail === 'string') {
            errorMsg = errJson.detail;
          }
        }
        throw new Error(errorMsg);
      }

      const data: PredictionResponseData = await res.json();
      setPredictionResult(data);
      setHasUnsavedChanges(false);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend prediction engine');
    } finally {
      setIsInferring(false);
    }
  };

  // Debounced auto-inference when autoPredict is enabled
  useEffect(() => {
    if (!autoPredict) {
      setHasUnsavedChanges(true);
      return;
    }
    const timer = setTimeout(() => {
      executePrediction();
    }, 400); // 400ms debounce
    return () => clearTimeout(timer);
  }, [sst, sla, currentU, currentV, latitude, longitude, date, autoPredict]);

  // Handle Preset Selection
  const handleSelectPreset = (profileId: string) => {
    setSelectedPresetId(profileId);
    if (!profileId || profileId === 'custom') {
      setSst('29.2');
      setSla('0.05');
      setCurrentU('0.12');
      setCurrentV('-0.08');
      setLatitude('15.0');
      setLongitude('87.5');
      setDate('2025-07-15');
      return;
    }
    const matched = presetProfiles.find((p) => p.profile_id === profileId);
    if (matched) {
      setSst(matched.sat_sst.toString());
      setSla(matched.sat_sla.toString());
      setLatitude(matched.latitude.toString());
      setLongitude(matched.longitude.toString());
      setDate(matched.date);
      if (matched.sat_current_u !== undefined) {
        setCurrentU(matched.sat_current_u.toString());
      }
      if (matched.sat_current_v !== undefined) {
        setCurrentV(matched.sat_current_v.toString());
      }
    }
  };

  const kpis = predictionResult?.kpis;
  const profile = predictionResult?.profile || [];

  return (
    <div className="space-y-6 font-sans">
      {/* 1. TOP BANNER */}
      <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
              <Thermometer className="h-5 w-5 text-cyan-400" />
              <span>OceanEmbed 3D Subsurface Temperature Reconstruction Studio</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Supply satellite surface parameters (SST, SLA, U, V) and geospatial coordinates to reconstruct high-fidelity vertical temperature profiles down to 1500m via Phase 6 production models.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Auto Predict Toggle */}
            <label className="flex items-center gap-2 text-xs text-zinc-300 cursor-pointer select-none bg-zinc-900/90 border border-zinc-800 px-3 py-2 rounded-lg">
              <input
                type="checkbox"
                checked={autoPredict}
                onChange={(e) => setAutoPredict(e.target.checked)}
                className="accent-cyan-500 rounded h-3.5 w-3.5 cursor-pointer"
              />
              <span className="text-[11px] font-medium">Auto-Predict on Change</span>
            </label>

            <button
              onClick={() => executePrediction()}
              disabled={isInferring || !isLocationOcean}
              className={`flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-xs font-semibold text-white shadow-lg transition ${!isLocationOcean
                ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed shadow-none'
                : hasUnsavedChanges
                  ? 'bg-gradient-to-r from-amber-500 to-rose-600 animate-pulse shadow-rose-500/30 cursor-pointer'
                  : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 shadow-cyan-500/20 cursor-pointer'
                } disabled:opacity-60`}
            >
              {isInferring ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Evaluating Models...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-white" />
                  <span>{hasUnsavedChanges ? 'Update Prediction Now' : 'Execute Live Prediction'}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 2. MAIN WORKSPACE (Parameters Form on Left, Output Visualizer on Right) */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Input Parameters Card */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg space-y-4">
          <div className="border-b border-zinc-800/80 pb-3 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                <Sliders className="h-4 w-4 text-cyan-400" />
                <span>Input Predictors</span>
              </h3>
              <p className="text-[11px] text-zinc-400">Satellite observations & spatio-temporal inputs</p>
            </div>
          </div>

          {/* Preset Profile Dropdown */}
          {presetProfiles.length > 0 && (
            <div className="space-y-1 text-xs">
              <label className="text-zinc-400 text-[10px] uppercase tracking-wider font-semibold">
                Load Genuine Argo Collocated Preset
              </label>
              <select
                value={selectedPresetId}
                onChange={(e) => handleSelectPreset(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/90 px-3 py-1.5 text-zinc-200 outline-none focus:border-cyan-500 text-xs cursor-pointer"
              >
                <option value="custom">-- Custom Parameters --</option>
                {presetProfiles.map((p) => (
                  <option key={p.profile_id} value={p.profile_id}>
                    Float {p.float_wmo} ({p.basin.replace('_', ' ')}) • {p.date}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Coordinates Grid */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Latitude (°N)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="25"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Longitude (°E)</label>
              <input
                type="number"
                step="0.1"
                min="50"
                max="100"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          {/* Land-Sea Mask Real-Time Warning Banner */}
          {!isLocationOcean && (
            <div className="flex items-start gap-2.5 rounded-lg bg-amber-950/80 border border-amber-800/90 p-3 text-xs text-amber-200 shadow-md">
              <AlertCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-amber-300 block text-[11px]">Selected location is land</span>
                <span className="text-[10px] text-amber-200/90 leading-snug">
                  Ocean temperature prediction unavailable. Please select an ocean coordinate within the North Indian Ocean domain (0°–26°N, 50°–100°E).
                </span>
              </div>
            </div>
          )}

          {/* Date Picker */}
          <div className="space-y-1 text-xs">
            <label className="text-zinc-300 text-[11px]">Observation Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono text-xs cursor-pointer"
            />
          </div>

          {/* Satellite Features */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Sea Surface Temp (SST, °C)</label>
              <input
                type="number"
                step="0.1"
                min="26"
                max="32"
                value={sst}
                onBlur={handleBlur}
                onChange={(e) => setSst(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Sea Level Anomaly (SLA, m)</label>
              <input
                type="number"
                step="0.01"
                min="-1.0"
                max="1.0"
                value={sla}
                onChange={(e) => setSla(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          {/* Geostrophic Current Velocities */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Current U (Zonal, m/s)</label>
              <input
                type="number"
                step="0.05"
                value={currentU}
                onChange={(e) => setCurrentU(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="text-zinc-300 text-[11px]">Current V (Meridional, m/s)</label>
              <input
                type="number"
                step="0.05"
                value={currentV}
                onChange={(e) => setCurrentV(e.target.value)}
                className="w-full rounded-lg border border-zinc-800 bg-zinc-900/80 px-3 py-2 text-zinc-100 outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3 text-[11px] text-zinc-400 space-y-1">
            <div className="font-semibold text-zinc-200">Production Inference Engine:</div>
            <p>
              Calls 20 calibrated depth models simultaneously on FastAPI backend, returning continuous vertical stratification $T(z)$ from surface skin to 1500m.
            </p>
          </div>
        </div>

        {/* Prediction Results & Profile Viewer */}
        <div className="rounded-xl border border-zinc-800 bg-[#0c0d12] p-5 shadow-lg lg:col-span-2 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">
                  Reconstructed Subsurface Temperature Profile T(z)
                </h3>
                <p className="text-xs text-zinc-400">
                  Location: {latitude}°N, {longitude}°E ({predictionResult?.basin ?? 'North Indian Ocean'}) • Date: {date}
                </p>
              </div>
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <CheckCircle2 className="h-4 w-4" />
                <span>Live Model Inferred</span>
              </span>
            </div>

            {error && (
              <div className="my-3 flex items-center gap-2 rounded-lg border border-rose-900/50 bg-rose-950/20 p-3 text-xs text-rose-300">
                <AlertCircle className="h-4 w-4 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* KPI Summary Cards */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 my-3 text-xs">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                <span className="text-zinc-400 text-[10px]">Surface Temp (10m)</span>
                <div className="font-mono text-base font-bold text-zinc-100 mt-0.5">
                  {kpis?.surfaceTemp ?? '--'} °C
                </div>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                <span className="text-zinc-400 text-[10px]">Mixed Layer Depth (MLD)</span>
                <div className="font-mono text-base font-bold text-cyan-300 mt-0.5">
                  {kpis?.mld ?? '--'} m
                </div>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                <span className="text-zinc-400 text-[10px]">Thermocline Depth</span>
                <div className="font-mono text-base font-bold text-amber-400 mt-0.5">
                  {kpis?.thermoclineDepth ?? '--'} m
                </div>
              </div>
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                <span className="text-zinc-400 text-[10px]">Deep Temp (1500m)</span>
                <div className="font-mono text-base font-bold text-emerald-400 mt-0.5">
                  {kpis?.targetDepthTemp ?? '--'} °C
                </div>
              </div>
            </div>

            {/* 20-Depth Reconstructed Temperature Table & Sounding Curve */}
            <div className="mt-4 max-h-[320px] overflow-y-auto rounded-lg border border-zinc-800 bg-[#08090d]">
              <table className="w-full text-left text-xs">
                <thead className="sticky top-0 bg-zinc-900/90 text-[10px] uppercase tracking-wider text-zinc-400 border-b border-zinc-800">
                  <tr>
                    <th className="px-3.5 py-2 font-semibold">Depth</th>
                    <th className="px-3.5 py-2 font-semibold">Reconstructed Temp</th>
                    <th className="px-3.5 py-2 font-semibold">Expected RMSE</th>
                    <th className="px-3.5 py-2 font-semibold">Expected R²</th>
                    <th className="px-3.5 py-2 font-semibold">Layer Classification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60 font-mono text-zinc-300 text-[11px]">
                  {profile.map((pt) => {
                    const layerTag =
                      pt.depth <= 30
                        ? 'Surface Mixed Layer'
                        : pt.depth <= 150
                          ? 'Thermocline Zone'
                          : pt.depth <= 500
                            ? 'Intermediate Ocean'
                            : 'Deep Water';

                    const tempColor =
                      pt.temperature > 26
                        ? 'text-rose-400'
                        : pt.temperature > 20
                          ? 'text-amber-400'
                          : pt.temperature > 12
                            ? 'text-cyan-400'
                            : 'text-blue-400';

                    return (
                      <tr key={pt.depth} className="hover:bg-zinc-900/40 transition">
                        <td className="px-3.5 py-1.5 font-bold text-zinc-200">{pt.depth}m</td>
                        <td className={`px-3.5 py-1.5 font-bold ${tempColor}`}>
                          {pt.temperature.toFixed(2)} °C
                        </td>
                        <td className="px-3.5 py-1.5 text-zinc-400">
                          ± {pt.expected_rmse?.toFixed(2) ?? '0.35'} °C
                        </td>
                        <td className="px-3.5 py-1.5 text-emerald-400">
                          {pt.expected_r2?.toFixed(3) ?? '0.850'}
                        </td>
                        <td className="px-3.5 py-1.5 font-sans text-[10px] text-zinc-400">
                          {layerTag}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Physical Feature Attributions Readout */}
          {predictionResult?.feature_attributions && (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3 text-xs space-y-1.5">
              <span className="font-semibold text-zinc-200 text-[11px]">
                Physical Attributions (Phase 7 Explainability):
              </span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[10px] text-zinc-400">
                <div className="rounded bg-zinc-900 p-2 border border-zinc-800">
                  <span className="font-semibold text-cyan-300 block">Surface (0-30m):</span>
                  {predictionResult.feature_attributions.surface_0_30m}
                </div>
                <div className="rounded bg-zinc-900 p-2 border border-zinc-800">
                  <span className="font-semibold text-amber-300 block">Thermocline (75-125m):</span>
                  {predictionResult.feature_attributions.thermocline_75_125m}
                </div>
                <div className="rounded bg-zinc-900 p-2 border border-zinc-800">
                  <span className="font-semibold text-emerald-300 block">Deep Ocean (300-1500m):</span>
                  {predictionResult.feature_attributions.deep_300_1500m}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PredictionPage;
