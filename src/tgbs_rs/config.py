# Sentinel-2 collections
S2_SR_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
S2_CLOUDSCORE_COLLECTION = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"

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
S2_QA_BAND = "cs_cdf"
CLEAR_THRESHOLD = 0.60

# CLOUD MASKING PARAMETERS
CLOUD_FILTER = 70  # % max CLOUDY_PIXEL_PERCENTAGE per image
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
