import ee
import pandas as pd
import numpy as np

from tgbs_rs.config.specs import (
    get_metric_label,
    get_annual_plot_order,
    get_seasonal_plot_order,
    make_annual_title,
    make_seasonal_title,
)

from tgbs_rs.visualization.plots import (
    set_plot_theme,
    plot_focal_vs_envelope,
    plot_category_mean_trajectories,
)

from tgbs_rs.visualization.tables import (
    select_analysis_columns,
    to_long_index_table,
    summarize_by_category_year,
    build_category_envelope,
    build_focal_series,
    build_corridor_series,
    join_focal_to_envelope,
    summarize_baseline_ranges,
    add_standardized_anomalies,
    summarize_baseline_vs_current,
    compute_site_trends,
    filter_season_table,
)


def _validate_composite_stat(composite_stat: str):
    """Validate the requested compositing statistic.

    Returns
    -------
    None
    """
    valid = {"mean", "median", "sum"}
    if composite_stat not in valid:
        raise ValueError(f"composite_stat must be one of {sorted(valid)}")


def _apply_stat(
    collection: ee.ImageCollection, composite_stat: str
) -> ee.Image:
    """Apply a supported compositing statistic to an ImageCollection.

    Returns
    -------
    ee.Image
    """
    if composite_stat == "mean":
        return collection.mean()
    if composite_stat == "median":
        return collection.median()
    if composite_stat == "sum":
        return collection.sum()
    raise ValueError(f"Unsupported composite_stat: {composite_stat}")


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


def reduce_image_over_region(
    image: ee.Image,
    region: ee.Geometry,
    bands: list[str],
    reducer: ee.Reducer | None = None,
    scale: int = 5566,
    tile_scale: int = 4,
) -> ee.Feature:
    """
    Reduce one image over a single region geometry and return a Feature with
    the reduced band values plus key image properties.
    """
    image = ee.Image(image).select(bands)
    reducer = reducer or ee.Reducer.mean()

    stats = image.reduceRegion(
        reducer=reducer,
        geometry=region,
        scale=scale,
        maxPixels=1e13,
        tileScale=tile_scale,
    )

    props = ee.Dictionary(
        {
            "date": image.get("date"),
            "year": image.get("year"),
            "month": image.get("month"),
            "day": image.get("day"),
            "image_count": image.get("image_count"),
            "temporal_scale": image.get("temporal_scale"),
            "composite_stat": image.get("composite_stat"),
            "system_time_start": image.get("system:time_start"),
        }
    ).combine(stats, overwrite=True)

    return ee.Feature(None, props)


def collection_to_region_timeseries(
    collection: ee.ImageCollection,
    region: ee.Geometry,
    bands: list[str],
    reducer: ee.Reducer | None = None,
    scale: int = 5566,
    tile_scale: int = 4,
) -> ee.FeatureCollection:
    """
    Reduce every image in a collection over a single region geometry and return
    a long-format FeatureCollection.
    """
    collection = ee.ImageCollection(collection)
    reducer = reducer or ee.Reducer.mean()

    fc = collection.map(
        lambda image: reduce_image_over_region(
            image=ee.Image(image),
            region=region,
            bands=bands,
            reducer=reducer,
            scale=scale,
            tile_scale=tile_scale,
        )
    )

    return ee.FeatureCollection(fc)


################################### Annual Metrics ############################################


def build_annual_metrics_long_table(
    annual_df: pd.DataFrame,
    metric_cols: list[str],
    extra_cols: list[str] = None,
) -> pd.DataFrame:
    """
    Convert a prepared annual site-year table into a long-format annual
    metrics table ready for summary building and plotting. This is the
    main entry point for annual HLS or Sentinel-2 metrics workflows.
    """
    extra_cols = extra_cols or [
        "date",
        "image_count",
        "temporal_scale",
        "composite_stat",
    ]
    core = select_analysis_columns(
        df=annual_df,
        value_cols=metric_cols,
        extra_cols=extra_cols,
    )

    id_cols = [c for c in core.columns if c not in metric_cols]
    return to_long_index_table(df=core, value_cols=metric_cols, id_cols=id_cols)


def build_annual_metrics_outputs(
    annual_long_df: pd.DataFrame,
) -> dict:
    """
    Build the core derived annual comparison products needed for focal,
    reference, degraded, baseline-current, anomaly, and trend analyses.
    The returned dictionary keeps the workflow compact while preserving each
    intermediate output for audit and downstream plotting.
    """
    category_summary = summarize_by_category_year(
        df_long=annual_long_df,
        group_cols=["site_category", "year"],
    )

    reference_envelope = build_category_envelope(
        df_long=annual_long_df,
        category="reference",
    )

    degraded_envelope = build_category_envelope(
        df_long=annual_long_df,
        category="degraded",
    )

    focal = build_focal_series(annual_long_df)
    corridor = build_corridor_series(annual_long_df)

    focal_vs_reference = join_focal_to_envelope(
        focal_long=focal,
        envelope_df=reference_envelope,
        envelope_label="reference",
    )

    corridor_vs_reference = join_focal_to_envelope(
        focal_long=corridor,
        envelope_df=reference_envelope,
        envelope_label="reference",
    )

    focal_vs_degraded = join_focal_to_envelope(
        focal_long=focal,
        envelope_df=degraded_envelope,
        envelope_label="degraded",
    )

    corridor_vs_degraded = join_focal_to_envelope(
        focal_long=corridor,
        envelope_df=degraded_envelope,
        envelope_label="degraded",
    )

    reference_baseline_ranges = summarize_baseline_ranges(
        df_long=annual_long_df,
        category="reference",
    )

    focal_reference_anomalies = add_standardized_anomalies(
        focal_long=focal_vs_reference,
        baseline_ranges=reference_baseline_ranges,
        label="reference",
    )

    period_summary = summarize_baseline_vs_current(annual_long_df)
    site_trends = compute_site_trends(annual_long_df)

    return {
        "annual_long": annual_long_df,
        "category_summary": category_summary,
        "reference_envelope": reference_envelope,
        "degraded_envelope": degraded_envelope,
        "focal": focal,
        "corridor": corridor,
        "focal_vs_reference": focal_vs_reference,
        "corridor_vs_reference": corridor_vs_reference,
        "focal_vs_degraded": focal_vs_degraded,
        "corridor_vs_degraded": corridor_vs_degraded,
        "reference_baseline_ranges": reference_baseline_ranges,
        "focal_reference_anomalies": focal_reference_anomalies,
        "period_summary": period_summary,
        "site_trends": site_trends,
    }


def run_annual_metrics_workflow(
    annual_df: pd.DataFrame,
    metric_cols: list[str],
) -> dict:
    """
    Run the full annual metrics table-building workflow starting from a
    prepared annual table. This wrapper keeps the notebook or analysis script
    concise while returning all core annual comparison products together.
    """
    annual_long = build_annual_metrics_long_table(
        annual_df=annual_df,
        metric_cols=metric_cols,
    )
    return build_annual_metrics_outputs(annual_long_df=annual_long)


def plot_annual_metrics_core_figures(
    outputs: dict,
    source_label: str,
    metric_cols: list[str],
    comparison_label: str = "Focal Vs Reference",
    envelope_label: str = "reference",
    use_spec_order: bool = True,
) -> list[tuple]:
    """
    Generate annual focal-versus-envelope figures for any requested metric list.
    The function can use family-aware preferred ordering from figure specs or
    preserve the metric order supplied by the caller.
    """
    set_plot_theme()
    figs = []

    ordered_metrics = (
        get_annual_plot_order(metric_cols) if use_spec_order else metric_cols
    )

    comparison_key = f"focal_vs_{envelope_label}"

    corridor_key = f"corridor_vs_{envelope_label}"
    corridor_df = outputs.get(corridor_key)

    for metric_col in ordered_metrics:
        fig, ax = plot_focal_vs_envelope(
            comparison_df=outputs[comparison_key],
            corridor_df=corridor_df,
            metric_col=metric_col,
            envelope_label=envelope_label,
            title=make_annual_title(
                metric_col=metric_col,
                comparison_label=comparison_label,
                source_label=source_label,
            ),
            ylabel=get_metric_label(metric_col),
        )
        figs.append((fig, ax))

    return figs


def plot_annual_metrics_category_figures(
    outputs: dict,
    source_label: str,
    metric_cols: list[str],
) -> list[tuple]:
    """
    Generate annual category mean trajectory figures for the requested metrics.
    These plots are useful as supporting diagnostics before or alongside the
    main focal-versus-reference envelope figures.
    """
    set_plot_theme()
    figs = []

    for metric_col in get_annual_plot_order(metric_cols):
        title = f"{source_label} Annual {get_metric_label(metric_col)}: Category Mean Trajectories"
        fig, ax = plot_category_mean_trajectories(
            summary_df=outputs["category_summary"],
            metric_col=metric_col,
            title=title,
            ylabel=get_metric_label(metric_col),
        )
        figs.append((fig, ax))

    return figs


######################## Seasonal Metrics ####################################


def build_seasonal_metrics_long_table(
    seasonal_df: pd.DataFrame,
    season: str,
    metric_cols: list[str],
) -> pd.DataFrame:
    """
    Filter a prepared seasonal summary table to one season and convert it into
    a long-format metrics table ready for comparison summaries and plots.
    This keeps wet and dry analyses clearly separated and fully parallel.
    """
    season_core = filter_season_table(
        df=seasonal_df,
        season=season,
        value_cols=metric_cols,
    )

    id_cols = [c for c in season_core.columns if c not in metric_cols]
    return to_long_index_table(
        df=season_core, value_cols=metric_cols, id_cols=id_cols
    )


def build_seasonal_metrics_outputs(
    seasonal_long_df: pd.DataFrame,
) -> dict:
    """
    Build the core derived seasonal comparison outputs for one season only.
    The result mirrors the annual workflow structure so wet and dry products
    can be interpreted and plotted with the same logic.
    """
    category_summary = summarize_by_category_year(
        df_long=seasonal_long_df,
        group_cols=["site_category", "year"],
    )

    reference_envelope = build_category_envelope(
        df_long=seasonal_long_df,
        category="reference",
    )

    degraded_envelope = build_category_envelope(
        df_long=seasonal_long_df,
        category="degraded",
    )

    focal = build_focal_series(seasonal_long_df)
    corridor = build_corridor_series(seasonal_long_df)

    focal_vs_reference = join_focal_to_envelope(
        focal_long=focal,
        envelope_df=reference_envelope,
        envelope_label="reference",
    )

    corridor_vs_reference = join_focal_to_envelope(
        focal_long=corridor,
        envelope_df=reference_envelope,
        envelope_label="reference",
    )

    focal_vs_degraded = join_focal_to_envelope(
        focal_long=focal,
        envelope_df=degraded_envelope,
        envelope_label="degraded",
    )

    corridor_vs_degraded = join_focal_to_envelope(
        focal_long=corridor,
        envelope_df=degraded_envelope,
        envelope_label="degraded",
    )

    reference_baseline_ranges = summarize_baseline_ranges(
        df_long=seasonal_long_df,
        category="reference",
    )

    focal_reference_anomalies = add_standardized_anomalies(
        focal_long=focal_vs_reference,
        baseline_ranges=reference_baseline_ranges,
        label="reference",
    )

    period_summary = summarize_baseline_vs_current(seasonal_long_df)
    site_trends = compute_site_trends(seasonal_long_df)

    return {
        "seasonal_long": seasonal_long_df,
        "category_summary": category_summary,
        "reference_envelope": reference_envelope,
        "degraded_envelope": degraded_envelope,
        "focal": focal,
        "corridor": corridor,
        "focal_vs_reference": focal_vs_reference,
        "corridor_vs_reference": corridor_vs_reference,
        "focal_vs_degraded": focal_vs_degraded,
        "corridor_vs_degraded": corridor_vs_degraded,
        "reference_baseline_ranges": reference_baseline_ranges,
        "focal_reference_anomalies": focal_reference_anomalies,
        "period_summary": period_summary,
        "site_trends": site_trends,
    }


def run_single_season_metrics_workflow(
    seasonal_df: pd.DataFrame,
    season: str,
    metric_cols: list[str],
) -> dict:
    """
    Run the full seasonal workflow for one season such as wet or dry starting
    from a prepared seasonal summary table. This wrapper keeps seasonal figure
    pipelines concise and preserves a clean separation between seasons.
    """
    seasonal_long = build_seasonal_metrics_long_table(
        seasonal_df=seasonal_df,
        season=season,
        metric_cols=metric_cols,
    )
    return build_seasonal_metrics_outputs(seasonal_long_df=seasonal_long)


def run_all_season_metrics_workflows(
    seasonal_df: pd.DataFrame,
    metric_cols: list[str],
    seasons: list[str] = None,
) -> dict:
    """
    Run the seasonal workflow for all requested seasons and return a nested
    output dictionary keyed by season. This provides a compact orchestration
    layer for wet and dry metrics analyses in one call.
    """
    seasons = seasons or ["wet", "dry"]
    return {
        season: run_single_season_metrics_workflow(
            seasonal_df=seasonal_df,
            season=season,
            metric_cols=metric_cols,
        )
        for season in seasons
    }


def plot_single_season_metrics_core_figures(
    outputs: dict,
    season: str,
    source_label: str,
    metric_cols: list[str],
    comparison_label: str = "Focal Vs Reference",
    envelope_label: str = "reference",
    use_spec_order: bool = True,
) -> list[tuple]:
    """
    Generate focal-versus-envelope figures for one season and any requested
    metric list. The function can use family-aware seasonal ordering from
    figure specs or preserve the metric order supplied by the caller.
    """
    set_plot_theme()
    figs = []

    ordered_metrics = (
        get_seasonal_plot_order(season=season, metric_cols=metric_cols)
        if use_spec_order
        else metric_cols
    )

    comparison_key = f"focal_vs_{envelope_label}"

    corridor_key = f"corridor_vs_{envelope_label}"
    corridor_df = outputs.get(corridor_key)

    for metric_col in ordered_metrics:
        fig, ax = plot_focal_vs_envelope(
            comparison_df=outputs[comparison_key],
            corridor_df=corridor_df,
            metric_col=metric_col,
            envelope_label=envelope_label,
            title=make_seasonal_title(
                metric_col=metric_col,
                season=season,
                comparison_label=comparison_label,
                source_label=source_label,
            ),
            ylabel=get_metric_label(metric_col),
        )
        figs.append((fig, ax))

    return figs


def plot_single_season_category_figures(
    outputs: dict,
    season: str,
    source_label: str,
    metric_cols: list[str],
) -> list[tuple]:
    """
    Generate category mean seasonal trajectory figures for one season only.
    These are useful supporting plots for checking whether focal, reference,
    and degraded groups separate consistently within the chosen season.
    """
    set_plot_theme()
    figs = []

    for season_name, metric_col in get_seasonal_plot_order(
        [(season, m) for m in metric_cols]
    ):
        season_label = season_name.replace("-", " ").title()
        title = f"{source_label} {season_label} {get_metric_label(metric_col)}: Category Mean Trajectories"
        fig, ax = plot_category_mean_trajectories(
            summary_df=outputs["category_summary"],
            metric_col=metric_col,
            title=title,
            ylabel=get_metric_label(metric_col),
        )
        figs.append((fig, ax))

    return figs
