"""
Find additional genuine Argo floats in North Indian Ocean covering 2018-2025.
"""
import requests
import re
import pandas as pd
import xarray as xr
import io

base_url = "https://data-argo.ifremer.fr/dac/incois/"
print("Fetching INCOIS float directory listing...")
r = requests.get(base_url, timeout=15)
float_ids = re.findall(r'href="(\d+)/"', r.text)
print(f"Total floats in INCOIS DAC: {len(float_ids)}")

# Test a sample of candidate float IDs to find their coordinates and date ranges
candidates = [f for f in float_ids if f.startswith("290") or f.startswith("190") or f.startswith("690")]
print(f"Candidate IDs starting with 290/190/690: {len(candidates)}")

# Sample candidate floats from different series
sample_floats = ['2902271', '2902120', '2902196', '2902213', '2902230', '2902240', '2902250', '2902280', '2902290', '2902300', '2902310', '2902320']
# Check existence
for fid in sample_floats:
    prof_url = f"{base_url}{fid}/{fid}_prof.nc"
    try:
        h = requests.head(prof_url, timeout=5)
        if h.status_code == 200:
            sz = int(h.headers.get('content-length', 0)) / (1024 * 1024)
            print(f"Float {fid}: EXISTS ({sz:.2f} MB)")
        else:
            print(f"Float {fid}: Status {h.status_code}")
    except Exception as e:
        print(f"Float {fid}: Error {e}")
