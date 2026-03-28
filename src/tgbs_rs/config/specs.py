METRIC_SPECS = {
    "NDVI": {
        "family": "vegetation_cover",
        "label": "NDVI",
        "annual_priority": "primary",
        "seasonal_priority": "primary",
        "higher_is_better": True,
    },
    "SAVI": {
        "family": "vegetation_cover",
        "label": "SAVI",
        "annual_priority": "supporting",
        "seasonal_priority": "supporting",
        "higher_is_better": True,
    },
    "EVI": {
        "family": "vegetation_cover",
        "label": "EVI",
        "annual_priority": "supporting",
        "seasonal_priority": "optional",
        "higher_is_better": True,
    },
    "NDMI": {
        "family": "moisture_disturbance",
        "label": "NDMI",
        "annual_priority": "primary",
        "seasonal_priority": "supporting",
        "higher_is_better": True,
    },
    "NBR": {
        "family": "moisture_disturbance",
        "label": "NBR",
        "annual_priority": "primary",
        "seasonal_priority": "supporting",
        "higher_is_better": True,
    },
}


SOURCE_SPECS = {
    "HLS": {
        "role": "official_long_term",
        "year_start": 2014,
        "year_end": 2025,
    },
    "Sentinel-2": {
        "role": "supplemental_current_period",
        "year_start": 2019,
        "year_end": 2025,
    },
}


SEASON_SPECS = {
    "wet": {
        "label": "Wet-Season",
        "priority": "primary",
    },
    "dry": {
        "label": "Dry-Season",
        "priority": "primary",
    },
}


FAMILY_ANNUAL_PLOT_ORDER = {
    "vegetation_cover": ["NDVI", "SAVI", "EVI"],
    "moisture_disturbance": ["NDMI", "NBR", "NDVI"],
}


FAMILY_SEASONAL_PLOT_ORDER = {
    "vegetation_cover": [
        ("wet", "NDVI"),
        ("dry", "NDVI"),
        ("wet", "SAVI"),
        ("dry", "SAVI"),
        ("wet", "EVI"),
        ("dry", "EVI"),
    ],
    "moisture_disturbance": [
        ("dry", "NDMI"),
        ("wet", "NDMI"),
        ("dry", "NBR"),
        ("wet", "NBR"),
        ("dry", "NDVI"),
        ("wet", "NDVI"),
    ],
}


def get_metric_family(metric_col: str) -> str:
    """
    Return the metric family for a given metric code. This is used to route
    ordering and labeling behavior through a shared metadata layer rather than
    hard-coding assumptions in workflow wrappers.
    """
    return METRIC_SPECS.get(metric_col, {}).get("family", "other")


def get_metric_label(metric_col: str) -> str:
    """
    Return the display label for a metric used in titles, axis labels, and
    figure text. This keeps metric naming centralized and consistent across
    annual and seasonal plots.
    """
    return METRIC_SPECS.get(metric_col, {}).get("label", metric_col)


def get_metric_priority(metric_col: str, temporal_scale: str = "annual") -> str:
    """
    Return the configured plotting priority for a metric at the requested
    temporal scale. This can help separate primary from supporting metrics
    when building figure sets.
    """
    key = (
        "annual_priority" if temporal_scale == "annual" else "seasonal_priority"
    )
    return METRIC_SPECS.get(metric_col, {}).get(key, "unspecified")


def get_metrics_plot_order(
    metric_cols: list[str],
    temporal_scale: str = "annual",
    season: str = None,
) -> list[str]:
    """
    Return a preferred plotting order for the requested metrics based on
    metric-family specifications. If no family-level order applies, the
    original metric list order is preserved.
    """
    if not metric_cols:
        return []

    families = {get_metric_family(m) for m in metric_cols}
    if len(families) != 1:
        return metric_cols

    family = next(iter(families))

    if temporal_scale == "annual":
        preferred = FAMILY_ANNUAL_PLOT_ORDER.get(family, [])
        ordered = [m for m in preferred if m in metric_cols]
        remainder = [m for m in metric_cols if m not in ordered]
        return ordered + remainder

    preferred_pairs = FAMILY_SEASONAL_PLOT_ORDER.get(family, [])
    ordered = [
        m for s, m in preferred_pairs if s == season and m in metric_cols
    ]
    remainder = [m for m in metric_cols if m not in ordered]
    return ordered + remainder


def get_annual_plot_order(metric_cols: list[str]) -> list[str]:
    """
    Return the preferred annual plotting order for the requested metrics.
    This uses family-specific ordering when possible and otherwise falls back
    to the input order provided by the caller.
    """
    return get_metrics_plot_order(
        metric_cols=metric_cols,
        temporal_scale="annual",
    )


def get_seasonal_plot_order(season: str, metric_cols: list[str]) -> list[str]:
    """
    Return the preferred plotting order for one season and a requested list
    of metrics. This keeps seasonal figure generation simple while preserving
    a consistent metric sequence for each analysis family.
    """
    return get_metrics_plot_order(
        metric_cols=metric_cols,
        temporal_scale="seasonal",
        season=season,
    )


def make_annual_title(
    metric_col: str, comparison_label: str, source_label: str
) -> str:
    """
    Build a standardized annual figure title from source, metric, and
    comparison context. This ensures that annual titles remain consistent
    across vegetation cover, moisture, disturbance, and future metric families.
    """
    metric_label = get_metric_label(metric_col)
    return f"{source_label} Annual {metric_label}: {comparison_label}"


def make_seasonal_title(
    metric_col: str,
    season: str,
    comparison_label: str,
    source_label: str,
) -> str:
    """
    Build a standardized seasonal figure title from source, season, metric,
    and comparison context. This keeps wet- and dry-season figures parallel
    across multiple analysis themes.
    """
    metric_label = get_metric_label(metric_col)
    season_label = SEASON_SPECS.get(season, {}).get("label", season.title())
    return f"{source_label} {season_label} {metric_label}: {comparison_label}"


def make_category_title(
    metric_col: str,
    source_label: str,
    temporal_label: str,
) -> str:
    """
    Build a standardized category-summary title for annual or seasonal metric
    figures. This is useful for focal, reference, and degraded category mean
    trajectory plots used as supporting diagnostics.
    """
    metric_label = get_metric_label(metric_col)
    return f"{source_label} {temporal_label} {metric_label}: Category Mean Trajectories"
