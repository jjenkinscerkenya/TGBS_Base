import ee


import ee


def build_monthly_band_composites(
    collection,
    band,
    start_date,
    end_date,
    composite_stat="median",
):
    """
    Build a monthly ImageCollection of composites for a selected band,
    keeping only months that contain at least one image.

    Parameters
    ----------
    collection : ee.ImageCollection
        Input image collection.
    band : str
        Name of the band to composite, e.g. 'NDVI'.
    start_date : str or ee.Date
        Inclusive start date.
    end_date : str or ee.Date
        Exclusive end date.
    composite_stat : str, default 'median'
        Monthly compositing statistic. Supported values:
        - 'median'
        - 'mean'

    Returns
    -------
    ee.ImageCollection
        ImageCollection containing one single-band image per month
        for months with at least one image.
    """
    collection = ee.ImageCollection(collection).select([band])
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)

    if composite_stat not in {"median", "mean"}:
        raise ValueError("composite_stat must be either 'median' or 'mean'.")

    n_months = end_date.difference(start_date, "month").toInt()
    month_offsets = ee.List.sequence(0, n_months.subtract(1))

    def _month_feature(month_offset):
        month_offset = ee.Number(month_offset)

        month_start = start_date.advance(month_offset, "month")
        month_end = month_start.advance(1, "month")

        monthly_col = collection.filterDate(month_start, month_end)
        monthly_count = monthly_col.size()

        return ee.Feature(
            None,
            {
                "month_start": month_start.millis(),
                "year": month_start.get("year"),
                "month": month_start.get("month"),
                "date": month_start.format("YYYY-MM-dd"),
                "n_images": monthly_count,
            },
        )

    # Build a FeatureCollection of candidate months, then keep only months with data
    months_fc = ee.FeatureCollection(month_offsets.map(_month_feature))
    valid_months_fc = months_fc.filter(ee.Filter.gt("n_images", 0))

    def _feature_to_monthly_image(feature):
        feature = ee.Feature(feature)

        month_start = ee.Date(feature.get("month_start"))
        month_end = month_start.advance(1, "month")

        monthly_col = collection.filterDate(month_start, month_end)

        if composite_stat == "median":
            composite = monthly_col.median()
        else:
            composite = monthly_col.mean()

        return ee.Image(composite.rename([band])).set(
            {
                "system:time_start": month_start.millis(),
                "date": feature.get("date"),
                "year": feature.get("year"),
                "month": feature.get("month"),
                "n_images": feature.get("n_images"),
                "composite_stat": composite_stat,
                "band": band,
            }
        )

    monthly_images = valid_months_fc.map(_feature_to_monthly_image)

    return ee.ImageCollection(monthly_images)


def reduce_image_over_sites(
    image,
    sites_fc,
    bands=None,
    reducer=None,
    scale=10,
    tile_scale=4,
):
    """
    Reduce one image over a set of site polygons and attach image time metadata.

    Parameters
    ----------
    image : ee.Image
        Input image.
    sites_fc : ee.FeatureCollection
        Site polygons with metadata fields such as:
        - site_id
        - site_name
        - site_category
    bands : list[str] or None, default None
        Bands to summarize. If None, use all image bands.
    reducer : ee.Reducer or None, default None
        Reducer to apply. Defaults to ee.Reducer.mean().
    scale : int, default 10
        Reduction scale in meters.
    tile_scale : int, default 4
        Tile scale for large reductions.

    Returns
    -------
    ee.FeatureCollection
        One feature per input site polygon for this image date.
    """
    image = ee.Image(image)
    sites_fc = ee.FeatureCollection(sites_fc)

    if bands is not None:
        image = image.select(bands)

    if reducer is None:
        reducer = ee.Reducer.mean()

    date = ee.Date(image.get("system:time_start"))

    reduced = image.reduceRegions(
        collection=sites_fc,
        reducer=reducer,
        scale=scale,
        tileScale=tile_scale,
    )

    def _set_time_props(feature):
        return ee.Feature(feature).set(
            {
                "date": date.format("YYYY-MM-dd"),
                "year": date.get("year"),
                "month": date.get("month"),
                "day": date.get("day"),
                "system_time_start": image.get("system:time_start"),
                "image_id": image.id(),
            }
        )

    return reduced.map(_set_time_props)


def collection_to_site_timeseries(
    collection,
    sites_fc,
    bands,
    reducer=None,
    scale=10,
    tile_scale=4,
):
    """
    Summarize an ImageCollection over site polygons and return a long-format
    FeatureCollection time series.

    Parameters
    ----------
    collection : ee.ImageCollection
        Processed image collection.
    sites_fc : ee.FeatureCollection
        Site polygons with site metadata already attached.
    bands : list[str]
        Bands or indices to summarize.
    reducer : ee.Reducer or None, default None
        Reducer to apply. Defaults to ee.Reducer.mean().
    scale : int, default 10
        Reduction scale in meters.
    tile_scale : int, default 4
        Tile scale for large reductions.

    Returns
    -------
    ee.FeatureCollection
        Long-format time series with one row per image per site polygon.
    """
    collection = ee.ImageCollection(collection)
    sites_fc = ee.FeatureCollection(sites_fc)

    if reducer is None:
        reducer = ee.Reducer.mean()

    fc_list = collection.map(
        lambda image: reduce_image_over_sites(
            image=image,
            sites_fc=sites_fc,
            bands=bands,
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )
    ).toList(collection.size())

    return ee.FeatureCollection(fc_list).flatten()
