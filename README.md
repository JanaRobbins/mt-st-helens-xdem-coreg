![GitHub repo size](https://img.shields.io/github/repo-size/JanaRobbins/mt-st-helens-xdem-coreg?style=plastic)  ![GitHub last commit](https://img.shields.io/github/last-commit/JanaRobbins/mt-st-helens-xdem-coreg?style=plastic) ![GitHub watchers](https://img.shields.io/github/watchers/JanaRobbins/mt-st-helens-xdem-coreg?style=plastic) ![GitHub repo directory count](https://img.shields.io/github/directory-file-count/JanaRobbins/mt-st-helens-xdem-coreg?style=plastic) ![](https://komarev.com/ghpvc/?username=JanaRobbins&style=plastic&label=Profile+views&color=ff69b4)

# DEM Co-registration – Mount St. Helens

This project performs DEM co-registration and uncertainty assessment for Mount St. Helens crater using the xDEM library.

## Data

Four elevation datasets were used:

- 1979 DEM (10 m, aerial photogrammetric, pre-coregistered)
- 1984 DEM (10 m, aerial photogrammetric, reference DEM, pre-coregistered)
- 2008 DSM (ALOS World 3D, originally 30 m, resampled to 10 m)
- 2025 DEM (USGS 3D Elevation Program, ~10 m resolution)

The 2008 and 2025 datasets were co-registered to the 1984 DEM.

## Method

- The 1984 DEM was used as the reference surface
- A stable terrain mask was manually created in ArcGIS Pro
- Stable areas included only unchanged terrain (outer crater rim and surrounding slopes)
- Areas of change (crater interior, lava dome, glacier) were excluded
- The mask was rasterized to match the DEM grid (same extent, resolution, and alignment)
- Co-registration was performed using the Nuth & Kääb method implemented in xDEM
- Only stable terrain pixels were used for fitting
- NMAD was calculated before and after co-registration

## Workflow

1. Align DEMs to the reference grid (1984 DEM)
2. Apply stable terrain mask
3. Perform Nuth & Kääb co-registration
4. Save corrected DEMs
5. Calculate NMAD before and after correction

## Outputs

- `dem_2008_coreg.tif`
- `dem_2025_coreg.tif`
- `coreg_stats.csv`

## Results

Co-registration reduced elevation differences on stable terrain:

| DEM | NMAD Before | NMAD After |
|-----|------------|-----------|
| 2008 | X.XX m | X.XX m |
| 2025 | X.XX m | X.XX m |

## Requirements

xdem
rasterio
numpy
pandas
matplotlib

## Reproducibility

The full co-registration workflow was implemented in Python using xDEM and is available in this repository.

## Author

Jana Robbins
