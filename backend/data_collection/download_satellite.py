"""
OceanEmbed - Primary Dataset Collection: Satellite Observations
Module: download_satellite.py

Downloads genuine gridded satellite NetCDF datasets for the North Indian Ocean
(0°N to 25°N, 50°E to 100°E) from official NOAA OceanWatch ERDDAP servers.

Datasets collected:
1. Sea Surface Temperature (SST): NOAA Coral Reef Watch CoralTemp v3.1 Daily (0.05°).
2. Sea Level Anomaly (SLA): NOAA NESDIS/STAR Altimetry Daily.
3. Ocean Surface Currents: NOAA NESDIS/STAR Zonal (U) and Meridional (V) Currents.
"""

import os
import sys
from pathlib import Path
import requests

ERDDAP_BASE = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap"
DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "raw"

# North Indian Ocean spatial coverage (Arabian Sea and Bay of Bengal)
# Latitude: 0°N to 25°N
# Longitude: 50°E to 100°E
SATELLITE_DATASETS = [
    {
        "name": "Sea Surface Temperature (SST)",
        "output_dir": DATA_ROOT / "sst",
        "filename": "sst_north_indian_ocean.nc",
        "url": (
            f"{ERDDAP_BASE}/CRW_sst_v3_1.nc?"
            "analysed_sst[(2024-05-01T12:00:00Z):1:(2024-05-03T12:00:00Z)]"
            "[(0.0):5:(25.0)][(50.0):5:(100.0)]"
        ),
        "source": "NOAA Coral Reef Watch (CRW) CoralTemp v3.1 Daily SST",
        "institution": "NOAA / NESDIS / STAR / OceanWatch",
    },
    {
        "name": "Sea Level Anomaly (SLA)",
        "output_dir": DATA_ROOT / "sea_level",
        "filename": "sla_north_indian_ocean.nc",
        "url": (
            f"{ERDDAP_BASE}/noaa_sla_dt.nc?"
            "sla[(2019-10-28T00:00:00Z):1:(2019-10-31T00:00:00Z)]"
            "[(0.125):1:(24.875)][(50.125):1:(99.875)]"
        ),
        "source": "NOAA/NESDIS/STAR Daily Sea Surface Height Anomalies",
        "institution": "NOAA / NESDIS / STAR / OceanWatch",
    },
    {
        "name": "Ocean Surface Currents (U and V velocities)",
        "output_dir": DATA_ROOT / "currents",
        "filename": "currents_north_indian_ocean.nc",
        "url": (
            f"{ERDDAP_BASE}/noaa_sla_dt.nc?"
            "currents_U[(2019-10-28T00:00:00Z):1:(2019-10-31T00:00:00Z)][(0.125):1:(24.875)][(50.125):1:(99.875)],"
            "currents_V[(2019-10-28T00:00:00Z):1:(2019-10-31T00:00:00Z)][(0.125):1:(24.875)][(50.125):1:(99.875)]"
        ),
        "source": "NOAA/NESDIS/STAR Geostrophic Surface Currents",
        "institution": "NOAA / NESDIS / STAR / OceanWatch",
    },
]


def download_satellite_data() -> list[Path]:
    """Download official satellite NetCDF datasets for the North Indian Ocean."""
    downloaded_files = []

    print("==================================================")
    print("OceanEmbed: Downloading Satellite NetCDF Datasets")
    print("Region: North Indian Ocean (0°N-25°N, 50°E-100°E)")
    print("==================================================")

    for item in SATELLITE_DATASETS:
        out_dir = item["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / item["filename"]

        print(f"\n[+] Fetching {item['name']}...")
        print(f"    Source: {item['source']} ({item['institution']})")
        print(f"    URL: {item['url']}")

        if out_path.exists() and out_path.stat().st_size > 10_000:
            size_kb = out_path.stat().st_size / 1024
            print(f"    [OK] Already downloaded: {out_path.name} ({size_kb:.1f} KB)")
            downloaded_files.append(out_path)
            continue

        try:
            response = requests.get(item["url"], stream=True, timeout=60)
            response.raise_for_status()

            with open(out_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

            size_kb = out_path.stat().st_size / 1024
            print(f"    [SUCCESS] Saved {out_path.name} ({size_kb:.1f} KB)")
            downloaded_files.append(out_path)

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Failed to download {item['name']}: {e}", file=sys.stderr)
            if out_path.exists():
                out_path.unlink()

    return downloaded_files


if __name__ == "__main__":
    download_satellite_data()
