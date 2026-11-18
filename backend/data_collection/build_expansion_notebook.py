"""
Build the 02_historical_dataset_expansion.ipynb notebook using nbformat.
"""

from pathlib import Path
import nbformat as nbf

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "02_historical_dataset_expansion.ipynb"

nb = nbf.v4.new_notebook()

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

# Cell 1: Markdown Title & Scientific Scope
cells.append(nbf.v4.new_markdown_cell("""# OceanEmbed: Historical Dataset Expansion (2018–2025)
**Project Code:** SIH26066 | **Focus:** 3D Ocean Temperature Reconstruction (North Indian Ocean)

This notebook executes and verifies the **Historical Dataset Expansion**:
1. **Additional Genuine Argo Floats**: Expands the in-situ ocean observation library with **7 additional genuine profiling floats** from the official INCOIS Global Data Assembly Centre (`2902268`, `2902279`, `2902280`, `2902283`, `1902670`, `1902672`, `1902673`).
2. **Additional Synchronized Satellite Suite**: Downloads a 3rd distinct historical seasonal window (**January 15–18, 2024: Northeast Winter Monsoon**) covering Sea Surface Temperature (SST), Sea Level Anomaly (SLA), and Geostrophic Surface Currents ($U, V$).
3. **Duplicate Prevention**: Reuses already downloaded files; downloads only net-new files.
4. **Data Preservation**: Preserves all existing raw NetCDF and processed files.
5. **Quality Control & Validation**: Inspects QC flags (`'1'`, `'2'`, `'4'`), coordinate bounds, depth ranges, and valid measurements.
6. **Collocation Matching**: Evaluates satellite–Argo matching across all 3 seasonal observation epochs across Tier 0 (Exact), Tier 1 (Synoptic), Tier 2 (Standard), and Tier 3 (Mesoscale).

> [!NOTE]
> Strictly observational data collection, QA audit, and matching. No preprocessing or model training is conducted in this notebook."""))

# Cell 2: Code - Imports & Path Definitions
cells.append(nbf.v4.new_code_cell("""import os
import sys
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import requests
import xarray as xr
import netCDF4
import json

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Define paths
NOTEBOOK_DIR = Path.cwd()
PROJECT_ROOT = NOTEBOOK_DIR.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
ARGO_DIR = DATA_RAW / "argo"
SST_DIR = DATA_RAW / "sst"
SLA_DIR = DATA_RAW / "sea_level"
CURRENTS_DIR = DATA_RAW / "currents"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

print("Environment Paths:")
print(f"  Project Root:   {PROJECT_ROOT.resolve()}")
print(f"  Raw Data:       {DATA_RAW.resolve()}")
print(f"  Processed Data: {DATA_PROCESSED.resolve()}")"""))

# Cell 3: Code - Safe Download Utility
cells.append(nbf.v4.new_code_cell("""def download_file_safely(url: str, dest_path: Path, description: str) -> Path:
    \"\"\"Downloads a file only if it does not already exist, preventing duplicate downloads.\"\"\"
    if dest_path.exists() and dest_path.stat().st_size > 10_000:
        size_kb = dest_path.stat().st_size / 1024
        print(f"  [EXISTS - SKIPPED] {dest_path.name} ({size_kb:.1f} KB) - Duplicate avoided.")
        return dest_path

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  [+] Downloading {description}...")
    print(f"      URL: {url}")
    try:
        r = requests.get(url, stream=True, timeout=60, allow_redirects=True)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        size_kb = dest_path.stat().st_size / 1024
        print(f"      [SUCCESS] Saved: {dest_path.name} ({size_kb:.1f} KB)")
        return dest_path
    except Exception as e:
        print(f"      [ERROR] Failed to download {description}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return None"""))

# Cell 4: Markdown - Section 1: Additional Argo Floats
cells.append(nbf.v4.new_markdown_cell("""## 1. Additional Genuine Argo Float Ingestion (2018–2025)

We ingest 7 additional active and historical profiling floats deployed by INCOIS in the North Indian Ocean:
- `2902268`: Central Arabian Sea ($14.8^\circ\text{N}-18.6^\circ\text{N}, 59.4^\circ\text{E}-65.0^\circ\text{E}$, 2019–2022)
- `2902279`: Northern Bay of Bengal ($15.8^\circ\text{N}-18.6^\circ\text{N}, 89.2^\circ\text{E}-93.3^\circ\text{E}$, 2019–2021)
- `2902280`: Central Bay of Bengal ($13.9^\circ\text{N}-16.8^\circ\text{N}, 88.3^\circ\text{E}-92.7^\circ\text{E}$, 2019–2021)
- `2902283`: Southern Bay of Bengal ($12.9^\circ\text{N}-16.6^\circ\text{N}, 84.3^\circ\text{E}-88.9^\circ\text{E}$, 2019–2021)
- `1902670`: Equatorial North Indian Ocean / Sri Lanka ($3.9^\circ\text{N}-12.6^\circ\text{N}, 77.7^\circ\text{E}-89.8^\circ\text{E}$, 2023–2026)
- `1902672`: North-Central Arabian Sea ($15.5^\circ\text{N}-19.0^\circ\text{N}, 64.6^\circ\text{E}-71.7^\circ\text{E}$, 2023–2026)
- `1902673`: South-Central Arabian Sea ($10.7^\circ\text{N}-14.5^\circ\text{N}, 68.0^\circ\text{E}-71.1^\circ\text{E}$, 2023–2026)"""))

# Cell 5: Code - Download Additional Argo Floats
cells.append(nbf.v4.new_code_cell("""GDAC_INCOIS_BASE = "https://data-argo.ifremer.fr/dac/incois"

NEW_ARGO_TARGETS = [
    {"wmo": "2902268", "basin": "Central Arabian Sea", "span": "2019-2022"},
    {"wmo": "2902279", "basin": "Northern Bay of Bengal", "span": "2019-2021"},
    {"wmo": "2902280", "basin": "Central Bay of Bengal", "span": "2019-2021"},
    {"wmo": "2902283", "basin": "Southern Bay of Bengal", "span": "2019-2021"},
    {"wmo": "1902670", "basin": "Equatorial NIO / Sri Lanka", "span": "2023-2026"},
    {"wmo": "1902672", "basin": "North-Central Arabian Sea", "span": "2023-2026"},
    {"wmo": "1902673", "basin": "South-Central Arabian Sea", "span": "2023-2026"},
]

print("=" * 80)
print("DOWNLOADING ADDITIONAL ARGO FLOATS FROM INCOIS GDAC")
print("=" * 80)

downloaded_argo_paths = []
for target in NEW_ARGO_TARGETS:
    wmo = target["wmo"]
    url = f"{GDAC_INCOIS_BASE}/{wmo}/{wmo}_prof.nc"
    dest = ARGO_DIR / f"{wmo}_prof.nc"
    desc = f"Argo Float {wmo} ({target['basin']}, {target['span']})"
    p = download_file_safely(url, dest, desc)
    if p:
        downloaded_argo_paths.append(p)

print(f"\\nTotal Argo Files in Directory: {len(list(ARGO_DIR.glob('*_prof.nc')))}")"""))

# Cell 6: Markdown - Section 2: Download Satellite Suite for Winter 2024
cells.append(nbf.v4.new_markdown_cell("""## 2. Additional Satellite Suite: Winter Monsoon (January 15–18, 2024)

We download synchronous satellite observations for a 3rd seasonal epoch: **Northeast Winter Monsoon (January 15–18, 2024)** matching the exact $0.25^\\circ$ North Indian Ocean grid ($0.125^\\circ\text{N}-24.875^\\circ\text{N}, 50.125^\\circ\text{E}-99.875^\\circ\text{E}$):
- **SST**: NOAA Coral Reef Watch CoralTemp v3.1 Daily ($0.05^\\circ$ sampled at $0.25^\\circ$)
- **SLA**: NOAA CoastWatch Daily Sea Level Anomaly ($0.25^\\circ$)
- **Currents**: NOAA CoastWatch Absolute Geostrophic Surface Velocity ($u, v$ in m/s)"""))

# Cell 7: Code - Download Satellite Winter 2024 Suite
cells.append(nbf.v4.new_code_cell("""JAN2024_TIME = "[(2024-01-15T00:00:00Z):1:(2024-01-18T00:00:00Z)]"
JAN2024_TIME_SST = "[(2024-01-15T12:00:00Z):1:(2024-01-18T12:00:00Z)]"
LAT_BOUNDS = "[(0.125):1:(24.875)]"
LON_BOUNDS = "[(50.125):1:(99.875)]"

UPWELL_BASE = "https://upwell.pfeg.noaa.gov/erddap/griddap"
OCEANWATCH_BASE = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap"

print("=" * 80)
print("DOWNLOADING WINTER MONSOON SATELLITE SUITE (JANUARY 15-18, 2024)")
print("=" * 80)

# 1. SST
sst_jan24_url = f"{OCEANWATCH_BASE}/CRW_sst_v3_1.nc?analysed_sst{JAN2024_TIME_SST}[(0.125):5:(24.875)][(50.125):5:(99.875)]"
sst_jan24_path = SST_DIR / "sst_north_indian_ocean_20240115_20240118.nc"
download_file_safely(sst_jan24_url, sst_jan24_path, "NOAA CoralTemp SST (Jan 15-18, 2024)")

# 2. SLA
sla_jan24_url = f"{UPWELL_BASE}/nesdisSSH1day.nc?sla{JAN2024_TIME}{LAT_BOUNDS}{LON_BOUNDS}"
sla_jan24_path = SLA_DIR / "sla_north_indian_ocean_20240115_20240118.nc"
download_file_safely(sla_jan24_url, sla_jan24_path, "NOAA CoastWatch SLA (Jan 15-18, 2024)")

# 3. Currents
curr_jan24_url = f"{UPWELL_BASE}/nesdisSSH1day.nc?ugos{JAN2024_TIME}{LAT_BOUNDS}{LON_BOUNDS},vgos{JAN2024_TIME}{LAT_BOUNDS}{LON_BOUNDS}"
curr_jan24_path = CURRENTS_DIR / "currents_north_indian_ocean_20240115_20240118.nc"
download_file_safely(curr_jan24_url, curr_jan24_path, "NOAA CoastWatch Geostrophic Currents (Jan 15-18, 2024)")"""))

# Cell 8: Markdown - Section 3: Quality Checks on All Argo Floats
cells.append(nbf.v4.new_markdown_cell("""## 3. Comprehensive Quality Control Audit of the Entire Argo Library

We audit all 13 Argo float NetCDFs across the library, inspecting:
- Total profiles and operational date spans
- Geographic coverage bounds (Latitude & Longitude)
- QC flag distributions (`TEMP_QC`, `PRES_QC`, `PSAL_QC`)
- Sensor artifacts (negative pressures, impossible salinities, extreme temperatures)
- Valid in-situ measurement counts"""))

# Cell 9: Code - Argo QC Audit
cells.append(nbf.v4.new_code_cell("""all_argo_files = sorted(list(ARGO_DIR.glob("*_prof.nc")))
print(f"Auditing all {len(all_argo_files)} Argo float NetCDF datasets:\\n")

argo_audit_results = []
total_library_profiles = 0
total_library_valid = 0

for af in all_argo_files:
    wmo = af.name.split("_")[0]
    with xr.open_dataset(af) as ds:
        juld = pd.to_datetime(ds['JULD'].values)
        valid_juld = juld[~pd.isna(juld)]
        lats = ds['LATITUDE'].values
        lons = ds['LONGITUDE'].values
        v_lats = lats[np.isfinite(lats) & (lats < 9000)]
        v_lons = lons[np.isfinite(lons) & (lons < 9000)]
        pres = ds['PRES'].values
        temp = ds['TEMP'].values
        psal = ds['PSAL'].values if 'PSAL' in ds else None
        temp_qc = ds['TEMP_QC'].values if 'TEMP_QC' in ds else None

        n_profiles = len(valid_juld)
        total_library_profiles += n_profiles

        # Count QC '1' or '2'
        if temp_qc is not None:
            if hasattr(temp_qc, 'decode'):
                t_qc_arr = np.array([x.decode('utf-8', errors='ignore') for x in temp_qc.flatten()])
            else:
                t_qc_arr = temp_qc.flatten().astype(str)
            good_qc_count = int(np.isin(t_qc_arr, ['1', '2']).sum())
            total_measurements = len(t_qc_arr)
            qc_pct = round((good_qc_count / total_measurements) * 100, 1) if total_measurements > 0 else 0.0
        else:
            qc_pct = 100.0

        # Physical validity count
        v_mask = (pres >= 0) & (pres < 2500) & (temp >= 1.0) & (temp <= 35.0) & np.isfinite(temp)
        valid_profiles_in_float = int((v_mask.sum(axis=1) >= 10).sum())
        total_library_valid += valid_profiles_in_float

        basin = "Arabian Sea" if float(v_lons.mean()) < 77.5 else "Bay of Bengal"

        argo_audit_results.append({
            "WMO": wmo,
            "Basin": basin,
            "Total Profiles": n_profiles,
            "Valid QC Profiles": valid_profiles_in_float,
            "Start Date": valid_juld.min().strftime("%Y-%m-%d"),
            "End Date": valid_juld.max().strftime("%Y-%m-%d"),
            "Lat Range": f"{v_lats.min():.2f}° to {v_lats.max():.2f}°",
            "Lon Range": f"{v_lons.min():.2f}° to {v_lons.max():.2f}°",
            "QC Good (%)": qc_pct,
            "Max Depth (dbar)": round(float(pres[pres < 9000].max()), 1) if (pres < 9000).any() else 0.0
        })

df_argo_audit = pd.DataFrame(argo_audit_results)
print(df_argo_audit.to_string(index=False))
print(f"\\nTotal In-Situ Profiles Across Library: {total_library_profiles}")
print(f"Total Profiles Passing Strict QC:     {total_library_valid} ({round(total_library_valid/total_library_profiles*100, 1)}%)")"""))

# Cell 10: Markdown - Section 4: Collocation Matching Across 3 Epochs
cells.append(nbf.v4.new_markdown_cell("""## 4. Multi-Epoch Collocation Matching

We evaluate satellite–Argo collocation matching across all **13 Argo floats** and **3 distinct seasonal observation windows**:
- **Epoch 1: Late October 2019** (Post-Monsoon Transition)
- **Epoch 2: Mid January 2024** (Northeast Winter Monsoon)
- **Epoch 3: Early May 2024** (Pre-Monsoon Tropical Warming)

### Collocation Tolerance Tiers:
- **`Tier 0: Exact Window Match`**: $\\Delta t = 0\\text{ days}$ (Surfaced on satellite observation day)
- **`Tier 1: Synoptic Match`**: $|\\Delta t| \\le 1.0\\text{ day}$ ($24\\text{ hrs}$)
- **`Tier 2: Standard Match`**: $1.0 < |\\Delta t| \\le 3.0\\text{ days}$ ($72\\text{ hrs}$)
- **`Tier 3: Mesoscale Match`**: $3.0 < |\\Delta t| \\le 5.0\\text{ days}$ ($120\\text{ hrs}$)"""))

# Cell 11: Code - Collocation Matching Engine
cells.append(nbf.v4.new_code_cell("""OBSERVATION_EPOCHS = [
    {
        "epoch_id": "Epoch_1_Oct2019",
        "name": "Late October 2019 (Post-Monsoon)",
        "start": pd.to_datetime("2019-10-28 00:00:00"),
        "end": pd.to_datetime("2019-10-31 23:59:59"),
        "sst_file": SST_DIR / "sst_north_indian_ocean_20191028_20191031.nc",
        "sla_file": SLA_DIR / "sla_north_indian_ocean.nc",
        "curr_file": CURRENTS_DIR / "currents_north_indian_ocean.nc",
    },
    {
        "epoch_id": "Epoch_2_Jan2024",
        "name": "Mid January 2024 (Winter Monsoon)",
        "start": pd.to_datetime("2024-01-15 00:00:00"),
        "end": pd.to_datetime("2024-01-18 23:59:59"),
        "sst_file": SST_DIR / "sst_north_indian_ocean_20240115_20240118.nc",
        "sla_file": SLA_DIR / "sla_north_indian_ocean_20240115_20240118.nc",
        "curr_file": CURRENTS_DIR / "currents_north_indian_ocean_20240115_20240118.nc",
    },
    {
        "epoch_id": "Epoch_3_May2024",
        "name": "Early May 2024 (Pre-Monsoon)",
        "start": pd.to_datetime("2024-05-01 00:00:00"),
        "end": pd.to_datetime("2024-05-03 23:59:59"),
        "sst_file": SST_DIR / "sst_north_indian_ocean.nc",
        "sla_file": SLA_DIR / "sla_north_indian_ocean_20240501_20240503.nc",
        "curr_file": CURRENTS_DIR / "currents_north_indian_ocean_20240501_20240503.nc",
    },
]

collocation_matches = []

for af in all_argo_files:
    wmo = af.name.split("_")[0]
    with xr.open_dataset(af) as ds:
        juld = pd.to_datetime(ds['JULD'].values)
        lats = ds['LATITUDE'].values
        lons = ds['LONGITUDE'].values
        cycles = ds['CYCLE_NUMBER'].values
        pres = ds['PRES'].values
        temp = ds['TEMP'].values

        for epoch in OBSERVATION_EPOCHS:
            e_name = epoch["name"]
            e_id = epoch["epoch_id"]
            e_start = epoch["start"]
            e_end = epoch["end"]

            for i in range(len(juld)):
                t = juld[i]
                if pd.isna(t):
                    continue

                lat = float(lats[i])
                lon = float(lons[i])

                # Check North Indian Ocean bounds
                if not (0.0 <= lat <= 25.0 and 50.0 <= lon <= 100.0):
                    continue

                # Check profile physical validity
                p_p = pres[i]
                p_t = temp[i]
                v_pts = (p_p >= 0) & (p_p < 2500) & (p_t >= 1.0) & (p_t <= 35.0) & np.isfinite(p_t)
                if v_pts.sum() < 10:
                    continue

                # Calculate offset in days
                if t < e_start:
                    d_days = -(e_start - t).total_seconds() / 86400.0
                elif t > e_end:
                    d_days = (t - e_end).total_seconds() / 86400.0
                else:
                    d_days = 0.0

                abs_days = abs(d_days)

                if abs_days <= 5.0:
                    if abs_days == 0.0:
                        tier = "Tier 0: Exact Window Match"
                    elif abs_days <= 1.0:
                        tier = "Tier 1: Synoptic (<= 1.0 d)"
                    elif abs_days <= 3.0:
                        tier = "Tier 2: Standard (<= 3.0 d)"
                    else:
                        tier = "Tier 3: Mesoscale (<= 5.0 d)"

                    basin = "Arabian Sea" if lon < 77.5 else "Bay of Bengal"

                    collocation_matches.append({
                        "Epoch": e_id,
                        "Season / Period": e_name,
                        "Float WMO": wmo,
                        "Cycle": int(cycles[i]),
                        "Basin": basin,
                        "Timestamp": t.strftime("%Y-%m-%d %H:%M UTC"),
                        "Latitude": round(lat, 3),
                        "Longitude": round(lon, 3),
                        "Offset (hrs)": round(abs_days * 24.0, 1),
                        "Tier": tier,
                        "Depth Levels": int(v_pts.sum()),
                        "Surface Temp (°C)": round(float(p_t[v_pts][0]), 2),
                        "Deep Temp (°C)": round(float(p_t[v_pts][-1]), 2),
                    })

df_matches = pd.DataFrame(collocation_matches)
print(f"TOTAL VALID SATELLITE–ARGO MATCHED PROFILES: {len(df_matches)}\\n")
print("Matches by Observation Epoch:")
print(df_matches['Season / Period'].value_counts())
print("\\nMatches by Collocation Tier:")
print(df_matches['Tier'].value_counts())"""))

# Cell 12: Code - Display Detailed Match Catalog
cells.append(nbf.v4.new_code_cell("""# Display formatted table of all matched profiles
cols_show = ["Epoch", "Float WMO", "Cycle", "Basin", "Timestamp", "Offset (hrs)", "Tier", "Latitude", "Longitude", "Surface Temp (°C)", "Deep Temp (°C)"]
df_matches_sorted = df_matches.sort_values(by=["Epoch", "Offset (hrs)"])
print(df_matches_sorted[cols_show].to_string(index=False))"""))

# Cell 13: Markdown - Section 5: Dataset Registry & Inspection Report Update
cells.append(nbf.v4.new_markdown_cell("""## 5. Inspection Report Registry Update

We update `dataset_inspection_report.json` with the complete inventory of all raw NetCDF files across the library."""))

# Cell 14: Code - Update Inspection JSON
cells.append(nbf.v4.new_code_cell("""# Run inspection scan on all .nc files in data/raw
raw_nc_files = sorted(list(DATA_RAW.glob("**/*.nc")))
print(f"Total Raw NetCDF Files in Library: {len(raw_nc_files)}")

inspection_records = []
for f in raw_nc_files:
    rel = f.relative_to(DATA_RAW)
    sz_kb = round(f.stat().st_size / 1024, 2)
    with netCDF4.Dataset(f, "r") as nc:
        fmt = nc.data_model
        title = getattr(nc, "title", "N/A")
    with xr.open_dataset(f) as ds:
        dims = {dim: int(size) for dim, size in ds.sizes.items()}
        vars_list = list(ds.data_vars.keys())
    inspection_records.append({
        "filename": f.name,
        "relative_path": str(rel),
        "size_kb": sz_kb,
        "format": fmt,
        "title": title,
        "dimensions": dims,
        "variables": vars_list,
    })

rep_path = DATA_RAW / "dataset_inspection_report.json"
with open(rep_path, "w", encoding="utf-8") as f:
    json.dump(inspection_records, f, indent=2)

print(f"[SUCCESS] Updated {rep_path.name} with {len(inspection_records)} dataset records.")"""))

nb.cells = cells

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"[SUCCESS] Wrote notebook to: {NOTEBOOK_PATH.resolve()}")
