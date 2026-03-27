import pandas as pd

from tgbs_rs.plotting.comparison_tables import (
    select_analysis_columns,
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
    get_annual_plot_order,
    make_annual_title,
    get_metric_label,
)
from timeseries_plots import (
    set_plot_theme,
    plot_focal_vs_envelope,
    plot_category_mean_trajectories,
)


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
        "focal_vs_reference": focal_vs_reference,
        "focal_vs_degraded": focal_vs_degraded,
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

    for metric_col in ordered_metrics:
        fig, ax = plot_focal_vs_envelope(
            comparison_df=outputs[comparison_key],
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
