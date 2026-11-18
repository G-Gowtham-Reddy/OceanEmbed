import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import L from 'leaflet';
import {
  MapPin,
  Radio,
  RotateCcw,
  Key,
  Sparkles,
  CheckCircle2,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import { RegionInfo, ArgoProfileItem, OceanApiResponse, PredictionResponseData } from '../types';
import oceanLandMask from '../data/ocean_land_mask.json';
import { API_BASE_URL } from '../config/api';

// Authoritative Land-Sea Mask Validation (CMEMS / NOAA 0.25-deg grid)
export const checkIsOcean = (lat: number, lon: number): { isOcean: boolean; message: string } => {
  if (lat < 0.0 || lat > 26.0 || lon < 50.0 || lon > 100.0) {
    return {
      isOcean: false,
      message: 'Selected location is outside North Indian Ocean domain (0°–26°N, 50°–100°E).',
    };
  }
  const grid = oceanLandMask.grid;
  const i = Math.round((lat - grid.lat_min) / grid.lat_step);
  const j = Math.round((lon - grid.lon_min) / grid.lon_step);
  const clampedI = Math.max(0, Math.min(grid.n_lat - 1, i));
  const clampedJ = Math.max(0, Math.min(grid.n_lon - 1, j));

  const mask = oceanLandMask.mask;
  if (mask[clampedI] && mask[clampedI][clampedJ] === 1) {
    return { isOcean: true, message: 'Valid ocean location.' };
  }
  return {
    isOcean: false,
    message: 'Selected location is land – ocean prediction unavailable.',
  };
};

interface OceanMapProps {
  selectedRegionId: string;
  onSelectRegion: (regionId: string) => void;
  regions: RegionInfo[];
  currentTemp?: number;
  date?: string;
  targetDepth?: number;
  onSelectCustomProfile?: (profileData: OceanApiResponse) => void;
}

// Custom Marker Icons for Argo Floats
const createArgoMarkerIcon = (isSelected: boolean) =>
  L.divIcon({
    className: 'custom-argo-marker',
    html: `
      <div style="position: relative; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 26px; height: 26px; border-radius: 50%; background: ${
          isSelected ? 'rgba(34, 211, 238, 0.45)' : 'rgba(6, 182, 212, 0.22)'
        }; border: 1.5px solid ${isSelected ? '#38bdf8' : '#22d3ee'}; animation: argoPulse 2.2s infinite ease-in-out;"></div>
        <div style="position: absolute; width: 12px; height: 12px; border-radius: 50%; background: ${
          isSelected ? '#38bdf8' : '#0891b2'
        }; border: 2px solid #090a10; box-shadow: 0 0 10px #22d3ee;"></div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
  });

// Custom Marker for Clicked Ocean Target Location
const createTargetMarkerIcon = () =>
  L.divIcon({
    className: 'custom-target-marker',
    html: `
      <div style="position: relative; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 28px; height: 28px; border-radius: 50%; border: 2px dashed #f43f5e;"></div>
        <div style="width: 10px; height: 10px; border-radius: 50%; background: #f43f5e; box-shadow: 0 0 12px #f43f5e;"></div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });

// Component to handle map clicks
interface ClickHandlerProps {
  onMapClick: (lat: number, lon: number) => void;
  onMouseMove: (lat: number, lon: number) => void;
}

const MapEventsHandler: React.FC<ClickHandlerProps> = ({ onMapClick, onMouseMove }) => {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
    mousemove(e) {
      onMouseMove(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

// Component to handle map recentering
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
};

export const OceanMap: React.FC<OceanMapProps> = ({
  selectedRegionId,
  onSelectRegion,
  regions,
  currentTemp: _currentTemp,
  date = new Date().toISOString().split('T')[0],
  targetDepth = 1000,
  onSelectCustomProfile,
}) => {
  // Environment Key or Manual Key
  const envKey = import.meta.env.VITE_MAPTILER_API_KEY || '';
  const [apiKey, setApiKey] = useState<string>(envKey);
  const [keyInput, setKeyInput] = useState<string>('');
  const [showKeyDialog, setShowKeyDialog] = useState<boolean>(false);
  const [tileError, setTileError] = useState<boolean>(false);

  // Map state
  const initialCenter: [number, number] = [12.5, 78.0];
  const initialZoom = 5;
  const [mapCenter, setMapCenter] = useState<[number, number]>(initialCenter);
  const [mapZoom, setMapZoom] = useState<number>(initialZoom);
  const [hoverCoords, setHoverCoords] = useState<{ lat: number; lon: number } | null>(null);

  // Argo profiles loaded from backend
  const [argoProfiles, setArgoProfiles] = useState<ArgoProfileItem[]>([]);
  const [selectedFloat, setSelectedFloat] = useState<ArgoProfileItem | null>(null);
  const [loadingFloats, setLoadingFloats] = useState<boolean>(true);

  // Clicked ocean location & ad-hoc prediction state
  const [clickedLocation, setClickedLocation] = useState<{
    lat: number;
    lon: number;
    loading: boolean;
    error: string | null;
    prediction: PredictionResponseData | null;
  } | null>(null);

  // Filter toggles
  const [showFloats, setShowFloats] = useState<boolean>(true);
  const [selectedBasinFilter, setSelectedBasinFilter] = useState<string>('all');

  // Load genuine Argo profiles from backend
  useEffect(() => {
    setLoadingFloats(true);
    fetch(`${API_BASE_URL}/api/ocean/profiles`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load Argo profiles');
        return res.json();
      })
      .then((data) => {
        if (data && data.profiles) {
          setArgoProfiles(data.profiles);
        }
        setLoadingFloats(false);
      })
      .catch(() => {
        setLoadingFloats(false);
      });
  }, []);

  // Update map center when region is changed from outside
  useEffect(() => {
    const reg = regions.find((r) => r.id === selectedRegionId);
    if (reg) {
      setMapCenter([reg.lat, reg.lon]);
      setMapZoom(6);
    }
  }, [selectedRegionId, regions]);

  // Handle map click anywhere on the ocean
  const handleMapClick = async (lat: number, lon: number) => {
    // 1. Authoritative Land-Sea Mask Check
    const maskCheck = checkIsOcean(lat, lon);
    if (!maskCheck.isOcean) {
      setClickedLocation({
        lat,
        lon,
        loading: false,
        error: maskCheck.message,
        prediction: null,
      });
      return;
    }

    setClickedLocation({
      lat,
      lon,
      loading: true,
      error: null,
      prediction: null,
    });

    try {
      // Find nearest region to infer realistic baseline satellite values
      const nearestRegion = regions.reduce((prev, curr) => {
        const dPrev = Math.hypot(prev.lat - lat, prev.lon - lon);
        const dCurr = Math.hypot(curr.lat - lat, curr.lon - lon);
        return dCurr < dPrev ? curr : prev;
      }, regions[0] || { baseSst: 29.0 });

      // Call backend live inference POST /api/predict
      const res = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: Number(lat.toFixed(3)),
          longitude: Number(lon.toFixed(3)),
          sat_sst: Number((nearestRegion?.baseSst || 29.0).toFixed(2)),
          sat_sla: Number((Math.sin(lat * 0.2) * 0.08).toFixed(3)),
          sat_current_u: Number((Math.cos(lon * 0.1) * 0.15).toFixed(3)),
          sat_current_v: Number((Math.sin(lat * 0.1) * 0.12).toFixed(3)),
          date: date,
        }),
      });

      if (!res.ok) {
        throw new Error(`Prediction API error: HTTP ${res.status}`);
      }

      const predictionData: PredictionResponseData = await res.json();
      setClickedLocation({
        lat,
        lon,
        loading: false,
        error: null,
        prediction: predictionData,
      });

      // Synchronize with dashboard if handler provided
      if (onSelectCustomProfile && predictionData) {
        onSelectCustomProfile({
          region: `Coord (${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`,
          regionId: predictionData.basin,
          coordinates: `${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E`,
          lat: Number(lat.toFixed(3)),
          lon: Number(lon.toFixed(3)),
          date: date,
          maxDepth: targetDepth,
          kpis: {
            surfaceTemp: predictionData.kpis.surfaceTemp,
            mld: predictionData.kpis.mld,
            thermoclineDepth: predictionData.kpis.thermoclineDepth,
            targetDepthTemp: predictionData.kpis.targetDepthTemp,
            activeFloats: 1,
          },
          profile: predictionData.profile,
          layers: predictionData.layers,
        });
      }
    } catch (err: any) {
      setClickedLocation({
        lat,
        lon,
        loading: false,
        error: err.message || 'Failed to generate subsurface temperature prediction',
        prediction: null,
      });
    }
  };

  // Inspect in-situ Argo profile
  const handleInspectArgoFloat = async (flt: ArgoProfileItem) => {
    setSelectedFloat(flt);
    try {
      const res = await fetch(`${API_BASE_URL}/api/ocean/profiles/${flt.profile_id}`);
      if (res.ok) {
        const fullProfile = await res.json();
        if (onSelectCustomProfile) {
          onSelectCustomProfile({
            region: `Argo Float #${flt.float_wmo} (Cycle ${flt.cycle_number})`,
            regionId: flt.basin.toLowerCase().replace('_', '-'),
            coordinates: `${flt.latitude.toFixed(3)}°N, ${flt.longitude.toFixed(3)}°E`,
            lat: flt.latitude,
            lon: flt.longitude,
            date: flt.date,
            maxDepth: targetDepth,
            kpis: {
              surfaceTemp: flt.surface_temp || flt.sat_sst,
              mld: 40.0,
              thermoclineDepth: 100,
              targetDepthTemp: flt.deep_temp_500m || 9.8,
              activeFloats: 1,
            },
            profile: fullProfile.profile.map((p: any) => ({
              depth: p.depth,
              temperature: p.observed_temp !== null ? p.observed_temp : p.predicted_temp,
              label: `${p.depth}m`,
            })),
            layers: fullProfile.layers || [],
          });
        }
      }
    } catch {
      // Ignore
    }
  };

  // Filtered Argo profiles
  const visibleProfiles = argoProfiles.filter((p) => {
    if (selectedBasinFilter === 'all') return true;
    return p.basin.toLowerCase() === selectedBasinFilter.toLowerCase();
  });

  // Base Tile Layer selection
  // 1. ESRI Dark Gray Canvas (Default high contrast dark scientific basemap, 0 API key required)
  // 2. ESRI Ocean Basemap (Detailed bathymetric depth contours & ocean trenches, 0 API key required)
  // 3. CartoDB Dark Matter (Clean vector-raster dark basemap, 0 API key required)
  // 4. MapTiler Dark Scientific (Active whenever user provides a MapTiler API key)
  const [basemapStyle, setBasemapStyle] = useState<'esri-dark' | 'esri-ocean' | 'carto-dark' | 'maptiler'>('esri-dark');

  const getTileConfig = () => {
    if (basemapStyle === 'maptiler' && apiKey && !tileError) {
      return {
        url: `https://api.maptiler.com/maps/dataviz-dark/{z}/{x}/{y}.png?key=${apiKey}`,
        attribution: '&copy; <a href="https://www.maptiler.com/copyright/">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        label: 'MapTiler Dark',
      };
    }
    if (basemapStyle === 'esri-ocean') {
      return {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attribution: '&copy; Esri, GEBCO, NOAA, National Geographic, DeLorme, HERE, Geonames.org',
        label: 'ESRI Ocean Bathymetry',
      };
    }
    if (basemapStyle === 'carto-dark') {
      return {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        label: 'CartoDB Dark Matter',
      };
    }
    // Default: ESRI World Dark Gray Canvas
    return {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
      attribution: '&copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      label: 'ESRI Dark Scientific',
    };
  };

  const currentTile = getTileConfig();

  return (
    <div className="relative flex flex-col h-full rounded-xl border border-zinc-800 bg-[#0c0d12] p-4 shadow-xl select-none">
      {/* 1. Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between border-b border-zinc-800/80 pb-3 mb-2 gap-2">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-zinc-100">
            North Indian Ocean Interactive Map
          </h3>
          <span className="text-[10px] bg-cyan-950/70 border border-cyan-800/60 text-cyan-300 px-2 py-0.5 rounded font-mono flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-cyan-400" />
            {currentTile.label}
          </span>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-2 text-xs">
          {/* Basemap Tile Switcher */}
          <select
            value={basemapStyle}
            onChange={(e) => setBasemapStyle(e.target.value as any)}
            className="rounded-md border border-cyan-800/60 bg-[#090b14] px-2.5 py-1 text-[11px] text-cyan-200 outline-none cursor-pointer hover:border-cyan-600 font-mono"
            title="Switch Scientific Basemap Layer"
          >
            <option value="esri-dark">ESRI Dark Scientific (Default)</option>
            <option value="esri-ocean">ESRI Ocean Bathymetry</option>
            <option value="carto-dark">CartoDB Dark Matter</option>
            <option value="maptiler">
              MapTiler Dark {apiKey ? '(Key Active)' : '(Custom Key)'}
            </option>
          </select>
          {/* Quick Basin Jumper */}
          <select
            value={selectedBasinFilter}
            onChange={(e) => {
              setSelectedBasinFilter(e.target.value);
              if (e.target.value === 'arabian_sea') {
                setMapCenter([16.5, 66.0]);
                setMapZoom(6);
                onSelectRegion('arabian-sea');
              } else if (e.target.value === 'bay_of_bengal') {
                setMapCenter([14.5, 87.0]);
                setMapZoom(6);
                onSelectRegion('bay-of-bengal');
              } else {
                setMapCenter(initialCenter);
                setMapZoom(initialZoom);
              }
            }}
            className="rounded-md border border-zinc-800 bg-zinc-900/90 px-2.5 py-1 text-[11px] text-zinc-200 outline-none cursor-pointer hover:border-zinc-700"
          >
            <option value="all">All Basins (Overview)</option>
            <option value="arabian_sea">Arabian Sea</option>
            <option value="bay_of_bengal">Bay of Bengal</option>
          </select>

          {/* Toggle Floats */}
          <button
            onClick={() => setShowFloats(!showFloats)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] border transition-all ${
              showFloats
                ? 'bg-cyan-950/80 border-cyan-700/60 text-cyan-300'
                : 'bg-zinc-900/80 border-zinc-800 text-zinc-400'
            }`}
          >
            <Radio className="h-3 w-3 text-cyan-400" />
            <span>Argo Floats ({loadingFloats ? '...' : argoProfiles.length})</span>
          </button>

          {/* Reset View */}
          <button
            onClick={() => {
              setMapCenter(initialCenter);
              setMapZoom(initialZoom);
              setClickedLocation(null);
            }}
            title="Reset Map View"
            className="flex items-center gap-1 p-1.5 rounded-md border border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:text-zinc-100 hover:border-zinc-700"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>

          {/* MapTiler Key Config Button */}
          <button
            onClick={() => setShowKeyDialog(!showKeyDialog)}
            title="Configure MapTiler API Key"
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] border ${
              apiKey
                ? 'border-emerald-800/60 bg-emerald-950/40 text-emerald-300'
                : 'border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Key className="h-3 w-3" />
            <span>{apiKey ? 'API Key Set' : 'Set Key'}</span>
          </button>
        </div>
      </div>

      {/* API Key Modal / Banner */}
      {showKeyDialog && (
        <div className="mb-3 rounded-lg border border-cyan-500/50 bg-[#090a12] p-3 text-xs shadow-2xl">
          <div className="flex items-center justify-between mb-1.5">
            <span className="font-semibold text-zinc-100 flex items-center gap-1.5">
              <Key className="h-3.5 w-3.5 text-cyan-400" />
              Configure MapTiler API Key
            </span>
            <button
              onClick={() => setShowKeyDialog(false)}
              className="text-zinc-400 hover:text-zinc-100"
            >
              ✕
            </button>
          </div>
          <p className="text-[11px] text-zinc-400 mb-2 leading-relaxed">
            MapTiler provides high-resolution dark scientific bathymetry tiles. You can also persist
            your key in <code className="text-cyan-300">frontend/.env</code> under{' '}
            <code className="text-cyan-300">VITE_MAPTILER_API_KEY</code>.
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Paste your MapTiler API key here..."
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              className="flex-1 rounded border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-xs font-mono text-zinc-100 outline-none focus:border-cyan-400"
            />
            <button
              onClick={() => {
                if (keyInput.trim()) {
                  setApiKey(keyInput.trim());
                  setTileError(false);
                  setShowKeyDialog(false);
                }
              }}
              className="rounded bg-cyan-600 px-3 py-1 font-medium text-white hover:bg-cyan-500 text-xs"
            >
              Apply Key
            </button>
          </div>
        </div>
      )}

      {/* 2. Interactive Leaflet Map Canvas */}
      <div className="relative flex-1 min-h-[500px] w-full rounded-lg bg-[#07080c] border border-zinc-800/80 overflow-hidden">
        <MapContainer
          center={initialCenter}
          zoom={initialZoom}
          minZoom={4}
          maxZoom={12}
          maxBounds={[
            [-5.0, 48.0],
            [30.0, 102.0],
          ]}
          className="h-full w-full"
          scrollWheelZoom={true}
        >
          <MapController center={mapCenter} zoom={mapZoom} />
          <MapEventsHandler
            onMapClick={handleMapClick}
            onMouseMove={(lat, lon) => setHoverCoords({ lat, lon })}
          />

          {/* Leaflet TileLayer */}
          <TileLayer
            key={currentTile.url}
            url={currentTile.url}
            attribution={currentTile.attribution}
            eventHandlers={{
              tileerror: () => {
                if (basemapStyle === 'maptiler') {
                  setTileError(true);
                  setBasemapStyle('esri-dark');
                }
              },
            }}
          />

          {/* Render In-Situ Argo Float Markers */}
          {showFloats &&
            visibleProfiles.map((flt) => {
              const isSelected = selectedFloat?.profile_id === flt.profile_id;
              return (
                <Marker
                  key={flt.profile_id}
                  position={[flt.latitude, flt.longitude]}
                  icon={createArgoMarkerIcon(isSelected)}
                  eventHandlers={{
                    click: () => handleInspectArgoFloat(flt),
                  }}
                >
                  <Popup>
                    <div className="p-3 font-sans">
                      <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-2">
                        <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-xs">
                          <Radio className="h-3.5 w-3.5" />
                          <span>Argo Float #{flt.float_wmo}</span>
                        </div>
                        <span className="text-[10px] font-mono bg-zinc-800 text-zinc-300 px-1.5 py-0.5 rounded">
                          Cycle {flt.cycle_number}
                        </span>
                      </div>

                      <div className="space-y-1 text-[11px] text-zinc-300 font-mono">
                        <div>
                          <span className="text-zinc-400">Date:</span> {flt.date}
                        </div>
                        <div>
                          <span className="text-zinc-400">Position:</span>{' '}
                          {flt.latitude.toFixed(3)}°N, {flt.longitude.toFixed(3)}°E
                        </div>
                        <div>
                          <span className="text-zinc-400">Basin:</span>{' '}
                          {flt.basin.replace('_', ' ')}
                        </div>
                        <div className="mt-2 pt-2 border-t border-zinc-800 grid grid-cols-2 gap-2 text-[10.5px]">
                          <div>
                            <span className="text-zinc-400 block text-[9px] uppercase">In-Situ SST</span>
                            <span className="text-cyan-300 font-bold">
                              {flt.surface_temp ? `${flt.surface_temp.toFixed(2)}°C` : 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-zinc-400 block text-[9px] uppercase">Thermocline (100m)</span>
                            <span className="text-emerald-400 font-bold">
                              {flt.thermocline_temp_100m
                                ? `${flt.thermocline_temp_100m.toFixed(2)}°C`
                                : 'N/A'}
                            </span>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => handleInspectArgoFloat(flt)}
                        className="mt-3 w-full rounded-md bg-cyan-950 border border-cyan-600/70 py-1.5 text-center text-xs font-semibold text-cyan-300 hover:bg-cyan-900 transition-colors"
                      >
                        Load Full In-Situ Profile →
                      </button>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

          {/* Render Clicked Ocean Location Marker */}
          {clickedLocation && (
            <Marker
              position={[clickedLocation.lat, clickedLocation.lon]}
              icon={createTargetMarkerIcon()}
            >
              <Popup autoPan={true}>
                <div className="p-3.5 font-sans min-w-[260px]">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-2">
                    <span className="font-semibold text-rose-400 text-xs flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5" />
                      Ocean Sounding Target
                    </span>
                    <span className="text-[10px] font-mono text-zinc-400">
                      {clickedLocation.lat.toFixed(3)}°N, {clickedLocation.lon.toFixed(3)}°E
                    </span>
                  </div>

                  {clickedLocation.loading ? (
                    <div className="py-4 flex flex-col items-center justify-center gap-2 text-zinc-400 text-xs">
                      <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                      <span>Reconstructing subsurface temperature...</span>
                    </div>
                  ) : clickedLocation.error ? (
                    <div className="py-2.5 px-3 rounded-lg bg-amber-950/80 border border-amber-800/90 text-[11px] text-amber-200 leading-snug flex items-start gap-2 shadow-inner">
                      <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-amber-300 block mb-0.5">Ocean Prediction Unavailable</span>
                        <span>{clickedLocation.error}</span>
                      </div>
                    </div>
                  ) : clickedLocation.prediction ? (
                    <div className="space-y-2 text-[11px]">
                      {/* Physical Layers Summary */}
                      <div className="grid grid-cols-2 gap-2 bg-zinc-900/90 border border-zinc-800 rounded p-2 text-zinc-300 font-mono">
                        <div>
                          <span className="text-[9px] text-zinc-400 uppercase block">Surface SST</span>
                          <span className="text-cyan-300 font-bold text-xs">
                            {clickedLocation.prediction.kpis.surfaceTemp.toFixed(2)}°C
                          </span>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-400 uppercase block">Thermocline</span>
                          <span className="text-emerald-400 font-bold text-xs">
                            {clickedLocation.prediction.kpis.thermoclineDepth}m
                          </span>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-400 uppercase block">Mixed Layer</span>
                          <span className="text-zinc-200">
                            {clickedLocation.prediction.kpis.mld}m
                          </span>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-400 uppercase block">Deep (1000m)</span>
                          <span className="text-cyan-200">
                            {clickedLocation.prediction.kpis.targetDepthTemp.toFixed(2)}°C
                          </span>
                        </div>
                      </div>

                      <div className="text-[10px] text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Physics-grounded 20-level prediction synchronized with chart</span>
                      </div>
                    </div>
                  ) : null}
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>

        {/* Floating Real-Time Hover Coordinate HUD */}
        <div className="absolute bottom-2 left-2 z-[400] flex items-center gap-2 bg-[#090a12]/90 border border-zinc-800 px-3 py-1.5 rounded-md text-[11px] font-mono text-zinc-400 shadow-xl pointer-events-none">
          <span className="text-cyan-400">Position:</span>
          {hoverCoords ? (
            <span className="flex items-center gap-1.5">
              <span>{hoverCoords.lat.toFixed(3)}°N, {hoverCoords.lon.toFixed(3)}°E</span>
              <span className="text-zinc-600">•</span>
              <span
                className={
                  checkIsOcean(hoverCoords.lat, hoverCoords.lon).isOcean
                    ? 'text-emerald-400 font-semibold'
                    : 'text-amber-400 font-semibold'
                }
              >
                {checkIsOcean(hoverCoords.lat, hoverCoords.lon).isOcean
                  ? 'Ocean'
                  : 'Land (Excluded)'}
              </span>
            </span>
          ) : (
            <span>Hover over map</span>
          )}
          <span className="text-zinc-600">|</span>
          <span className="text-zinc-300">Click anywhere to sound</span>
        </div>

        {/* Floating Quick Region Badges */}
        <div className="absolute top-2 right-2 z-[400] flex flex-col gap-1.5 pointer-events-auto">
          {regions.map((reg) => {
            const isSelected = selectedRegionId === reg.id;
            return (
              <button
                key={reg.id}
                onClick={() => {
                  onSelectRegion(reg.id);
                  setMapCenter([reg.lat, reg.lon]);
                  setMapZoom(6);
                }}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition-all text-left flex items-center justify-between gap-2 backdrop-blur-md ${
                  isSelected
                    ? 'bg-cyan-950/95 text-cyan-300 border border-cyan-500/80 shadow-md'
                    : 'bg-[#090a12]/85 text-zinc-300 border border-zinc-800 hover:text-white hover:border-zinc-700'
                }`}
              >
                <span>{reg.name}</span>
                <span className="font-mono text-[10px] text-cyan-400">{reg.baseSst}°C</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default OceanMap;
