from pathlib import Path

#################### FILE PATH HANDLING #######################

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "aoi"
OUTPUTS_DIR = REPO_ROOT / "outputs"
RASTER_DIR = OUTPUTS_DIR / "rasters"
TABLES_DIR = OUTPUTS_DIR / "tables"
LANDSCAPE_RASTER_DIR = RASTER_DIR / "landscape_metrics"

# Output directory names
OUTPUT_DIRS = {
    "plots": OUTPUTS_DIR / "plots",
    "maps": OUTPUTS_DIR / "maps",
    "tables": OUTPUTS_DIR / "tables",
    "rasters": OUTPUTS_DIR / "rasters",
    "sampling_design": OUTPUTS_DIR / "sampling_design",
}

#################### AOI BOUNDARIES ##########################
AOI_PATHS = {
    "kwale": DATA_DIR / "kwale_county.geojson",
    "buda": DATA_DIR / "buda_aoi.geojson",
    "gogoni": DATA_DIR / "gogoni_aoi.geojson",
    "shimba_hills": DATA_DIR / "shimba_hills_aoi.geojson",
    "ks_rehab_blocks": DATA_DIR / "ks_rehab_blocks.geojson",
    "degraded_1": DATA_DIR / "degraded_1_aoi.geojson",
    "degraded_2": DATA_DIR / "degraded_2_aoi.geojson",
    "degraded_3": DATA_DIR / "degraded_3_aoi.geojson",
    "corridor": DATA_DIR / "corridor_dissolved_aoi.geojson",
}

#################### EE DATASETS ##########################
# CHIRPS Precipitation Daily Reanalysis: Climate Hazards Center InfraRed Precipitation With Station Data
CHIRPS_COLLECTION = "UCSB-CHC/CHIRPS/V3/DAILY_RNL"
CHIRPS_PRECIP_BAND = "precipitation"

# Global Biodiversity Intactness Index
BII_1KM = "projects/earthengine-legacy/assets/projects/sat-io/open-datasets/BII/BII_1km"
BII_MASK = "projects/earthengine-legacy/assets/projects/sat-io/open-datasets/BII/BII_Mask"
BII_MAIN_BAND = "BII All"
BII_BANDS = [
    "Land Use",
    "Land Use Intensity",
    "BII All",
    "BII Amphibians",
    "BII Birds",
    "BII Forbs",
    "BII Graminoids",
    "BII Mammals",
    "BII All Plants",
    "BII Reptiles",
    "BII Trees",
    "BII All Vertebrates",
]

# ESA WORLDCOVER
ESA = "ESA/WorldCover/v200"
ESA_MAP_BAND = "Map"

ESA_CLASS_VALUES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]

ESA_CLASS_NAMES = [
    "Tree cover",
    "Shrubland",
    "Grassland",
    "Cropland",
    "Built-up",
    "Bare / sparse vegetation",
    "Snow and ice",
    "Permanent water bodies",
    "Herbaceous wetland",
    "Mangroves",
    "Moss and lichen",
]

# 1m Global Canopy Height Model
CANOPY = "projects/sat-io/open-datasets/facebook/meta-canopy-height"

GL_FOREST_CHANGE = "UMD/hansen/global_forest_change_2024_v1_12"
GL_AGBM = "projects/sat-io/open-datasets/ESA/ESA_CCI_AGB"

# iSDA Total Soil Carbon
ISDA = "ISDASOIL/Africa/v1/carbon_total"
ISDA_TOPSOIL_MEAN_BAND = "mean_0_20"

# Global Elevation
DEM = "COPERNICUS/DEM/GLO30"

# IUCN Protected Areas
IUCN = "WCMC/WDPA/current/polygons"

# Global admin boundary datasets
GLOBAL_ADM2 = "FAO/GAUL/2015/level2"

# Sentinel-2 collections
S2_SR_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
S2_CLOUD_PROB_COLLECTION = "COPERNICUS/S2_CLOUD_PROBABILITY"

# Landsat-8 collections
L8_SR_COLLECTION = "LANDSAT/LC08/C02/T1_L2"

# HLS
HLS_L30_COLLECTION = "NASA/HLS/HLSL30/v002"  # Landsat OLI
HLS_S30_COLLECTION = "NASA/HLS/HLSS30/v002"  # Sentinel MSI

# Dynamic World V1
DYNAMIC_WORLD = "GOOGLE/DYNAMICWORLD/V1"
DW_WOODY_BANDS = ["trees_prob", "woody_prob"]

#################### SENTINEL VARIABLES ##########################
S2_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
S2_ALL_BANDS = [
    "B2",
    "B3",
    "B4",
    "B5",
    "B6",
    "B7",
    "B8",
    "B8A",
    "B11",
    "B12",
    "NDVI",
    "EVI",
    "NDWI",
    "MNDWI",
    "SAVI",
    "NDMI",
    "NBR",
    "NIRv",
    "NDRE",
]
# BLUE_BAND = "B2"
# GREEN_BAND = "B3"
# RED_BAND = "B4"
# RE1_BAND = "B5"
# RE2_BAND = "B6"
# RE3_BAND = "B7"
# NIR_BAND = "B8"
# NARROW_NIR_BAND = "B8A"
# SWIR1_BAND = "B11"
# SWIR2_BAND = "B12"

S2_INDEX_BANDS = [
    "NDVI",  # Normalized Difference Vegetation Index
    "EVI",  # Enhanced Vegetation Index
    "NDWI",  # Normalized Difference Water Index
    "MNDWI",  # Modified Normalized Difference Water Index
    "SAVI",  # Soil-Adjusted Vegetation Index
    "NDMI",  # Normalized Difference Moisture Index
    "NBR",  # Normalized Burn Ratio
    "NIRv",  # Near-Infrared Reflectance of Vegetation
    "NDRE",  # Normalized Difference Red Edge
]

S2_SCALE_FACTOR = 0.0001

# CLOUD MASKING PARAMETERS
CLOUD_FILTER = 50  # % max CLOUDY_PIXEL_PERCENTAGE per image
CLD_PRB_THRESH = 40  # % s2cloudless probability threshold
NIR_DRK_THRESH = 0.15  # reflectance (0..1) threshold for dark pixels
CLD_PRJ_DIST_KM = 1.0  # max shadow search distance (km)
BUFFER_M = 50  # dilation buffer for cloud+shadow mask (m)
ERODE_RADIUS_M = 40  # small erosion to denoise speckle (m)

# Performance for heavy ops
DDT_SCALE_M = 100  # scale used for directionalDistanceTransform (m)
MORPH_SCALE_M = 20  # scale used for focal ops (m)

# Default analysis scale
S2_SCALE = 10

# S2 index names
S2_VEGETATION_INDEX_BANDS = ["NDVI", "EVI", "SAVI", "NIRv", "NDRE"]
S2_MOISTURE_INDEX_BANDS = ["NDMI", "NDWI", "MNDWI"]
S2_DISTURBANCE_INDEX_BANDS = ["NBR"]

PRIORITY_INDICES = ["NBR", "NDMI", "NDVI", "NIRv", "SAVI"]

#################### LANDSAT VARIABLES #########################
# Core optical SR bands used for the translated workflow
L8_BANDS = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]

# BLUE_BAND = "SR_B2"
# GREEN_BAND = "SR_B3"
# RED_BAND = "SR_B4"
# NIR_BAND = "SR_B5"
# SWIR1_BAND = "SR_B6"
# SWIR2_BAND = "SR_B7"

L8_INDEX_BANDS = [
    "NDVI",  # Normalized Difference Vegetation Index
    "EVI",  # Enhanced Vegetation Index
    "NDWI",  # Normalized Difference Water Index
    "MNDWI",  # Modified Normalized Difference Water Index
    "SAVI",  # Soil-Adjusted Vegetation Index
    "NDMI",  # Normalized Difference Moisture Index
    "NBR",  # Normalized Burn Ratio
    "NIRv",  # Near-Infrared Reflectance of Vegetation
]

# Landsat Collection 2 Level-2 surface reflectance scaling
L8_SCALE_FACTOR = 0.0000275
L8_ADD_OFFSET = -0.2

# CLOUD MASKING PARAMETERS
# Closest analog to Sentinel CLOUDY_PIXEL_PERCENTAGE
L8_CLOUD_FILTER = 50  # % max CLOUD_COVER per image

# Default analysis scale
L8_SCALE = 30

#################### HLS VARIABLES ##########################
# Native HLS shared reflectance scaling
HLS_SCALE_FACTOR = 0.0001
HLS_ADD_OFFSET = 0.0

# Common cross-sensor HLS band schema for merged trend analysis
HLS_COMMON_BANDS = ["BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2"]

# Optional native source band lists
HLS_L30_SOURCE_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7"]
HLS_S30_SOURCE_BANDS = ["B2", "B3", "B4", "B8A", "B11", "B12"]

HLS_MERGED_BANDS = [
    "BLUE",
    "GREEN",
    "RED",
    "NIR",
    "SWIR1",
    "SWIR2",
    "NDVI",
    "EVI",
    "NDWI",
    "MNDWI",
    "SAVI",
    "NDMI",
    "NBR",
    "NIRv",
]

HLS_INDEX_BANDS = [
    "NDVI",  # Normalized Difference Vegetation Index
    "EVI",  # Enhanced Vegetation Index
    "NDWI",  # Normalized Difference Water Index
    "MNDWI",  # Modified Normalized Difference Water Index
    "SAVI",  # Soil-Adjusted Vegetation Index
    "NDMI",  # Normalized Difference Moisture Index
    "NBR",  # Normalized Burn Ratio
    "NIRv",  # Near-Infrared Reflectance of Vegetation
]

# Fmask-based QA controls
HLS_CLOUD_FILTER = 50  # max CLOUD_COVERAGE per image
HLS_MASK_ADJACENT = True
HLS_MASK_SNOW = True
HLS_MASK_WATER_IN_QA = (
    False  # keep False if you want separate spectral water masking
)
HLS_MASK_MODERATE_AEROSOL = False
HLS_MASK_HIGH_AEROSOL = True

# Default analysis scale
HLS_SCALE = 30

#################### ANALYSIS BAND COMBINATIONS ##########################
PRODUCTIVITY_BANDS = ["NIRv", "EVI", "NDVI"]
VEGETATION_COVER = ["NDVI", "EVI", "SAVI"]
DISTURBANCE = ["NDMI", "NBR"]
SPATIAL_CHANGE = ["NDVI", "NIRV", "NDMI", "NBR", "SAVI"]


#################### GLOBAL VARIABLES ##########################
# Google Earth Engine Project
GEE_PROJECT = "charrell-personal"

# Time-series defaults
S2_BASELINE_START = "2019-01-01"
BASELINE_START = "2014-01-01"
BASELINE_END = "2017-12-31"
CURRENT_START = "2018-01-01"
CURRENT_END = "2025-12-31"

# Seasonal definitions
WET_MONTHS = [3, 4, 5]
DRY_MONTHS = [7, 8, 9, 10]

# Site categories
FOCAL_LABEL = "focal"
REFERENCE_LABEL = "reference"
DEGRADED_LABEL = "degraded"

# Export defaults
DEFAULT_MAX_PIXELS = 1e13
DEFAULT_FILE_FORMAT = "GeoTIFF"
DEFAULT_CRS = "EPSG:4326"
DRIVE_FOLDER = "TGBS_Kwale_Baseline"
LAND_METRICS_DRIVE_FOLDER = "TGBS_Kwale_Landscape_Metrics"
SPATIAL_CHANGE_DRIVE_FOLDER = "TGBS_Kwale_Spatial_Change"

PLOTTING_SCALE_DICT = {
    "hillshade": 30,
    "dem": 30,
    "slope": 30,
    "canopy_height": 30,  # downsampled from 1m for consistent plotting
    "land_cover": 30,
    "soil_carbon": 30,
    "bii_all": 30,
    "forest_2000": 30,
    "forest_loss": 30,
}
