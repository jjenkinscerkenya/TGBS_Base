import ee

from tgbs_rs.config.config import (
    BII_1KM,
    BII_MASK,
    ESA,
    CANOPY,
    ISDA,
    DEM,
    BII_BANDS,
    BII_MAIN_BAND,
    ESA_MAP_BAND,
    ISDA_TOPSOIL_MEAN_BAND,
    GL_FOREST_CHANGE,
)
from tgbs_rs.data.topography import calc_terrain
from tgbs_rs.utils import _clip_and_mask_image


# Global Forest Change
def get_forest_2000(aoi: ee.Geometry):
    """
    Return a clipped image of tree canopy cover for year 2000.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest_2000 = gfc.select("treecover2000")
    return _clip_and_mask_image(forest_2000, aoi)


def get_forest_loss_image(aoi: ee.Geometry, tree_cover_threshold=10):
    """
    Return a clipped binary forest loss image for the provided AOI.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest2000 = gfc.select("treecover2000").gte(tree_cover_threshold)
    loss = gfc.select("loss")

    forest_loss = forest2000.And(loss).rename("forest_loss")

    return _clip_and_mask_image(forest_loss, aoi)


def get_forest_loss_year_image(aoi: ee.Geometry, tree_cover_threshold=10):
    """
    Return a clipped forest loss year image for the provided AOI.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest2000 = gfc.select("treecover2000").gte(tree_cover_threshold)
    lossyear = gfc.select("lossyear").updateMask(forest2000).rename("lossyear")

    return _clip_and_mask_image(lossyear, aoi)


# BII


def load_bii_image():
    """
    Load the BII stack and rename bands using BII_BANDS.

    Assumes the asset is an ImageCollection that should be converted to bands.
    """
    bii_ic = ee.ImageCollection(BII_1KM)
    bii_img = bii_ic.toBands().rename(BII_BANDS)
    return bii_img


def process_bii_image():
    """
    Process BII into:
    - BII bands only (self-masked)
    - Land Use
    - Land Use Intensity masked to non-target classes
    - BII mask applied
    """
    bii_img = load_bii_image()

    bii_mask = ee.Image(BII_MASK)
    bii_bands = bii_img.select("^BII.*").selfMask()

    lc_mask = (
        bii_img.select("Land Use").neq(2).And(bii_img.select("Land Use").neq(5))
    )

    lui = bii_img.select("Land Use Intensity").updateMask(lc_mask)

    processed = (
        bii_bands.addBands(bii_img.select("Land Use"))
        .addBands(lui.rename("Land Use Intensity"))
        .updateMask(bii_mask)
    )

    return processed


def get_bii_all(aoi):
    """Return the processed BII All band clipped to AOI."""
    bii = process_bii_image().select(BII_MAIN_BAND)
    return _clip_and_mask_image(bii, aoi).rename("BII_All")


# ESA WorldCover


def get_esa_landcover(aoi):
    """
    Return the raw ESA WorldCover categorical Map band clipped to AOI.
    """
    esa_img = ee.ImageCollection(ESA).first().select(ESA_MAP_BAND)
    return _clip_and_mask_image(esa_img, aoi).rename("Land_Cover")


# Canopy Height


def get_canopy_height(aoi):
    """
    Return the canopy height mosaic clipped to AOI with an explicit AOI mask.
    """
    canopy = ee.ImageCollection(CANOPY).mosaic().rename("Canopy_Height")
    return _clip_and_mask_image(canopy, aoi)


# iSDA Total Soil Carbon


def load_isda_image():
    """
    Load the iSDA total soil carbon image.
    """
    return ee.Image(ISDA)


def get_isda_topsoil_mean(aoi):
    """
    Return the configured iSDA topsoil mean carbon band clipped to AOI.
    """
    soil = (
        load_isda_image().select(ISDA_TOPSOIL_MEAN_BAND).rename("Soil_Carbon")
    )
    return _clip_and_mask_image(soil, aoi)


# DEM / Terrain


def load_dem_collection():
    """Load the Copernicus GLO30 DEM ImageCollection."""
    return ee.ImageCollection(DEM)


def get_terrain_layers(aoi):
    """
    Build terrain layers from the DEM collection and clip to AOI.

    Returns a multiband ee.Image with:
    - ELEVATION
    - SLOPE
    - ASPECT
    - HILLSHADE
    """
    dem_ic = load_dem_collection()
    terrain = calc_terrain(dem_ic)
    return _clip_and_mask_image(terrain, aoi)


def get_dem(aoi):
    """Return DEM clipped to AOI."""
    return get_terrain_layers(aoi).select("ELEVATION").rename("DEM")


def get_slope(aoi):
    """Return slope clipped to AOI."""
    return get_terrain_layers(aoi).select("SLOPE")


def get_hillshade(aoi):
    """Return hillshade clipped to AOI."""
    return get_terrain_layers(aoi).select("HILLSHADE")


# Baseline orchestration


def build_baseline_layers(aoi):
    """
    Build all requested baseline layers and return them as a dictionary of ee.Images.
    """
    terrain = get_terrain_layers(aoi)

    layers = {
        "dem": terrain.select("ELEVATION").rename("DEM"),
        "slope": terrain.select("SLOPE"),
        "hillshade": terrain.select("HILLSHADE"),
        "canopy_height": get_canopy_height(aoi),
        "land_cover": get_esa_landcover(aoi),
        "soil_carbon": get_isda_topsoil_mean(aoi),
        "bii_all": get_bii_all(aoi),
        "forest_2000": get_forest_2000(aoi),
        "forest_loss": get_forest_loss_image(aoi),
    }

    return layers
