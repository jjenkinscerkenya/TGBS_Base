import ee
from tgbs_rs.utils import _validate_s2_sr_date_range
from config import *


# Cloud Masking
def mask_edges(image):
    """Masks edge pixels for 20m and 60m bands"""
    return image.updateMask(image.select("B8A").mask()).updateMask(
        image.select("B9").mask()
    )


def get_s2_sr_cld_col(aoi, start_date, end_date):
    """
    Join S2_SR_HARMONIZED with S2_CLOUD_PROBABILITY (by system:index), filtered to AOI/dates.

    Args:
        aoi (ee.Geometry)
        start_date (ee.Date)
        end_date (ee.Date)

    Returns:
        ee.ImageCollection: A filtered collection of S2_SR_HAR and S2_CLOUD_PROB collections
    """
    # Validate dates
    _validate_s2_sr_date_range(aoi, start_date, end_date)

    # Import and filter S2 SR.
    s2_sr_col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", CLOUD_FILTER))
        .map(mask_edges)
    )

    # Import and filter s2cloudless.
    s2_cloudless_col = (
        ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
    )

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    joined = ee.ImageCollection(
        ee.Join.saveFirst("s2cloudless").apply(
            **{
                "primary": s2_sr_col,
                "secondary": s2_cloudless_col,
                "condition": ee.Filter.equals(
                    leftField="system:index", rightField="system:index"
                ),
            }
        )
    )

    return joined


def add_cld_shdw_mask(img):
    """
    Build a cloud+shadow mask for a Sentinel-2 SR image.

    Uses s2cloudless cloud probability (thresholded), dark NIR pixels (reflectance)
    excluding water (SCL == 6), and a directional shadow projection along the solar
    azimuth. Applies an opening (erosion then dilation) in meters to clean/grow the mask.

    Args:
        img (ee.Image): A COPERNICUS/S2_SR_HARMONIZED image joined with an s2cloudless
            image (accessible via img.get('s2cloudless')) and including the SCL band.

    Returns:
        img (ee.Image): The original image with an added 'cloudmask' band (1 = cloud|shadow, 0 = clear).
    """
    # Cloud mask from s2cloudless
    cld_prb = ee.Image(img.get("s2cloudless")).select("probability")
    is_cloud = cld_prb.gt(CLD_PRB_THRESH)

    # Dark pixels (NIR) excluding water (SCL == 6)
    not_water = img.select("SCL").neq(6)
    nir_refl = img.select("B8").multiply(0.0001)
    dark_pixels = nir_refl.lt(NIR_DRK_THRESH).And(not_water)

    # Project shadows from clouds along solar azimuth
    # Angle in DEGREES, distance in PIXELS (per docs). Reproject the cloud mask
    # to a coarse grid so "pixels" == DDT_SCALE_M, then convert km -> pixels.
    shadow_azimuth_deg = ee.Number(90).subtract(
        ee.Number(img.get("MEAN_SOLAR_AZIMUTH_ANGLE"))
    )
    max_dist_px = (
        ee.Number(CLD_PRJ_DIST_KM).multiply(1000.0).divide(DDT_SCALE_M).int()
    )

    clouds_for_ddt = is_cloud.reproject(
        crs=img.select(0).projection(), scale=DDT_SCALE_M
    )
    cld_proj = (
        clouds_for_ddt.directionalDistanceTransform(
            shadow_azimuth_deg, max_dist_px
        )
        .select("distance")
        .mask()
    )

    is_shadow = cld_proj.And(dark_pixels)

    # Combine cloud + shadow then apply opening (erode → dilate) in METERS
    cld_or_shdw = is_cloud.Or(is_shadow)
    opened = (
        cld_or_shdw.reproject(
            crs=img.select(0).projection(), scale=MORPH_SCALE_M
        )
        .focalMin(ERODE_RADIUS_M, units="meters")
        .focalMax(BUFFER_M, units="meters")
    )

    return img.addBands(opened.rename("cloudmask"))


def apply_cld_shdw_mask(img):
    """Invert 'cloudmask' and apply it to ALL bands."""
    clear = img.select("cloudmask").Not()
    return img.updateMask(clear)


def build_cloudfree_s2sr_col(aoi, start_date, end_date):
    """Return the collection with cloud and cloud shadow masks applied."""
    col = (
        get_s2_sr_cld_col(aoi, start_date, end_date)
        .map(add_cld_shdw_mask)
        .map(apply_cld_shdw_mask)
    )
    return col


# Water Masking
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
