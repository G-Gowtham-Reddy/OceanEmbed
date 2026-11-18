"""
Inspect dates and locations of candidate INCOIS floats.
"""
import requests
import xarray as xr
import pandas as pd
import io

base_url = "https://data-argo.ifremer.fr/dac/incois"
candidates = ['2902271', '2902213', '2902230', '2902250', '2902280', '2902290', '2902300', '2902196']

for fid in candidates:
    prof_url = f"{base_url}/{fid}/{fid}_prof.nc"
    try:
        r = requests.get(prof_url, timeout=20)
        if r.status_code == 200:
            with xr.open_dataset(io.BytesIO(r.content)) as ds:
                juld = pd.to_datetime(ds['JULD'].values)
                valid_t = juld[~pd.isna(juld)]
                lats = ds['LATITUDE'].values
                lons = ds['LONGITUDE'].values
                v_lats = lats[lats < 9000]
                v_lons = lons[lons < 9000]
                if len(valid_t) > 0 and len(v_lats) > 0:
                    t_min = valid_t.min().strftime('%Y-%m-%d')
                    t_max = valid_t.max().strftime('%Y-%m-%d')
                    lat_min = v_lats.min()
                    lat_max = v_lats.max()
                    lon_min = v_lons.min()
                    lon_max = v_lons.max()
                    # Check if North Indian Ocean (Lat >= 0, 50 <= Lon <= 100)
                    in_nio = (lat_max >= 0) and (lon_min <= 100) and (lon_max >= 50)
                    print(f"Float {fid} ({len(r.content)/1024:.0f} KB, {len(valid_t)} profiles): "
                          f"Dates: {t_min} to {t_max} | Lat: {lat_min:.2f} to {lat_max:.2f} | "
                          f"Lon: {lon_min:.2f} to {lon_max:.2f} | In NIO: {in_nio}")
    except Exception as e:
        print(f"Float {fid} error: {e}")
