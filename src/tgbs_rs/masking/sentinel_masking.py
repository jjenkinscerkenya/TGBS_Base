import ee

from tgbs_rs.config.config import (
    S2_SR_COLLECTION,
    S2_CLOUD_PROB_COLLECTION,
    CLOUD_FILTER,
    CLD_PRB_THRESH,
    NIR_DRK_THRESH,
    CLD_PRJ_DIST_KM,
    DDT_SCALE_M,
    MORPH_SCALE_M,
    ERODE_RADIUS_M,
    BUFFER_M,
)


# Cloud masking
def mask_edges(image: ee.Image) -> ee.Image:
    """Mask noisy edge pixels using Sentinel-2 20 m and 60 m band masks."""
    return image.updateMask(image.select("B8A").mask()).updateMask(
        image.select("B9").mask()
    )


def get_s2_sr_cld_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Join Sentinel-2 SR and s2cloudless collections filtered to the AOI and date range."""

    s2_sr_col = (
        ee.ImageCollection(S2_SR_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", CLOUD_FILTER))
        .map(mask_edges)
    )

    s2_cloudless_col = (
        ee.ImageCollection(S2_CLOUD_PROB_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
    )

    return ee.ImageCollection(
        ee.Join.saveFirst("s2cloudless").apply(
            primary=s2_sr_col,
            secondary=s2_cloudless_col,
            condition=ee.Filter.equals(
                leftField="system:index", rightField="system:index"
            ),
        )
    )


def add_cld_shdw_mask(image: ee.Image) -> ee.Image:
    """Add a cloud-shadow mask band using s2cloudless probability, dark pixels, and shadow projection."""
    cld_prb = ee.Image(image.get("s2cloudless")).select("probability")
    is_cloud = cld_prb.gt(CLD_PRB_THRESH)

    not_water = image.select("SCL").neq(6)
    dark_pixels = (
        image.select("B8").multiply(0.0001).lt(NIR_DRK_THRESH).And(not_water)
    )

    shadow_azimuth_deg = ee.Number(90).subtract(
        ee.Number(image.get("MEAN_SOLAR_AZIMUTH_ANGLE"))
    )
    max_dist_px = (
        ee.Number(CLD_PRJ_DIST_KM).multiply(1000).divide(DDT_SCALE_M).int()
    )

    clouds_for_ddt = is_cloud.reproject(
        crs=image.select(0).projection(), scale=DDT_SCALE_M
    )
    cld_proj = (
        clouds_for_ddt.directionalDistanceTransform(
            shadow_azimuth_deg, max_dist_px
        )
        .select("distance")
        .mask()
    )

    is_shadow = cld_proj.And(dark_pixels)

    opened = (
        is_cloud.Or(is_shadow)
        .reproject(crs=image.select(0).projection(), scale=MORPH_SCALE_M)
        .focalMin(ERODE_RADIUS_M, units="meters")
        .focalMax(BUFFER_M, units="meters")
    )

    return image.addBands(opened.rename("cloudmask"))


def apply_cld_shdw_mask(image: ee.Image) -> ee.Image:
    """Apply the inverse of the cloud-shadow mask to all bands."""
    return image.updateMask(image.select("cloudmask").Not())


def build_cloudfree_s2sr_col(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
) -> ee.ImageCollection:
    """Build a Sentinel-2 SR collection with cloud and shadow masking applied."""
    return (
        get_s2_sr_cld_col(aoi, start_date, end_date)
        .map(add_cld_shdw_mask)
        .map(apply_cld_shdw_mask)
    )


# Water masking
def build_s2_non_water_mask(
    s2_collection: ee.ImageCollection,
    mndwi_thresh: float = 0.1,
    ndvi_thresh: float = 0.2,
    nir_thresh: float = 0.15,
) -> ee.Image:
    """Build a boolean non-water mask from a Sentinel-2 composite using simple spectral thresholds."""
    comp = s2_collection.median()
    water = (
        comp.select("MNDWI")
        .gt(mndwi_thresh)
        .And(comp.select("NDVI").lt(ndvi_thresh))
        .And(comp.select("B8").lt(nir_thresh))
    )
    return water.Not().rename("non_water")


def apply_water_mask(image: ee.Image, non_water_mask: ee.Image) -> ee.Image:
    """Apply a precomputed non-water mask to all bands of an image."""
    return image.updateMask(non_water_mask)
