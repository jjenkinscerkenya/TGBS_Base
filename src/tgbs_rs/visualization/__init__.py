"""
Visualization module for plots and tables.

Provides plotting functions and table preparation utilities for analysis output.
"""

from .tables import (
    select_analysis_columns,
    filter_season_table,
    to_long_index_table,
    prepare_composite_table,
    merge_monthly_to_full_grid,
    add_period_label,
    add_season_label,
    add_valid_value_flag,
    flag_rows_with_missing_values,
    sort_site_time,
    summarize_by_category_year,
    build_category_envelope,
    build_focal_series,
    join_focal_to_envelope,
    summarize_baseline_ranges,
    add_standardized_anomalies,
    summarize_baseline_vs_current,
    compute_site_trends,
    aggregate_monthly_to_seasonal,
    aggregate_monthly_to_seasonal_with_support,
    aggregate_monthly_to_seasonal_with_thresholds,
)

from .plots import (
    plot_baseline_panels_from_rasters,
    plot_forest_panels_from_rasters,
    set_plot_theme,
    format_title,
    finalize_timeseries_axis,
    plot_focal_vs_envelope,
    plot_category_mean_trajectories,
    plot_focal_anomaly_series,
    drop_site_year,
)

__all__ = [
    # Tables
    "select_analysis_columns",
    "add_period_label",
    "add_season_label",
    "add_valid_value_flag",
    "flag_rows_with_missing_values",
    "sort_site_time",
    "filter_season_table",
    "to_long_index_table",
    "prepare_composite_table",
    "merge_monthly_to_full_grid",
    "summarize_by_category_year",
    "build_category_envelope",
    "build_focal_series",
    "join_focal_to_envelope",
    "summarize_baseline_ranges",
    "add_standardized_anomalies",
    "summarize_baseline_vs_current",
    "compute_site_trends",
    "aggregate_monthly_to_seasonal",
    "aggregate_monthly_to_seasonal_with_support",
    "aggregate_monthly_to_seasonal_with_thresholds",
    # Plots
    "plot_baseline_panels_from_rasters",
    "plot_forest_panels_from_rasters",
    "set_plot_theme",
    "format_title",
    "finalize_timeseries_axis",
    "plot_focal_vs_envelope",
    "plot_category_mean_trajectories",
    "plot_focal_anomaly_series",
    "drop_site_year",
]
