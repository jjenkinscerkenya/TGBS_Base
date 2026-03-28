"""
Metrics module for temporal analysis and metric calculations.

Provides time-series compositing, disturbance detection, landscape metrics,
and vegetation/productivity/moisture indices.
"""

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

from .temporal import (
    _validate_composite_stat,
    _apply_stat,
    _time_windows,
)

__all__ = [
    "get_metric_label",
    "get_annual_plot_order",
    "get_seasonal_plot_order",
    "make_annual_title",
    "make_seasonal_title",
    "set_plot_theme",
    "plot_focal_vs_envelope",
    "plot_category_mean_trajectories",
    "_validate_composite_stat",
    "_apply_stat",
    "_time_windows",
]
