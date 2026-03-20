import ee

from tgbs_rs.config import (
    L8_SR_COLLECTION,
    L8_CLOUD_FILTER,
)


def mask_edges(image: ee.Image) -> ee.Image:
    """
    Placeholder for interface compatibility with the Sentinel workflow.

    Landsat 8 C2 L2 does not require the Sentinel-specific B8A/B9 edge-mask logic,
    so this function returns the image unchanged.
    """
    return image


def get_l8_sr_cld_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Filter Landsat 8 SR to the AOI and date range."""
    return (
        ee.ImageCollection(L8_SR_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUD_COVER", L8_CLOUD_FILTER))
        .map(mask_edges)
    )


def add_cld_shdw_mask(image: ee.Image) -> ee.Image:
    """
    Add a cloud-shadow mask band using Landsat 8 C2 L2 QA bands.

    Closest approximation to the Sentinel cloud/shadow mask:
    - QA_PIXEL bits 0-4 screen fill, dilated cloud, cirrus, cloud, cloud shadow
    - QA_RADSAT screens saturated pixels
    """
    qa_pixel = image.select("QA_PIXEL")
    qa_mask = qa_pixel.bitwiseAnd(int("11111", 2)).neq(0)

    rad_sat_mask = image.select("QA_RADSAT").neq(0)

    cloudmask = qa_mask.Or(rad_sat_mask).rename("cloudmask")

    return image.addBands(cloudmask)


def apply_cld_shdw_mask(image: ee.Image) -> ee.Image:
    """Apply the inverse of the cloud-shadow mask to all bands."""
    return image.updateMask(image.select("cloudmask").Not())


def build_cloudfree_l8sr_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Build a Landsat 8 SR collection with cloud and shadow masking applied."""
    return (
        get_l8_sr_cld_col(aoi, start_date, end_date)
        .map(add_cld_shdw_mask)
        .map(apply_cld_shdw_mask)
    )


def build_l8_non_water_mask(
    l8_collection: ee.ImageCollection,
    mndwi_thresh: float = 0.1,
    ndvi_thresh: float = 0.2,
    nir_thresh: float = 0.15,
) -> ee.Image:
    """Build a boolean non-water mask from a Landsat 8 composite using simple spectral thresholds."""
    comp = l8_collection.median()
    water = (
        comp.select("MNDWI")
        .gt(mndwi_thresh)
        .And(comp.select("NDVI").lt(ndvi_thresh))
        .And(comp.select("SR_B5").lt(nir_thresh))
    )
    return water.Not().rename("non_water")


def apply_water_mask(image: ee.Image, non_water_mask: ee.Image) -> ee.Image:
    """Apply a precomputed non-water mask to all bands of an image."""
    return image.updateMask(non_water_mask)
