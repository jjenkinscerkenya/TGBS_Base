"""
Configuration module for project paths and Earth Engine assets.

Provides centralized access to file paths, AOI boundaries, Earth Engine asset
identifiers, band specifications, and visualization parameters.
"""

# File paths and directories
from .config import (
    REPO_ROOT,
    DATA_DIR,
    OUTPUTS_DIR,
    RASTER_DIR,
    TABLES_DIR,
    LANDSCAPE_RASTER_DIR,
    OUTPUT_DIRS,
    AOI_PATHS,
)

# Earth Engine datasets - Baseline/Reference
from .config import (
    BII_1KM,
    BII_MASK,
    BII_MAIN_BAND,
    BII_BANDS,
    ESA,
    ESA_MAP_BAND,
    ESA_CLASS_VALUES,
    ESA_CLASS_NAMES,
    CANOPY,
    GL_FOREST_CHANGE,
    GL_AGBM,
    ISDA,
    ISDA_TOPSOIL_MEAN_BAND,
    DEM,
    IUCN,
    GLOBAL_ADM2,
)

# Earth Engine datasets - Sensor Collections
from .config import (
    S2_SR_COLLECTION,
    S2_CLOUD_PROB_COLLECTION,
    L8_SR_COLLECTION,
    HLS_L30_COLLECTION,
    HLS_S30_COLLECTION,
    DYNAMIC_WORLD,
    DW_WOODY_BANDS,
)

# Sentinel-2 Band and Index Configuration
from .config import (
    S2_BANDS,
    S2_ALL_BANDS,
    S2_INDEX_BANDS,
    S2_SCALE_FACTOR,
    S2_SCALE,
    S2_VEGETATION_INDEX_BANDS,
    S2_MOISTURE_INDEX_BANDS,
    S2_DISTURBANCE_INDEX_BANDS,
)

# Sentinel-2 Cloud Masking Parameters
from .config import (
    CLOUD_FILTER,
    CLD_PRB_THRESH,
    NIR_DRK_THRESH,
    CLD_PRJ_DIST_KM,
    BUFFER_M,
    ERODE_RADIUS_M,
    DDT_SCALE_M,
    MORPH_SCALE_M,
)

# Landsat-8 Band and Index Configuration
from .config import (
    L8_BANDS,
    L8_INDEX_BANDS,
    L8_SCALE_FACTOR,
    L8_ADD_OFFSET,
    L8_SCALE,
    L8_VEGETATION_INDEX_BANDS,
    L8_MOISTURE_INDEX_BANDS,
    L8_DISTURBANCE_INDEX_BANDS,
)

# HLS Band and Index Configuration
from .config import (
    HLS_BANDS,
    HLS_ALL_BANDS,
    HLS_INDEX_BANDS,
    HLS_SCALE_FACTOR,
    HLS_SCALE,
    HLS_VEGETATION_INDEX_BANDS,
    HLS_MOISTURE_INDEX_BANDS,
    HLS_DISTURBANCE_INDEX_BANDS,
)

# Visualization parameters
from .config_vis import (
    SITES_VIS_PARAMS,
    S2_VIS_PARAMS,
    L8_VIS_PARAMS,
    HLS_VIS_PARAMS,
    DW_BINARY_VIS_PARAMS,
    BASELINE_VIS_PARAMS,
)

__all__ = [
    # Paths
    "REPO_ROOT",
    "DATA_DIR",
    "OUTPUTS_DIR",
    "RASTER_DIR",
    "TABLES_DIR",
    "LANDSCAPE_RASTER_DIR",
    "OUTPUT_DIRS",
    "AOI_PATHS",
    # Baseline datasets
    "BII_1KM",
    "BII_MASK",
    "BII_MAIN_BAND",
    "BII_BANDS",
    "ESA",
    "ESA_MAP_BAND",
    "ESA_CLASS_VALUES",
    "ESA_CLASS_NAMES",
    "CANOPY",
    "GL_FOREST_CHANGE",
    "GL_AGBM",
    "ISDA",
    "ISDA_TOPSOIL_MEAN_BAND",
    "DEM",
    "IUCN",
    "GLOBAL_ADM2",
    # Sensor collections
    "S2_SR_COLLECTION",
    "S2_CLOUD_PROB_COLLECTION",
    "L8_SR_COLLECTION",
    "HLS_L30_COLLECTION",
    "HLS_S30_COLLECTION",
    "DYNAMIC_WORLD",
    "DW_WOODY_BANDS",
    # Sentinel-2
    "S2_BANDS",
    "S2_ALL_BANDS",
    "S2_INDEX_BANDS",
    "S2_SCALE_FACTOR",
    "S2_SCALE",
    "S2_VEGETATION_INDEX_BANDS",
    "S2_MOISTURE_INDEX_BANDS",
    "S2_DISTURBANCE_INDEX_BANDS",
    "CLOUD_FILTER",
    "CLD_PRB_THRESH",
    "NIR_DRK_THRESH",
    "CLD_PRJ_DIST_KM",
    "BUFFER_M",
    "ERODE_RADIUS_M",
    "DDT_SCALE_M",
    "MORPH_SCALE_M",
    # Landsat-8
    "L8_BANDS",
    "L8_INDEX_BANDS",
    "L8_SCALE_FACTOR",
    "L8_ADD_OFFSET",
    "L8_SCALE",
    "L8_VEGETATION_INDEX_BANDS",
    "L8_MOISTURE_INDEX_BANDS",
    "L8_DISTURBANCE_INDEX_BANDS",
    # HLS
    "HLS_BANDS",
    "HLS_ALL_BANDS",
    "HLS_INDEX_BANDS",
    "HLS_SCALE_FACTOR",
    "HLS_SCALE",
    "HLS_VEGETATION_INDEX_BANDS",
    "HLS_MOISTURE_INDEX_BANDS",
    "HLS_DISTURBANCE_INDEX_BANDS",
    # Visualization
    "SITES_VIS_PARAMS",
    "S2_VIS_PARAMS",
    "L8_VIS_PARAMS",
    "HLS_VIS_PARAMS",
    "DW_BINARY_VIS_PARAMS",
    "BASELINE_VIS_PARAMS",
]
