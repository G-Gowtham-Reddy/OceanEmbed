"""
OceanEmbed - Primary Dataset Collection: Argo Float Observations
Module: download_argo.py

Downloads genuine in-situ Argo profiling float NetCDF datasets (*_prof.nc)
from the official Argo Global Data Assembly Centre (GDAC) hosted at IFREMER
and Indian National Centre for Ocean Information Services (INCOIS).

Target Region: North Indian Ocean (Arabian Sea and Bay of Bengal).
"""

import os
import sys
from pathlib import Path
import requests

GDAC_BASE_URL = "https://data-argo.ifremer.fr/dac/incois"

# Selected active/comprehensive INCOIS floats in North Indian Ocean:
# - 2902264: Bay of Bengal (9.3°N - 16.7°N, 82.2°E - 90.7°E)
# - 2902265: Arabian Sea (14.6°N - 16.8°N, 68.1°E - 72.6°E)
TARGET_FLOATS = [
    {
        "wmo": "2902264",
        "basin": "Bay of Bengal (North Indian Ocean)",
        "dac": "INCOIS",
    },
    {
        "wmo": "2902265",
        "basin": "Arabian Sea (North Indian Ocean)",
        "dac": "INCOIS",
    },
]

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "argo"


def download_argo_floats(target_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Download authentic Argo NetCDF profile files from the official GDAC."""
    target_dir.mkdir(parents=True, exist_ok=True)
    downloaded_files = []

    print("==================================================")
    print("OceanEmbed: Downloading Argo Profile Datasets")
    print(f"Source: {GDAC_BASE_URL}")
    print(f"Destination: {target_dir}")
    print("==================================================")

    for float_info in TARGET_FLOATS:
        wmo = float_info["wmo"]
        basin = float_info["basin"]
        filename = f"{wmo}_prof.nc"
        url = f"{GDAC_BASE_URL}/{wmo}/{filename}"
        output_file = target_dir / filename

        print(f"\n[+] Fetching Argo Float WMO {wmo} ({basin})...")
        print(f"    URL: {url}")

        if output_file.exists() and output_file.stat().st_size > 100_000:
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"    [OK] Already downloaded: {output_file.name} ({size_mb:.2f} MB)")
            downloaded_files.append(output_file)
            continue

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"    [SUCCESS] Downloaded {filename}: {size_mb:.2f} MB ({downloaded:,} bytes)")
            downloaded_files.append(output_file)

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Failed to download float {wmo}: {e}", file=sys.stderr)
            if output_file.exists():
                output_file.unlink()

    return downloaded_files


if __name__ == "__main__":
    download_argo_floats()
