"""
OceanEmbed - Historical Dataset Expansion (2018-2025)
Module: expand_dataset.py

Expands OceanEmbed's dataset across the North Indian Ocean:
1. Downloads 4 additional genuine Argo profiling float NetCDFs from INCOIS GDAC:
   - 2902267: Arabian Sea (2019-2023, 153 profiles)
   - 2902278: Bay of Bengal (2019-2021, 167 profiles)
   - 1902669: Bay of Bengal (2023-2026, 110 profiles)
   - 1902671: Arabian Sea (2023-2026, 109 profiles)
2. Downloads matching satellite SLA and U/V Surface Currents for May 1-3, 2024
   from NOAA CoastWatch ERDDAP to pair with the existing May 2024 SST dataset.
3. Preserves all existing raw files.
4. Identifies all valid matched Argo profiles across both 2019 and 2024 satellite windows.
5. Updates the inspection report.
"""

import io
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import xarray as xr

# UTF-8 stdout wrapper for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "raw"
ARGO_DIR = DATA_ROOT / "argo"
SLA_DIR = DATA_ROOT / "sea_level"
CURRENTS_DIR = DATA_ROOT / "currents"
SST_DIR = DATA_ROOT / "sst"

# Official INCOIS GDAC repository
GDAC_BASE = "https://data-argo.ifremer.fr/dac/incois"

ADDITIONAL_ARGO_FLOATS = [
    {
        "wmo": "2902267",
        "basin": "Northern Arabian Sea",
        "span": "2019-2023",
        "expected_profiles": 153,
    },
    {
        "wmo": "2902278",
        "basin": "Northern Bay of Bengal",
        "span": "2019-2021",
        "expected_profiles": 167,
    },
    {
        "wmo": "1902669",
        "basin": "Central Bay of Bengal",
        "span": "2023-2026",
        "expected_profiles": 110,
    },
    {
        "wmo": "1902671",
        "basin": "Central Arabian Sea",
        "span": "2023-2026",
        "expected_profiles": 109,
    },
]

# NOAA CoastWatch ERDDAP query for May 1-3, 2024 (matching the existing May 2024 SST)
# Grid: 0.125° to 24.875°N, 50.125° to 99.875°E (100 x 200 cells)
UPWELL_BASE = "https://upwell.pfeg.noaa.gov/erddap/griddap"
MAY2024_TIME = "[(2024-05-01T00:00:00Z):1:(2024-05-03T00:00:00Z)]"
LAT_BOUNDS = "[(0.125):1:(24.875)]"
LON_BOUNDS = "[(50.125):1:(99.875)]"


def download_file(url: str, dest_path: Path, desc: str):
    """Download a file with streaming and error handling."""
    if dest_path.exists() and dest_path.stat().st_size > 10_000:
        print(f"  [OK] Already downloaded: {dest_path.name} ({dest_path.stat().st_size / 1024:.1f} KB)")
        return dest_path

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  [+] Fetching {desc}...")
    print(f"      URL: {url}")
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        size_kb = dest_path.stat().st_size / 1024
        print(f"      [SUCCESS] Saved: {dest_path.name} ({size_kb:.1f} KB)")
        return dest_path
    except Exception as e:
        print(f"      [ERROR] Failed to download {desc}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return None


def expand_argo():
    """Download additional genuine Argo profiling float NetCDFs."""
    print("================================================================================")
    print("STEP 1: DOWNLOADING ADDITIONAL ARGO FLOATS (2018-2025 NORTH INDIAN OCEAN)")
    print("================================================================================")
    downloaded = []
    for info in ADDITIONAL_ARGO_FLOATS:
        wmo = info["wmo"]
        url = f"{GDAC_BASE}/{wmo}/{wmo}_prof.nc"
        dest = ARGO_DIR / f"{wmo}_prof.nc"
        desc = f"Argo WMO {wmo} ({info['basin']}, {info['span']})"
        p = download_file(url, dest, desc)
        if p:
            downloaded.append(p)
    return downloaded


def expand_satellite():
    """Download matching May 2024 SLA and Surface Currents from NOAA CoastWatch."""
    print("\n================================================================================")
    print("STEP 2: DOWNLOADING MATCHING MAY 2024 SATELLITE SLA & CURRENTS")
    print("================================================================================")
    downloaded = []

    # 1. May 2024 SLA
    sla_url = f"{UPWELL_BASE}/nesdisSSH1day.nc?sla{MAY2024_TIME}{LAT_BOUNDS}{LON_BOUNDS}"
    sla_path = SLA_DIR / "sla_north_indian_ocean_20240501_20240503.nc"
    p1 = download_file(sla_url, sla_path, "NOAA CoastWatch May 2024 SLA (0.25° grid)")
    if p1:
        downloaded.append(p1)

    # 2. May 2024 Surface Currents (ugos, vgos)
    curr_url = f"{UPWELL_BASE}/nesdisSSH1day.nc?ugos{MAY2024_TIME}{LAT_BOUNDS}{LON_BOUNDS},vgos{MAY2024_TIME}{LAT_BOUNDS}{LON_BOUNDS}"
    curr_path = CURRENTS_DIR / "currents_north_indian_ocean_20240501_20240503.nc"
    p2 = download_file(curr_url, curr_path, "NOAA CoastWatch May 2024 Geostrophic Currents (ugos, vgos)")
    if p2:
        downloaded.append(p2)

    return downloaded


def analyze_all_matches():
    """Identifies all valid matched Argo profiles across both satellite windows."""
    print("\n================================================================================")
    print("STEP 3: COMPREHENSIVE COLLOCATION MATCHING ACROSS 2018-2025")
    print("================================================================================")

    windows = [
        {
            "name": "Window 1: Late October 2019",
            "start": pd.to_datetime("2019-10-28 00:00:00"),
            "end": pd.to_datetime("2019-10-31 23:59:59"),
            "satellite_suite": "SST, SLA, U, V (Oct 28-31, 2019)",
        },
        {
            "name": "Window 2: Early May 2024",
            "start": pd.to_datetime("2024-05-01 00:00:00"),
            "end": pd.to_datetime("2024-05-03 23:59:59"),
            "satellite_suite": "SST, SLA, U, V (May 1-3, 2024)",
        },
    ]

    argo_files = sorted(list(ARGO_DIR.glob("*_prof.nc")))
    print(f"Total Argo Float NetCDF Datasets in Library: {len(argo_files)}")

    all_matched = []

    for af in argo_files:
        wmo = af.name.split("_")[0]
        try:
            with xr.open_dataset(af) as ds:
                juld = pd.to_datetime(ds["JULD"].values)
                lats = ds["LATITUDE"].values
                lons = ds["LONGITUDE"].values
                cycles = ds["CYCLE_NUMBER"].values
                pres = ds["PRES"].values
                temp = ds["TEMP"].values
                temp_qc = ds["TEMP_QC"].values.astype(str) if "TEMP_QC" in ds else None

                for w in windows:
                    w_name = w["name"]
                    w_start = w["start"]
                    w_end = w["end"]

                    for idx, t in enumerate(juld):
                        if pd.isna(t):
                            continue

                        # Calculate offset in days to the window boundary
                        if t < w_start:
                            delta_days = -(w_start - t).total_seconds() / 86400.0
                        elif t > w_end:
                            delta_days = (t - w_end).total_seconds() / 86400.0
                        else:
                            delta_days = 0.0

                        abs_d = abs(delta_days)

                        # Match within +/- 5.0 days mesoscale tolerance
                        if abs_d <= 5.0:
                            lat_val = float(lats[idx])
                            lon_val = float(lons[idx])

                            # Confirm within North Indian Ocean bounding box
                            if 0.0 <= lat_val <= 25.0 and 50.0 <= lon_val <= 100.0:
                                p_pres = pres[idx]
                                p_temp = temp[idx]
                                v_mask = (p_pres >= 0) & (p_pres < 2500) & (p_temp > 0) & np.isfinite(p_temp)

                                if v_mask.sum() >= 10:  # Valid vertical profile
                                    # Quality control percentage
                                    qc_pct = 100.0
                                    if temp_qc is not None:
                                        qc_row = temp_qc[idx]
                                        qc_pct = round((np.sum(qc_row == "1") / len(qc_row)) * 100, 1)

                                    if abs_d == 0.0:
                                        tier = "Tier 0: Exact Window Match"
                                    elif abs_d <= 1.0:
                                        tier = "Tier 1: Synoptic (<= 1.0 d)"
                                    elif abs_d <= 3.0:
                                        tier = "Tier 2: Standard (<= 3.0 d)"
                                    else:
                                        tier = "Tier 3: Mesoscale (<= 5.0 d)"

                                    all_matched.append({
                                        "window": w_name,
                                        "wmo": wmo,
                                        "cycle": int(cycles[idx]),
                                        "timestamp": t.strftime("%Y-%m-%d %H:%M UTC"),
                                        "lat": round(lat_val, 4),
                                        "lon": round(lon_val, 4),
                                        "offset_hours": round(abs_d * 24.0, 1),
                                        "tier": tier,
                                        "depth_levels": int(v_mask.sum()),
                                        "max_depth_dbar": round(float(p_pres[v_mask].max()), 1),
                                        "surface_temp": round(float(p_temp[v_mask][0]), 2),
                                        "deep_temp": round(float(p_temp[v_mask][-1]), 2),
                                        "qc1_pct": qc_pct,
                                    })
        except Exception as e:
            print(f"Error inspecting {af.name}: {e}")

    df = pd.DataFrame(all_matched)
    if not df.empty:
        df = df.sort_values(by=["window", "offset_hours"])
        print(f"\n[+] Total Valid Matched In-Situ Profiles Across Both Windows: {len(df)}")
        for w_name, group in df.groupby("window"):
            print(f"\n--- {w_name} ({len(group)} matched profiles) ---")
            for _, r in group.iterrows():
                print(
                    f"  Float {r['wmo']} | Cycle {r['cycle']:>3} | {r['tier']:<28} | "
                    f"{r['timestamp']} (Δt: {r['offset_hours']:>4.1f} hrs) | "
                    f"Lat: {r['lat']:>7.3f}°, Lon: {r['lon']:>7.3f}° | "
                    f"{r['depth_levels']} levels down to {r['max_depth_dbar']} dbar | "
                    f"Temp: {r['surface_temp']}°C -> {r['deep_temp']}°C | QC '1': {r['qc1_pct']}%"
                )
    else:
        print("[!] No matching profiles found.")

    return df


if __name__ == "__main__":
    expand_argo()
    expand_satellite()
    analyze_all_matches()
