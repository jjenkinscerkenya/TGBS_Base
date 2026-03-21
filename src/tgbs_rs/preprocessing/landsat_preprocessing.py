import ee

from tgbs_rs.config.config import (
    L8_SR_COLLECTION,
    L8_SCALE_FACTOR,
    L8_ADD_OFFSET,
)
from tgbs_rs.masking.landsat_masking import (
    build_cloudfree_l8sr_col,
    build_l8_non_water_mask,
    apply_water_mask,
)
from tgbs_rs.indices.landsat_indices import (
    select_base_l8_bands,
    calc_tgbs_indices,
)


def validate_l8_sr_date_range(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
):
    """
    Raises ValueError if the provided date window does not overlap the available
    LANDSAT/LC08/C02/T1_L2 imagery over the AOI, or if start_date >= end_date.

    Assumes start_date and end_date are ee.Date.
    """
    col = ee.ImageCollection(L8_SR_COLLECTION).filterBounds(aoi)

    # No imagery over AOI
    if col.size().getInfo() == 0:
        raise ValueError("No Landsat 8 SR imagery found for the provided AOI.")

    # Dataset temporal bounds (ms since epoch) over AOI
    min_ts = col.aggregate_min("system:time_start").getInfo()
    max_ts = col.aggregate_max("system:time_start").getInfo()
    min_str = ee.Date(min_ts).format("YYYY-MM-dd").getInfo()
    max_str = ee.Date(max_ts).format("YYYY-MM-dd").getInfo()

    # Convert user inputs (ms + strings)
    s_ms = start_date.millis().getInfo()
    e_ms = end_date.millis().getInfo()
    s_str = start_date.format("YYYY-MM-dd").getInfo()
    e_str = end_date.format("YYYY-MM-dd").getInfo()

    if s_ms >= e_ms:
        raise ValueError(
            f"Invalid date range: start_date ({s_str}) must be earlier than end_date ({e_str})."
        )

    # Must overlap dataset window: [start, end) vs [min_ts, max_ts]
    if s_ms >= max_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is on/after the most recent L8_SR date over this AOI ({max_str})."
        )
    if e_ms <= min_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is on/before the earliest L8_SR date over this AOI ({min_str})."
        )
    if s_ms < min_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is earlier than the first available L8_SR date over this AOI ({min_str})."
        )
    if e_ms > max_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is later than the most recent L8_SR date over this AOI ({max_str})."
        )


def process_l8_image(image: ee.Image) -> ee.Image:
    """Select core Landsat-8 bands, scale reflectance, and add TGBS indices."""
    source = image
    image = (
        select_base_l8_bands(source)
        .multiply(L8_SCALE_FACTOR)
        .add(L8_ADD_OFFSET)
    )
    image = calc_tgbs_indices(image)
    return image.copyProperties(source, ["system:time_start"])


def get_l8_sr_collection(
    aoi: ee.Geometry,
    start_date: ee.Date,
    end_date: ee.Date,
    apply_water_masking: bool = False,
) -> ee.ImageCollection:
    """Build a cloud-masked Landsat 8 SR collection with indices for the AOI and date range."""
    validate_l8_sr_date_range(aoi, start_date, end_date)

    l8_cloudfree = build_cloudfree_l8sr_col(aoi, start_date, end_date)
    l8_processed = l8_cloudfree.map(process_l8_image)

    if not apply_water_masking:
        return l8_processed

    non_water_mask = build_l8_non_water_mask(l8_processed)
    return l8_processed.map(lambda img: apply_water_mask(img, non_water_mask))
