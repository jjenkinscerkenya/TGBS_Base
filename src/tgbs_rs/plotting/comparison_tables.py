import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def select_analysis_columns(
    df: pd.DataFrame,
    value_cols: list[str],
    extra_cols: list[str] = None,
) -> pd.DataFrame:
    """
    Return a slim analysis table containing only the columns needed for
    comparison and plotting. This keeps downstream summaries auditable
    and avoids carrying unnecessary retained bands through every step.
    """
    base_cols = ["site_id", "site_name", "site_category", "year", "period"]
    extra_cols = extra_cols or []
    cols = [c for c in base_cols + extra_cols + value_cols if c in df.columns]
    return df.loc[:, cols].copy()


def filter_season_table(
    df: pd.DataFrame,
    season: str,
    value_cols: list[str],
) -> pd.DataFrame:
    """
    Filter a seasonal summary table to a single season such as wet or dry.
    The returned table remains in site-year form and is ready for the same
    category summaries used in the annual workflow.
    """
    keep_cols = ["site_id", "site_name", "site_category", "year", "season"]
    keep_cols += [c for c in ["period"] if c in df.columns]
    keep_cols += [c for c in value_cols if c in df.columns]
    out = df.loc[df["season"].eq(season), keep_cols].copy()
    if "period" not in out.columns:
        out["period"] = np.where(out["year"] <= 2017, "baseline", "current")
    return out


def to_long_index_table(
    df: pd.DataFrame,
    value_cols: list[str],
    id_cols: list[str],
) -> pd.DataFrame:
    """
    Convert a wide site-year table into a long index table with one row per
    site-year-index combination. This makes it easier to build generic
    summaries, envelopes, anomalies, and seaborn plotting workflows.
    """
    return df.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name="index_name",
        value_name="value",
    )


def summarize_by_category_year(
    df_long: pd.DataFrame,
    group_cols: list[str],
) -> pd.DataFrame:
    """
    Build category-year summaries for each index using mean, median, spread,
    and sample size. These summaries are useful for quick diagnostics,
    reporting tables, and optional category mean overlays in plots.
    """
    return (
        df_long
        .groupby(group_cols + ["index_name"], dropna=False)["value"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
            q25=lambda s: s.quantile(0.25),
            q75=lambda s: s.quantile(0.75),
        )
        .reset_index()
    )


def build_category_envelope(
    df_long: pd.DataFrame,
    category: str,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Build a category envelope across sites for each year and index. The result
    gives min-max and interquartile ranges that can be used as ribbons behind
    the focal trajectory for reference or degraded comparisons.
    """
    x = df_long.loc[df_long["site_category"].eq(category)].copy()
    return (
        x.groupby([year_col, "index_name"], dropna=False)["value"]
        .agg(
            n_sites="count",
            mean="mean",
            median="median",
            min="min",
            max="max",
            q25=lambda s: s.quantile(0.25),
            q75=lambda s: s.quantile(0.75),
        )
        .reset_index()
        .assign(site_category=category)
    )


def build_focal_series(
    df_long: pd.DataFrame,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Extract the focal trajectory in long format for each year and index.
    This produces the line that will typically sit on top of the reference
    or degraded envelopes in the main comparison figures.
    """
    return (
        df_long.loc[df_long["site_category"].eq("focal")]
        .sort_values([ "index_name", year_col ])
        .reset_index(drop=True)
    )


def join_focal_to_envelope(
    focal_long: pd.DataFrame,
    envelope_df: pd.DataFrame,
    year_col: str = "year",
    envelope_label: str = "reference",
) -> pd.DataFrame:
    """
    Join the focal series to a category envelope so each focal observation
    carries the comparison range for the same year and index. This becomes
    the main plotting-ready comparison table for focal-vs-reference or
    focal-vs-degraded visualizations.
    """
    cols = [year_col, "index_name", "mean", "median", "min", "max", "q25", "q75", "n_sites"]
    env = envelope_df.loc[:, cols].copy()
    env = env.rename(
        columns={
            "mean": f"{envelope_label}_mean",
            "median": f"{envelope_label}_median",
            "min": f"{envelope_label}_min",
            "max": f"{envelope_label}_max",
            "q25": f"{envelope_label}_q25",
            "q75": f"{envelope_label}_q75",
            "n_sites": f"{envelope_label}_n_sites",
        }
    )
    return focal_long.merge(env, on=[year_col, "index_name"], how="left")


def summarize_baseline_ranges(
    df_long: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    """
    Summarize the baseline-period distribution for a chosen category and index.
    These baseline ranges are useful for contextual tables, interpretation
    notes, and standardized anomaly calculations for the focal site.
    """
    x = df_long.loc[
        df_long["site_category"].eq(category) & df_long["period"].eq("baseline")
    ].copy()

    return (
        x.groupby(["index_name"], dropna=False)["value"]
        .agg(
            baseline_n="count",
            baseline_mean="mean",
            baseline_std="std",
            baseline_median="median",
            baseline_min="min",
            baseline_max="max",
            baseline_q25=lambda s: s.quantile(0.25),
            baseline_q75=lambda s: s.quantile(0.75),
        )
        .reset_index()
        .assign(site_category=category)
    )


def add_standardized_anomalies(
    focal_long: pd.DataFrame,
    baseline_ranges: pd.DataFrame,
    label: str = "reference",
) -> pd.DataFrame:
    """
    Add focal anomalies relative to a category's baseline mean and standard
    deviation for each index. This helps quantify whether focal productivity
    is within, above, or below the historical reference baseline.
    """
    base = baseline_ranges.loc[:, ["index_name", "baseline_mean", "baseline_std"]].copy()
    base = base.rename(
        columns={
            "baseline_mean": f"{label}_baseline_mean",
            "baseline_std": f"{label}_baseline_std",
        }
    )
    out = focal_long.merge(base, on="index_name", how="left")
    out[f"{label}_baseline_anomaly"] = out["value"] - out[f"{label}_baseline_mean"]
    out[f"{label}_baseline_zscore"] = (
        out[f"{label}_baseline_anomaly"] / out[f"{label}_baseline_std"]
    )
    return out


def summarize_baseline_vs_current(
    df_long: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize baseline and current periods separately for each site category
    and index. This provides concise reporting tables for directional change
    and complements the time-series plots with period-level summaries.
    """
    return (
        df_long
        .groupby(["site_category", "period", "index_name"], dropna=False)["value"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
        )
        .reset_index()
    )


def compute_site_trends(
    df_long: pd.DataFrame,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Compute a simple linear slope per site and index using numpy polyfit.
    This gives a compact trend table for quick interpretation of annual or
    seasonal trajectories without introducing heavier statistical machinery.
    """
    def _fit(group: pd.DataFrame) -> pd.Series:
        x = group[year_col].to_numpy(dtype=float)
        y = group["value"].to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 2:
            return pd.Series({"n_obs": mask.sum(), "slope": np.nan, "intercept": np.nan})
        slope, intercept = np.polyfit(x[mask], y[mask], 1)
        return pd.Series({"n_obs": mask.sum(), "slope": slope, "intercept": intercept})

    return (
        df_long
        .groupby(["site_id", "site_name", "site_category", "index_name"], dropna=False)
        .apply(_fit)
        .reset_index()
    )