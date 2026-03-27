import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


sns.set_theme(style="whitegrid", context="talk")


def drop_site_year(df: object, site_id: str, year: int) -> object:
    """
    Return a copy with one site-year removed.
    This is useful for excluding known low-quality or incomplete observations before analysis.
    """
    return df.loc[~(df["site_id"].eq(site_id) & df["year"].eq(year))].copy()


def load_metrics_table(path: str) -> object:
    """
    Read a landscape-metrics CSV and lightly standardize a few key columns.
    This keeps filtering, reshaping, and plotting steps simple and consistent.
    """
    df = pd.read_csv(path)
    for col in ["metric", "level", "metric_level"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def subset_metrics(
    df: object, metrics: list[str], level: str | None = None
) -> object:
    """
    Filter the table to a selected set of metrics and, if desired, one metric level.
    This is the main helper for building focused figures without repeating filter code.
    """
    out = df[df["metric"].isin([m.lower() for m in metrics])].copy()
    if level is not None and "level" in out.columns:
        out = out[out["level"].eq(level.lower())].copy()
    return out


def format_metric_labels(df: object, metric_col: str = "metric") -> object:
    """
    Return a copy with cleaner display labels for metrics.
    This keeps plot titles and facet labels readable without changing the source values.
    """
    out = df.copy()
    label_map = {
        "enn_mn": "ENN Mn",
        "proxim_mn": "Prox Mn",
        "core_mn": "Core Area Mn",
        "cpland": "Core Area Percent Of Landscape",
        "tca": "Total Core Area",
        "shape_mn": "Shape Mn",
        "area_mn": "Area Mn",
    }
    out[metric_col] = out[metric_col].map(
        lambda x: label_map.get(x, str(x).replace("_", " ").title())
    )
    return out


def subset_metric_family(
    df: object,
    metrics: list[str],
    level: str | None = None,
    class_value: str | int | None = None,
) -> object:
    """
    Filter to a selected metric family and optionally one level or class.
    This is the main helper for building clean figures from the long metrics tables.
    """
    out = df[df["metric"].isin(metrics)].copy()
    if level is not None and "level" in out.columns:
        out = out[out["level"].eq(level)].copy()
    if class_value is not None and "class" in out.columns:
        out = out[out["class"].astype(str).eq(str(class_value))].copy()
    return out


def title_case_metric_labels(df: object, metric_col: str = "metric") -> object:
    """
    Return a copy with display-friendly metric labels for facets and legends.
    This improves figure readability without changing the underlying values.
    """
    out = df.copy()
    out[metric_col] = (
        out[metric_col].astype(str).str.replace("_", " ").str.title()
    )
    return out


def add_site_year(df: object, site_col: str = "site_id") -> object:
    """
    Create a compact site-year label for matrix and multivariate plots.
    This makes heatmaps and PCA outputs easier to read and sort.
    """
    out = df.copy()
    out["site_year"] = out[site_col].astype(str) + "_" + out["year"].astype(str)
    return out


def pivot_metric_matrix(
    df: object, metrics: list[str], site_col: str = "site_id"
) -> object:
    """
    Build a wide site-year-by-metric matrix from long landscape-metric tables.
    This is the core structure needed for heatmaps and PCA.
    """
    d = add_site_year(
        subset_metrics(df, metrics, level="landscape"), site_col=site_col
    )
    return d.pivot_table(
        index="site_year", columns="metric", values="value", aggfunc="mean"
    ).sort_index()


def zscore_columns(df: object) -> object:
    """
    Standardize each numeric column to mean zero and unit variance.
    This allows metrics on different scales to be compared fairly.
    """
    return (df - df.mean()) / df.std(ddof=0)


def prepare_pca_scores(
    df: object, metrics: list[str], site_col: str = "site_id"
) -> object:
    """
    Run PCA on a standardized site-year metric matrix and return tidy PC scores.
    The result is ready for seaborn scatterplots and temporal trajectory overlays.
    """
    X = pivot_metric_matrix(df, metrics=metrics, site_col=site_col).dropna()
    Z = StandardScaler().fit_transform(X)
    pcs = PCA(n_components=2).fit_transform(Z)

    out = pd.DataFrame(pcs, index=X.index, columns=["PC1", "PC2"]).reset_index(
        names="site_year"
    )
    out[site_col] = out["site_year"].str.rsplit("_", n=1).str[0]
    out["year"] = out["site_year"].str.rsplit("_", n=1).str[-1].astype(int)
    return out


def plot_landscape_metric_facets(
    df: object,
    metrics: list[str],
    site_col: str = "site_id",
    col_wrap: int = 2,
    palette: str = "muted",
) -> object:
    """
    Plot multi-panel yearly trajectories for key landscape metrics by site.
    This is the clearest overview figure for comparing temporal pattern change across sites.
    """
    d = title_case_metric_labels(subset_metrics(df, metrics, level="landscape"))

    g = sns.relplot(
        data=d,
        x="year",
        y="value",
        hue=site_col,
        col="metric",
        kind="line",
        marker="o",
        markers=True,
        dashes=False,
        col_wrap=col_wrap,
        palette=palette,
        facet_kws={"sharey": False, "sharex": True},
        height=4,
        aspect=1.35,
        linewidth=2,
        markersize=6,
    )
    g.set_axis_labels("Year", "Metric Value")
    g.set_titles("{col_name}")
    g.fig.subplots_adjust(top=0.88)
    g.fig.suptitle("Landscape Metric Trajectories By Site")
    return g


def plot_site_year_heatmap(
    df: object,
    metrics: list[str],
    site_col: str = "site_id",
    figsize: tuple = (10, 8),
    cmap: str = "crest",
) -> object:
    """
    Plot a standardized heatmap of landscape metrics across all site-years.
    This gives a compact overview of which site-years are structurally similar or distinct.
    """
    M = zscore_columns(
        pivot_metric_matrix(df, metrics=metrics, site_col=site_col)
    )

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        M,
        cmap=cmap,
        center=0,
        linewidths=0.4,
        cbar_kws={"label": "Standardized Value"},
        ax=ax,
    )
    ax.set_title("Standardized Landscape Metrics By Site-Year")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Site-Year")
    return fig, ax


def plot_pland_trajectories(
    df: object,
    site_col: str = "site_id",
    class_col: str = "class",
    palette: str = "muted",
) -> object:
    """
    Plot class-level percent-of-landscape trajectories through time for each site.
    This version uses a fixed panel layout so sites appear in a consistent, report-ready order.
    """
    d = df[df["metric"].eq("pland")].copy()
    d[class_col] = d[class_col].astype(str)

    layout = {
        "buda": (0, 0),
        "gogoni": (1, 0),
        "shimba_hills": (2, 0),
        "degraded_1": (0, 1),
        "degraded_2": (1, 1),
        "degraded_3": (2, 1),
        "ks_rehab": (3, 0),
    }

    fig, axes = plt.subplots(4, 2, figsize=(14, 18), sharex=True, sharey=True)
    axes = pd.DataFrame(axes)

    for site, (r, c) in layout.items():
        ax = axes.iloc[r, c]
        ds = d[d[site_col].eq(site)].copy()

        if ds.empty:
            ax.set_visible(False)
            continue

        sns.lineplot(
            data=ds,
            x="year",
            y="value",
            hue=class_col,
            marker="o",
            palette=palette,
            linewidth=2,
            markersize=6,
            ax=ax,
        )
        ax.set_title(site.replace("_", " ").title())
        ax.set_xlabel("Year")
        ax.set_ylabel("Percent Of Landscape")

    used = set(layout.values())
    for r in range(4):
        for c in range(2):
            if (r, c) not in used:
                axes.iloc[r, c].axis("off")

    handles, labels = axes.iloc[0, 0].get_legend_handles_labels()
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()

    fig.legend(
        handles,
        labels,
        title="Class",
        loc="center right",
        bbox_to_anchor=(0.98, 0.5),
        frameon=True,
    )
    fig.suptitle("Class-Level Pland Trajectories By Site", y=0.995)
    fig.tight_layout(rect=[0, 0, 0.92, 0.985])
    return fig, axes


def plot_pca_site_years(
    df: object,
    metrics: list[str],
    site_col: str = "site_id",
    palette: str = "muted",
    annotate: bool = True,
) -> object:
    """
    Plot site-years in two-dimensional PCA space using standardized landscape metrics.
    This version uses a wider layout, puts the legend outside the plot, and labels only the most recent year per site.
    """
    d = prepare_pca_scores(df, metrics=metrics, site_col=site_col)
    d = d.sort_values([site_col, "year"]).copy()

    fig, ax = plt.subplots(figsize=(12, 6.5))

    sns.scatterplot(
        data=d,
        x="PC1",
        y="PC2",
        hue=site_col,
        style=site_col,
        palette=palette,
        s=110,
        ax=ax,
    )

    sns.lineplot(
        data=d,
        x="PC1",
        y="PC2",
        hue=site_col,
        palette=palette,
        legend=False,
        linewidth=1.8,
        ax=ax,
    )

    if annotate:
        latest = d.groupby(site_col, as_index=False).tail(1)
        for _, r in latest.iterrows():
            ax.text(
                r["PC1"],
                r["PC2"],
                str(r["year"]),
                fontsize=10,
                alpha=0.9,
                ha="left",
                va="bottom",
            )

    ax.set_title("PCA Of Site-Years From Landscape Metrics")
    ax.legend(
        title="Site Id",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
    )
    fig.tight_layout(rect=[0, 0, 0.82, 1])
    return fig, ax


def plot_connectivity_metric_facets(
    df: object,
    site_col: str = "site_id",
    metrics: list[str] = ["enn_mn", "proxim_mn"],
    level: str = "class",
    class_value: str | int = 1,
    palette: str = "muted",
) -> object:
    """
    Plot yearly connectivity trajectories by site for ENN and or PROX.
    This is useful for seeing whether woody patches are becoming more isolated or more connected through time.
    """
    d = subset_metric_family(
        df, metrics=metrics, level=level, class_value=class_value
    )
    d = format_metric_labels(d)

    g = sns.FacetGrid(
        data=d,
        col="metric",
        hue=site_col,
        col_order=[
            m
            for m in format_metric_labels(pd.DataFrame({"metric": metrics}))[
                "metric"
            ]
        ],
        sharex=True,
        sharey=False,
        height=4,
        aspect=1.35,
        palette=palette,
    )
    g.map_dataframe(
        sns.lineplot,
        x="year",
        y="value",
        marker="o",
        dashes=False,
        linewidth=2,
        markersize=6,
    )
    g.add_legend(title="Site Id")
    g.set_axis_labels("Year", "Metric Value")
    g.set_titles("{col_name}")
    g.fig.subplots_adjust(top=0.82, wspace=0.18)
    g.fig.suptitle("Connectivity Metric Trajectories By Site", y=0.97)
    return g


def plot_core_metric_facets(
    df: object,
    site_col: str = "site_id",
    metrics: list[str] = ["core_mn", "cpland", "tca"],
    level: str = "class",
    class_value: str | int = 1,
    col_wrap: int = 2,
    palette: str = "muted",
) -> object:
    """
    Plot yearly core-area trajectories by site for mean core area, core percent, and total core area.
    This is useful for judging whether woody cover is developing more interior area during recovery.
    """
    d = subset_metric_family(
        df, metrics=metrics, level=level, class_value=class_value
    )
    d = format_metric_labels(d)

    g = sns.relplot(
        data=d,
        x="year",
        y="value",
        hue=site_col,
        col="metric",
        kind="line",
        marker="o",
        dashes=False,
        palette=palette,
        linewidth=2,
        markersize=6,
        col_wrap=col_wrap,
        facet_kws={"sharex": True, "sharey": False},
        height=4,
        aspect=1.35,
    )
    g.set_axis_labels("Year", "Metric Value")
    g.set_titles("{col_name}")
    g.fig.subplots_adjust(top=0.88)
    g.fig.suptitle("Core Area Metric Trajectories By Site")
    return g


def plot_shape_metric_trajectories(
    df: object,
    site_col: str = "site_id",
    level: str = "class",
    class_value: str | int = 1,
    palette: str = "muted",
) -> object:
    """
    Plot yearly trajectories for mean patch shape complexity by site.
    This helps show whether patches are becoming more compact or more irregular through time.
    """
    d = subset_metric_family(
        df, metrics=["shape_mn"], level=level, class_value=class_value
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=d,
        x="year",
        y="value",
        hue=site_col,
        marker="o",
        dashes=False,
        palette=palette,
        linewidth=2,
        markersize=6,
        ax=ax,
    )
    ax.set_title("Shape Mn Trajectories By Site")
    ax.set_xlabel("Year")
    ax.set_ylabel("Metric Value")
    ax.legend(
        title="Site Id",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
    )
    return fig, ax


def plot_area_metric_trajectories(
    df: object,
    site_col: str = "site_id",
    level: str = "class",
    class_value: str | int = 1,
    palette: str = "muted",
) -> object:
    """
    Plot yearly trajectories for mean patch area by site.
    This helps distinguish whether recovery is producing larger patch units or many small patches.
    """
    d = subset_metric_family(
        df, metrics=["area_mn"], level=level, class_value=class_value
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=d,
        x="year",
        y="value",
        hue=site_col,
        marker="o",
        dashes=False,
        palette=palette,
        linewidth=2,
        markersize=6,
        ax=ax,
    )
    ax.set_title("Area Mn Trajectories By Site")
    ax.set_xlabel("Year")
    ax.set_ylabel("Metric Value")
    ax.legend(
        title="Site Id",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
    )
    return fig, ax


def plot_metric_heatmap(
    df: object,
    metric: str,
    site_col: str = "site_id",
    level: str = "class",
    class_value: str | int = 1,
    cmap: str = "crest",
    figsize: tuple = (8, 6),
) -> object:
    """
    Plot a site-by-year heatmap for one selected metric.
    This is useful for quickly spotting the strongest temporal shifts and cross-site contrasts.
    """
    d = subset_metric_family(
        df, metrics=[metric], level=level, class_value=class_value
    )
    M = d.pivot_table(
        index=site_col, columns="year", values="value", aggfunc="mean"
    ).sort_index()

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        M, cmap=cmap, linewidths=0.4, cbar_kws={"label": "Metric Value"}, ax=ax
    )
    ax.set_title(
        format_metric_labels(pd.DataFrame({"metric": [metric]}))["metric"].iloc[
            0
        ]
        + " By Site And Year"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Site Id")
    return fig, ax


def plot_metric_small_multiples(
    df: object,
    metrics: list[str],
    site_col: str = "site_id",
    level: str = "class",
    class_value: str | int = 1,
    palette: str = "muted",
    col_wrap: int = 2,
) -> object:
    """
    Plot several selected metrics as compact site-by-year small multiples.
    This is useful for building a concise recovery dashboard from a chosen subset of new metrics.
    """
    d = subset_metric_family(
        df, metrics=metrics, level=level, class_value=class_value
    )
    d = format_metric_labels(d)

    g = sns.relplot(
        data=d,
        x="year",
        y="value",
        hue=site_col,
        col="metric",
        kind="line",
        marker="o",
        dashes=False,
        palette=palette,
        linewidth=2,
        markersize=6,
        col_wrap=col_wrap,
        facet_kws={"sharex": True, "sharey": False},
        height=4,
        aspect=1.35,
    )
    g.set_axis_labels("Year", "Metric Value")
    g.set_titles("{col_name}")
    g.fig.subplots_adjust(top=0.88)
    g.fig.suptitle("Metric Trajectories By Site")
    return g


def baseline_deltas(
    df: object, metrics: list[str], site_col: str = "site_id"
) -> object:
    """
    Compute per-site change from the first observed year for selected landscape metrics.
    This is useful when you want to emphasize direction and magnitude of change over time.
    """
    d = (
        subset_metrics(df, metrics, level="landscape")
        .sort_values([site_col, "metric", "year"])
        .copy()
    )
    d["baseline_value"] = d.groupby([site_col, "metric"])["value"].transform(
        "first"
    )
    d["delta_from_baseline"] = d["value"] - d["baseline_value"]
    return d


def order_sites(
    df: object, order: list[str], site_col: str = "site_id"
) -> object:
    """
    Apply a fixed categorical site order for more consistent figures across the workflow.
    This is useful when you want a stable focal-reference-degraded ordering in every plot.
    """
    out = df.copy()
    out[site_col] = pd.Categorical(
        out[site_col], categories=order, ordered=True
    )
    return out
