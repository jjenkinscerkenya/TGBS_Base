import ee


def _validate_s2_sr_date_range(aoi, start_date, end_date):
    """
    Raises ValueError if the provided date window does not overlap the available
    COPERNICUS/S2_SR_HARMONIZED imagery over the AOI, or if start_date >= end_date.

    Assumes start_date and end_date are ee.Date.
    """
    col = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(aoi)

    # No imagery over AOI
    if col.size().getInfo() == 0:
        raise ValueError("No Sentinel-2 SR imagery found for the provided AOI.")

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
    # Start must be < max_ts (i.e. before the most recent image)
    if s_ms >= max_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is on/after the most recent S2_SR date over this AOI ({max_str})."
        )
    # End must be > min_ts (i.e. after the earliest image)
    if e_ms <= min_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is on/before the earliest S2_SR date over this AOI ({min_str})."
        )
    # Keep bounds within dataset window for stricter validity
    if s_ms < min_ts:
        raise ValueError(
            f"Invalid start_date: {s_str} is earlier than the first available S2_SR date over this AOI ({min_str})."
        )
    if e_ms > max_ts:
        raise ValueError(
            f"Invalid end_date: {e_str} is later than the most recent S2_SR date over this AOI ({max_str})."
        )
