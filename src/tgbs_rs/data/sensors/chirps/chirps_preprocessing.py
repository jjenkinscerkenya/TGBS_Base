import ee

from tgbs_rs.config.config import CHIRPS_COLLECTION, CHIRPS_PRECIP_BAND


def validate_chirps_date_range(
    aoi: ee.Geometry,
    start_date: ee.Date,
    end_date: ee.Date,
):
    """
    Raise ValueError if the requested date range does not overlap the available
    CHIRPS v3 Daily Reanalysis imagery over the AOI, or if start_date >= end_date.

    Assumes start_date and end_date are ee.Date.
    """
    col = ee.ImageCollection(CHIRPS_COLLECTION).filterBounds(aoi)

    if col.size().getInfo() == 0:
        raise ValueError("No CHIRPS imagery found for the provided AOI.")

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
            f"Invalid start_date: {s_str} is on/after the most recent CHIRPS date over this AOI ({max_str})."
        )

    if e_ms <= min_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is on/before the earliest CHIRPS date over this AOI ({min_str})."
        )

    if s_ms < min_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is earlier than the first available CHIRPS date over this AOI ({min_str})."
        )

    if e_ms > max_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is later than the most recent CHIRPS date over this AOI ({max_str})."
        )


def process_chirps_image(image: ee.Image) -> ee.Image:
    """
    Select the CHIRPS precipitation band and preserve time properties.

    Output band:
    - precipitation (mm/day)
    """
    source = ee.Image(image)
    image = source.select([CHIRPS_PRECIP_BAND])
    return image.copyProperties(
        source, ["system:time_start", "year", "month", "day"]
    )


def get_chirps_collection(
    aoi: ee.Geometry,
    start_date: str | ee.Date,
    end_date: str | ee.Date,
) -> ee.ImageCollection:
    """
    Build a CHIRPS v3 Daily Reanalysis precipitation collection for the AOI and date range.

    Dataset:
    - UCSB-CHC/CHIRPS/V3/DAILY_RNL

    Units:
    - precipitation in mm/day
    """
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)

    validate_chirps_date_range(aoi, start_date, end_date)

    col = (
        ee.ImageCollection(CHIRPS_COLLECTION)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(process_chirps_image)
    )

    return col
