import ee

from tgbs_rs.config import (
    HLS_L30_COLLECTION,
    HLS_S30_COLLECTION,
    HLS_SCALE_FACTOR,
    HLS_ADD_OFFSET,
)
from tgbs_rs.data.sensors.hls.hls_masking import (
    build_cloudfree_hls_l30_col,
    build_cloudfree_hls_s30_col,
    build_hls_non_water_mask,
    apply_water_mask,
)
from tgbs_rs.data.sensors.hls.hls_indices import (
    select_base_hls_bands,
    calc_tgbs_indices,
)


def validate_hls_date_range(
    aoi: ee.Geometry, start_date: ee.Date, end_date: ee.Date
):
    """
    Raises ValueError if the provided date window does not overlap the available
    HLSL30/HLSS30 imagery over the AOI, or if start_date >= end_date.

    Assumes start_date and end_date are ee.Date.
    """
    l30 = ee.ImageCollection(HLS_L30_COLLECTION).filterBounds(aoi)
    s30 = ee.ImageCollection(HLS_S30_COLLECTION).filterBounds(aoi)
    col = l30.merge(s30)

    if col.size().getInfo() == 0:
        raise ValueError("No HLS imagery found for the provided AOI.")

    min_ts = col.aggregate_min("system:time_start").getInfo()
    max_ts = col.aggregate_max("system:time_start").getInfo()
    min_str = ee.Date(min_ts).format("YYYY-MM-dd").getInfo()
    max_str = ee.Date(max_ts).format("YYYY-MM-dd").getInfo()

    s_ms = start_date.millis().getInfo()
    e_ms = end_date.millis().getInfo()
    s_str = start_date.format("YYYY-MM-dd").getInfo()
    e_str = end_date.format("YYYY-MM-dd").getInfo()

    if s_ms >= e_ms:
        raise ValueError(
            f"Invalid date range: start_date ({s_str}) must be earlier than end_date ({e_str})."
        )

    if s_ms >= max_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is on/after the most recent HLS date over this AOI ({max_str})."
        )
    if e_ms <= min_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is on/before the earliest HLS date over this AOI ({min_str})."
        )
    if s_ms < min_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is earlier than the first available HLS date over this AOI ({min_str})."
        )
    if e_ms > max_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is later than the most recent HLS date over this AOI ({max_str})."
        )


def harmonize_hls_l30_bands(image: ee.Image) -> ee.Image:
    """
    Rename HLSL30 source bands to a common merged band schema.

    HLSL30:
    B2 -> BLUE
    B3 -> GREEN
    B4 -> RED
    B5 -> NIR
    B6 -> SWIR1
    B7 -> SWIR2
    """
    source = image
    image = image.select(
        ["B2", "B3", "B4", "B5", "B6", "B7"],
        ["BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2"],
    )
    return ee.Image(
        image.copyProperties(source, ["system:time_start", "system:index"])
    )


def harmonize_hls_s30_bands(image: ee.Image) -> ee.Image:
    """
    Rename HLSS30 source bands to a common merged band schema.

    HLSS30:
    B2  -> BLUE
    B3  -> GREEN
    B4  -> RED
    B8A -> NIR
    B11 -> SWIR1
    B12 -> SWIR2
    """
    source = image
    image = image.select(
        ["B2", "B3", "B4", "B8A", "B11", "B12"],
        ["BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2"],
    )
    return ee.Image(
        image.copyProperties(source, ["system:time_start", "system:index"])
    )


def process_hls_l30_image(image: ee.Image) -> ee.Image:
    """Rename HLSL30 bands and add TGBS indices."""
    source = image
    image = harmonize_hls_l30_bands(source)
    image = select_base_hls_bands(image)
    image = calc_tgbs_indices(image)
    return image.copyProperties(source, ["system:time_start"])


def process_hls_s30_image(image: ee.Image) -> ee.Image:
    """Rename HLSS30 bands and add TGBS indices."""
    source = image
    image = harmonize_hls_s30_bands(source)
    image = select_base_hls_bands(image)
    image = calc_tgbs_indices(image)
    return image.copyProperties(source, ["system:time_start"])


def get_hls_l30_collection(
    aoi: ee.Geometry,
    start_date: ee.Date,
    end_date: ee.Date,
) -> ee.ImageCollection:
    """Build a processed HLSL30 collection with indices."""
    return build_cloudfree_hls_l30_col(aoi, start_date, end_date).map(
        process_hls_l30_image
    )


def get_hls_s30_collection(
    aoi: ee.Geometry,
    start_date: ee.Date,
    end_date: ee.Date,
) -> ee.ImageCollection:
    """Build a processed HLSS30 collection with indices."""
    return build_cloudfree_hls_s30_col(aoi, start_date, end_date).map(
        process_hls_s30_image
    )


def get_hls_merged_collection(
    aoi: ee.Geometry,
    start_date: ee.Date,
    end_date: ee.Date,
    apply_water_masking: bool = False,
) -> ee.ImageCollection:
    """
    Build a merged processed HLS collection (L30 + S30) with shared bands and indices.

    This is the recommended official long-term 30 m trend collection.
    """
    validate_hls_date_range(aoi, start_date, end_date)

    hls_l30 = get_hls_l30_collection(aoi, start_date, end_date)
    hls_s30 = get_hls_s30_collection(aoi, start_date, end_date)

    merged = hls_l30.merge(hls_s30).sort("system:time_start")

    if not apply_water_masking:
        return merged

    non_water_mask = build_hls_non_water_mask(merged)
    return merged.map(
        lambda img: ee.Image(apply_water_mask(img, non_water_mask))
    )
