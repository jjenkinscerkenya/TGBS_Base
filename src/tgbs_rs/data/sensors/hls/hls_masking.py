import ee

from tgbs_rs.config import (
    HLS_L30_COLLECTION,
    HLS_S30_COLLECTION,
    HLS_CLOUD_FILTER,
    HLS_MASK_ADJACENT,
    HLS_MASK_SNOW,
    HLS_MASK_WATER_IN_QA,
    HLS_MASK_MODERATE_AEROSOL,
    HLS_MASK_HIGH_AEROSOL,
)


def get_hls_l30_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Filter HLSL30 to the AOI and date range."""
    return (
        ee.ImageCollection(HLS_L30_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUD_COVERAGE", HLS_CLOUD_FILTER))
    )


def get_hls_s30_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Filter HLSS30 to the AOI and date range."""
    return (
        ee.ImageCollection(HLS_S30_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUD_COVERAGE", HLS_CLOUD_FILTER))
    )


def add_fmask_cloud_mask(image: ee.Image) -> ee.Image:
    """
    Add a cloud/shadow/snow/aerosol mask from HLS Fmask.

    Fmask bits:
    - bit 1: cloud
    - bit 2: adjacent to cloud/shadow
    - bit 3: cloud shadow
    - bit 4: snow/ice
    - bit 5: water
    - bits 6-7: aerosol level
    """
    fmask = image.select("Fmask")

    is_cloud = fmask.bitwiseAnd(1 << 1).neq(0)
    is_adjacent = fmask.bitwiseAnd(1 << 2).neq(0)
    is_shadow = fmask.bitwiseAnd(1 << 3).neq(0)
    is_snow = fmask.bitwiseAnd(1 << 4).neq(0)
    is_water = fmask.bitwiseAnd(1 << 5).neq(0)

    aerosol = fmask.rightShift(6).bitwiseAnd(3)
    is_moderate_aerosol = aerosol.eq(2)
    is_high_aerosol = aerosol.eq(3)

    mask = is_cloud.Or(is_shadow)

    if HLS_MASK_ADJACENT:
        mask = mask.Or(is_adjacent)

    if HLS_MASK_SNOW:
        mask = mask.Or(is_snow)

    if HLS_MASK_WATER_IN_QA:
        mask = mask.Or(is_water)

    if HLS_MASK_MODERATE_AEROSOL:
        mask = mask.Or(is_moderate_aerosol)

    if HLS_MASK_HIGH_AEROSOL:
        mask = mask.Or(is_high_aerosol)

    return image.addBands(mask.rename("cloudmask"))


def apply_cld_shdw_mask(image: ee.Image) -> ee.Image:
    """Apply the inverse of the HLS QA-derived mask to all bands."""
    return image.updateMask(image.select("cloudmask").Not())


def build_cloudfree_hls_l30_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Build an HLSL30 collection with QA masking applied."""
    return (
        get_hls_l30_col(aoi, start_date, end_date)
        .map(add_fmask_cloud_mask)
        .map(apply_cld_shdw_mask)
    )


def build_cloudfree_hls_s30_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Build an HLSS30 collection with QA masking applied."""
    return (
        get_hls_s30_col(aoi, start_date, end_date)
        .map(add_fmask_cloud_mask)
        .map(apply_cld_shdw_mask)
    )


def build_hls_non_water_mask(
    hls_collection: ee.ImageCollection,
    mndwi_thresh: float = 0.1,
    ndvi_thresh: float = 0.2,
    nir_thresh: float = 0.15,
) -> ee.Image:
    """Build a boolean non-water mask from an HLS composite using simple spectral thresholds."""
    comp = hls_collection.median()
    water = (
        comp.select("MNDWI")
        .gt(mndwi_thresh)
        .And(comp.select("NDVI").lt(ndvi_thresh))
        .And(comp.select("NIR").lt(nir_thresh))
    )
    return water.Not().rename("non_water")


def apply_water_mask(image: ee.Image, non_water_mask: ee.Image) -> ee.Image:
    """Apply a precomputed non-water mask to all bands of an image."""
    return image.updateMask(non_water_mask)
