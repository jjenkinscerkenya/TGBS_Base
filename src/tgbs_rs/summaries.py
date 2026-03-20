import ee
import pandas as pd


def build_annual_band_composites(
    collection,
    band,
    start_date,
    end_date,
    composite_stat="median",
):
    """
    Build an annual ImageCollection of composites for a selected band,
    keeping only years that contain at least one image.

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
        Annual compositing statistic. Supported values:
        - 'median'
        - 'mean'

    Returns
    -------
    ee.ImageCollection
        ImageCollection containing one single-band image per year
        for years with at least one image.
    """
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)

    if composite_stat not in ["median", "mean"]:
        raise ValueError("composite_stat must be either 'median' or 'mean'")

    start_year = ee.Number.parse(start_date.format("YYYY"))
    end_year = ee.Number.parse(end_date.advance(-1, "day").format("YYYY"))

    years = ee.List.sequence(start_year, end_year)

    def make_annual_composite(year):
        year = ee.Number(year)
        year_start = ee.Date.fromYMD(year, 1, 1)
        year_end = year_start.advance(1, "year")

        annual_subset = collection.filterDate(year_start, year_end).select(
            [band]
        )

        image_count = annual_subset.size()

        if composite_stat == "median":
            composite = annual_subset.median()
        else:
            composite = annual_subset.mean()

        return ee.Image(
            ee.Algorithms.If(
                image_count.gt(0),
                composite.rename(band)
                .set("year", year)
                .set("system:time_start", year_start.millis())
                .set("image_count", image_count),
                None,
            )
        )

    annual_images = years.map(make_annual_composite)

    return ee.ImageCollection.fromImages(annual_images)


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
                "image_count": image.get("image_count"),
                "temporal_scale": image.get("temporal_scale"),
                "composite_stat": image.get("composite_stat"),
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


def build_annual_index_collections(
    collection,
    bands,
    start_date,
    end_date,
    composite_stat="median",
):
    """
    Build a dictionary of annual ImageCollections, one per band.
    """
    annual_collections = {}

    for band in bands:
        annual_collections[band] = build_annual_band_composites(
            collection=collection,
            band=band,
            start_date=start_date,
            end_date=end_date,
            composite_stat=composite_stat,
        )

    return annual_collections


def build_annual_index_timeseries(
    annual_collections,
    sites_fc,
    reducer=None,
    scale=10,
    tile_scale=4,
):
    """
    Convert annual composite collections to per-site long-format time series.
    """
    if reducer is None:
        reducer = ee.Reducer.mean()

    timeseries_dict = {}

    for band, annual_col in annual_collections.items():
        timeseries_dict[band] = collection_to_site_timeseries(
            collection=annual_col,
            sites_fc=sites_fc,
            bands=[band],
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )

    return timeseries_dict


def featurecollection_to_timeseries_df(fc, value_band):
    """
    Convert an ee.FeatureCollection of site-year summaries to a pandas DataFrame.
    """
    features = fc.getInfo()["features"]

    rows = []
    for feat in features:
        props = feat["properties"]
        rows.append(
            {
                "site_id": props.get("site_id"),
                "site_name": props.get("site_name"),
                "site_category": props.get("site_category"),
                "year": props.get("year"),
                "date": props.get("date"),
                "value": props.get(value_band),
                "image_count": props.get("image_count"),
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(["site_category", "site_name", "year"]).reset_index(
        drop=True
    )
    return df


def annual_collection_to_site_timeseries_df(
    annual_collection,
    sites_fc,
    band,
    reducer=None,
    scale=10,
    tile_scale=4,
):
    """
    Convert an annual composite ImageCollection to a pandas DataFrame
    by evaluating one annual image at a time.

    This avoids forcing Earth Engine to execute all reduceRegions
    operations concurrently.
    """
    if reducer is None:
        reducer = ee.Reducer.mean()

    annual_collection = ee.ImageCollection(annual_collection).sort(
        "system:time_start"
    )

    image_list = annual_collection.toList(annual_collection.size())
    n_images = annual_collection.size().getInfo()

    rows = []

    for i in range(n_images):
        image = ee.Image(image_list.get(i))

        reduced_fc = reduce_image_over_sites(
            image=image,
            sites_fc=sites_fc,
            bands=[band],
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )

        features = reduced_fc.getInfo()["features"]

        for feat in features:
            props = feat["properties"]
            rows.append(
                {
                    "site_id": props.get("site_id"),
                    "site_name": props.get("site_name"),
                    "site_category": props.get("site_category"),
                    "source_file": props.get("source_file"),
                    "date": props.get("date"),
                    "year": props.get("year"),
                    "month": props.get("month"),
                    "day": props.get("day"),
                    "value": props.get(band),
                    "image_count": props.get("image_count"),
                }
            )

    df = pd.DataFrame(rows)
    df = df.sort_values(["site_category", "site_name", "year"]).reset_index(
        drop=True
    )
    return df


def build_annual_multiband_composites(
    collection,
    bands,
    start_date,
    end_date,
    composite_stat="median",
):
    """
    Build an annual ImageCollection of multi-band composites, keeping only
    years that contain at least one image.

    Parameters
    ----------
    collection : ee.ImageCollection
        Input image collection.
    bands : list[str]
        Band names to composite.
    start_date : str or ee.Date
        Inclusive start date.
    end_date : str or ee.Date
        Exclusive end date.
    composite_stat : str, default 'median'
        Supported values: 'median', 'mean'.

    Returns
    -------
    ee.ImageCollection
        One multi-band image per year.
    """
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)

    if composite_stat not in ["median", "mean"]:
        raise ValueError("composite_stat must be either 'median' or 'mean'")

    start_year = ee.Number.parse(start_date.format("YYYY"))
    end_year = ee.Number.parse(end_date.advance(-1, "day").format("YYYY"))
    years = ee.List.sequence(start_year, end_year)

    def make_annual_composite(year):
        year = ee.Number(year)
        year_start = ee.Date.fromYMD(year, 1, 1)
        year_end = year_start.advance(1, "year")

        annual_subset = collection.filterDate(year_start, year_end).select(
            bands
        )
        image_count = annual_subset.size()

        if composite_stat == "median":
            composite = annual_subset.median()
        else:
            composite = annual_subset.mean()

        return ee.Image(
            ee.Algorithms.If(
                image_count.gt(0),
                composite.set(
                    {
                        "year": year,
                        "system:time_start": year_start.millis(),
                        "image_count": image_count,
                        "temporal_scale": "annual",
                        "composite_stat": composite_stat,
                    }
                ),
                None,
            )
        )

    return ee.ImageCollection.fromImages(years.map(make_annual_composite))
