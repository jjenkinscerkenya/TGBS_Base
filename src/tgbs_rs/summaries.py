import ee


def _validate_composite_stat(composite_stat: str) -> None:
    """Validate the requested compositing statistic.

    Returns
    -------
    None
    """
    if composite_stat not in {"median", "mean"}:
        raise ValueError("composite_stat must be either 'median' or 'mean'")


def _apply_stat(
    collection: ee.ImageCollection, composite_stat: str
) -> ee.Image:
    """Apply a supported compositing statistic to an ImageCollection.

    Returns
    -------
    ee.Image
    """
    return (
        collection.median() if composite_stat == "median" else collection.mean()
    )


def _time_windows(
    start_date: ee.Date, end_date: ee.Date, temporal_scale: str
) -> ee.FeatureCollection:
    """Build a FeatureCollection of annual or monthly time windows.

    Returns
    -------
    ee.FeatureCollection
    """
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)

    if temporal_scale == "annual":
        start_year = ee.Number.parse(start_date.format("YYYY"))
        end_year = ee.Number.parse(end_date.advance(-1, "day").format("YYYY"))
        offsets = ee.List.sequence(0, end_year.subtract(start_year))

        def make_window(offset):
            offset = ee.Number(offset)
            window_start = ee.Date.fromYMD(start_year.add(offset), 1, 1)
            return ee.Feature(
                None,
                {
                    "window_start": window_start.millis(),
                    "date": window_start.format("YYYY-MM-dd"),
                    "year": window_start.get("year"),
                    "month": None,
                    "day": None,
                },
            )

    elif temporal_scale == "monthly":
        n_months = end_date.difference(start_date, "month").toInt()
        offsets = ee.List.sequence(0, n_months.subtract(1))

        def make_window(offset):
            offset = ee.Number(offset)
            window_start = start_date.advance(offset, "month")
            return ee.Feature(
                None,
                {
                    "window_start": window_start.millis(),
                    "date": window_start.format("YYYY-MM-dd"),
                    "year": window_start.get("year"),
                    "month": window_start.get("month"),
                    "day": None,
                },
            )

    else:
        raise ValueError("temporal_scale must be either 'annual' or 'monthly'")

    return ee.FeatureCollection(offsets.map(make_window))


def build_period_composites(
    collection: ee.ImageCollection,
    bands: list[str],
    start_date: str | ee.Date,
    end_date: str | ee.Date,
    temporal_scale: str = "annual",
    composite_stat: str = "median",
) -> ee.ImageCollection:
    """Build annual or monthly single-band or multi-band composites for periods with data.

    Returns
    -------
    ee.ImageCollection
    """
    _validate_composite_stat(composite_stat)

    collection = ee.ImageCollection(collection).select(bands)
    start_date = ee.Date(start_date)
    end_date = ee.Date(end_date)
    windows = _time_windows(start_date, end_date, temporal_scale)

    def make_composite(feature):
        feature = ee.Feature(feature)
        window_start = ee.Date(feature.get("window_start"))
        window_end = (
            window_start.advance(1, "year")
            if temporal_scale == "annual"
            else window_start.advance(1, "month")
        )
        subset = collection.filterDate(window_start, window_end)
        image_count = subset.size()
        composite = _apply_stat(subset, composite_stat)

        return ee.Image(
            ee.Algorithms.If(
                image_count.gt(0),
                composite.set(
                    {
                        "system:time_start": window_start.millis(),
                        "date": feature.get("date"),
                        "year": feature.get("year"),
                        "month": feature.get("month"),
                        "day": feature.get("day"),
                        "image_count": image_count,
                        "temporal_scale": temporal_scale,
                        "composite_stat": composite_stat,
                    }
                ),
                None,
            )
        )

    # Convert FeatureCollection to List, map, then back to ImageCollection
    images_list = windows.toList(windows.size()).map(make_composite)
    return ee.ImageCollection.fromImages(images_list)


def reduce_image_over_sites(
    image: ee.Image,
    sites_fc: ee.FeatureCollection,
    bands: list[str] | None = None,
    reducer: ee.Reducer | None = None,
    scale: int = 10,
    tile_scale: int = 4,
) -> ee.FeatureCollection:
    """Reduce one image over site polygons and attach image metadata to each output feature."""
    image = ee.Image(image.select(bands) if bands else image)
    reducer = reducer or ee.Reducer.mean()

    reduced = image.reduceRegions(
        collection=ee.FeatureCollection(sites_fc),
        reducer=reducer,
        scale=scale,
        tileScale=tile_scale,
    )

    meta = ee.Dictionary(
        {
            "image_id": image.get("system:index"),
            "system_time_start": image.get("system:time_start"),
            "year": image.get("year"),
            "month": image.get("month"),
            "day": image.get("day"),
            "date": image.get("date"),
            "image_count": image.get("image_count"),
            "temporal_scale": image.get("temporal_scale"),
            "composite_stat": image.get("composite_stat"),
        }
    )

    return reduced.map(lambda f: ee.Feature(f).setMulti(meta))


def collection_to_site_timeseries(
    collection: ee.ImageCollection,
    sites_fc: ee.FeatureCollection,
    bands: list[str],
    reducer: ee.Reducer | None = None,
    scale: int = 10,
    tile_scale: int = 4,
) -> ee.FeatureCollection:
    """Reduce every image in a collection over site polygons and return a long-format FeatureCollection.

    Returns
    -------
    ee.FeatureCollection
    """
    collection = ee.ImageCollection(collection)
    reducer = reducer or ee.Reducer.mean()

    fc_list = collection.map(
        lambda image: reduce_image_over_sites(
            image=ee.Image(image),
            sites_fc=sites_fc,
            bands=bands,
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )
    ).toList(collection.size())

    return ee.FeatureCollection(fc_list).flatten()


def build_index_collections(
    collection: ee.ImageCollection,
    bands: list[str],
    start_date: str | ee.Date,
    end_date: str | ee.Date,
    temporal_scale: str = "annual",
    composite_stat: str = "median",
) -> dict[str, ee.ImageCollection]:
    """Build one single-band composite collection per band for a requested temporal scale.

    Returns
    -------
    dict[str, ee.ImageCollection]
    """
    return {
        band: build_period_composites(
            collection=collection,
            bands=[band],
            start_date=start_date,
            end_date=end_date,
            temporal_scale=temporal_scale,
            composite_stat=composite_stat,
        )
        for band in bands
    }


def build_index_timeseries(
    collections: dict[str, ee.ImageCollection],
    sites_fc: ee.FeatureCollection,
    reducer: ee.Reducer | None = None,
    scale: int = 10,
    tile_scale: int = 4,
) -> dict[str, ee.FeatureCollection]:
    """Convert a dictionary of composite collections into per-site long-format time series.

    Returns
    -------
    dict[str, ee.FeatureCollection]
    """
    reducer = reducer or ee.Reducer.mean()
    return {
        band: collection_to_site_timeseries(
            collection=col,
            sites_fc=sites_fc,
            bands=[band],
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )
        for band, col in collections.items()
    }
