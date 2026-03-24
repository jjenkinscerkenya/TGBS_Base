import numpy as np
import pandas as pd

from tgbs_rs.plotting.comparison_tables import (
    filter_season_table,
    to_long_index_table,
    summarize_by_category_year,
    build_category_envelope,
    build_focal_series,
    join_focal_to_envelope,
    summarize_baseline_ranges,
    add_standardized_anomalies,
    summarize_baseline_vs_current,
    compute_site_trends,
)
from figure_specs import (
    get_seasonal_plot_order,
    make_seasonal_title,
    get_metric_label,
)
from timeseries_plots import (
    set_plot_theme,
    plot_focal_vs_envelope,
    plot_category_mean_trajectories,
)


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

    focal_vs_reference = join_focal_to_envelope(
        focal_long=focal,
        envelope_df=reference_envelope,
        envelope_label="reference",
    )

    focal_vs_degraded = join_focal_to_envelope(
        focal_long=focal,
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
        "focal_vs_reference": focal_vs_reference,
        "focal_vs_degraded": focal_vs_degraded,
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

    for metric_col in ordered_metrics:
        fig, ax = plot_focal_vs_envelope(
            comparison_df=outputs[comparison_key],
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
