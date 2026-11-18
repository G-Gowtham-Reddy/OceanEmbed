"""
Build and execute the Phase 4 Preprocessing Jupyter Notebook using nbformat and ipykernel.
"""

import json
from pathlib import Path
import nbformat as nbf

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "01_phase4_data_preprocessing.ipynb"

# Create a new notebook
nb = nbf.v4.new_notebook()

# Metadata
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3 (.venv)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.14.0"
    }
}

cells = []

# Cell 1: Markdown Title & Abstract
cells.append(nbf.v4.new_markdown_cell("""# OceanEmbed: Phase 4 – Data Preprocessing Pipeline
**Project Code:** SIH26066 | **Focus:** 3D Ocean Temperature Reconstruction (North Indian Ocean)

This notebook implements the complete **Phase 4 Preprocessing & Collocation Pipeline**:
1. **Raw Argo Ingestion & Quality Control**: Ingests all 6 authentic North Indian Ocean Argo floats (`1902669`, `1902671`, `2902264`, `2902265`, `2902267`, `2902278`), filtering strictly with official Argo QC flags (`'1'` and `'2'`) and physical sanity bounds.
2. **Pressure to Depth Transformation**: Converts sea pressure ($P$ in decibars) to true physical depth ($z$ in metres) using the UNESCO / Saunders (1981) latitude-dependent gravity formula.
3. **Vertical Standardization**: Interpolates discrete, uneven in-situ vertical measurements onto **21 Standard Oceanographic Depth Levels** ($0\\text{ to } 2,000\\text{ m}$).
4. **2D Bilinear Satellite Collocation**: Collocates Sea Surface Temperature (SST), Sea Level Anomaly (SLA), and Geostrophic Surface Currents ($U$ and $V$) onto the exact spatial coordinates $(\\text{Lat}, \\text{Lon})$ of each profile.
5. **Multi-Tier Temporal Matching**: Categorizes samples across **Tier 0 (Exact)**, **Tier 1 (Synoptic $\\le 1\\text{d}$)**, **Tier 2 (Standard $\\le 3\\text{d}$)**, and **Tier 3 (Mesoscale $\\le 5\\text{d}$)**.
6. **Data Leakage Prevention**: Assigns float-stratified and temporal split groups (`split_group_wmo`) to prevent spatial/temporal leakage in downstream ML training.
7. **Dual-Format Export**: Saves the final processed dataset to both **CSV** (human inspectable) and **Parquet** (high-performance columnar format)."""))

# Cell 2: Imports & Environment Configuration
cells.append(nbf.v4.new_code_cell("""import os
import sys
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import RegularGridInterpolator, interp1d

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Define paths relative to the notebook directory
NOTEBOOK_DIR = Path.cwd()
PROJECT_ROOT = NOTEBOOK_DIR.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

print("Environment Paths:")
print(f"  Project Root:   {PROJECT_ROOT.resolve()}")
print(f"  Raw Data:       {DATA_RAW.resolve()}")
print(f"  Processed Data: {DATA_PROCESSED.resolve()}")"""))

# Cell 3: Markdown - Physics & Standard Depths
cells.append(nbf.v4.new_markdown_cell("""## 1. Physics Definitions & Standard Depth Levels

We standardize vertical temperature profiles onto **21 Oceanographic Standard Depth Levels** spanning from the surface ($0\\text{ m}$) down to the bathypelagic layer ($2,000\\text{ m}$):
- **Epipelagic Mixed Layer (0–100 m)**: High vertical density ($0, 5, 10, 20, 30, 50, 75, 100\\text{ m}$) to resolve diurnal solar heating and the mixed layer base.
- **Thermocline Transition Zone (100–500 m)**: Intermediate density ($125, 150, 200, 250, 300, 400, 500\\text{ m}$) to capture intense thermal gradients and internal wave dynamics.
- **Mesopelagic & Deep Ocean (500–2,000 m)**: Sparse density ($600, 750, 1000, 1250, 1500, 2000\\text{ m}$) where thermal stratification stabilizes.

### Pressure-to-Depth Conversion (Saunders 1981)
Sea pressure $P$ (dbar) is converted to depth $z$ (m) accounting for the latitude-dependent gravitational acceleration $g(\\phi)$:
$$g(\\phi) = 9.780318 \\times \\left(1 + 5.2788 \\times 10^{-3} \\sin^2\\phi + 2.36 \\times 10^{-5} \\sin^4\\phi\\right)$$
$$z(P, \\phi) = \\frac{1 - 1.25 \\times 10^{-5} P}{g(\\phi)} \\times \\frac{P \\times 10^4}{1025.0}$$"""))

# Cell 4: Code - Depth Conversion & Grid Definition
cells.append(nbf.v4.new_code_cell("""# 21 Standard Oceanographic Depth Levels (metres)
STANDARD_DEPTHS = np.array([
    0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0,
    125.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0,
    600.0, 750.0, 1000.0, 1250.0, 1500.0, 2000.0
], dtype=np.float64)

DEPTH_COLUMN_NAMES = [f"temp_depth_{int(d)}m" for d in STANDARD_DEPTHS]
SAL_COLUMN_NAMES = [f"sal_depth_{int(d)}m" for d in STANDARD_DEPTHS]


def pressure_to_depth_saunders(pressure_dbar: np.ndarray, latitude_deg: float) -> np.ndarray:
    \"\"\"Converts pressure (decibars) to physical depth (metres) via Saunders (1981).\"\"\"
    phi = np.radians(latitude_deg)
    sin2_phi = np.sin(phi) ** 2
    sin4_phi = np.sin(phi) ** 4
    g_phi = 9.780318 * (1.0 + 5.2788e-3 * sin2_phi + 2.36e-5 * sin4_phi)
    depth_m = ((1.0 - 1.25e-5 * pressure_dbar) / g_phi) * (pressure_dbar * 1e4 / 1025.0)
    return np.maximum(0.0, depth_m)


print(f"Target Depth Levels Count: {len(STANDARD_DEPTHS)}")
print("Standard Depths (m):", STANDARD_DEPTHS)
test_depth = pressure_to_depth_saunders(np.array([1000.0]), 15.0)[0]
print(f"Verification: 1000 dbar at 15°N -> {test_depth:.2f} metres")"""))

# Cell 5: Markdown - Argo Float QC & Ingestion
cells.append(nbf.v4.new_markdown_cell("""## 2. In-Situ Argo Ingestion & Quality Control Filtering

We load all 6 Argo float NetCDFs from `data/raw/argo/` and enforce strict scientific filtering:
1. **Flag Filtering**: Keep only measurements with `TEMP_QC` and `PRES_QC` in `['1', '2']` (Good or Probably Good).
2. **Physical Boundary Checks**:
   - $0 \\le \\text{Depth} \\le 2,500\\text{ m}$
   - $1.0 \\le \\text{Temperature} \\le 35.0^\\circ\\text{C}$
   - $15.0 \\le \\text{Salinity} \\le 42.0\\text{ PSU}$
3. **Vertical Monotonicity & Degeneracy**: Sort depth levels monotonically, remove duplicate depth readings, and discard profiles with fewer than 10 valid measurements.
4. **Vertical Interpolation**: Piecewise linear interpolation onto `STANDARD_DEPTHS`. Near-surface readings ($\\le 10\\text{ m}$) are constant-extrapolated to $0\\text{ m}$. Deep levels beyond the observed maximum depth remain `NaN` (no ungrounded extrapolation)."""))

# Cell 6: Code - Argo Ingestion Function
cells.append(nbf.v4.new_code_cell("""def process_single_argo_profile(
    pres_raw, temp_raw, psal_raw, temp_qc_raw, pres_qc_raw, lat, lon
):
    \"\"\"Applies QC filtering, converts pressure to depth, and interpolates to standard depths.\"\"\"
    # Decode string QC flags if bytes
    if hasattr(temp_qc_raw, 'decode'):
        t_qc = np.array([x.decode('utf-8', errors='ignore') for x in temp_qc_raw])
    else:
        t_qc = temp_qc_raw.astype(str)

    if hasattr(pres_qc_raw, 'decode'):
        p_qc = np.array([x.decode('utf-8', errors='ignore') for x in pres_qc_raw])
    else:
        p_qc = pres_qc_raw.astype(str)

    # Valid QC mask: '1' (good) or '2' (probably good)
    good_qc = np.isin(t_qc, ['1', '2']) & np.isin(p_qc, ['1', '2'])

    # Valid finite numbers
    finite_mask = (
        np.isfinite(pres_raw) & np.isfinite(temp_raw) &
        (pres_raw >= 0.0) & (pres_raw < 2500.0) &
        (temp_raw >= 1.0) & (temp_raw <= 35.0)
    )

    combined_mask = good_qc & finite_mask
    if combined_mask.sum() < 10:
        return None, None  # Degenerate or invalid profile

    valid_pres = pres_raw[combined_mask]
    valid_temp = temp_raw[combined_mask]

    # Convert pressure to true depth (metres)
    depths_m = pressure_to_depth_saunders(valid_pres, lat)

    # Sort monotonically by depth
    sort_idx = np.argsort(depths_m)
    depths_sorted = depths_m[sort_idx]
    temp_sorted = valid_temp[sort_idx]

    # Remove duplicates
    unique_depths, unique_indices = np.unique(depths_sorted, return_index=True)
    unique_temp = temp_sorted[unique_indices]

    if len(unique_depths) < 10:
        return None, None

    # Near-surface handling: if shallowest level is <= 10m, extrapolate to surface (0m)
    if unique_depths[0] <= 10.0 and unique_depths[0] > 0.0:
        unique_depths = np.insert(unique_depths, 0, 0.0)
        unique_temp = np.insert(unique_temp, 0, unique_temp[0])

    # Interpolate onto STANDARD_DEPTHS
    interp_fn = interp1d(
        unique_depths, unique_temp, kind='linear', bounds_error=False, fill_value=np.nan
    )
    temp_interp = interp_fn(STANDARD_DEPTHS)

    # Process salinity if present
    sal_interp = np.full(len(STANDARD_DEPTHS), np.nan)
    if psal_raw is not None:
        valid_psal = psal_raw[combined_mask]
        sal_mask = np.isfinite(valid_psal) & (valid_psal >= 15.0) & (valid_psal <= 42.0)
        if sal_mask.sum() >= 10:
            s_d = depths_m[sal_mask]
            s_v = valid_psal[sal_mask]
            s_sidx = np.argsort(s_d)
            s_du, s_u_idx = np.unique(s_d[s_sidx], return_index=True)
            s_vu = s_v[s_sidx][s_u_idx]
            if s_du[0] <= 10.0 and s_du[0] > 0.0:
                s_du = np.insert(s_du, 0, 0.0)
                s_vu = np.insert(s_vu, 0, s_vu[0])
            s_fn = interp1d(s_du, s_vu, kind='linear', bounds_error=False, fill_value=np.nan)
            sal_interp = s_fn(STANDARD_DEPTHS)

    return temp_interp, sal_interp"""))

# Cell 7: Markdown - Ingestion Execution
cells.append(nbf.v4.new_markdown_cell("""## 3. Ingestion & Quality Filtering of the Argo Library

We process all 6 NetCDF float files and extract standardized vertical profiles, observation timestamps, cycle numbers, and geographic coordinates."""))

# Cell 8: Code - Ingestion Loop
cells.append(nbf.v4.new_code_cell("""argo_files = sorted(list((DATA_RAW / "argo").glob("*_prof.nc")))
print(f"Scanning {len(argo_files)} Argo float files in {DATA_RAW / 'argo'}:\\n")

all_argo_records = []
total_raw_profiles = 0
total_valid_profiles = 0

for af in argo_files:
    wmo = af.name.split("_")[0]
    with xr.open_dataset(af) as ds:
        juld = pd.to_datetime(ds['JULD'].values)
        lats = ds['LATITUDE'].values
        lons = ds['LONGITUDE'].values
        cycles = ds['CYCLE_NUMBER'].values
        pres_all = ds['PRES'].values
        temp_all = ds['TEMP'].values
        psal_all = ds['PSAL'].values if 'PSAL' in ds else None
        temp_qc_all = ds['TEMP_QC'].values if 'TEMP_QC' in ds else np.full_like(temp_all, '1', dtype=str)
        pres_qc_all = ds['PRES_QC'].values if 'PRES_QC' in ds else np.full_like(pres_all, '1', dtype=str)

        file_raw = len(juld)
        file_valid = 0
        total_raw_profiles += file_raw

        for i in range(file_raw):
            dt = juld[i]
            lat = float(lats[i])
            lon = float(lons[i])

            # Check valid coordinates in North Indian Ocean (0-25°N, 50-100°E)
            if pd.isna(dt) or np.isnan(lat) or np.isnan(lon):
                continue
            if not (0.0 <= lat <= 25.0 and 50.0 <= lon <= 100.0):
                continue

            psal_row = psal_all[i] if psal_all is not None else None
            t_interp, s_interp = process_single_argo_profile(
                pres_all[i], temp_all[i], psal_row,
                temp_qc_all[i], pres_qc_all[i], lat, lon
            )

            if t_interp is not None:
                valid_levels_count = int(np.sum(~np.isnan(t_interp)))
                if valid_levels_count >= 8:  # At least 8 standard depth levels
                    rec = {
                        "float_wmo": str(wmo),
                        "cycle_number": int(cycles[i]),
                        "datetime": dt,
                        "date": dt.strftime("%Y-%m-%d"),
                        "time_utc": dt.strftime("%H:%M:%S"),
                        "latitude": round(lat, 4),
                        "longitude": round(lon, 4),
                        "day_of_year": int(dt.dayofyear),
                        "year": int(dt.year),
                        "month": int(dt.month),
                        "valid_standard_levels": valid_levels_count,
                    }
                    for idx, cname in enumerate(DEPTH_COLUMN_NAMES):
                        rec[cname] = round(float(t_interp[idx]), 3) if not np.isnan(t_interp[idx]) else np.nan
                    for idx, sname in enumerate(SAL_COLUMN_NAMES):
                        rec[sname] = round(float(s_interp[idx]), 3) if not np.isnan(s_interp[idx]) else np.nan

                    all_argo_records.append(rec)
                    file_valid += 1
                    total_valid_profiles += 1

        print(f"  Float {wmo}: {file_valid:>3}/{file_raw:<3} profiles passed QC ({round(file_valid/file_raw*100, 1)}%)")

df_argo = pd.DataFrame(all_argo_records)
print(f"\\nTotal Raw Profiles Scanned:    {total_raw_profiles}")
print(f"Total Valid QC Profiles Kept:  {total_valid_profiles}")"""))

# Cell 9: Markdown - Satellite Suite Ingestion & Interpolators
cells.append(nbf.v4.new_markdown_cell("""## 4. Satellite Multimodal Suite & 2D Bilinear Collocation

We load the two synchronized satellite observation suites:
- **Suite 1 (Late October 2019)**:
  - SST: `data/raw/sst/sst_north_indian_ocean_20191028_20191031.nc`
  - SLA: `data/raw/sea_level/sla_north_indian_ocean.nc`
  - Currents ($U, V$): `data/raw/currents/currents_north_indian_ocean.nc`
- **Suite 2 (Early May 2024)**:
  - SST: `data/raw/sst/sst_north_indian_ocean.nc`
  - SLA: `data/raw/sea_level/sla_north_indian_ocean_20240501_20240503.nc`
  - Currents ($U, V$): `data/raw/currents/currents_north_indian_ocean_20240501_20240503.nc`

For each daily time slice, we construct **2D Bilinear Interpolators** (`scipy.interpolate.RegularGridInterpolator`) to map the regular $0.25^\\circ$ grids onto each profile's exact floating-point coordinate $(\\text{Lat}, \\text{Lon})$."""))

# Cell 10: Code - Load Satellite Grids & Collocation Engine
cells.append(nbf.v4.new_code_cell("""def build_bilinear_interpolators_for_suite(sst_path, sla_path, curr_path):
    \"\"\"Loads NetCDF files and builds daily 2D bilinear interpolators for SST, SLA, U, V.\"\"\"
    ds_sst = xr.open_dataset(sst_path)
    ds_sla = xr.open_dataset(sla_path)
    ds_curr = xr.open_dataset(curr_path)

    sst_var = 'analysed_sst' if 'analysed_sst' in ds_sst else list(ds_sst.data_vars.keys())[0]
    sla_var = 'sla' if 'sla' in ds_sla else list(ds_sla.data_vars.keys())[0]
    u_var = 'ugos' if 'ugos' in ds_curr else ('currents_U' if 'currents_U' in ds_curr else 'u')
    v_var = 'vgos' if 'vgos' in ds_curr else ('currents_V' if 'currents_V' in ds_curr else 'v')

    lat_sst = ds_sst['latitude'].values if 'latitude' in ds_sst else ds_sst['lat'].values
    lon_sst = ds_sst['longitude'].values if 'longitude' in ds_sst else ds_sst['lon'].values
    lat_sla = ds_sla['latitude'].values if 'latitude' in ds_sla else ds_sla['lat'].values
    lon_sla = ds_sla['longitude'].values if 'longitude' in ds_sla else ds_sla['lon'].values
    lat_cur = ds_curr['latitude'].values if 'latitude' in ds_curr else ds_curr['lat'].values
    lon_cur = ds_curr['longitude'].values if 'longitude' in ds_curr else ds_curr['lon'].values

    times = pd.to_datetime(ds_sst['time'].values)
    daily_interpolators = {}

    for t_idx, t_val in enumerate(times):
        date_str = t_val.strftime("%Y-%m-%d")

        arr_sst = ds_sst[sst_var].values[t_idx]
        arr_sla = ds_sla[sla_var].values[t_idx]
        arr_u = ds_curr[u_var].values[t_idx]
        arr_v = ds_curr[v_var].values[t_idx]

        def make_interp(lats, lons, values):
            y = lats.copy()
            x = lons.copy()
            z = values.copy()
            if y[1] < y[0]:
                y = y[::-1]
                z = z[::-1, :]
            if x[1] < x[0]:
                x = x[::-1]
                z = z[:, ::-1]
            return RegularGridInterpolator(
                (y, x), z, method='linear', bounds_error=False, fill_value=np.nan
            )

        daily_interpolators[date_str] = {
            "date": date_str,
            "timestamp": t_val,
            "sst_interp": make_interp(lat_sst, lon_sst, arr_sst),
            "sla_interp": make_interp(lat_sla, lon_sla, arr_sla),
            "u_interp": make_interp(lat_cur, lon_cur, arr_u),
            "v_interp": make_interp(lat_cur, lon_cur, arr_v),
        }

    return daily_interpolators, times.min(), times.max()


# Build interpolators for Suite 1 (Oct 2019)
interp_suite_2019, t_min_2019, t_max_2019 = build_bilinear_interpolators_for_suite(
    DATA_RAW / "sst" / "sst_north_indian_ocean_20191028_20191031.nc",
    DATA_RAW / "sea_level" / "sla_north_indian_ocean.nc",
    DATA_RAW / "currents" / "currents_north_indian_ocean.nc",
)

# Build interpolators for Suite 2 (May 2024)
interp_suite_2024, t_min_2024, t_max_2024 = build_bilinear_interpolators_for_suite(
    DATA_RAW / "sst" / "sst_north_indian_ocean.nc",
    DATA_RAW / "sea_level" / "sla_north_indian_ocean_20240501_20240503.nc",
    DATA_RAW / "currents" / "currents_north_indian_ocean_20240501_20240503.nc",
)

print(f"Suite 1 (Late Oct 2019): {len(interp_suite_2019)} daily interpolators ready ({t_min_2019.strftime('%Y-%m-%d')} to {t_max_2019.strftime('%Y-%m-%d')})")
print(f"Suite 2 (Early May 2024): {len(interp_suite_2024)} daily interpolators ready ({t_min_2024.strftime('%Y-%m-%d')} to {t_max_2024.strftime('%Y-%m-%d')})")"""))

# Cell 11: Markdown - Spatiotemporal Matching & Tier Categorization
cells.append(nbf.v4.new_markdown_cell("""## 5. Spatiotemporal Collocation & Match Tier Classification

Each Argo profile is matched against both satellite suites using strictly evaluated temporal offset $|\\Delta t|$:
- **`tier0_exact`**: Profile surfaced **inside the satellite window** ($\\Delta t = 0\\text{ days}$).
- **`tier1_synoptic_1d`**: Profile surfaced within **$\\le 1.0\\text{ day}$ (24 hrs)** of the satellite window.
- **`tier2_standard_3d`**: Profile surfaced within **$1.0 < |\\Delta t| \\le 3.0\\text{ days}$ (72 hrs)**.
- **`tier3_mesoscale_5d`**: Profile surfaced within **$3.0 < |\\Delta t| \\le 5.0\\text{ days}$ (120 hrs)**.

For each matched profile, the 2D bilinear interpolator extracts:
- `sat_sst` (Sea Surface Temperature, $^\\circ\\text{C}$)
- `sat_sla` (Sea Level Anomaly, $\\text{m}$)
- `sat_current_u` (Zonal surface current velocity, $\\text{m/s}$)
- `sat_current_v` (Meridional surface current velocity, $\\text{m/s}$)
- `sat_current_speed` (Total velocity magnitude $\\sqrt{u^2 + v^2}$, $\\text{m/s}$)"""))

# Cell 12: Code - Collocation Execution
cells.append(nbf.v4.new_code_cell("""collocated_records = []

suites = [
    {"name": "Epoch_2019", "interpolators": interp_suite_2019, "t_min": t_min_2019, "t_max": t_max_2019},
    {"name": "Epoch_2024", "interpolators": interp_suite_2024, "t_min": t_min_2024, "t_max": t_max_2024},
]

for idx, row in df_argo.iterrows():
    prof_time = row['datetime']
    prof_lat = row['latitude']
    prof_lon = row['longitude']

    for suite in suites:
        s_name = suite["name"]
        interps = suite["interpolators"]
        t_start = pd.to_datetime(suite["t_min"].strftime("%Y-%m-%d 00:00:00"))
        t_end = pd.to_datetime(suite["t_max"].strftime("%Y-%m-%d 23:59:59"))

        if prof_time < t_start:
            offset_days = -(t_start - prof_time).total_seconds() / 86400.0
            closest_date = t_start.strftime("%Y-%m-%d")
        elif prof_time > t_end:
            offset_days = (prof_time - t_end).total_seconds() / 86400.0
            closest_date = t_end.strftime("%Y-%m-%d")
        else:
            offset_days = 0.0
            closest_date = prof_time.strftime("%Y-%m-%d")

        abs_offset_days = abs(offset_days)
        abs_offset_hours = abs_offset_days * 24.0

        if abs_offset_days <= 5.0:
            if abs_offset_days == 0.0:
                match_tier = "tier0_exact"
            elif abs_offset_days <= 1.0:
                match_tier = "tier1_synoptic_1d"
            elif abs_offset_days <= 3.0:
                match_tier = "tier2_standard_3d"
            else:
                match_tier = "tier3_mesoscale_5d"

            day_engine = interps.get(closest_date, list(interps.values())[0])

            point = np.array([[prof_lat, prof_lon]])
            val_sst = float(day_engine["sst_interp"](point)[0])
            val_sla = float(day_engine["sla_interp"](point)[0])
            val_u = float(day_engine["u_interp"](point)[0])
            val_v = float(day_engine["v_interp"](point)[0])

            # Skip if on continental land mask
            if np.isnan(val_sst) or np.isnan(val_sla) or np.isnan(val_u) or np.isnan(val_v):
                continue

            curr_speed = np.sqrt(val_u ** 2 + val_v ** 2)

            sample = row.to_dict()
            sample.update({
                "satellite_epoch": s_name,
                "collocated_satellite_date": closest_date,
                "temporal_offset_days": round(offset_days, 2),
                "temporal_offset_hours": round(abs_offset_hours, 1),
                "match_tier": match_tier,
                "sat_sst": round(val_sst, 3),
                "sat_sla": round(val_sla, 4),
                "sat_current_u": round(val_u, 4),
                "sat_current_v": round(val_v, 4),
                "sat_current_speed": round(float(curr_speed), 4),
                # Data Leakage Prevention Groupings
                "split_group_wmo": f"wmo_{row['float_wmo']}",
                "split_group_basin": "Arabian_Sea" if prof_lon < 77.5 else "Bay_of_Bengal",
            })
            collocated_records.append(sample)

df_collocated = pd.DataFrame(collocated_records)
print(f"Total Successfully Collocated Profiles: {len(df_collocated)}\\n")
print("Collocation Distribution by Match Tier:")
print(df_collocated['match_tier'].value_counts())"""))

# Cell 13: Markdown - Data Leakage Prevention
cells.append(nbf.v4.new_markdown_cell("""## 6. Data Leakage Prevention Strategy

In oceanographic deep-learning and spatial reconstruction tasks, naive random train/test splitting causes severe **data leakage** because:
1. Profiles from the same float are separated by only 5–10 days along a continuous Lagrangian drift path.
2. Near-identical water masses would be present in both training and test sets, artificially inflating accuracy scores.

### Mitigation in OceanEmbed:
1. **`split_group_wmo`**: Grouping by robotic float WMO (`wmo_2902264`, `wmo_1902669`, etc.) ensures entire float life-trajectories remain held out during cross-validation (`GroupKFold` / `LeaveOneGroupOut`).
2. **`split_group_basin`**: Distinct basin tags (`Arabian_Sea` vs `Bay_of_Bengal`) support cross-basin generalization testing.
3. **`satellite_epoch`**: Separation by temporal epoch (`Epoch_2019` vs `Epoch_2024`) enables zero-leakage out-of-time evaluation."""))

# Cell 14: Code - Inspect Collocated Dataset
cells.append(nbf.v4.new_code_cell("""cols_to_preview = [
    'float_wmo', 'cycle_number', 'date', 'latitude', 'longitude',
    'match_tier', 'temporal_offset_hours', 'sat_sst', 'sat_sla',
    'sat_current_speed', 'temp_depth_0m', 'temp_depth_100m', 'temp_depth_500m', 'temp_depth_1000m'
]

print(df_collocated[cols_to_preview].to_string(index=False))"""))

# Cell 15: Markdown - Export Processed Datasets
cells.append(nbf.v4.new_markdown_cell("""## 7. Dual-Format Dataset Export & Quality Verification

We export the finalized, leakage-protected dataset to two formats:
1. **CSV** (`collocated_ocean_profiles.csv`): Human-readable, transparent, easily inspectable.
2. **Parquet** (`collocated_ocean_profiles.parquet`): Type-safe, compressed columnar format for high-speed ML training in Phase 5."""))

# Cell 16: Code - Export & Verification
cells.append(nbf.v4.new_code_cell("""df_export = df_collocated.copy()
df_export['datetime'] = pd.to_datetime(df_export['datetime'])

csv_path = DATA_PROCESSED / "collocated_ocean_profiles.csv"
parquet_path = DATA_PROCESSED / "collocated_ocean_profiles.parquet"

df_export.to_csv(csv_path, index=False)
df_export.to_parquet(parquet_path, index=False)

csv_size_kb = csv_path.stat().st_size / 1024
pq_size_kb = parquet_path.stat().st_size / 1024

print("================================================================================")
print("             PHASE 4 DATASET PREPROCESSING COMPLETED SUCCESSFULLY                ")
print("================================================================================")
print(f"  CSV Saved:      {csv_path.name} ({csv_size_kb:.1f} KB)")
print(f"  Parquet Saved:  {parquet_path.name} ({pq_size_kb:.1f} KB)")
print(f"  Total Profiles: {len(df_export)}")
print(f"  Total Columns:  {len(df_export.columns)}")
print(f"  Depth Grid:     21 Standard Oceanographic Depths (0 to 2000m)")
print("================================================================================")"""))

nb.cells = cells

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"[SUCCESS] Wrote updated notebook to: {NOTEBOOK_PATH.resolve()}")
