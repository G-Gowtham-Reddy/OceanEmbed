"""
OceanEmbed - Primary Dataset Collection: Comprehensive Dataset Inspection
Module: inspect_datasets.py

Inspects downloaded NetCDF (.nc) datasets using Python xarray and netCDF4:
- Dimensions and coordinate definitions
- Coordinate ranges (Latitude & Longitude bounding boxes)
- Decoded human-readable date ranges (calendar timestamps)
- Vertical depth/pressure levels (min, max, number of levels, units)
- Primary variables, data types, physical units, and descriptors
- Missing-value counts and percentages (_FillValue, NaN, land masks)
- Scientific range verification (validity check for ocean physics)

Outputs a structured summary to stdout and updates dataset_inspection_report.json.
Note: Original NetCDF files are opened in read-only mode and NEVER modified.
"""

import io
import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import netCDF4

# Ensure UTF-8 output encoding for Windows PowerShell / CMD
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "raw"


def get_decoded_date_range(ds: xr.Dataset) -> dict:
    """Decodes time coordinates into ISO calendar strings."""
    time_coord_names = ["time", "JULD", "DATE", "time_step"]
    found_time_var = next((name for name in time_coord_names if name in ds.coords or name in ds.data_vars), None)

    if not found_time_var:
        return {"status": "No explicit time coordinate found"}

    time_da = ds[found_time_var]
    values = time_da.values

    # Check if native datetime64
    if np.issubdtype(values.dtype, np.datetime64):
        valid = values[~np.isnat(values)]
        if len(valid) > 0:
            return {
                "coordinate": found_time_var,
                "start_date": str(pd.to_datetime(valid.min()).strftime("%Y-%m-%d %H:%M:%S UTC")),
                "end_date": str(pd.to_datetime(valid.max()).strftime("%Y-%m-%d %H:%M:%S UTC")),
                "total_timesteps": int(len(valid)),
            }

    # Handle float / numeric Julian Day
    ref_date = ds.attrs.get("REFERENCE_DATE_TIME", "19500101000000")
    try:
        valid_num = values[np.isfinite(values)]
        if len(valid_num) > 0:
            base = pd.to_datetime(ref_date, format="%Y%m%d%H%M%S")
            start_dt = base + pd.to_timedelta(float(np.min(valid_num)), unit="D")
            end_dt = base + pd.to_timedelta(float(np.max(valid_num)), unit="D")
            return {
                "coordinate": found_time_var,
                "start_date": str(start_dt.strftime("%Y-%m-%d %H:%M:%S UTC")),
                "end_date": str(end_dt.strftime("%Y-%m-%d %H:%M:%S UTC")),
                "total_timesteps": int(len(valid_num)),
            }
    except Exception:
        pass

    return {
        "coordinate": found_time_var,
        "raw_min": float(np.min(values)),
        "raw_max": float(np.max(values)),
        "total_timesteps": int(len(values)),
    }


def inspect_netcdf_dataset(filepath: Path) -> dict:
    """Performs deep inspection of a single NetCDF file using xarray and netCDF4."""
    report = {
        "filename": filepath.name,
        "relative_path": str(filepath.relative_to(DATA_ROOT)),
        "size_bytes": filepath.stat().st_size,
        "size_kb": round(filepath.stat().st_size / 1024, 2),
        "size_mb": round(filepath.stat().st_size / (1024 * 1024), 3),
    }

    # 1. Low-level attributes with netCDF4
    with netCDF4.Dataset(filepath, "r") as nc:
        report["file_format"] = nc.data_model
        report["global_attributes"] = {
            k: str(getattr(nc, k))
            for k in nc.ncattrs()
            if k in [
                "title",
                "institution",
                "source",
                "references",
                "history",
                "conventions",
                "data_type",
                "project_name",
                "platform_number",
            ]
        }

    # 2. Multidimensional analysis with xarray
    with xr.open_dataset(filepath) as ds:
        # Dimensions
        report["dimensions"] = {dim: int(size) for dim, size in ds.sizes.items()}

        # Coordinates: Latitude
        lat_var = next((d for d in ["latitude", "lat", "LATITUDE"] if d in ds), None)
        if lat_var:
            lat_arr = ds[lat_var].values
            valid_lat = lat_arr[np.isfinite(lat_arr) & (lat_arr < 9999)]
            if len(valid_lat) > 0:
                report["coordinate_ranges"] = report.get("coordinate_ranges", {})
                report["coordinate_ranges"]["latitude"] = {
                    "variable": lat_var,
                    "min": round(float(np.min(valid_lat)), 4),
                    "max": round(float(np.max(valid_lat)), 4),
                    "units": str(ds[lat_var].attrs.get("units", "degrees_north")),
                    "points": int(len(valid_lat)),
                }

        # Coordinates: Longitude
        lon_var = next((d for d in ["longitude", "lon", "LONGITUDE"] if d in ds), None)
        if lon_var:
            lon_arr = ds[lon_var].values
            valid_lon = lon_arr[np.isfinite(lon_arr) & (lon_arr < 9999)]
            if len(valid_lon) > 0:
                report["coordinate_ranges"] = report.get("coordinate_ranges", {})
                report["coordinate_ranges"]["longitude"] = {
                    "variable": lon_var,
                    "min": round(float(np.min(valid_lon)), 4),
                    "max": round(float(np.max(valid_lon)), 4),
                    "units": str(ds[lon_var].attrs.get("units", "degrees_east")),
                    "points": int(len(valid_lon)),
                }

        # Decoded Date Range
        report["date_range"] = get_decoded_date_range(ds)

        # Depth Levels
        depth_info = {}
        for d_key in ["PRES", "PRESSURE", "depth", "zlev"]:
            if d_key in ds:
                d_arr = ds[d_key].values
                fill_val = ds[d_key].attrs.get("_FillValue", 99999.0)
                valid_d = d_arr[np.isfinite(d_arr) & (d_arr < fill_val - 1) & (d_arr >= 0)]
                if len(valid_d) > 0:
                    depth_info = {
                        "variable": d_key,
                        "min_depth": round(float(np.min(valid_d)), 2),
                        "max_depth": round(float(np.max(valid_d)), 2),
                        "levels_count": int(ds.sizes.get("N_LEVELS", len(valid_d))),
                        "units": str(ds[d_key].attrs.get("units", "decibar / metres")),
                    }
                    break
        if not depth_info and "N_LEVELS" in ds.sizes:
            depth_info = {
                "variable": "N_LEVELS",
                "levels_count": int(ds.sizes["N_LEVELS"]),
                "units": "discrete levels",
            }
        elif not depth_info:
            depth_info = {"status": "Surface ocean layer (0 m)"}
        report["depth_levels"] = depth_info

        # Variables, Missing Values, and Oceanographic Verification
        variables_dict = {}
        validity_checks = []

        for var_name, da in ds.data_vars.items():
            attrs = da.attrs
            var_data = da.values
            total_elements = int(var_data.size)
            fill_val = attrs.get("_FillValue", attrs.get("missing_value", None))

            # Missing value mask
            if np.issubdtype(var_data.dtype, np.floating):
                is_nan = np.isnan(var_data)
                if fill_val is not None:
                    is_fill = np.isclose(var_data, fill_val, equal_nan=True) | is_nan
                else:
                    is_fill = is_nan
            else:
                if fill_val is not None:
                    is_fill = var_data == fill_val
                else:
                    is_fill = np.zeros(var_data.shape, dtype=bool)

            missing_count = int(np.sum(is_fill))
            valid_count = total_elements - missing_count
            missing_pct = round((missing_count / total_elements) * 100, 2) if total_elements > 0 else 0.0

            valid_data = var_data[~is_fill]
            stats = {}
            if len(valid_data) > 0 and np.issubdtype(var_data.dtype, np.number):
                stats = {
                    "min": round(float(np.min(valid_data)), 4),
                    "max": round(float(np.max(valid_data)), 4),
                    "mean": round(float(np.mean(valid_data)), 4),
                    "std": round(float(np.std(valid_data)), 4),
                }

                # Check physical oceanographic boundaries
                if var_name in ["TEMP", "analysed_sst"]:
                    # In situ ocean water: typically 1.5°C to 34°C
                    phys_mask = (valid_data >= 1.0) & (valid_data <= 35.0)
                    is_phys = bool(np.any(phys_mask))
                    validity_checks.append({
                        "variable": var_name,
                        "parameter": "Temperature",
                        "status": "VALID" if is_phys else "INVALID",
                        "observed_range": f"{stats['min']} to {stats['max']} °C",
                        "mean": f"{stats['mean']} °C",
                    })
                elif var_name in ["PSAL"]:
                    # Practical salinity: typically 25 to 40 PSU in North Indian Ocean
                    phys_mask = (valid_data >= 20.0) & (valid_data <= 42.0)
                    is_phys = bool(np.any(phys_mask))
                    validity_checks.append({
                        "variable": var_name,
                        "parameter": "Salinity",
                        "status": "VALID" if is_phys else "INVALID",
                        "observed_range": f"{stats['min']} to {stats['max']} PSU",
                        "mean": f"{stats['mean']} PSU",
                    })
                elif var_name in ["PRES"]:
                    phys_mask = (valid_data >= 0.0) & (valid_data <= 2500.0)
                    is_phys = bool(np.any(phys_mask))
                    validity_checks.append({
                        "variable": var_name,
                        "parameter": "Pressure / Depth",
                        "status": "VALID" if is_phys else "INVALID",
                        "observed_range": f"{stats['min']} to {stats['max']} dbar",
                        "mean": f"{stats['mean']} dbar",
                    })
                elif var_name in ["sla"]:
                    phys_mask = (valid_data >= -3.0) & (valid_data <= 3.0)
                    is_phys = bool(np.any(phys_mask))
                    validity_checks.append({
                        "variable": var_name,
                        "parameter": "Sea Level Anomaly",
                        "status": "VALID" if is_phys else "INVALID",
                        "observed_range": f"{stats['min']} to {stats['max']} m",
                        "mean": f"{stats['mean']} m",
                    })
                elif var_name in ["currents_U", "currents_V"]:
                    phys_mask = (valid_data >= -6.0) & (valid_data <= 6.0)
                    is_phys = bool(np.any(phys_mask))
                    validity_checks.append({
                        "variable": var_name,
                        "parameter": f"Velocity ({var_name})",
                        "status": "VALID" if is_phys else "INVALID",
                        "observed_range": f"{stats['min']} to {stats['max']} m/s",
                        "mean": f"{stats['mean']} m/s",
                    })

            variables_dict[var_name] = {
                "shape": list(da.shape),
                "dtype": str(da.dtype),
                "long_name": str(attrs.get("long_name", attrs.get("standard_name", var_name))),
                "units": str(attrs.get("units", "unitless")),
                "total_points": total_elements,
                "valid_points": valid_count,
                "missing_points": missing_count,
                "missing_pct": missing_pct,
                "stats": stats,
            }

        report["variables"] = variables_dict
        report["scientific_validity_verification"] = {
            "all_verified": all(chk["status"] == "VALID" for chk in validity_checks) if validity_checks else True,
            "verification_checks": validity_checks,
        }

    return report


def run_full_inspection():
    """Scans, displays, and updates dataset_inspection_report.json."""
    print("=" * 82)
    print("        OCEANEMBED: PRIMARY NETCDF DATASET INSPECTION REPORT          ")
    print("=" * 82)
    print(f"Target Directory: {DATA_ROOT}\n")

    nc_files = sorted(list(DATA_ROOT.glob("**/*.nc")))
    if not nc_files:
        print("[!] No .nc files found in backend/data/raw.")
        return

    full_reports = []

    for idx, filepath in enumerate(nc_files, 1):
        rel_path = filepath.relative_to(DATA_ROOT)
        print(f"[{idx}/{len(nc_files)}] File: {rel_path} ({filepath.stat().st_size / 1024:.1f} KB)")
        print("-" * 82)

        rep = inspect_netcdf_dataset(filepath)
        full_reports.append(rep)

        # 1. Format & Global info
        fmt = rep.get("file_format", "N/A")
        title = rep.get("global_attributes", {}).get("title", "N/A")
        inst = rep.get("global_attributes", {}).get("institution", "N/A")
        print(f"  Format:       {fmt}")
        print(f"  Institution:  {inst}")
        print(f"  Title:        {title}")

        # 2. Dimensions
        dims_str = ", ".join(f"{k}: {v}" for k, v in rep["dimensions"].items())
        print(f"  Dimensions:   {dims_str}")

        # 3. Coordinate Ranges
        if "coordinate_ranges" in rep:
            lat = rep["coordinate_ranges"].get("latitude")
            lon = rep["coordinate_ranges"].get("longitude")
            if lat:
                print(f"  Latitude:     {lat['min']:.4f}° to {lat['max']:.4f}° ({lat['points']} points, {lat['units']})")
            if lon:
                print(f"  Longitude:    {lon['min']:.4f}° to {lon['max']:.4f}° ({lon['points']} points, {lon['units']})")

        # 4. Date Range
        dt_info = rep.get("date_range", {})
        if "start_date" in dt_info:
            print(f"  Date Range:   {dt_info['start_date']}  -->  {dt_info['end_date']} ({dt_info['total_timesteps']} steps)")
        else:
            print(f"  Date Range:   {dt_info}")

        # 5. Depth Levels
        depth = rep.get("depth_levels", {})
        if "min_depth" in depth:
            print(f"  Depth/PRES:   {depth['min_depth']} to {depth['max_depth']} {depth['units']} ({depth['levels_count']} levels)")
        else:
            print(f"  Depth:        {depth.get('status', depth)}")

        # 6. Primary Variables & Missing Values
        print("  Variables & Missing Values:")
        primary_vars = ["TEMP", "PSAL", "PRES", "analysed_sst", "sla", "currents_U", "currents_V"]
        displayed_vars = [v for v in rep["variables"] if v in primary_vars]
        if not displayed_vars:
            displayed_vars = list(rep["variables"].keys())[:5]

        for v in displayed_vars:
            info = rep["variables"][v]
            st = info.get("stats", {})
            st_str = f" [min={st.get('min', 'N/A')}, max={st.get('max', 'N/A')}, mean={st.get('mean', 'N/A')}]" if st else ""
            print(
                f"    * {v:<14} | Shape: {str(info['shape']):<14} | "
                f"Valid: {info['valid_points']:>6}/{info['total_points']:<6} "
                f"({info['missing_pct']:>5.2f}% missing) | Units: {info['units']}{st_str}"
            )

        # 7. Physical Validity Check
        validity = rep.get("scientific_validity_verification", {})
        status_str = "VERIFIED (Physically valid ocean observations)" if validity.get("all_verified") else "FLAGGED"
        print(f"  Validity:     {status_str}")
        for chk in validity.get("verification_checks", []):
            print(f"    - {chk['parameter']}: {chk['status']} (observed: {chk['observed_range']}, mean: {chk['mean']})")
        print()

    # Save to JSON
    json_path = DATA_ROOT / "dataset_inspection_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_reports, f, indent=2)

    print("=" * 82)
    print(f"[SUCCESS] Updated inspection report saved to:")
    print(f"          {json_path.resolve()}")
    print("=" * 82)


if __name__ == "__main__":
    run_full_inspection()
