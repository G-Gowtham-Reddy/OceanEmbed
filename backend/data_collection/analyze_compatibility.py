"""
OceanEmbed - Dataset Compatibility Analysis
Module: analyze_compatibility.py

Analyzes:
1. Temporal overlap between Argo floats and satellite observation windows.
2. Spatial / geographical bounding box overlap.
3. Spatial resolution differences (point profile vs gridded 0.05° / 0.25°).
4. Argo Quality Control (QC) flag distributions (POSITION_QC, TEMP_QC, PSAL_QC, PRES_QC).
5. Invalid values, outliers, and sensor artifacts.
6. Identification of matching/colocatable Argo profiles.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "raw"


def analyze_argo_qc(filepath: Path):
    """Analyzes QC flags and invalid values in an Argo NetCDF file."""
    ds = xr.open_dataset(filepath)
    wmo = filepath.name.split("_")[0]

    # Time & Position
    juld = pd.to_datetime(ds["JULD"].values)
    lats = ds["LATITUDE"].values
    lons = ds["LONGITUDE"].values
    cycles = ds["CYCLE_NUMBER"].values

    # QC Flags
    pos_qc = ds["POSITION_QC"].values.astype(str) if "POSITION_QC" in ds else None
    temp_qc = ds["TEMP_QC"].values.astype(str) if "TEMP_QC" in ds else None
    psal_qc = ds["PSAL_QC"].values.astype(str) if "PSAL_QC" in ds else None
    pres_qc = ds["PRES_QC"].values.astype(str) if "PRES_QC" in ds else None

    # Values
    temp = ds["TEMP"].values
    psal = ds["PSAL"].values
    pres = ds["PRES"].values

    total_levels = temp.size

    def summarize_qc(qc_arr):
        if qc_arr is None:
            return {}
        flat = qc_arr.flatten()
        unique, counts = np.unique(flat, return_counts=True)
        return {str(u): int(c) for u, c in zip(unique, counts)}

    # Outliers / invalid values check
    invalid_pres = ((pres < 0) | (pres > 3000)) & np.isfinite(pres) & (pres < 90000)
    invalid_temp = ((temp < -2) | (temp > 35)) & np.isfinite(temp) & (temp < 90000)
    invalid_psal = ((psal < 10) | (psal > 42)) & np.isfinite(psal) & (psal < 90000)

    # DataFrame of all profiles
    profiles_df = pd.DataFrame({
        "wmo": wmo,
        "cycle": cycles,
        "datetime": juld,
        "date_str": [t.strftime("%Y-%m-%d") for t in juld],
        "latitude": lats,
        "longitude": lons,
        "pos_qc": pos_qc.flatten() if pos_qc is not None else ["N/A"] * len(juld),
    })

    summary = {
        "wmo": wmo,
        "total_profiles": len(juld),
        "total_level_measurements": total_levels,
        "date_min": str(juld.min()),
        "date_max": str(juld.max()),
        "lat_range": (float(lats.min()), float(lats.max())),
        "lon_range": (float(lons.min()), float(lons.max())),
        "qc_distribution": {
            "TEMP_QC": summarize_qc(temp_qc),
            "PSAL_QC": summarize_qc(psal_qc),
            "PRES_QC": summarize_qc(pres_qc),
        },
        "artifact_counts": {
            "invalid_pres_count": int(invalid_pres.sum()),
            "invalid_temp_count": int(invalid_temp.sum()),
            "invalid_psal_count": int(invalid_psal.sum()),
        },
    }

    return summary, profiles_df


def run_compatibility_analysis():
    print("================================================================================")
    print("              OCEANEMBED: MULTI-DATASET COMPATIBILITY ANALYSIS                  ")
    print("================================================================================\n")

    # 1. Load satellite temporal & spatial boundaries
    sat_info = {}
    sat_files = {
        "SST": DATA_ROOT / "sst" / "sst_north_indian_ocean.nc",
        "SLA": DATA_ROOT / "sea_level" / "sla_north_indian_ocean.nc",
        "Currents": DATA_ROOT / "currents" / "currents_north_indian_ocean.nc",
    }

    for name, p in sat_files.items():
        with xr.open_dataset(p) as ds:
            times = pd.to_datetime(ds["time"].values)
            lat_var = "latitude" if "latitude" in ds else "lat"
            lon_var = "longitude" if "longitude" in ds else "lon"
            lats = ds[lat_var].values
            lons = ds[lon_var].values
            res_lat = round(float(abs(lats[1] - lats[0])), 4) if len(lats) > 1 else None
            res_lon = round(float(abs(lons[1] - lons[0])), 4) if len(lons) > 1 else None
            sat_info[name] = {
                "t_min": times.min(),
                "t_max": times.max(),
                "time_steps": [t.strftime("%Y-%m-%d") for t in times],
                "lat_bounds": (float(lats.min()), float(lats.max())),
                "lon_bounds": (float(lons.min()), float(lons.max())),
                "spatial_res": f"{res_lat}° x {res_lon}° (~{int(res_lat * 111)} km)",
            }

    print("--- 1. SATELLITE DATASET PROPERTIES ---")
    for name, info in sat_info.items():
        print(f"[{name}]")
        print(f"  Time Window:        {info['t_min'].strftime('%Y-%m-%d')} to {info['t_max'].strftime('%Y-%m-%d')} ({len(info['time_steps'])} days: {info['time_steps']})")
        print(f"  Spatial Coverage:   Lat {info['lat_bounds'][0]:.3f}° to {info['lat_bounds'][1]:.3f}°, Lon {info['lon_bounds'][0]:.3f}° to {info['lon_bounds'][1]:.3f}°")
        print(f"  Spatial Resolution: {info['spatial_res']}")
    print()

    # 2. Analyze Argo Floats
    print("--- 2. ARGO FLOAT QUALITY CONTROL & ARTIFACT AUDIT ---")
    argo_summaries = []
    all_profiles_list = []
    for f in (DATA_ROOT / "argo").glob("*_prof.nc"):
        summ, df = analyze_argo_qc(f)
        argo_summaries.append(summ)
        all_profiles_list.append(df)
        print(f"[Float WMO {summ['wmo']}]")
        print(f"  Observation Span:   {summ['date_min'][:10]} to {summ['date_max'][:10]} ({summ['total_profiles']} profile cycles)")
        print(f"  Trajectory Bounds:  Lat {summ['lat_range'][0]:.3f}° to {summ['lat_range'][1]:.3f}°, Lon {summ['lon_range'][0]:.3f}° to {summ['lon_range'][1]:.3f}°")
        print(f"  QC Flags Summary (TEMP_QC): {summ['qc_distribution']['TEMP_QC']}")
        print(f"  QC Flags Summary (PSAL_QC): {summ['qc_distribution']['PSAL_QC']}")
        print(f"  Artifacts / Outliers: Pres < 0: {summ['artifact_counts']['invalid_pres_count']}, Temp Outliers: {summ['artifact_counts']['invalid_temp_count']}, Psal Outliers: {summ['artifact_counts']['invalid_psal_count']}")
    print()

    all_profiles_df = pd.concat(all_profiles_list, ignore_index=True)

    # 3. Match profiles against satellite observation windows
    print("--- 3. SPATIOTEMPORAL PROFILE MATCHING ---")

    # Match against SLA & Currents window (2019-10-28 to 2019-10-31)
    sla_start = pd.to_datetime("2019-10-28")
    sla_end = pd.to_datetime("2019-10-31 23:59:59")
    sla_window_matches = all_profiles_df[
        (all_profiles_df["datetime"] >= sla_start - pd.Timedelta(days=5)) &
        (all_profiles_df["datetime"] <= sla_end + pd.Timedelta(days=5))
    ]

    print(f"Argo profiles within +/- 5 days of SLA / Currents (Oct 28 - Oct 31, 2019): {len(sla_window_matches)}")
    for idx, row in sla_window_matches.iterrows():
        print(f"  Float {row['wmo']} | Cycle {row['cycle']:>3} | Date: {row['datetime'].strftime('%Y-%m-%d %H:%M UTC')} | Lat: {row['latitude']:.3f}°, Lon: {row['longitude']:.3f}°")

    # Match against SST window (2024-05-01 to 2024-05-03)
    sst_start = pd.to_datetime("2024-05-01")
    sst_end = pd.to_datetime("2024-05-03 23:59:59")
    sst_window_matches = all_profiles_df[
        (all_profiles_df["datetime"] >= sst_start - pd.Timedelta(days=30)) &
        (all_profiles_df["datetime"] <= sst_end + pd.Timedelta(days=30))
    ]
    print(f"\nArgo profiles within +/- 30 days of downloaded SST window (May 1 - May 3, 2024): {len(sst_window_matches)}")
    print("  -> (Floats 2902264 and 2902265 operated from 2018 to early 2023, while SST was sampled from May 2024).")

    return sat_info, argo_summaries, sla_window_matches


if __name__ == "__main__":
    run_compatibility_analysis()
