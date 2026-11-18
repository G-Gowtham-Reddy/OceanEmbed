"""
OceanEmbed - Phase 3 Dataset Collection Pipeline
Module: collect_all.py

Master pipeline that executes:
1. download_argo.py      (Argo CTD profiles from official IFREMER GDAC)
2. download_satellite.py (SST, SLA, Surface Currents from NOAA OceanWatch)
3. inspect_datasets.py   (Deep NetCDF inspection using xarray & netCDF4)
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_collection.download_argo import download_argo_floats
from data_collection.download_satellite import download_satellite_data
from data_collection.inspect_datasets import run_inspection


def main():
    print("================================================================")
    print("   OCEANEMBED: PHASE 3 PRIMARY DATASET COLLECTION PIPELINE      ")
    print("   Target: North Indian Ocean (Arabian Sea & Bay of Bengal)     ")
    print("================================================================\n")

    print(">>> STEP 1: Downloading in-situ Argo profiling float NetCDFs...")
    argo_files = download_argo_floats()
    print(f"\n[+] Argo collection completed: {len(argo_files)} file(s).\n")

    print(">>> STEP 2: Downloading gridded satellite observation NetCDFs...")
    sat_files = download_satellite_data()
    print(f"\n[+] Satellite collection completed: {len(sat_files)} file(s).\n")

    print(">>> STEP 3: Running comprehensive NetCDF inspection with xarray & netCDF4...")
    run_inspection()
    print("\n[+] Phase 3 Primary Dataset Collection completed successfully!")


if __name__ == "__main__":
    main()
