from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

AOI_PATHS = {
    "kwale": DATA_DIR / "kwale_county.geojson",
    "buda": DATA_DIR / "buda_aoi.geojson",
    "gogoni": DATA_DIR / "gogoni_aoi.geojson",
    "shimba_hills": DATA_DIR / "shimba_hills_aoi.geojson",
    "ks_rehab": DATA_DIR / "ks_rehab_aoi.geojson",
    "ks_rehab_blocks": DATA_DIR / "ks_rehab_blocks_2509_epsg_4326.geojson",
    "degraded_1": DATA_DIR / "degraded_1_aoi.geojson",
    "degraded_2": DATA_DIR / "degraded_2_aoi.geojson",
}

#################### EE DATASETS ##########################
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

# Sentinel-2 processing
S2_BANDS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]

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

# Common index names
VEGETATION_INDEX_BANDS = ["NDVI", "EVI", "SAVI", "NIRv", "NDRE"]
MOISTURE_INDEX_BANDS = ["NDMI", "NDWI", "MNDWI"]
DISTURBANCE_INDEX_BANDS = ["NBR"]

# Time-series defaults
BASELINE_START = "2017-01-01"
BASELINE_END = "2019-12-31"
CURRENT_START = "2023-01-01"
CURRENT_END = "2025-12-31"

# Seasonal definitions
WET_MONTHS = [3, 4, 5, 11, 12]
DRY_MONTHS = [1, 2, 6, 7, 8, 9, 10]

# Site categories
FOCAL_LABEL = "focal"
REFERENCE_LABEL = "reference"
DEGRADED_LABEL = "degraded"

# Export defaults
DEFAULT_MAX_PIXELS = 1e13
DEFAULT_FILE_FORMAT = "GeoTIFF"
DEFAULT_CRS = "EPSG:4326"

# Output directory names
OUTPUT_DIRS = {
    "plots": "outputs/plots",
    "maps": "outputs/maps",
    "tables": "outputs/tables",
    "rasters": "outputs/rasters",
}

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

############# Visualization parameters #########################

FOREST_COVER_VIS = {"min": 0, "max": 100, "palette": ["#000000", "#1F951F"]}

FOREST_LOSS_VIS = {
    "min": 0,
    "max": 1,
    "palette": ["#ffffff", "#ff0000"],
}

LOSS_YEAR_VIS = {
    "min": 0,
    "max": 24,
    "palette": [
        "#ffffcc",
        "#ffeda0",
        "#fed976",
        "#feb24c",
        "#fd8d3c",
        "#fc4e2a",
        "#e31a1c",
        "#bd0026",
        "#800026",
    ],
}

DEM_VIS_MUTED = {
    "min": 0,
    "max": 800,
    "palette": ["#334e68", "#7b9e87", "#b7b7a4", "#d4a373", "#f1faee"],
}

SLOPE_VIS = {
    "min": 0,
    "max": 45,
    "palette": ["#f7fcf0", "#ccebc5", "#7bccc4", "#2b8cbe", "#084081"],
}

SLOPE_VIS_DARK_TO_ORANGE = {
    "min": 0,
    "max": 45,
    "palette": [
        "#0b1f3a",
        "#1f4e79",
        "#4fa3c4",
        "#fdae61",
        "#d94801",
    ],
}

HILLSHADE_VIS = {"min": 0, "max": 255, "palette": ["#000000", "#ffffff"]}

CANOPY_VIS = {
    "min": 0,
    "max": 15,
    "palette": [
        "#440154",
        "#482775",
        "#3E4A89",
        "#31688E",
        "#26828E",
        "#1F9E89",
        "#67C165",
        "#B8D73D",
        "#FDE623",
    ],
}

SOIL_CARBON_VIS = {
    "min": 0,
    "max": 40,
    "palette": [
        "#fff7ec",
        "#fee8c8",
        "#fdd49e",
        "#fdbb84",
        "#e34a33",
        "#7f0000",
    ],
}

# Start with 0-1 if BII is fractional. If your layer is 0-100, change max to 100.
BII_VIS = {
    "min": 0,
    "max": 1,
    "palette": ["#d73027", "#fee08b", "#d9ef8b", "#1a9850"],
}

ESA_WORLDCOVER_VIS = {
    "min": 10,
    "max": 100,
    "palette": [
        "#006400",  # 10 Tree cover
        "#ffbb22",  # 20 Shrubland
        "#ffff4c",  # 30 Grassland
        "#f096ff",  # 40 Cropland
        "#fa0000",  # 50 Built-up
        "#b4b4b4",  # 60 Bare/sparse vegetation
        "#f0f0f0",  # 70 Snow and ice
        "#0064c8",  # 80 Permanent water bodies
        "#0096a0",  # 90 Herbaceous wetland
        "#00cf75",  # 95 Mangroves
        "#fae6a0",  # 100 Moss and lichen
    ],
}

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
