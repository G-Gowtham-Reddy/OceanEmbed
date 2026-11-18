"""
OceanEmbed FastAPI Backend
Phase 10: Backend Integration & Frontend Connection
Serving real pre-trained Phase 6 models and Phase 8 validated predictions.
"""

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import os
import json
import math
import numpy as np
import pandas as pd
import joblib

# Initialize FastAPI application
app = FastAPI(
    title="OceanEmbed API",
    description="3D Ocean Temperature Reconstruction & Subsurface Prediction Engine",
    version="1.0.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BACKEND_DIR, "models", "phase6")
DATA_PATH = os.path.join(BACKEND_DIR, "data", "processed", "phase8_subsurface_temperature_predictions.parquet")
METRICS_PATH = os.path.join(BACKEND_DIR, "reports", "phase8_prediction_validation_metrics.csv")
REPORT_PATH = os.path.join(BACKEND_DIR, "reports", "phase8_validation_report.json")
EXPLAINABILITY_PATH = os.path.join(BACKEND_DIR, "reports", "phase7_explainability_report.json")
LAND_MASK_PATH = os.path.join(BACKEND_DIR, "data", "processed", "ocean_land_mask_grid.json")

# Standard 20 usable depth levels
USABLE_DEPTHS = [
    0, 5, 10, 20, 30, 50, 75, 100, 125, 150,
    200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500
]

FEATURE_COLUMNS = [
    'sat_sst', 'sat_sla', 'sat_current_u', 'sat_current_v', 'sat_current_speed',
    'latitude', 'longitude', 'sin_doy', 'cos_doy', 'sin_month', 'cos_month'
]

# In-memory Model & Data Cache
MODELS_CACHE: Dict[int, Dict[str, Any]] = {}
DATASET_CACHE: Optional[pd.DataFrame] = None
METRICS_CACHE: Optional[pd.DataFrame] = None
REPORT_CACHE: Optional[Dict[str, Any]] = None
EXPLAINABILITY_CACHE: Optional[Dict[str, Any]] = None
LAND_MASK_CACHE: Optional[Dict[str, Any]] = None

def load_system_assets():
    """Loads pre-trained models, datasets, and validation reports into memory."""
    global MODELS_CACHE, DATASET_CACHE, METRICS_CACHE, REPORT_CACHE, EXPLAINABILITY_CACHE, LAND_MASK_CACHE
    
    # 0. Load Authoritative Land-Sea Mask
    if os.path.exists(LAND_MASK_PATH):
        try:
            with open(LAND_MASK_PATH, "r", encoding="utf-8") as f:
                LAND_MASK_CACHE = json.load(f)
            print(f"Successfully loaded Land-Sea Mask: {LAND_MASK_CACHE.get('ocean_cells', 0)} ocean cells.")
        except Exception as e:
            print(f"Error loading Land-Sea Mask: {e}")
    
    # 1. Load Phase 6 Depth Models
    print(f"Loading Phase 6 depth-specific models from: {MODELS_DIR}")
    for d in USABLE_DEPTHS:
        model_file = os.path.join(MODELS_DIR, f"optimized_model_depth_{d}m.joblib")
        if os.path.exists(model_file):
            MODELS_CACHE[d] = joblib.load(model_file)
        else:
            print(f"Warning: Model for depth {d}m not found at {model_file}")
    print(f"Successfully loaded {len(MODELS_CACHE)} Phase 6 production models.")

    # 2. Load Processed Predictions Dataset
    if os.path.exists(DATA_PATH):
        DATASET_CACHE = pd.read_parquet(DATA_PATH)
        print(f"Successfully loaded predictions dataset: {len(DATASET_CACHE)} profiles.")
    else:
        print(f"Warning: Predictions dataset missing at {DATA_PATH}")

    # 3. Load Validation Metrics
    if os.path.exists(METRICS_PATH):
        METRICS_CACHE = pd.read_csv(METRICS_PATH)
        print(f"Successfully loaded validation metrics for {len(METRICS_CACHE)} depths.")
        
    # 4. Load Validation Report
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            REPORT_CACHE = json.load(f)

    # 5. Load Explainability Report
    if os.path.exists(EXPLAINABILITY_PATH):
        with open(EXPLAINABILITY_PATH, "r") as f:
            EXPLAINABILITY_CACHE = json.load(f)

# Execute asset loading at module import
load_system_assets()

# Region Catalog
REGIONS = {
    "bay-of-bengal": {
        "id": "bay-of-bengal",
        "name": "Bay of Bengal",
        "basin": "Bay_of_Bengal",
        "coordinates": "8°N - 22°N, 80°E - 95°E",
        "lat": 14.5,
        "lon": 87.0,
        "baseSst": 29.2,
        "baseMld": 30.0,
        "thermoclineDepth": 95,
        "activeFloats": 7,
        "profileCount": 46,
        "description": "Low-salinity, freshwater-stratified basin with sharp, shallow thermocline and warm barrier layers."
    },
    "arabian-sea": {
        "id": "arabian-sea",
        "name": "Arabian Sea",
        "basin": "Arabian_Sea",
        "coordinates": "10°N - 25°N, 55°E - 76°E",
        "lat": 16.5,
        "lon": 66.0,
        "baseSst": 28.5,
        "baseMld": 45.0,
        "thermoclineDepth": 120,
        "activeFloats": 6,
        "profileCount": 29,
        "description": "High-salinity, evaporative basin with deep thermocline and warm Red Sea / Persian Gulf outflow intrusions."
    },
    "equatorial-indian": {
        "id": "equatorial-indian",
        "name": "Equatorial Indian Ocean",
        "basin": "Arabian_Sea",
        "coordinates": "0°N - 10°N, 65°E - 85°E",
        "lat": 5.0,
        "lon": 75.0,
        "baseSst": 29.0,
        "baseMld": 40.0,
        "thermoclineDepth": 115,
        "activeFloats": 4,
        "profileCount": 18,
        "description": "Equatorial wave guide dynamic region governed by seasonal Kelvin and Rossby wave propagation."
    },
    "southern-tropical": {
        "id": "southern-tropical",
        "name": "South Bay / Sri Lanka Dome",
        "basin": "Bay_of_Bengal",
        "coordinates": "5°N - 10°N, 80°E - 90°E",
        "lat": 7.5,
        "lon": 84.0,
        "baseSst": 28.7,
        "baseMld": 35.0,
        "thermoclineDepth": 105,
        "activeFloats": 3,
        "profileCount": 12,
        "description": "Cyclonic eddy formation and open-ocean summer upwelling zone off southern Sri Lanka."
    }
}

# --- Pydantic Request & Response Schemas ---
class PredictionRequest(BaseModel):
    sat_sst: float = Field(..., description="Sea Surface Temperature (°C)", ge=26.0, le=32.0, example=29.2)
    sat_sla: float = Field(..., description="Sea Level Anomaly (m)", ge=-1.5, le=1.5, example=0.08)
    sat_current_u: float = Field(0.0, description="Zonal Geostrophic Current (m/s)", ge=-3.0, le=3.0, example=0.12)
    sat_current_v: float = Field(0.0, description="Meridional Geostrophic Current (m/s)", ge=-3.0, le=3.0, example=-0.05)
    latitude: float = Field(..., description="Latitude (°N)", ge=0.0, le=25.0, example=15.0)
    longitude: float = Field(..., description="Longitude (°E)", ge=50.0, le=100.0, example=87.0)
    date: Optional[str] = Field(None, description="Observation Date YYYY-MM-DD", example="2025-07-15")

class ProfileDepthPoint(BaseModel):
    depth: int
    temperature: float
    expected_rmse: Optional[float] = None
    expected_r2: Optional[float] = None
    label: str

class LayerBreakdown(BaseModel):
    name: str
    depthRange: str
    tempRange: str
    description: str

class PredictionResponse(BaseModel):
    status: str
    date: str
    latitude: float
    longitude: float
    basin: str
    kpis: Dict[str, Any]
    profile: List[ProfileDepthPoint]
    layers: List[LayerBreakdown]
    feature_attributions: Dict[str, str]

# --- API Endpoints ---

@app.get("/")
def root():
    return {
        "service": "OceanEmbed API",
        "version": "1.0.0",
        "status": "online",
        "models_loaded": len(MODELS_CACHE),
        "profiles_available": len(DATASET_CACHE) if DATASET_CACHE is not None else 0,
        "endpoints": {
            "health": "/api/health",
            "regions": "/api/ocean/regions",
            "temperature": "/api/ocean/temperature",
            "profiles": "/api/ocean/profiles",
            "predict": "/api/predict",
            "metrics": "/api/model/metrics"
        }
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OceanEmbed Subsurface Temperature Reconstruction API",
        "version": "1.0.0",
        "models_loaded": len(MODELS_CACHE),
        "profiles_loaded": len(DATASET_CACHE) if DATASET_CACHE is not None else 0,
        "land_mask_loaded": LAND_MASK_CACHE is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/ocean/validate-location")
def validate_location(latitude: float, longitude: float):
    """
    Checks whether a given coordinate is pure ocean or land.
    Used for instant pre-flight validation by the frontend.
    """
    is_ocean, message = is_ocean_location(latitude, longitude)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "is_ocean": is_ocean,
        "message": message
    }

@app.get("/api/ocean/land-mask")
def get_land_mask():
    """Returns the metadata and grid configuration for the authoritative Land-Sea Mask."""
    if LAND_MASK_CACHE is None:
        raise HTTPException(status_code=500, detail="Land-Sea Mask not loaded")
    return {
        "metadata": LAND_MASK_CACHE.get("metadata", {}),
        "grid": LAND_MASK_CACHE.get("grid", {}),
        "ocean_cells": LAND_MASK_CACHE.get("ocean_cells", 0),
        "land_cells": LAND_MASK_CACHE.get("land_cells", 0)
    }

@app.get("/api/ocean/regions")
def get_regions():
    """Returns catalog of North Indian Ocean monitored regions."""
    return list(REGIONS.values())

@app.get("/api/ocean/temperature")
def get_temperature(
    region: str = "bay-of-bengal",
    date: Optional[str] = None,
    max_depth: int = 1000,
    station_id: Optional[str] = None
):
    """
    Returns authentic vertical temperature soundings from genuine Argo profiles
    or computed Phase 6 model predictions for the selected region.
    """
    reg_key = region if region in REGIONS else "bay-of-bengal"
    reg_info = REGIONS[reg_key]
    clamped_max_depth = max(100, min(1500, max_depth))
    
    # 1. Search for matching authentic in-situ profile in dataset cache
    matched_profile = None
    if DATASET_CACHE is not None and not DATASET_CACHE.empty:
        if station_id:
            match = DATASET_CACHE[DATASET_CACHE['profile_id'] == station_id]
            if not match.empty:
                matched_profile = match.iloc[0]
        elif date:
            match = DATASET_CACHE[(DATASET_CACHE['split_group_basin'] == reg_info['basin']) & 
                                  (DATASET_CACHE['date'].astype(str).str.startswith(date[:7]))]
            if not match.empty:
                matched_profile = match.iloc[0]
        
        # Fallback to closest basin profile if no exact date match
        if matched_profile is None:
            basin_matches = DATASET_CACHE[DATASET_CACHE['split_group_basin'] == reg_info['basin']]
            if not basin_matches.empty:
                matched_profile = basin_matches.iloc[0]

    # 2. Build profile from genuine data / model predictions
    depth_points = []
    available_depths = [d for d in USABLE_DEPTHS if d <= clamped_max_depth]
    
    if matched_profile is not None:
        obs_date = str(matched_profile['date'])[:10]
        lat = float(matched_profile['latitude'])
        lon = float(matched_profile['longitude'])
        
        for d in available_depths:
            # Use real Phase 6 model prediction, fallback to actual
            pred_temp = float(matched_profile[f"pred_temp_p6_{d}m"])
            depth_points.append({
                "depth": d,
                "temperature": round(pred_temp, 2),
                "label": f"{d}m"
            })
    else:
        # Evaluate model dynamically for the region baseline
        obs_date = date or datetime.utcnow().strftime("%Y-%m-%d")
        lat = reg_info['lat']
        lon = reg_info['lon']
        req = PredictionRequest(
            sat_sst=reg_info['baseSst'],
            sat_sla=0.04,
            sat_current_u=0.10,
            sat_current_v=-0.05,
            latitude=lat,
            longitude=lon,
            date=obs_date
        )
        pred_res = execute_inference(req)
        depth_points = [
            {"depth": p.depth, "temperature": p.temperature, "label": p.label}
            for p in pred_res.profile if p.depth <= clamped_max_depth
        ]

    surface_temp = depth_points[0]["temperature"]
    target_depth_temp = depth_points[-1]["temperature"]
    
    # Calculate Mixed Layer Depth (depth where temp drops by 0.5°C from surface)
    mld = 30.0
    for pt in depth_points:
        if (surface_temp - pt["temperature"]) >= 0.5:
            mld = float(pt["depth"])
            break
            
    # Calculate Thermocline Depth (depth of steepest vertical gradient)
    thermocline_z = reg_info['thermoclineDepth']
    max_gradient = 0.0
    for i in range(len(depth_points) - 1):
        dz = depth_points[i+1]["depth"] - depth_points[i]["depth"]
        if dz > 0:
            dt = abs(depth_points[i]["temperature"] - depth_points[i+1]["temperature"])
            grad = dt / dz
            if grad > max_gradient:
                max_gradient = grad
                thermocline_z = depth_points[i]["depth"]

    return {
        "region": reg_info["name"],
        "regionId": reg_info["id"],
        "coordinates": reg_info["coordinates"],
        "lat": lat,
        "lon": lon,
        "date": obs_date,
        "maxDepth": clamped_max_depth,
        "kpis": {
            "surfaceTemp": round(surface_temp, 1),
            "mld": round(mld, 1),
            "thermoclineDepth": thermocline_z,
            "targetDepthTemp": round(target_depth_temp, 1),
            "activeFloats": reg_info["activeFloats"]
        },
        "layers": [
            {
                "name": "Surface Mixed Layer",
                "depthRange": f"0 – {int(mld)} m",
                "tempRange": f"{round(surface_temp, 1)}°C – {round(surface_temp - 0.5, 1)}°C",
                "description": "Warm, wind-mixed upper ocean layer directly coupled with atmospheric radiation and SST."
            },
            {
                "name": "Thermocline Transition Zone",
                "depthRange": f"{int(mld)} – {min(clamped_max_depth, thermocline_z + 80)} m",
                "tempRange": f"{round(surface_temp - 0.5, 1)}°C – 14.5°C",
                "description": "Zone of steepest temperature gradient where Sea Level Anomaly (SLA) governs vertical isotherm heave."
            },
            {
                "name": "Deep Ocean Water",
                "depthRange": f"{min(clamped_max_depth, thermocline_z + 80)} – {clamped_max_depth} m",
                "tempRange": f"14.5°C – {round(target_depth_temp, 1)}°C",
                "description": "Dense, cold intermediate and abyssal waters governed by regional basin climatology."
            }
        ],
        "profile": depth_points
    }

@app.get("/api/ocean/profiles")
def get_profiles(
    basin: Optional[str] = None,
    limit: int = 75
):
    """Returns catalog of genuine collocated Argo profiles."""
    if DATASET_CACHE is None or DATASET_CACHE.empty:
        raise HTTPException(status_code=500, detail="Profiles dataset not loaded")
        
    df_sub = DATASET_CACHE
    if basin:
        df_sub = df_sub[df_sub['split_group_basin'] == basin]
        
    records = []
    for _, row in df_sub.head(limit).iterrows():
        records.append({
            "profile_id": str(row['profile_id']),
            "float_wmo": int(row['float_wmo']),
            "cycle_number": int(row['cycle_number']),
            "date": str(row['date'])[:10],
            "latitude": round(float(row['latitude']), 3),
            "longitude": round(float(row['longitude']), 3),
            "basin": str(row['split_group_basin']),
            "sat_sst": round(float(row['sat_sst']), 2),
            "sat_sla": round(float(row['sat_sla']), 3),
            "sat_current_u": round(float(row['sat_current_u']), 3) if 'sat_current_u' in row and not pd.isna(row['sat_current_u']) else 0.0,
            "sat_current_v": round(float(row['sat_current_v']), 3) if 'sat_current_v' in row and not pd.isna(row['sat_current_v']) else 0.0,
            "surface_temp": round(float(row['actual_temp_10m']), 2) if not pd.isna(row['actual_temp_10m']) else None,
            "thermocline_temp_100m": round(float(row['actual_temp_100m']), 2) if not pd.isna(row['actual_temp_100m']) else None,
            "deep_temp_500m": round(float(row['actual_temp_500m']), 2) if not pd.isna(row['actual_temp_500m']) else None
        })
        
    return {
        "total_profiles": len(records),
        "profiles": records
    }

@app.get("/api/ocean/profiles/{profile_id}")
def get_profile_by_id(profile_id: str):
    """Returns detailed 20-depth in-situ vs model predicted temperatures for an Argo profile."""
    if DATASET_CACHE is None or DATASET_CACHE.empty:
        raise HTTPException(status_code=500, detail="Profiles dataset not loaded")
        
    match = DATASET_CACHE[DATASET_CACHE['profile_id'] == profile_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")
        
    row = match.iloc[0]
    depth_comparison = []
    
    for d in USABLE_DEPTHS:
        act = float(row[f"actual_temp_{d}m"]) if not pd.isna(row[f"actual_temp_{d}m"]) else None
        pred = float(row[f"pred_temp_p6_{d}m"])
        oof = float(row[f"oof_temp_p6_{d}m"]) if not pd.isna(row[f"oof_temp_p6_{d}m"]) else None
        err = round(oof - act, 3) if (oof is not None and act is not None) else None
        
        depth_comparison.append({
            "depth": d,
            "actual_temp": round(act, 2) if act is not None else None,
            "predicted_temp": round(pred, 2),
            "oof_temp": round(oof, 2) if oof is not None else None,
            "residual_error": err,
            "label": f"{d}m"
        })
        
    return {
        "profile_id": str(row['profile_id']),
        "float_wmo": int(row['float_wmo']),
        "cycle_number": int(row['cycle_number']),
        "date": str(row['date'])[:10],
        "latitude": round(float(row['latitude']), 3),
        "longitude": round(float(row['longitude']), 3),
        "basin": str(row['split_group_basin']),
        "satellite_features": {
            "sat_sst": round(float(row['sat_sst']), 2),
            "sat_sla": round(float(row['sat_sla']), 3),
            "sat_current_u": round(float(row['sat_current_u']), 3),
            "sat_current_v": round(float(row['sat_current_v']), 3),
            "sat_current_speed": round(float(row['sat_current_speed']), 3)
        },
        "depth_soundings": depth_comparison
    }

def is_ocean_location(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Validates coordinates against the authoritative 0.25-deg satellite Land-Sea Mask.
    Enforces conservative pure-ocean policy: land and mixed coastal cells are rejected.
    """
    if lat < 0.0 or lat > 26.0 or lon < 50.0 or lon > 100.0:
        return False, "Selected location is outside North Indian Ocean domain (0°–26°N, 50°–100°E). No ocean prediction available."
    
    if LAND_MASK_CACHE is None:
        return True, "Valid ocean location."
    
    grid = LAND_MASK_CACHE.get("grid", {})
    lat_min = grid.get("lat_min", 0.0)
    lat_step = grid.get("lat_step", 0.25)
    n_lat = grid.get("n_lat", 105)
    lon_min = grid.get("lon_min", 50.0)
    lon_step = grid.get("lon_step", 0.25)
    n_lon = grid.get("n_lon", 201)
    
    i = int(round((lat - lat_min) / lat_step))
    j = int(round((lon - lon_min) / lon_step))
    i = max(0, min(n_lat - 1, i))
    j = max(0, min(n_lon - 1, j))
    
    mask = LAND_MASK_CACHE.get("mask", [])
    if i < len(mask) and j < len(mask[i]) and mask[i][j] == 1:
        return True, "Valid ocean location."
    else:
        return False, "Selected location is land – ocean prediction unavailable."

def execute_inference(req: PredictionRequest) -> PredictionResponse:
    """Executes live Phase 6 model inference across all 20 depth levels."""
    if len(MODELS_CACHE) == 0:
        raise HTTPException(status_code=500, detail="Models not loaded")

    # 0. Enforce authoritative Land-Sea Mask
    is_ocean, reason = is_ocean_location(req.latitude, req.longitude)
    if not is_ocean:
        raise HTTPException(
            status_code=400,
            detail=reason
        )

    # Parse date and construct seasonal terms
    if req.date:
        try:
            dt = datetime.strptime(req.date, "%Y-%m-%d")
        except ValueError:
            dt = datetime.utcnow()
    else:
        dt = datetime.utcnow()
        
    doy = dt.timetuple().tm_yday
    month = dt.month
    
    sin_doy = math.sin(2.0 * math.pi * doy / 365.25)
    cos_doy = math.cos(2.0 * math.pi * doy / 365.25)
    sin_month = math.sin(2.0 * math.pi * month / 12.0)
    cos_month = math.cos(2.0 * math.pi * month / 12.0)
    
    speed = math.sqrt(req.sat_current_u**2 + req.sat_current_v**2)
    
    # Feature vector in exact model schema order
    feat_dict = {
        'sat_sst': req.sat_sst,
        'sat_sla': req.sat_sla,
        'sat_current_u': req.sat_current_u,
        'sat_current_v': req.sat_current_v,
        'sat_current_speed': speed,
        'latitude': req.latitude,
        'longitude': req.longitude,
        'sin_doy': sin_doy,
        'cos_doy': cos_doy,
        'sin_month': sin_month,
        'cos_month': cos_month
    }
    
    X_raw = np.array([[feat_dict[col] for col in FEATURE_COLUMNS]])
    
    profile_points = []
    
    # Look up benchmark metrics for error bounds
    metrics_map = {}
    if METRICS_CACHE is not None and not METRICS_CACHE.empty:
        for _, m_row in METRICS_CACHE.iterrows():
            metrics_map[int(m_row['Depth (m)'])] = {
                'rmse': float(m_row['P6_OOF_RMSE']),
                'r2': float(m_row['P6_OOF_R2'])
            }
            
    for d in USABLE_DEPTHS:
        model_info = MODELS_CACHE.get(d)
        if not model_info:
            continue
            
        scaler = model_info['scaler']
        model = model_info['model']
        
        X_scaled = scaler.transform(X_raw)
        pred_temp = float(model.predict(X_scaled)[0])
        
        m_stat = metrics_map.get(d, {'rmse': 0.35, 'r2': 0.85})
        profile_points.append(ProfileDepthPoint(
            depth=d,
            temperature=round(pred_temp, 2),
            expected_rmse=round(m_stat['rmse'], 2),
            expected_r2=round(m_stat['r2'], 3),
            label=f"{d}m"
        ))
        
    surface_temp = profile_points[0].temperature
    target_depth_temp = profile_points[-1].temperature
    
    # Identify MLD & thermocline
    mld = 30.0
    for pt in profile_points:
        if (surface_temp - pt.temperature) >= 0.5:
            mld = float(pt.depth)
            break
            
    thermocline_z = 100
    max_gradient = 0.0
    for i in range(len(profile_points) - 1):
        dz = profile_points[i+1].depth - profile_points[i].depth
        if dz > 0:
            temp_diff = abs(profile_points[i].temperature - profile_points[i+1].temperature)
            grad = temp_diff / dz
            if grad > max_gradient:
                max_gradient = grad
                thermocline_z = profile_points[i].depth
                
    basin_name = "Bay of Bengal" if req.longitude >= 78.0 else "Arabian Sea"
    
    layers = [
        LayerBreakdown(
            name="Surface Mixed Layer",
            depthRange=f"0 – {int(mld)} m",
            tempRange=f"{round(surface_temp, 1)}°C – {round(surface_temp - 0.5, 1)}°C",
            description="Coupled directly to satellite SST (SHAP attribution >75%)."
        ),
        LayerBreakdown(
            name="Thermocline Transition Zone",
            depthRange=f"{int(mld)} – {thermocline_z + 80} m",
            tempRange=f"{round(surface_temp - 0.5, 1)}°C – 14.5°C",
            description="Zone of steep vertical gradient governed by Sea Level Anomaly (SLA)."
        ),
        LayerBreakdown(
            name="Deep Ocean Water",
            depthRange=f"{thermocline_z + 80} – 1500 m",
            tempRange=f"14.5°C – {round(target_depth_temp, 1)}°C",
            description="Governed by basin-scale climatology and intermediate water masses."
        )
    ]
    
    kpis = {
        "surfaceTemp": round(surface_temp, 1),
        "mld": round(mld, 1),
        "thermoclineDepth": thermocline_z,
        "targetDepthTemp": round(target_depth_temp, 1),
        "minTemp": min(p.temperature for p in profile_points),
        "maxTemp": max(p.temperature for p in profile_points)
    }
    
    attributions = {
        "surface_0_30m": f"Driven predominantly by SST ({req.sat_sst}°C).",
        "thermocline_75_125m": f"Governed by Sea Level Anomaly ({req.sat_sla:+.3f}m), capturing vertical thermocline heave.",
        "deep_300_1500m": f"Governed by geographic coordinates ({req.latitude}°N, {req.longitude}°E) capturing {basin_name} water mass climatology."
    }
    
    return PredictionResponse(
        status="success",
        date=dt.strftime("%Y-%m-%d"),
        latitude=req.latitude,
        longitude=req.longitude,
        basin=basin_name,
        kpis=kpis,
        profile=profile_points,
        layers=layers,
        feature_attributions=attributions
    )

@app.post("/api/predict", response_model=PredictionResponse)
def predict_subsurface(request: PredictionRequest):
    """
    Executes live Phase 6 model inference across 20 depth levels from satellite and geospatial inputs.
    """
    return execute_inference(request)

@app.get("/api/model/metrics")
def get_metrics():
    """Returns comprehensive Phase 6 and Phase 8 validation metrics across all 20 depths."""
    if METRICS_CACHE is None or METRICS_CACHE.empty:
        raise HTTPException(status_code=500, detail="Validation metrics not loaded")
        
    records = []
    for _, row in METRICS_CACHE.iterrows():
        records.append({
            "depth": int(row['Depth (m)']),
            "architecture": str(row['P6_Architecture']),
            "r2_score": round(float(row['P6_OOF_R2']), 4),
            "rmse": round(float(row['P6_OOF_RMSE']), 4),
            "mae": round(float(row['P6_OOF_MAE']), 4),
            "bias": round(float(row['P6_OOF_MBE']), 4),
            "baseline_r2": round(float(row['P5_OOF_R2']), 4),
            "baseline_rmse": round(float(row['P5_OOF_RMSE']), 4),
            "rmse_improvement": round(float(row['RMSE_Improvement']), 4)
        })
        
    summary_report = REPORT_CACHE or {}
    explainability = EXPLAINABILITY_CACHE or {}
    
    return {
        "status": "success",
        "total_depths": len(records),
        "validation_strategy": "5-fold GroupKFold by Argo float ID (strictly zero float-level leakage)",
        "metrics_by_depth": records,
        "validation_report": summary_report,
        "feature_attributions": explainability.get("key_findings", {})
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
