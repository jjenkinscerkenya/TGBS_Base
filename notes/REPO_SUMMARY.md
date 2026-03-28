# TGBS_Base Repository Comprehensive Summary

## 1. Repository Structure and Overview

The **TGBS_Base** repository contains a comprehensive Python-based remote sensing analysis framework for monitoring landscape metrics, vegetation dynamics, and ecological disturbance in the Kwale County region of Kenya. The project is organized as a package called `tgbs_rs` with the following high-level structure:

```
TGBS_Base/
├── src/tgbs_rs/                    # Main package source code
│   ├── config/                     # Configuration and specifications
│   │   ├── config.py              # File paths, EE datasets, band definitions, constants
│   │   ├── specs.py               # Metric specifications and labeling
│   │   └── config_vis.py           # Visualization configuration
│   ├── data/                        # Data loading and preprocessing modules
│   │   ├── baseline.py            # Global baseline data (BII, forest loss, etc.)
│   │   ├── topography.py          # Terrain analysis (elevation, slope, aspect)
│   │   └── sensors/               # Sensor-specific processing
│   │       ├── hls/               # Harmonized Landsat-Sentinel processing
│   │       ├── sentinel/          # Sentinel-2 specific processing
│   │       ├── landsat/           # Landsat auxiliary processing
│   │       └── dynamic_world/     # Dynamic World land classification
│   ├── metrics/                    # Analysis and metrics calculation
│   │   └── temporal.py            # Temporal aggregation, seasonal/annual metrics
│   ├── visualization/              # Output generation
│   │   ├── plots.py               # Matplotlib-based figure generation
│   │   └── tables.py              # Pandas-based table transformations
│   ├── io.py                       # Data I/O utilities
│   ├── utils.py                    # General utility functions
│   └── __init__.py
├── notebooks/                      # Jupyter notebooks for analysis workflows
│   ├── ee_notebooks/              # Earth Engine data preparation
│   │   ├── baseline_data.ipynb
│   │   ├── composites.ipynb
│   │   ├── landscape_metrics.ipynb
│   │   └── site_aois.ipynb
│   ├── plotting_notebooks/        # Result visualization and analysis
│   │   ├── baseline_plots.ipynb
│   │   ├── disturbance_metrics_plots.ipynb
│   │   ├── landscape_metrics_plots.ipynb
│   │   └── ... (other metric-specific plots)
│   └── landscape_metrics.r
├── aoi/                            # Geospatial boundary files (GeoJSON/GeoPackage)
│   ├── kwale_county.geojson
│   ├── buda_aoi.geojson
│   ├── gogoni_aoi.geojson
│   ├── shimba_hills_aoi.geojson
│   ├── ks_rehab_blocks.geojson
│   └── degraded_1-3_aoi.geojson
├── outputs/                        # Analysis results
│   ├── maps/                      # Map products
│   ├── plots/                     # Figure outputs (organized by metric type)
│   ├── rasters/                   # GeoTIFF raster outputs
│   └── tables/                    # CSV time-series tables
├── references/                     # Documentation and references
├── pyproject.toml                 # Package configuration and dependencies
├── REPO_SUMMARY.md                # This comprehensive summary
└── README.md                       # Installation and basic usage instructions
```

### Key Project Characteristics

- **Temporal Scope**: 2014-2025 analysis window with baseline (2014-2017) and current period (2018-2025)
- **Geospatial Focus**: Kwale County, Kenya with multiple focal, reference, and degraded sites
- **Data Sources**: Google Earth Engine (GEE) with automated collection building and processing
- **Primary Outputs**: Time-series metrics, comparison tables, and anomaly analyses
- **Site Categories**: 
  - **Focal**: KS Rehab (restoration site)
  - **Reference**: Buda, Gogoni, Shimba Hills (undisturbed reference sites)
  - **Degraded**: Degraded 1-3 (degradation comparison sites)

---

## 2. Key Configuration Files and Core Modules

### 2.1 Configuration Layer (`src/tgbs_rs/config/`)

#### [config.py](src/tgbs_rs/config/config.py)
The central configuration file defines all file paths, Earth Engine datasets, spectral band definitions, and analysis constants.

**Key Path Constants:**
- `REPO_ROOT`: Root directory of the repository
- `DATA_DIR`, `OUTPUTS_DIR`, `RASTER_DIR`, `TABLES_DIR`: Output and data directory structures
- `AOI_PATHS`: Dictionary mapping site names to GeoJSON boundary files
- `OUTPUT_DIRS`: Dictionary of output subdirectories

**Global Earth Engine Datasets:**
- **Global Biodiversity Intactness Index (BII)**: 1km resolution biodiversity metrics
- **ESA WorldCover v2.0**: Land cover classification with 11 classes
- **Facebook Meta Canopy Height**: 1m global canopy height model
- **Global Forest Change (Hansen/UMD)**: Forest loss detection and year of disturbance
- **ESA CCI Aboveground Biomass**: Global biomass estimates
- **ISDA Total Soil Carbon**: African soil organic carbon
- **COPERNICUS DEM GLO30**: 30m global elevation model
- **IUCN Protected Areas**: Global protected area boundaries
- **Sentinel-2** collections (L2A surface reflectance and cloud probability)
- **Landsat-8** Collection 2 Level-2C surface reflectance
- **HLS (Harmonized Landsat-Sentinel)**: L30 (Landsat OLI) and S30 (Sentinel MSI) 30m harmonized reflectance

**Spectral Band Definitions & Time-Series Parameters:**
- `S2_BASELINE_START`, `BASELINE_START/END`, `CURRENT_START/END`: Temporal windows for analysis
- `WET_MONTHS`, `DRY_MONTHS`: Seasonal month definitions
- `FOCAL_LABEL`, `REFERENCE_LABEL`, `DEGRADED_LABEL`: Site category identifiers
- Cloud filtering thresholds, scale factors, and mosaic parameters for each sensor

#### [specs.py](src/tgbs_rs/config/specs.py)
Metadata specifications for metrics, sources, and seasons that control analysis workflows and figure generation.

**Core Specifications:**
- **METRIC_SPECS**: Defines metric families (vegetation_cover, moisture_disturbance), priority levels (primary/supporting/optional), and directional interpretation (higher_is_better)
  - Vegetation metrics: NDVI, SAVI, EVI
  - Moisture/Disturbance metrics: NDMI, NBR
- **SOURCE_SPECS**: Data source roles (official_long_term vs. supplemental_current_period) with temporal bounds
  - HLS: 2014-2025 (long-term archive)
  - Sentinel-2: 2019-2025 (high-resolution current period)
- **SEASON_SPECS**: Seasonal definitions (wet, dry) with processing priorities
- **Plotting Order Families**: Define family-aware metric ordering for consistent visualization

#### [config_vis.py](src/tgbs_rs/config/config_vis.py)
Visualization configuration for consistent theming, color palettes, and figure specifications across outputs.

### 2.2 Core Data Modules (`src/tgbs_rs/data/`)

#### [baseline.py](src/tgbs_rs/data/baseline.py)
Loads and processes global baseline datasets (not time-varying).

**Key Functions:**
- `get_forest_2000()`: Extract 2000 tree canopy cover from Global Forest Change
- `get_forest_loss_image()`: Binary forest loss detection layer
- `get_forest_loss_year_image()`: Year of forest loss occurrence
- `load_bii_image()` / `process_bii_image()`: Load and process Biodiversity Intactness Index with masking
- `get_bii_all()`: Clipped BII band to AOI
- Elevation, slope, aspect, and hillshade calculations

#### [topography.py](src/tgbs_rs/data/topography.py)
Terrain analysis utilities using COPERNICUS DEM.

**Key Functions:**
- `calc_elevation()`: Extract and mosaic DEM
- `calc_slope()`: Compute slope in degrees
- `calc_aspect()`: Compute aspect from DEM
- `calc_hillshade()`: Generate hillshade for visualization
- `calc_terrain()`: Build complete terrain stack (elevation, slope, aspect, hillshade)

#### [io.py](src/tgbs_rs/io.py)
Data input/output operations for Earth Engine and local file interactions.

#### [utils.py](src/tgbs_rs/utils.py)
General utility functions including:
- `_clip_and_mask_image()`: Clip and mask images to AOI while preserving existing masks
- `clip_collection_to_aoi()`: Apply clipping to all images in a collection
- `geojson_to_ee_geometry()`: Convert local GeoJSON files to Earth Engine geometries
- `build_site_feature()` / `load_site_feature()`: Build metadata-rich site features from boundaries
- `build_default_sites_featurecollection()`: Build standard TGBS site collection (KS Rehab, reference sites, degraded sites)
- `buffer_sites_fc()`: Buffer site geometries while preserving properties

### 2.3 Metrics Module (`src/tgbs_rs/metrics/`)

#### [temporal.py](src/tgbs_rs/metrics/temporal.py)
**Purpose**: Central module for temporal aggregation, statistical reduction, and calculation of annual and seasonal metrics from image collections.

**Key Function Categories:**

**A. Time Window and Composite Building:**
- `_time_windows()`: Create annual or monthly feature collections defining analysis windows
- `_apply_stat()`: Apply median or mean compositing to image collections
- `build_period_composites()`: Build single-band or multi-band annual/monthly composites with image counts and metadata
- `build_index_collections()`: Create separate composite collections for each band/index

**B. Spatial Reduction and Time-Series Extraction:**
- `reduce_image_over_sites()`: Reduce single image over site polygons with specified reducer (mean, median, etc.)
- `collection_to_site_timeseries()`: Map spatial reduction across entire image collection to produce long-format site time-series
- `build_index_timeseries()`: Convert dictionary of composite collections into per-site time-series for each index

**C. Annual Metrics Workflow:**
- `build_annual_metrics_long_table()`: Transform prepared annual dataframe to long-format metrics table
- `build_annual_metrics_outputs()`: Generate comprehensive annual comparison products including:
  - Category summaries (mean per site-category-year)
  - Reference and degraded envelopes (min/max/mean bounds)
  - Focal site series isolated
  - Focal vs. reference comparisons
  - Baseline ranges for standardization
  - Standardized anomalies relative to reference baseline
  - Baseline vs. current period summaries
  - Linear trend estimates per site
- `run_annual_metrics_workflow()`: Convenient wrapper executing full annual pipeline
- `plot_annual_metrics_core_figures()`: Generate focal-vs-envelope comparison plots
- `plot_annual_metrics_category_figures()`: Generate category mean trajectory diagnostic plots

**D. Seasonal Metrics Workflow:**
- `build_seasonal_metrics_long_table()`: Filter and reshape seasonal data to long format
- `build_seasonal_metrics_outputs()`: Generate seasonal comparison products (parallel to annual)
- `run_seasonal_metrics_workflow()`: Convenient seasonal pipeline wrapper
- `plot_seasonal_metrics_core_figures()`: Generate seasonal comparison plots

### 2.4 Visualization Module (`src/tgbs_rs/visualization/`)

#### [plots.py](src/tgbs_rs/visualization/plots.py)
Matplotlib-based figure generation for remote sensing outputs.

#### [tables.py](src/tgbs_rs/visualization/tables.py)
Pandas-based data transformations for table generation and analysis outputs:
- Long-format table reshaping
- Category summaries and envelopes
- Baseline range calculations
- Anomaly standardization
- Trend computation

---

## 3. HLS and Sentinel Data Sources with Spectral Indices

### 3.1 Overview: Two-Sensor Strategy

The TGBS project uses a complementary two-sensor approach for optical time-series analysis:

| Aspect | HLS | Sentinel-2 |
|--------|-----|-----------|
| **Role** | Official long-term optical archive | High-resolution current period analysis |
| **Temporal Coverage** | 2014-2025 | 2019-2025 |
| **Spatial Resolution** | 30m harmonized | 10-20m native |
| **Compositing** | Annual/monthly | Annual/monthly |
| **Primary Use** | Trend detection, baseline establishment | Current state validation, detailed anomaly analysis |

### 3.2 HLS Data Source: Long-Term Archive (2014-2025)

#### Overview
The **Harmonized Landsat-Sentinel (HLS)** dataset provides a fused, consistently-processed 30m optical time-series combining:
- **HLSL30**: Landsat 8 OLI (Operational Land Imager) observations
- **HLSS30**: Sentinel-2 MSI (Multispectral Instrument) observations harmonized to Landsat 8 band structure

HLS is the official long-term optical archive for the TGBS project because it provides:
- Consistent processing and radiometric calibration across both sensors
- Seamless temporal coverage at high cadence (5-day combined revisit)
- Coverage since 2014 (Landsat-8 launch), enabling robust baseline establishment
- Pre-harmonized band structure eliminating cross-sensor complications

#### HLS Band Structure and Base Reflectance Bands
Both HLSL30 and HLSS30 are harmonized to the same output band schema through [hls_preprocessing.py](src/tgbs_rs/data/sensors/hls/hls_preprocessing.py):

**Harmonized HLS Common Bands (50m and 30m outputs):**
- **BLUE** (wavelength ~0.48 µm): B2 (L30) / B2 (S30) – Blue reflectance, water detection
- **GREEN** (wavelength ~0.56 µm): B3 (L30) / B3 (S30) – Green reflectance, vegetation vigor
- **RED** (wavelength ~0.65 µm): B4 (L30) / B4 (S30) – Red reflectance, vegetation absorption
- **NIR** (wavelength ~0.87 µm): B5 (L30) / B8A (S30) – Near-infrared, vegetation response
- **SWIR1** (wavelength ~1.61 µm): B6 (L30) / B11 (S30) – Shortwave IR, vegetation moisture
- **SWIR2** (wavelength ~2.19 µm): B7 (L30) / B12 (S30) – Shortwave IR, biomass/fire detection

#### HLS Cloud and Quality Masking ([hls_masking.py](src/tgbs_rs/data/sensors/hls/hls_masking.py))
HLS includes Fmask-based quality assurance flags that are parsed and applied:

**Fmask Quality Interpretation:**
- Bit 1: Cloud
- Bit 2: Adjacent to cloud/shadow (optional masking)
- Bit 3: Cloud shadow
- Bit 4: Snow/ice (optional masking)
- Bit 5: Water (optional masking)
- Bits 6-7: Aerosol level (optional moderate/high aerosol masking)

**Configuration** (from [config.py](src/tgbs_rs/config/config.py)):
```python
HLS_CLOUD_FILTER = 50           # Max cloud coverage percentage per image
HLS_MASK_ADJACENT = True        # Include adjacent-to-cloud masking
HLS_MASK_SNOW = True            # Include snow/ice masking
HLS_MASK_WATER_IN_QA = False    # Keep False; use spectral masking instead
HLS_MASK_HIGH_AEROSOL = True    # Include high aerosol masking
```

**Processing Pipeline:**
1. Filter L30 and S30 collections by AOI, date range, and cloud percentage
2. Parse Fmask QA bits and construct cloud/shadow mask
3. Apply inverse mask (inverted cloud layer) to all reflectance bands
4. Merge L30 and S30 collections (sorted by date) into unified time-series
5. Optional water masking using spectral thresholds (MNDWI, NDVI, NIR)

**Key Functions:**
- `build_cloudfree_hls_l30_col()`: L30 with Fmask masking applied
- `build_cloudfree_hls_s30_col()`: S30 with Fmask masking applied
- `get_hls_merged_collection()`: Combined L30+S30 with optional water masking
- `build_hls_non_water_mask()`: Spectral water detection (MNDWI > 0.1, NDVI < 0.2, NIR < 0.15)

#### HLS Spectral Indices ([hls_indices.py](src/tgbs_rs/data/sensors/hls/hls_indices.py))
The full TGBS-oriented HLS index set calculated via `calc_tgbs_indices()`:

**Vegetation Indices:**
- **NDVI** (Normalized Difference Vegetation Index): $(NIR - RED) / (NIR + RED)$
  - Standard proxy for green vegetation vigor and cover
  - Range: -1 to +1 (higher = more vegetation)
  
- **EVI** (Enhanced Vegetation Index): $2.5 \times \frac{NIR - RED}{NIR + 6 \times RED - 7.5 \times BLUE + 1}$
  - Improved vegetation sensitivity in higher biomass and variable soil backgrounds
  - Reduces atmospheric and soil influences
  
- **SAVI** (Soil-Adjusted Vegetation Index): $\frac{NIR - RED}{NIR + RED + L} \times (1 + L)$ (L=0.5)
  - Reduces soil background effects in sparsely vegetated landscapes
  - Stabilizes index in areas with low vegetation cover

**Water/Moisture Indices:**
- **NDWI** (Normalized Difference Water Index): $(GREEN - NIR) / (GREEN + NIR)$
  - Highlights surface water and vegetation water-related contrast
  
- **MNDWI** (Modified Normalized Difference Water Index): $(GREEN - SWIR1) / (GREEN + SWIR1)$
  - Enhances open-water detection against land surfaces
  - Minimizes vegetation and soil reflectance
  
- **NDMI** (Normalized Difference Moisture Index): $(NIR - SWIR1) / (NIR + SWIR1)$
  - Moisture-sensitive index for vegetation and surface dryness assessment
  - Indicates water stress in vegetation

**Disturbance / Biomass-Proxy Indices:**
- **NBR** (Normalized Burn Ratio): $(NIR - SWIR2) / (NIR + SWIR2)$
  - Burn severity detection and broader disturbance screening
  - Sensitive to biomass changes and charring
  
- **NIRv** (Near-Infrared Reflectance of Vegetation): $NIR \times NDVI$
  - Vegetation productivity proxy combining NIR reflectance and NDVI
  - Correlates with light-use efficiency and gross primary productivity (GPP)

**Core HLS Functions:**
- `select_base_hls_bands()`: Extract the 6-band harmonized stack (BLUE, GREEN, RED, NIR, SWIR1, SWIR2)
- `calc_tgbs_indices()`: Add all 8 indices (NDVI, EVI, NDWI, MNDWI, SAVI, NDMI, NBR, NIRv)
- Individual index functions for selective calculation

#### HLS Preprocessing Functions ([hls_preprocessing.py](src/tgbs_rs/data/sensors/hls/hls_preprocessing.py))
- `validate_hls_date_range()`: Verify requested date range overlaps with available HLS imagery
- `harmonize_hls_l30_bands()`: Rename L30 bands to common schema
- `harmonize_hls_s30_bands()`: Rename S30 bands to common schema
- `process_hls_l30_image()`: Band renaming + index calculation for L30
- `process_hls_s30_image()`: Band renaming + index calculation for S30
- `get_hls_l30_collection()`: Return processed L30 collection
- `get_hls_s30_collection()`: Return processed S30 collection
- `get_hls_merged_collection()`: Return merged L30+S30 with optional water masking (recommended)

---

### 3.3 Sentinel-2 Data Source: High-Resolution Current Period (2019-2025)

#### Overview
**Sentinel-2** (Copernicus Sentinel-2A and 2B) provides high-resolution multispectral imagery at 10m (VNIR), 20m (red-edge), and 60m (coastal/SWIR) native resolution. The TGBS project uses the **Copernicus/S2_SR_HARMONIZED** collection (Level-2A surface reflectance, radiometrically harmonized) as a supplemental higher-resolution platform for the 2019-2025 current period.

**Advantages over HLS for detailed analysis:**
- Native 10m resolution (vs. 30m HLS) enables finer site discrimination
- Additional red-edge band (B8A) sensitive to chlorophyll and canopy stress
- Higher temporal frequency (~5-day revisit)
- Excellent for detecting intra-annual and sub-pixel variability

**Limitation:**
- Sentinel-2 coverage begins in 2015 (data quality from 2015-2016 variable); standardized processing from 2019 onward

#### Sentinel-2 Band Structure and Base Reflectance Bands
[sentinel_preprocessing.py](src/tgbs_rs/data/sensors/sentinel/sentinel_preprocessing.py) selects and scales the following Sentinel-2 bands to a common analysis set:

**Native Sentinel-2 Bands (Level-2A Surface Reflectance, COPERNICUS/S2_SR_HARMONIZED):**
- **B2** (BLUE, wavelength ~0.49 µm, 10m): Blue reflectance, water detection
- **B3** (GREEN, wavelength ~0.56 µm, 10m): Green reflectance, vegetation vigor
- **B4** (RED, wavelength ~0.67 µm, 10m): Red reflectance, vegetation absorption
- **B5, B6, B7**: Red-edge bands (20m, ~0.71-0.78 µm) – sensitive to chlorophyll; not used in indices but available
- **B8** (NIR, wavelength ~0.84 µm, 10m): Near-infrared reflectance, vegetation structure
- **B8A** (Red-Edge NIR, wavelength ~0.87 µm, 20m): Red-edge band, chlorophyll and canopy stress
- **B11** (SWIR1, wavelength ~1.61 µm, 20m): Shortwave IR, vegetation moisture
- **B12** (SWIR2, wavelength ~2.19 µm, 20m): Shortwave IR, biomass/fire detection

**Scale Factor:** Sentinel-2 L2A data is scaled by `S2_SCALE_FACTOR = 0.0001` to convert integer reflectance (0-10000) to normalized reflectance (0-1).

#### Sentinel-2 Cloud and Quality Masking ([sentinel_masking.py](src/tgbs_rs/data/sensors/sentinel/sentinel_masking.py))
Sentinel-2 cloud/shadow masking is sophisticated and includes multiple steps:

**Cloud Detection Approach:**
1. **S2Cloudless Probability**: Join Sentinel-2 SR with s2cloudless cloud probability collection
   - Threshold: `CLD_PRB_THRESH = 40%` (pixels with >40% cloud probability masked)
   
2. **Dark Pixel Shadow Detection**: Identify dark pixels in NIR (B8 < 0.15 reflectance) over non-water areas
   - Threshold: `NIR_DRK_THRESH = 0.15`
   
3. **Directional Shadow Projection**: Project detected clouds along solar azimuth to find cast shadows
   - Shadow search distance: `CLD_PRJ_DIST_KM = 1.0` km
   - Scale: `DDT_SCALE_M = 100` m (directional distance transform)
   
4. **Morphological Refinement**: Apply erosion and dilation to denoise mask
   - Erosion radius: `ERODE_RADIUS_M = 40` m
   - Dilation buffer: `BUFFER_M = 50` m
   - Morphology scale: `MORPH_SCALE_M = 20` m

**Configuration** (from [config.py](src/tgbs_rs/config/config.py)):
```python
CLOUD_FILTER = 50               # Max CLOUDY_PIXEL_PERCENTAGE per image
CLD_PRB_THRESH = 40            # % s2cloudless probability threshold
NIR_DRK_THRESH = 0.15          # Reflectance threshold for dark pixels
CLD_PRJ_DIST_KM = 1.0          # Max shadow search distance (km)
BUFFER_M = 50                  # Dilation buffer (m)
ERODE_RADIUS_M = 40            # Erosion radius (m)
```

**Processing Pipeline:**
1. Filter Sentinel-2 SR by AOI, date range, and pixel-level cloud percentage
2. Mask noisy edge pixels using B8A (20m) and B9 (60m) native masks
3. Join with s2cloudless cloud probability collection by system:index
4. Add cloud/shadow mask band (`cloudmask`) using probability, dark pixels, and shadow projection
5. Apply inverse mask to all reflectance bands
6. Optional water masking using spectral thresholds (same as HLS)

**Key Functions:**
- `build_cloudfree_s2sr_col()`: S2 SR with cloud/shadow masking applied (recommended)
- `add_cld_shdw_mask()`: Construct cloud/shadow mask from s2cloudless + dark pixels + shadow projection
- `build_s2_non_water_mask()`: Spectral water detection (MNDWI > 0.1, NDVI < 0.2, NIR < 0.15)

#### Sentinel-2 Spectral Indices ([sentinel_indices.py](src/tgbs_rs/data/sensors/sentinel/sentinel_indices.py))
The full TGBS-oriented Sentinel-2 index set calculated via `calc_tgbs_indices()`:

**Vegetation Indices:**
- **NDVI**: $(B8 - B4) / (B8 + B4)$
  - Standard vegetation vigor and cover proxy
  
- **EVI**: $2.5 \times \frac{B8 - B4}{B8 + 6 \times B4 - 7.5 \times B2 + 1}$
  - Enhanced sensitivity in dense biomass; same formula as HLS
  
- **SAVI**: $\frac{B8 - B4}{B8 + B4 + L} \times (1 + L)$ (L=0.5)
  - Soil background reduction; same as HLS

**Water/Moisture Indices:**
- **NDWI**: $(B3 - B8) / (B3 + B8)$
  - Water and vegetation water-contrast detection
  
- **MNDWI**: $(B3 - B11) / (B3 + B11)$
  - Open-water enhancement
  
- **NDMI**: $(B8 - B11) / (B8 + B11)$
  - Vegetation and surface moisture assessment

**Disturbance / Biomass-Proxy Indices:**
- **NBR**: $(B8 - B12) / (B8 + B12)$
  - Burn and disturbance detection
  
- **NIRv**: $B8 \times NDVI$
  - Productivity proxy; same as HLS

**Red-Edge Index (Sentinel-2 Exclusive):**
- **NDRE** (Normalized Difference Red Edge): $(B8A - B5) / (B8A + B5)$
  - Red-edge vegetation condition proxy sensitive to canopy chlorophyll and biomass variation
  - Unique to Sentinel-2; not available in HLS at same resolution
  - Useful for detecting subtle canopy stress and LAI variation

**Core Sentinel-2 Functions:**
- `select_base_s2_bands()`: Select all 10 reflectance bands (B2-B8, B8A, B11, B12)
- `calc_tgbs_indices()`: Add all 9 indices (NDVI, EVI, NDWI, MNDWI, SAVI, NDMI, NBR, NIRv, NDRE)
- Individual index functions for selective calculation

#### Sentinel-2 Preprocessing Functions ([sentinel_preprocessing.py](src/tgbs_rs/data/sensors/sentinel/sentinel_preprocessing.py))
- `validate_s2_sr_date_range()`: Verify requested date range overlaps with available Sentinel-2 imagery
- `process_s2_image()`: Select base bands, apply scale factor, calculate indices, preserve metadata
- `get_s2_sr_collection()`: Return processed Sentinel-2 collection with optional water masking (recommended)

---

### 3.4 Index Summary and Use Cases

| Index | Category | Data Type | Formula | Primary Use | HLS | S2 | S2-Only |
|-------|----------|-----------|---------|-------------|-----|----|----|
| NDVI | Vegetation | Normalized Difference | $(NIR - RED)/(NIR + RED)$ | Vegetation cover & vigor | ✓ | ✓ | |
| EVI | Vegetation | Enhanced | $2.5 \times (NIR - RED)/(NIR + 6R - 7.5B + 1)$ | High-biomass adjustment | ✓ | ✓ | |
| SAVI | Vegetation | Soil-Adjusted | $(NIR - RED)/(NIR + RED + 0.5) \times 1.5$ | Low-cover areas | ✓ | ✓ | |
| NDWI | Water/Moisture | Normalized Difference | $(GREEN - NIR)/(GREEN + NIR)$ | Water & vegetation moisture | ✓ | ✓ | |
| MNDWI | Water/Moisture | Modified Normalized | $(GREEN - SWIR1)/(GREEN + SWIR1)$ | Open-water detection | ✓ | ✓ | |
| NDMI | Water/Moisture | Normalized Difference | $(NIR - SWIR1)/(NIR + SWIR1)$ | Vegetation dryness | ✓ | ✓ | |
| NBR | Disturbance | Normalized Difference | $(NIR - SWIR2)/(NIR + SWIR2)$ | Burn & disturbance | ✓ | ✓ | |
| NIRv | Productivity | Product | $NIR \times NDVI$ | Productivity proxy | ✓ | ✓ | |
| NDRE | Vegetation (Chlorophyll) | Normalized Difference | $(B8A - B5)/(B8A + B5)$ | Canopy chlorophyll/stress | | ✓ | ✓ |

---

## 4. Temporal Aggregation and Metrics Calculation with temporal.py

### 4.1 Overview and Purpose

The [temporal.py](src/tgbs_rs/metrics/temporal.py) module is the **central processing engine** for the TGBS project. Its core purpose is to:

1. **Aggregate image collections** into temporally-reduced composites (annual/monthly)
2. **Reduce spatial data** to site-level statistics using polygon aggregation
3. **Build time-series tables** linking spectral indices to site, year, season, and category
4. **Calculate baseline metrics** and anomaly detection
5. **Generate comparison products** (focal vs. reference, trends, envelopes)
6. **Orchestrate analysis workflows** (annual and seasonal pipelines)

The module transitions seamlessly from Earth Engine image processing (lazy evaluation) to pandas DataFrames (eager computation), enabling efficient large-scale time-series analysis while maintaining interpretability through structured table outputs.

### 4.2 Time-Window and Composite Building

#### Purpose
Raw satellite imagery is noisy due to clouds, atmospheric variability, and sensor differences. The first step in time-series analysis is to aggregate multiple images within defined temporal windows into clean, reduceable composites.

#### Key Concepts

**Temporal Scale:** Analysis windows can be defined at annual or monthly scales:
- **Annual**: One composite per calendar year (Jan 1 - Dec 31)
- **Monthly**: One composite per calendar month (e.g., Jan 2014, Feb 2014, etc.)

**Composite Statistic:** Multiple images within a window are reduced to a single output using:
- **Median**: Default; robust to outliers and persistent clouds
- **Mean**: Alternative; captures average conditions

**Metadata Tracking:** Each composite image carries property metadata:
- `system:time_start`: Composite window start timestamp
- `date`: Human-readable date (YYYY-MM-dd format)
- `year`, `month`, `day`: Temporal components
- `image_count`: Number of source images in composite (important for data quality)
- `temporal_scale`: "annual" or "monthly"
- `composite_stat`: "median" or "mean"

#### Key Functions

**`_time_windows(start_date, end_date, temporal_scale)`**
Builds a feature collection of temporal windows (annual or monthly) spanning the analysis period.
- **Input**: `start_date`, `end_date` (ee.Date), `temporal_scale` ("annual" or "monthly")
- **Output**: `ee.FeatureCollection` with one feature per window, containing window bounds and date properties
- **Example**: `_time_windows("2014-01-01", "2017-12-31", "annual")` → 4 annual windows

**`_apply_stat(collection, composite_stat)`**
Applies a compositing statistic (median or mean) to reduce an image collection to a single image.
- **Input**: `ee.ImageCollection`, `composite_stat` ("median" or "mean")
- **Output**: `ee.Image` (single composite)

**`build_period_composites(collection, bands, start_date, end_date, temporal_scale="annual", composite_stat="median")`**
Orchestrates the full composite-building workflow. For each temporal window:
1. Filters the image collection to that window
2. Counts images in the window
3. Applies the compositing statistic
4. Attaches metadata properties to the output composite

- **Input**: `ee.ImageCollection`, list of band names, date range, temporal scale, statistic
- **Output**: `ee.ImageCollection` with composites (typically 4-12 images for annual or 48-144 for monthly)
- **Example Use**: Annual HLS median composites aggregating 5-20 acquisition per year into 1 clean image

**`build_index_collections(collection, bands, start_date, end_date, temporal_scale, composite_stat)`**
Convenience wrapper creating one separate composite collection **per band/index**. Useful when each index needs independent downstream processing.

- **Input**: Same as `build_period_composites`
- **Output**: `dict[str, ee.ImageCollection]` with one entry per band
- **Example**: `{"NDVI": <annual NDVI composites>, "NDMI": <annual NDMI composites>, ...}`

---

### 4.3 Spatial Reduction and Time-Series Extraction

#### Purpose
After temporal compositing, the next step is to extract site-level statistics by reducing each composite image to summary values within site polygon boundaries.

#### Key Concepts

**Reducer:** An Earth Engine operation that summarizes pixel values over a region:
- Default: `ee.Reducer.mean()` (average reflectance/index over site polygon)
- Alternatives: median, min, max, stdDev, percentiles, etc.

**Tile Scale:** Parameter controlling computation breakdown for Earth Engine:
- Default: `tile_scale=4` (balance between precision and memory)
- Increase if hitting memory limits; decrease for higher precision

**Scale (pixels):** Resolution used for reduction:
- Default: `scale=10` (10m pixels)
- Match actual sensor resolution (10m for Sentinel, 30m for HLS) for accurate statistics

#### Key Functions

**`reduce_image_over_sites(image, sites_fc, bands=None, reducer=None, scale=10, tile_scale=4)`**
Reduces a **single image** over all site polygons and attaches image metadata.

- **Input**: `ee.Image`, `ee.FeatureCollection` (sites), list of band names, `ee.Reducer`, spatial resolution
- **Output**: `ee.FeatureCollection` where each feature is one site with columns for:
  - Site properties (site_id, site_name, site_category)
  - Reduced band values (mean NDVI, mean NDMI, etc.)
  - Image-level metadata (year, date, image_count, temporal_scale, composite_stat)

**`collection_to_site_timeseries(collection, sites_fc, bands, reducer=None, scale=10, tile_scale=4)`**
Maps `reduce_image_over_sites` across an **entire image collection** to build a long-format time-series table.

1. Iterates through each composite image in the collection
2. Reduces that image to sites using `reduce_image_over_sites`
3. Flattens all site-reduction results into a single FeatureCollection
4. Exports as a pandas DataFrame or CSV

- **Input**: `ee.ImageCollection`, `ee.FeatureCollection`, band list, etc.
- **Output**: `ee.FeatureCollection` with shape: (N_sites × N_images) rows, each row = one site-image combination
- **Example**: Annual HLS collection (4 composites) × 7 sites → 28 rows (site-year pairs)

**`build_index_timeseries(collections_dict, sites_fc, reducer=None, scale=10, tile_scale=4)`**
Orchestrates `collection_to_site_timeseries` for **multiple indices simultaneously**.

- **Input**: `dict[str, ee.ImageCollection]` (e.g., one collection per index), sites_fc
- **Output**: `dict[str, ee.FeatureCollection]` with one FeatureCollection per index variable
- **Example**: Starting with `{"NDVI": <collection>, "NDMI": <collection>, ...}` produces timeseries for each index that can be individually exported

---

### 4.4 Annual Metrics Workflow

#### Overview
The annual metrics workflow is the primary analysis pipeline for the TGBS project. It takes prepared annual site-level data and generates comprehensive comparison products for focal vs. reference/degraded analysis.

#### Data Flow Diagram
```
Annual Time-Series DataFrame (site, year, metric columns)
                    ↓
         [build_annual_metrics_long_table]
                    ↓
         Long-Format Annual Table (one row per site-year-metric)
                    ↓
         [build_annual_metrics_outputs]
                    ↓
    ┌─────────────────────────────────────────────────┐
    │ Dictionary of 11 Derived Output Products:       │
    ├─────────────────────────────────────────────────┤
    │ annual_long: Long-format input                  │
    │ category_summary: Mean per site-category-year   │
    │ reference_envelope: Min/mean/max per year       │
    │ degraded_envelope: Min/mean/max per year        │
    │ focal: Focal site series isolated               │
    │ focal_vs_reference: Joined comparison           │
    │ focal_vs_degraded: Joined comparison            │
    │ reference_baseline_ranges: Stats for anomalies  │
    │ focal_reference_anomalies: Standardized anomaly │
    │ period_summary: Baseline vs. current avg        │
    │ site_trends: Linear trend per site              │
    └─────────────────────────────────────────────────┘
```

#### Key Functions

**`build_annual_metrics_long_table(annual_df, metric_cols, extra_cols=None)`**
Transforms a prepared annual site-metric DataFrame into long-format (melted) table suitable for grouped analysis and plotting.

- **Input**: Annual DataFrame with columns [site_id, year, metric1, metric2, ...], list of metric column names
- **Output**: Long DataFrame with columns [site_id, site_name, site_category, year, date, image_count, metric, value]
  - One row per site-year-metric combination
  - All metadata columns preserved for filtering and grouping

**Example Input:**
```
site_id  site_name  site_category  year  NDVI   NDMI   date
ks_rehab KS Rehab   focal          2014  0.567  0.234  2014-01-01
```

**Example Output:**
```
site_id  site_name  site_category  year  date       metric  value
ks_rehab KS Rehab   focal          2014  2014-01-01 NDVI    0.567
ks_rehab KS Rehab   focal          2014  2014-01-01 NDMI    0.234
```

**`build_annual_metrics_outputs(annual_long_df)`**
Generates all 11 derived annual analysis products from the long-format table:

1. **`category_summary`**: Mean values per site-category-year
   - Used for: Envelope construction, category diagnostics
   
2. **`reference_envelope`**: Min, mean, max bounds per year for reference sites
   - Used for: Focal-vs-reference comparison
   
3. **`degraded_envelope`**: Min, mean, max bounds per year for degraded sites
   - Used for: Focal-vs-degraded comparison (optional)
   
4. **`focal`**: Focal site (KS Rehab) series isolated into long format
   - Used for: Comparison targets
   
5. **`focal_vs_reference`**: Focal values joined to reference envelope on year
   - Columns: year, metric, focal_value, reference_min, reference_mean, reference_max
   - Used for: Plotting focal trajectories against envelope
   
6. **`focal_vs_degraded`**: Same as focal_vs_reference but with degraded envelope
   - Used for: Alternative comparison
   
7. **`reference_baseline_ranges`**: Mean ± std per metric for reference sites during baseline period (2014-2017)
   - Used for: Standardization and anomaly calculation
   
8. **`focal_reference_anomalies`**: Standardized anomaly = (focal_value - reference_mean) / reference_std
   - Values > |1| indicate anomalies beyond 1σ
   - Used for: Anomaly detection plots
   
9. **`period_summary`**: Mean per metric for baseline (2014-2017) vs. current (2018-2025) periods
   - Used for: Period-level comparison statistics
   
10. **`site_trends`**: Linear regression slope per site-metric
    - Positive slope = increasing trend
    - Used for: Trend detection and significance testing

**`run_annual_metrics_workflow(annual_df, metric_cols)`**
Convenience wrapper chaining `build_annual_metrics_long_table` and `build_annual_metrics_outputs` in sequence.
- **Input**: Same as `build_annual_metrics_long_table`
- **Output**: Dictionary of 11 products (same as `build_annual_metrics_outputs`)

**`plot_annual_metrics_core_figures(outputs, source_label, metric_cols, comparison_label="Focal Vs Reference", envelope_label="reference", use_spec_order=True)`**
Generates focal-vs-envelope comparison plots for all metrics in metric_cols.

- For each metric:
  - Plot focal site trajectory (line)
  - Overlay reference envelope (shaded region or error bars)
  - Title: "HLS Annual NDVI: Focal Vs Reference"
  - Family-aware metric ordering if use_spec_order=True
  
- **Output**: List of (matplotlib.figure, ax) tuples (one per metric)

**`plot_annual_metrics_category_figures(outputs, source_label, metric_cols)`**
Generates category mean trajectory diagnostic plots.

- For each metric:
  - Plot three lines: focal (solid), reference (dashed), degraded (dotted)
  - Useful for reviewing whether focal and reference sites diverge consistently
  
- **Output**: List of (fig, ax) tuples

#### Typical Annual Workflow Usage

```python
# 1. Build long-format table
annual_long = tgbs_rs.metrics.temporal.build_annual_metrics_long_table(
    annual_df=df_annual_composites,
    metric_cols=["NDVI", "NDMI", "NBR", "EVI"]
)

# 2. Generate all outputs
outputs = tgbs_rs.metrics.temporal.build_annual_metrics_outputs(annual_long_df=annual_long)

# 3. Plot focal vs. reference
figs = tgbs_rs.metrics.temporal.plot_annual_metrics_core_figures(
    outputs=outputs,
    source_label="HLS",
    metric_cols=["NDVI", "NDMI"]
)

# 4. Inspect specific products
print(outputs["focal_reference_anomalies"].head())
print(outputs["site_trends"])
```

---

### 4.5 Seasonal Metrics Workflow

#### Overview
Seasonal analysis separates annual data into wet-season and dry-season metrics, recognizing that vegetation dynamics are fundamentally different across Kenya's bimodal rainfall patterns.

**Seasonal Months** (from [config.py](src/tgbs_rs/config/config.py)):
- **Wet**: March, April, May (MAM = long rains)
- **Dry**: July, August, September, October (JASO = dry season)
- Alternative seasons (short rains, post-harvest) can be defined ad-hoc

#### Data Flow
```
Seasonal Time-Series DataFrame (site, year, month, metric columns)
                    ↓
    [build_seasonal_metrics_long_table] ← for "wet" season
                    ↓
        Long-Format Seasonal Table (filtered to wet months)
                    ↓
    [build_seasonal_metrics_outputs]
                    ↓
    Dictionary of 11 Seasonal Products (per season)
```

#### Key Differences from Annual Workflow

1. **Filtering Step**: Raw seasonal table filters to months in the target season before structural reshaping
2. **Parallel Processing**: Wet and dry workflows run independently to maintain clear separation
3. **Seasonal Ordering**: Plotting uses family-aware seasonal metric order (e.g., wet NDVI, dry NDVI, wet SAVI, dry SAVI)

#### Key Functions

**`build_seasonal_metrics_long_table(seasonal_df, season, metric_cols)`**
Filters a prepared seasonal summary table to one season and reshapes to long format.

- **Input**: Seasonal DataFrame with [site_id, year, month, metric columns], season ("wet" or "dry"), metric list
- **Processing**: 
  1. Filter rows to months matching the season definition
  2. Reshape to long format (one row per site-year-metric)
- **Output**: Long DataFrame (similar structure to annual, but subset to season months)

**`build_seasonal_metrics_outputs(seasonal_long_df)`**
Generates 11 seasonal products (identical structure to annual outputs).

- For each season:
  - Category summary, reference envelope, degraded envelope
  - Focal series, focal-vs-reference, focal-vs-degraded
  - Baseline ranges, anomalies, period summary, trends
  - All computed separately for wet-season and dry-season data

**`run_single_season_metrics_workflow(seasonal_df, season, metric_cols)`**
Convenience wrapper for one season.
- **Input**: Seasonal DataFrame, season name, metric list
- **Output**: Dictionary of 11 seasonal products for that season

**`run_all_season_metrics_workflows(seasonal_df, metric_cols, seasons=["wet", "dry"])`**
Orchestrates workflows for all seasons simultaneously.
- **Output**: Nested dictionary: `{"wet": {11 products}, "dry": {11 products}}`

**`plot_single_season_metrics_core_figures(outputs, season, source_label, metric_cols, ...)`**
Generates focal-vs-envelope plots for one season with family-aware metric ordering.

- Format: ("wet", "dry") tuples in plot order (e.g., wet NDVI, dry NDVI, wet SAVI, dry SAVI)
- **Output**: List of (fig, ax) tuples

**`plot_single_season_category_figures(outputs, season, source_label, metric_cols, ...)`**
Generates category trajectory diagnostic plots for one season.

#### Typical Seasonal Workflow Usage

```python
# 1. Run both wet and dry workflows
all_seasons = tgbs_rs.metrics.temporal.run_all_season_metrics_workflows(
    seasonal_df=df_seasonal_composites,
    metric_cols=["NDVI", "NDMI", "NBR"]
)

# 2. Plot wet season
wet_figs = tgbs_rs.metrics.temporal.plot_single_season_metrics_core_figures(
    outputs=all_seasons["wet"],
    season="wet",
    source_label="HLS",
    metric_cols=["NDVI", "NDMI"]
)

# 3. Plot dry season
dry_figs = tgbs_rs.metrics.temporal.plot_single_season_metrics_core_figures(
    outputs=all_seasons["dry"],
    season="dry",
    source_label="HLS",
    metric_cols=["NDVI", "NDMI"]
)

# 4. Compare wet vs. dry anomalies
wet_anomalies = all_seasons["wet"]["focal_reference_anomalies"]
dry_anomalies = all_seasons["dry"]["focal_reference_anomalies"]
```

---

### 4.6 Summary of Technical Implementation Details

#### Scaling and Performance
- **Image reduction scale**: 10m (Sentinel) or 30m (HLS) for spatial precision
- **Tile scale**: 4 (default) for memory-efficient Earth Engine computation
- **Composite approach**: Median preferred over mean for robustness to outliers

#### Quality Metadata
- **Image count**: Tracked per composite (e.g., 5 images in annual median → more robust)
- **System index**: Preserved to trace origins back to raw imagery
- **Time properties**: Year, month, day, date string recorded for filtering and grouping

#### Handling Missing Data
- Composites with zero images in a window are excluded (filtered out post-processing)
- Site-year combinations with no data are dropped (no interpolation)
- Anomalies computed only when baseline reference statistics are available

#### Trend Calculation
- Linear regression per site-metric pair
- Slope units: Metric value change per year (e.g., NDVI/year)
- Computed on all available years (2014-2025 for HLS, 2019-2025 for Sentinel)

---

## 5. Key Analysis Outputs and Interpretation

### 5.1 The 11 Core Outputs Explained

All annual and seasonal workflows produce the same 11 derived products. Understanding these outputs is essential for interpreting TGBS results.

#### Output 1: `annual_long` (or `seasonal_long`)
**Structure**: Long-format DataFrame with one row per site-year-metric combination

**Columns**: site_id, site_name, site_category, year, month, day, date, image_count, temporal_scale, composite_stat, metric, value

**Purpose**: Foundation table for all downstream analysis; enables filtering, grouping, and subsetting

**Example Row**:
```
site_id: ks_rehab
site_category: focal
year: 2014
metric: NDVI
value: 0.567
image_count: 8
```

**Use Cases**:
- Export raw annual/seasonal metrics to CSV
- Inspect data quality (image_count > 4 = good replication)
- Filter by site category, year range, or metric family
- Merge with external datasets

---

#### Output 2: `category_summary`
**Structure**: Mean values per site-category-year combination

**Columns**: site_category, year, metric, value_mean

**Purpose**: Aggregates individual site data to category level (focal, reference, degraded) for pattern recognition

**Example**:
```
site_category: reference
year: 2014
metric: NDVI
value_mean: 0.623  (average of Buda, Gogoni, Shimba Hills)
```

**Interpretation**:
- If reference_mean increases steadily 2014-2025 → healthy reference sites
- If focal_mean < reference_mean in baseline (2014-2017) → likely degraded/different at start
- If focal_mean rises rapidly 2018-2025 (current period) → potential restoration response

**Use Cases**:
- Diagnostic plots showing reference stability and focal trajectories
- Baseline definition (reference mean ± std during 2014-2017)
- Identifying site-specific vs. regional drivers of change

---

#### Output 3: `reference_envelope`
**Structure**: Min, mean, max bounds per year from reference sites

**Columns**: year, metric, ref_min, ref_mean, ref_max

**Purpose**: Establishes reference site variability bounds for comparison

**Calculation**:
```
per year:
  ref_mean = mean(values from Buda, Gogoni, Shimba Hills)
  ref_min = min(values from reference sites)
  ref_max = max(values from reference sites)
```

**Interpretation**:
- **ref_mean**: Expected "healthy" value for the region in that year
- **ref_min to ref_max**: Natural variability among intact reference sites
- **Wide envelope** (max - min large): High spatial heterogeneity in reference sites
- **Shrinking envelope over time**: Convergence in reference site conditions

**Use Cases**:
- Plotting focal trajectories within/outside reference envelope
- Testing whether focal anomalies are within natural reference bounds
- Climate influence detection (if all reference sites change together, likely climate-driven)

---

#### Output 4: `degraded_envelope`
**Structure**: Same as reference_envelope but from degraded sites (Degraded 1-3)

**Purpose**: Establishes baseline of known-degraded conditions for comparison

**Interpretation**:
- Values consistently **below** focal and reference → truly degraded
- Values **similar to focal** → focal may be degraded too
- Values **above focal** → focal in best condition (restoration success?)

**Use Cases**:
- Focal-vs-degraded comparison (less commonly used than focal-vs-reference)
- Thresholding: Areas where focal < degraded envelope may require intervention

---

#### Output 5: `focal`
**Structure**: Long-format series for the focal site (KS Rehab) only

**Columns**: year, metric, value, date, image_count

**Purpose**: Isolates the restoration site time-series for detailed analysis

**Example**:
```
ks_rehab NDVI trajectory:
2014: 0.501
2015: 0.510
...
2024: 0.612
2025: 0.625
```

**Use Cases**:
- Independent focal analysis (compare to self over time, not to reference)
- Export focal metrics for ecological correlations (e.g., tree planting activities)

---

#### Output 6: `focal_vs_reference`
**Structure**: Focal and reference envelope joined on year

**Columns**: year, metric, focal_value, ref_min, ref_mean, ref_max, focal_above_ref_mean, focal_within_envelope

**Purpose**: Direct comparison of focal trajectory to reference bounds

**Interpretation**:
- **focal_above_ref_mean**: Focal is currently more vigorous than typical reference site
- **focal_within_envelope**: Focal is within natural reference variability (no anomaly)
- **focal < ref_min**: Focal is below all reference sites (severe anomaly)

**Calculation**:
```
focal_above_ref_mean = (focal_value > ref_mean)
focal_within_envelope = (focal_value >= ref_min) & (focal_value <= ref_max)
```

**Visualization**:
```
    ref_max ─────────────────  (upper bound)
            ╱                   (envelope)
 ref_mean ╱                     (typical reference)
          │
    focal ●─────────●─────●     (focal trajectory)
          │                    
    ref_min ─────────────────  (lower bound)
    
    ←── baseline ──→←── current ──→
      2014-2017      2018-2025
```

**Use Cases**:
- Main focal-vs-reference comparison plotting
- Anomaly detection (focal outside envelope = anomaly)

---

#### Output 7: `focal_vs_degraded`
**Structure**: Same as focal_vs_reference but with degraded envelope

**Purpose**: Alternative comparison baseline

**Use Cases**:
- Show focal is improving relative to degraded (if applicable)
- Less commonly interrogated than focal_vs_reference

---

#### Output 8: `reference_baseline_ranges`
**Structure**: Summary statistics for reference sites during baseline period (2014-2017)

**Columns**: metric, baseline_mean, baseline_std, baseline_min, baseline_max, baseline_median

**Purpose**: Establishes reference normal conditions for anomaly standardization

**Example**:
```
NDVI baseline_mean: 0.623, baseline_std: 0.034
NDMI baseline_mean: 0.245, baseline_std: 0.012
```

**Use Cases**:
- Compute standardized anomalies: (focal - baseline_mean) / baseline_std
- Anomalies > +1 or < -1 indicate significant deviations
- Anomalies > +2 indicate extreme events

---

#### Output 9: `focal_reference_anomalies`
**Structure**: Focal vs. reference with standardized anomalies added

**Columns**: year, metric, focal_value, ref_mean, anomaly_value (standardized)

**Purpose**: Quantifies how far focal deviates from reference baseline in units of reference variability

**Calculation**:
```
anomaly = (focal_value - baseline_mean) / baseline_std
```

**Interpretation**:
- **anomaly = 0**: Focal equals reference baseline
- **anomaly = +1**: Focal is 1σ above reference baseline (10% probability in normal distribution)
- **anomaly = +2**: Focal is 2σ above baseline (2.5% probability; rare / extreme)
- **anomaly = -1**: Focal is 1σ below baseline (degradation signal)

**Example**:
```
Year  NDVI_focal  Baseline_Mean  Baseline_Std  Anomaly
2017  0.601       0.623          0.034         -0.647 (slightly below)
2020  0.643       0.623          0.034         +0.588 (slightly above)
2024  0.685       0.623          0.034         +1.824 (significantly above!)
```

**Visualization** (anomaly plot):
```
      +2 ─────────────────────── (extreme anomaly threshold)
         │
       +1 ──┬─────────────────── (significant anomaly threshold)
         │  │           ╱╲
         │  │          ╱  ╲
       0  ──●─────────●──●─●─ (focal = baseline)
         │        2014  2020 2024
         │
      -1 ─────────────────────── (degradation threshold)
         │
      -2 ─────────────────────── (severe degradation)
```

**Use Cases**:
- Identify years where focal had unusually high or low values
- Detect restoration response (positive anomalies in current period)
- Detect degradation events (negative anomalies)

---

#### Output 10: `period_summary`
**Structure**: Mean values per metric for baseline vs. current periods

**Columns**: metric, baseline_mean (2014-2017), current_mean (2018-2025), difference, pct_change

**Purpose**: High-level period comparison for impact assessment

**Example**:
```
NDVI
  Baseline (2014-2017): 0.601
  Current (2018-2025):  0.635
  Difference:          +0.034
  Pct Change:          +5.7%
```

**Interpretation**:
- **Positive difference**: Improvement (increased vegetation vigor/productivity)
- **Negative difference**: Degradation (decreased vegetation)
- **Pct change > 5%**: Significant change (substantive restoration or loss)

**Use Cases**:
- Summary statistics for reports and presentations
- Quick assessment of restoration effectiveness
- Comparison across multiple projects

---

#### Output 11: `site_trends`
**Structure**: Linear regression slope per site-metric pair

**Columns**: site_id, site_category, metric, slope_per_year, r_squared, p_value

**Purpose**: Quantifies directional long-term change (increasing vs. decreasing)

**Calculation**:
```
Linear regression: metric_value ~ year
slope = change per year (units: metric/year, e.g., NDVI/year)
r_squared = proportion of variance explained (0-1; higher = stronger trend)
p_value = statistical significance (p < 0.05 = statistically significant)
```

**Example**:
```
Site: ks_rehab
Metric: NDVI
Slope: +0.0089 NDVI/year  (increasing ~0.009 per year)
R-squared: 0.72           (strong fit)
P-value: 0.0012           (highly significant)
```

**Interpretation**:
- **Positive slope**: Greening trend (restoration, natural regrowth, or climate-driven)
- **Negative slope**: Browning trend (degradation or drought)
- **Strong r-squared (>0.6)**: Trend is clear and consistent
- **Weak r-squared (<0.3)**: High year-to-year variability (climate, phenology)
- **p < 0.05**: Statistically significant (unlikely due to chance)

**Typical TGBS Expectations**:
- **Reference sites**: Slope ≈ 0 or slightly positive (stable or natural greening)
- **Focal site pre-restoration**: Negative slope (degradation)
- **Focal site post-restoration**: Positive slope (recovery)

**Use Cases**:
- Assess long-term restoration trajectory
- Compare focal trend to reference (focal > reference = improvement)
- Statistical testing of intervention effectiveness

---

### 5.2 Focal vs. Reference Comparison Framework

#### Conceptual Foundation
The focal-vs-reference comparison is the core analysis framework of TGBS. It answers: **"Is the focal site (restoration intervention) different from undisturbed reference sites, and if so, by how much?"**

#### Key Assumptions
1. **Reference sites are undisturbed**: Buda, Gogoni, Shimba Hills represent intact regional conditions
2. **Reference sites are representative**: Natural variability within reference bounds reflects "healthy" conditions
3. **Focal site differences are meaningful**: Deviation from reference = response to restoration (or other drivers)

#### Interpretation Logic

**Scenario A: Focal WITHIN reference envelope (2014-2017 baseline)**
```
Interpretation: Focal site started in healthy condition (or similar to reference)
Implication: Baseline already matches reference; test whether current period shows divergence
```

**Scenario B: Focal BELOW reference envelope (2014-2017 baseline)**
```
Interpretation: Focal site started degraded or different from reference
Implication: Baseline period shows deficit; assess whether restoration closes the gap
Success criterion: Focal approaches reference mean by end period
```

**Scenario C: Focal ABOVE reference envelope throughout**
```
Interpretation: Focal site consistently more vigorous than reference
Implication: Either site selection bias (naturally better site) or undocumented driver
Action: Review site history; check for confounding factors (elevation, soil type, management)
```

**Scenario D: Focal trajectory crosses reference envelope over time**
```
Interpretation: Focal changes relative to reference (either improvement or degradation)
Implication: Clear temporal response; test if coincides with known interventions
Success criterion: Upward crossing (low → high relative to reference) = restoration success
```

---

### 5.3 Envelope Construction and Interpretation

#### What is an Envelope?
An **envelope** is the min-mean-max bounds of a group's data over time. For TGBS:

```
Reference Envelope (for each year):
  Min: minimum value from Buda, Gogoni, or Shimba Hills
  Mean: average of three reference sites
  Max: maximum value from the three sites
```

#### Why Use Envelopes?
1. **Capture natural variability**: Single-reference comparison would be arbitrary
2. **Visualize range of healthy conditions**: Envelope = "what is normal?" for the region
3. **Interpret focal anomalies**: Is focal outside normal range?

#### Interpreting Envelope Width
```
Narrow envelope (max - min small):
  → Reference sites are similar
  → Regional conditions are homogeneous
  → Focal deviations are meaningful

Wide envelope (max - min large):
  → Reference sites are heterogeneous
  → Local site factors matter (microclimate, soil, slope)
  → Focal must deviate more to be "significant"
```

#### Time-Varying Envelopes
If reference envelope **shrinks over time**:
- Reference sites converge to similar conditions
- Possible: Regional greening (climate driver)
- Interpretation: Focal changes may be climate-driven too

If reference envelope **widens over time**:
- Reference sites diverge
- Possible: Differential climate impacts or site-specific stochasticity
- Interpretation: Hard to attribute focal changes to intervention alone

---

### 5.4 Seasonal Interpretation

#### Wet vs. Dry Season Dynamics
```
Wet Season (MAM - March/April/May):
  - High rainfall, peak vegetation growth
  - Strong NDVI, EVI signals (maximum annual values)
  - Low NDMI (vegetation water stressed → lower index)
  - Best for detecting active vegetation

Dry Season (JASO - July/August/Sept/Oct):
  - Minimal rainfall, vegetation stress
  - Lower NDVI, EVI (senescence, dormancy)
  - High NDMI (low water availability)
  - Best for detecting drought resilience
```

#### Restoration Signal Detection
```
Success Indicator 1: Wet Season Greening
  - Focal wet-season NDVI increases pre-to-post intervention
  - Approaching reference wet-season mean
  - Indicates restoration enabling higher peak growth

Success Indicator 2: Dry Season Resilience
  - Focal dry-season NDVI/NDMI improve (less stress)
  - Indicates deeper soil water reserves (mature vegetation)
  - Takes longer to manifest than wet-season response

Success Indicator 3: Seasonal Amplitude
  - Difference between wet and dry seasons increases
  - Indicates stronger vegetation seasonality
  - Sign of mature forest developing distinct dormancy
```

---

### 5.5 Practical Guidance on Output Interpretation

#### Step 1: Check Data Quality
```python
# Before interpreting results:
if outputs["annual_long"]["image_count"].min() < 3:
    print("WARNING: Some years have <3 images in composite (noisy)")
    
# Inspect for missing years
missing_years = set(range(2014, 2026)) - set(outputs["annual_long"]["year"].unique())
if missing_years:
    print(f"Missing data: {missing_years}")
```

#### Step 2: Review Baseline and Current Period Separately
```python
# Baseline (2014-2017): What was the starting condition?
baseline = outputs["annual_long"][outputs["annual_long"]["year"] <= 2017]
baseline_focal = baseline[baseline["site_category"] == "focal"]["value"].mean()

# Current (2018-2025): Has it improved?
current = outputs["annual_long"][outputs["annual_long"]["year"] >= 2018]
current_focal = current[current["site_category"] == "focal"]["value"].mean()

# Compute gain
gain = current_focal - baseline_focal
print(f"Focal site gain: {gain:.4f} ({gain/baseline_focal*100:.1f}%)")
```

#### Step 3: Compare to Reference Baseline
```python
# What is "normal" for the region?
baseline_ref = outputs["reference_baseline_ranges"]
print(baseline_ref)

# Is focal within normal range?
if abs(outputs["focal_reference_anomalies"]["anomaly_value"]).max() < 1:
    print("Focal is within 1σ of reference (normal variability)")
else:
    print("Focal has significant anomalies (>1σ deviations)")
```

#### Step 4: Assess Trends
```python
# Are there directional changes?
trends = outputs["site_trends"]
focal_trend = trends[trends["site_id"] == "ks_rehab"]

for metric in ["NDVI", "NDMI"]:
    slope = focal_trend[focal_trend["metric"] == metric]["slope_per_year"].values[0]
    p_val = focal_trend[focal_trend["metric"] == metric]["p_value"].values[0]
    
    if slope > 0 and p_val < 0.05:
        print(f"{metric}: Significant greening trend ({slope:.4f}/year, p={p_val:.4f})")
    elif slope < 0 and p_val < 0.05:
        print(f"{metric}: Significant browning trend ({slope:.4f}/year, p={p_val:.4f})")
    else:
        print(f"{metric}: No significant trend")
```

#### Step 5: Visualize and Contextualize
```python
# Plot focal vs. reference
# Plot anomaly time series
# Cross-reference with external data:
#   - Rainfall records (climate influence?)
#   - Tree planting records (intervention timing?)
#   - Fire history (disturbance?)
#   - Management changes (policy shifts?)
```

---

### 5.6 Common Pitfalls and Mitigation

| Pitfall | Risk | Mitigation |
|---------|------|-----------|
| **Too few images per composite** | Noisy, cloudy composites | Check `image_count > 4`; consider monthly composites |
| **Confounding climate signal** | Attribution unclear (intervention vs. climate) | Compare focal trend to reference trend; if similar, likely climate |
| **Seasonal misalignment** | Wrong interpretation of phenology | Use separate seasonal workflows (wet vs. dry) |
| **Reference site heterogeneity** | Wide envelopes hide signal | Check if reference sites diverge; may need subset analysis |
| **Short time-series post-intervention** | Trend reversal possible | 5+ years data recommended for trend significance |
| **Ignoring baseline condition** | Anchoring bias | Always report baseline vs. current separately |
| **Statistical over-interpretation** | p < 0.05 ≠ ecologically significant | Report effect size (difference, %) not just p-value |
