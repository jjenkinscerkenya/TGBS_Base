INDEX_SPECS = {
    "NIRv": {
        "family": "productivity",
        "label": "NIRv",
        "annual_priority": "primary",
        "seasonal_priority": "primary",
    },
    "EVI": {
        "family": "productivity",
        "label": "EVI",
        "annual_priority": "supporting",
        "seasonal_priority": "optional",
    },
    "NDVI": {
        "family": "productivity",
        "label": "NDVI",
        "annual_priority": "communication",
        "seasonal_priority": "optional",
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


ANNUAL_PLOT_ORDER = [
    "NIRv",
    "EVI",
    "NDVI",
]


SEASONAL_PLOT_ORDER = [
    ("wet", "NIRv"),
    ("dry", "NIRv"),
    ("wet", "EVI"),
    ("dry", "EVI"),
]


def get_metric_label(metric_col: str) -> str:
    """
    Return the display label for a metric used in titles, axis labels, and
    other figure text. This centralizes figure naming so future additions such
    as disturbance, moisture, or biomass metrics stay consistent.
    """
    return INDEX_SPECS.get(metric_col, {}).get("label", metric_col)


def get_annual_plot_order(metric_cols: list[str] = None) -> list[str]:
    """
    Return the preferred annual plotting order filtered to the metrics that are
    currently available. This keeps workflow code simple while preserving a
    consistent primary-to-supporting figure sequence.
    """
    metric_cols = metric_cols or ANNUAL_PLOT_ORDER
    return [m for m in ANNUAL_PLOT_ORDER if m in metric_cols]


def get_seasonal_plot_order(
    season_metric_pairs: list[tuple[str, str]] = None,
) -> list[tuple[str, str]]:
    """
    Return the preferred seasonal plotting order filtered to the requested
    season-metric pairs. This supports a consistent wet-first and dry-second
    figure sequence while allowing optional support metrics when desired.
    """
    season_metric_pairs = season_metric_pairs or SEASONAL_PLOT_ORDER
    return [p for p in SEASONAL_PLOT_ORDER if p in season_metric_pairs]


def make_annual_title(metric_col: str, comparison_label: str, source_label: str) -> str:
    """
    Build a standardized annual figure title using source, metric, and
    comparison context. This keeps annual HLS and Sentinel-2 figure naming
    consistent across primary and supporting outputs.
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
    Build a standardized seasonal figure title using source, season, metric,
    and comparison context. This ensures wet and dry figures are clearly
    labeled and visually parallel to the annual products.
    """
    metric_label = get_metric_label(metric_col)
    season_label = SEASON_SPECS.get(season, {}).get("label", season.title())
    return f"{source_label} {season_label} {metric_label}: {comparison_label}"

