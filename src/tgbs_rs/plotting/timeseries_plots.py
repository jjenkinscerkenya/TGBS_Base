import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def set_plot_theme() -> None:
    """
    Apply a consistent seaborn theme for all time-series figures in the repo.
    This creates a clean, muted plotting style so annual and seasonal products
    share the same visual grammar and remain presentation-ready.
    """
    sns.set_theme(style="whitegrid", context="talk", palette="muted")


def format_title(
    metric_label: str, temporal_label: str, comparison_label: str
) -> str:
    """
    Build a consistent capitalized title for time-series figures from metric,
    temporal context, and comparison type. This keeps figure titles uniform
    across annual, seasonal, focal-reference, and focal-degraded outputs.
    """
    return f"{temporal_label} {metric_label}: {comparison_label}"


def finalize_timeseries_axis(
    ax: plt.Axes,
    title: str,
    ylabel: str,
    xlabel: str = "Year",
    legend_position: str = "right",
) -> None:
    """
    Apply final axis labels, title, legend placement, and cleanup for a
    time-series figure. Legends can be placed outside the main plotting area
    by designating legend position "right" or "bottom".
    """
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if legend_position == "right":
        ax.legend(
            frameon=True,
            title=None,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0,
        )
    elif legend_position == "bottom":
        ax.legend(
            frameon=True,
            title=None,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
        )
    else:
        ax.legend(frameon=True, title=None)

    sns.despine()
    plt.tight_layout()


def plot_focal_vs_envelope(
    comparison_df: pd.DataFrame,
    metric_col: str,
    envelope_label: str,
    title: str,
    ylabel: str,
    figsize: tuple = (11, 5),
) -> tuple:
    """
    Plot the focal trajectory against a comparison category envelope using a
    shaded interquartile ribbon, full range ribbon, and comparison median line.
    This is the core figure pattern for focal-vs-reference and focal-vs-degraded
    annual or seasonal trajectory figures.
    """
    d = comparison_df.loc[comparison_df["index_name"].eq(metric_col)].copy()
    d = d.sort_values("year")

    fig, ax = plt.subplots(figsize=figsize)

    ax.fill_between(
        d["year"],
        d[f"{envelope_label}_q25"],
        d[f"{envelope_label}_q75"],
        alpha=0.22,
        label=f"{envelope_label.capitalize()} IQR",
    )

    ax.fill_between(
        d["year"],
        d[f"{envelope_label}_min"],
        d[f"{envelope_label}_max"],
        alpha=0.10,
        label=f"{envelope_label.capitalize()} Range",
    )

    sns.lineplot(
        data=d,
        x="year",
        y=f"{envelope_label}_median",
        linestyle="--",
        linewidth=2,
        label=f"{envelope_label.capitalize()} Median",
        ax=ax,
    )

    sns.lineplot(
        data=d,
        x="year",
        y="value",
        marker="o",
        linewidth=2.5,
        label="Focal",
        ax=ax,
    )

    finalize_timeseries_axis(ax=ax, title=title, ylabel=ylabel)
    return fig, ax


def plot_category_mean_trajectories(
    summary_df: pd.DataFrame,
    metric_col: str,
    title: str,
    ylabel: str,
    x_col: str = "year",
    figsize: tuple = (11, 5),
) -> tuple:
    """
    Plot category mean trajectories across time for focal, reference, and
    degraded groups for any requested metric. This is a reusable diagnostic
    figure for checking grouped category behavior before or alongside the main
    focal-versus-envelope comparisons.
    """
    d = summary_df.loc[summary_df["index_name"].eq(metric_col)].copy()
    d = d.sort_values([x_col, "site_category"])

    fig, ax = plt.subplots(figsize=figsize)

    sns.lineplot(
        data=d,
        x=x_col,
        y="mean",
        hue="site_category",
        marker="o",
        linewidth=2.2,
        ax=ax,
    )

    finalize_timeseries_axis(
        ax=ax, title=title, ylabel=ylabel, xlabel=x_col.title()
    )
    return fig, ax


def plot_focal_anomaly_series(
    anomaly_df: pd.DataFrame,
    metric_col: str,
    anomaly_col: str,
    title: str,
    ylabel: str,
    figsize: tuple = (11, 5),
) -> tuple:
    """
    Plot a focal anomaly time series relative to a reference or degraded
    baseline. This provides a compact way to show whether focal conditions
    are moving above or below the chosen baseline through time.
    """
    d = anomaly_df.loc[anomaly_df["index_name"].eq(metric_col)].copy()
    d = d.sort_values("year")

    fig, ax = plt.subplots(figsize=figsize)

    sns.lineplot(
        data=d,
        x="year",
        y=anomaly_col,
        marker="o",
        linewidth=2.3,
        label="Focal Anomaly",
        ax=ax,
    )

    ax.axhline(0, linestyle="--", linewidth=1.2, color="0.4")
    finalize_timeseries_axis(ax=ax, title=title, ylabel=ylabel)
    return fig, ax
