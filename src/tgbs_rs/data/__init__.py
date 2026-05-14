"""
Data loading and processing module.

Provides access to baseline datasets (DEM, ESA, ISDA, BII, etc.) and sensor-specific
preprocessing, indices, and masking operations.
"""

from .baseline import (
    get_forest_2000,
    get_forest_loss_image,
    get_forest_loss_year_image,
    get_bii_all,
    get_esa_landcover,
    get_canopy_height,
    get_isda_topsoil_mean,
    get_terrain_layers,
    get_dem,
    get_slope,
    get_hillshade,
    build_baseline_layers,
)

from .topography import calc_elevation, calc_terrain

__all__ = [
    "get_forest_2000",
    "get_forest_loss_image",
    "get_forest_loss_year_image",
    "get_bii_all",
    "get_esa_landcover",
    "get_canopy_height",
    "get_isda_topsoil_mean",
    "get_terrain_layers",
    "get_dem",
    "get_slope",
    "get_hillshade",
    "build_baseline_layers",
    "calc_elevation",
    "calc_terrain",
]
