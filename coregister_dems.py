import os
import sys
from pathlib import Path

# Clear conflicting values
os.environ.pop("PROJ_LIB", None)
os.environ.pop("PROJ_DATA", None)
os.environ.pop("GDAL_DATA", None)

# Correct conda env root from the interpreter path
env_root = Path(sys.executable).resolve().parent
# For your case this should be:
# C:\Users\User\anaconda3\envs\xdem_env

# Candidate locations for PROJ/GDAL data
proj_candidates = [
    env_root / "Library" / "share" / "proj",
    env_root / "Lib" / "site-packages" / "rasterio" / "proj_data",
]

gdal_candidates = [
    env_root / "Library" / "share" / "gdal",
    env_root / "Lib" / "site-packages" / "rasterio" / "gdal_data",
]

proj_path = None
gdal_path = None

for p in proj_candidates:
    if (p / "proj.db").exists():
        proj_path = p
        break

for g in gdal_candidates:
    if g.exists():
        gdal_path = g
        break

print("Python executable:", sys.executable)
print("env_root:", env_root)
print("PROJ candidates:", proj_candidates)
print("GDAL candidates:", gdal_candidates)

if proj_path is None:
    raise RuntimeError("Could not find proj.db in expected conda/rasterio locations.")

os.environ["PROJ_LIB"] = str(proj_path)
os.environ["PROJ_DATA"] = str(proj_path)

if gdal_path is not None:
    os.environ["GDAL_DATA"] = str(gdal_path)

print("Using PROJ path:", os.environ["PROJ_LIB"])
print("Using GDAL path:", os.environ.get("GDAL_DATA", "not set"))
import numpy as np
import pandas as pd
import rasterio
import xdem
import xdem
# -------------------------
# Paths
# -------------------------
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REF_PATH = DATA_DIR / "dem_1984.tif"
DEM_PATHS = [
    DATA_DIR / "dem_2008.tif",
    DATA_DIR / "dem_2025.tif",
]
MASK_PATH = DATA_DIR / "stable_mask.tif"


# -------------------------
# Functions
# -------------------------
def load_mask(mask_path):
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
    return mask.astype(bool)


def get_stats(ref_dem, other_dem, stable_mask):
    ref_arr = np.squeeze(ref_dem.data)
    oth_arr = np.squeeze(other_dem.data)

    diff = ref_arr - oth_arr
    valid = stable_mask & np.isfinite(diff)
    vals = diff[valid]

    return {
        "median": float(np.nanmedian(vals)),
        "nmad": float(xdem.spatialstats.nmad(vals)),
    }


def ensure_same_grid(ref_dem, dem):
    if dem.shape == ref_dem.shape and dem.transform == ref_dem.transform and dem.crs == ref_dem.crs:
        return dem
    return dem.reproject(ref_dem)


# -------------------------
# Main processing
# -------------------------
def main():
    print("Loading reference DEM...")
    ref_dem = xdem.DEM(REF_PATH)

    print("Loading stable mask...")
    stable_mask = load_mask(MASK_PATH)

    results = []

    for dem_path in DEM_PATHS:
        print(f"\nProcessing {dem_path.name}...")

        dem = xdem.DEM(dem_path)
        dem = ensure_same_grid(ref_dem, dem)

        # Before coreg
        before = get_stats(ref_dem, dem, stable_mask)
        print(f"Before NMAD: {before['nmad']:.3f}")

        # Nuth & Kääb
        coreg = xdem.coreg.NuthKaab()

        ref_arr = np.squeeze(ref_dem.data)
        dem_arr = np.squeeze(dem.data)
        valid_mask = stable_mask & np.isfinite(ref_arr) & np.isfinite(dem_arr)

        coreg.fit(
            reference_elev=ref_dem,
            to_be_aligned_elev=dem,
            inlier_mask=valid_mask
        )

        dem_coreg = coreg.apply(dem)

        # Save result
        out_path = OUTPUT_DIR / f"{dem_path.stem}_coreg.tif"
        dem_coreg.save(out_path)
        print(f"Saved: {out_path}")

        # After coreg
        after = get_stats(ref_dem, dem_coreg, stable_mask)
        print(f"After NMAD: {after['nmad']:.3f}")

        results.append({
            "DEM": dem_path.name,
            "Before_NMAD": before["nmad"],
            "After_NMAD": after["nmad"]
        })

    # Save stats
    df = pd.DataFrame(results)
    csv_path = OUTPUT_DIR / "coreg_stats.csv"
    df.to_csv(csv_path, index=False)

    print("\nDONE")
    print(df)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    main()