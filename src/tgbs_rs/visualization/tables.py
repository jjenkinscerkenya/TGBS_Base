import pandas as pd
import numpy as np


################## Table Preperation and Cleaning ###################
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


def normalize_temporal_columns(
    df: pd.DataFrame, temporal_scale: str
) -> pd.DataFrame:
    """
    Standardize year, month, and day columns based on whether the table is annual or monthly.
    This normalizes expected null temporal fields so downstream functions do not need to handle
    multiple raw export conventions.
    """
    out = df.copy()

    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce").astype(
            "Int64"
        )

    if temporal_scale == "annual":
        if "month" in out.columns:
            out = out.drop(columns=["month"])
        if "day" in out.columns:
            out = out.drop(columns=["day"])

    elif temporal_scale == "monthly":
        if "month" in out.columns:
            out["month"] = pd.to_numeric(out["month"], errors="coerce").astype(
                "Int64"
            )
        if "day" in out.columns:
            out = out.drop(columns=["day"])

    else:
        raise ValueError("temporal_scale must be 'annual' or 'monthly'.")

    return out


def add_period_label(
    df: pd.DataFrame,
    baseline_start: int = 2014,
    baseline_end: int = 2017,
    current_start: int = 2018,
    current_end: int = 2025,
) -> pd.DataFrame:
    """
    Add a baseline/current period label from the year column.
    This creates a simple analysis field that supports later group summaries and
    baseline-to-current comparison tables.
    """
    out = df.copy()
    out["period"] = pd.NA

    out.loc[out["year"].between(baseline_start, baseline_end), "period"] = (
        "baseline"
    )
    out.loc[out["year"].between(current_start, current_end), "period"] = (
        "current"
    )

    return out


def sort_site_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort the table in a stable, human-readable order by site metadata and time.
    This makes inspection easier and ensures reproducible ordering before export
    or reshaping.
    """
    sort_cols = [
        c
        for c in ["site_category", "site_id", "year", "month"]
        if c in df.columns
    ]
    return df.sort_values(sort_cols).reset_index(drop=True)


def drop_rows_with_missing_values(
    df: pd.DataFrame,
    value_columns: list[str],
) -> pd.DataFrame:
    """
    Remove rows where one or more analytical value columns are missing.
    This is the strict preparation option for analysis steps that require complete
    values for all requested indices.
    """
    return df.dropna(subset=value_columns).reset_index(drop=True)


def flag_rows_with_missing_values(
    df: pd.DataFrame,
    value_columns: list[str],
) -> pd.DataFrame:
    """
    Add simple missing-data flags without dropping rows.
    This preserves the raw record structure while making it easy to filter incomplete
    observations during later analysis.
    """
    out = df.copy()
    out["has_any_missing_value"] = out[value_columns].isna().any(axis=1)
    out["n_missing_values"] = out[value_columns].isna().sum(axis=1)
    return out


def keep_core_columns(
    df: pd.DataFrame,
    value_columns: list[str],
) -> pd.DataFrame:
    """
    Keep only core metadata, audit columns, and requested analytical value
    columns. This is useful for creating compact analysis-specific tables from
    the master annual, monthly, or seasonal tables.
    """
    core_cols = [
        c
        for c in [
            "site_id",
            "site_name",
            "site_category",
            "source_file",
            "year",
            "month",
            "season",
            "date",
            "image_count",
            "temporal_scale",
            "composite_stat",
            "period",
            "has_any_missing_value",
            "n_missing_values",
            "row_was_missing",
            "has_all_values",
            "has_any_value",
        ]
        if c in df.columns
    ]
    keep_cols = core_cols + [c for c in value_columns if c in df.columns]
    return df.loc[:, keep_cols].copy()


def melt_value_columns_long(
    df: pd.DataFrame,
    value_columns: list[str],
    variable_name: str = "index_name",
    value_name: str = "value",
) -> pd.DataFrame:
    """
    Reshape a wide table of indices or bands into a long table for grouped analysis.
    This creates a canonical structure that is easier to use for envelopes, anomalies,
    trend statistics, and plotting.
    """
    id_cols = [c for c in df.columns if c not in value_columns]
    out = df.melt(
        id_vars=id_cols,
        value_vars=value_columns,
        var_name=variable_name,
        value_name=value_name,
    )
    return out.reset_index(drop=True)


def prepare_composite_table(
    df: pd.DataFrame,
    temporal_scale: str,
    value_columns: list[str],
    drop_incomplete_rows: bool = False,
) -> pd.DataFrame:
    """
    Apply the core preparation workflow to a raw annual or monthly composite table.
    This standardizes temporal columns, adds baseline/current labels, optionally drops
    incomplete analytical rows, and returns a sorted analysis-ready table.
    """
    out = normalize_temporal_columns(df, temporal_scale=temporal_scale)
    out = add_period_label(out)
    out = flag_rows_with_missing_values(out, value_columns=value_columns)

    if drop_incomplete_rows:
        out = drop_rows_with_missing_values(out, value_columns=value_columns)

    return sort_site_time(out)


def subset_metric_tables(
    annual_master: pd.DataFrame,
    seasonal_master: pd.DataFrame,
    metric_cols: list[str],
) -> tuple:
    """
    Create compact annual and seasonal analysis tables from the master tables
    for one thematic metric group. This keeps script bodies short and makes
    each analysis theme easy to configure.
    """
    annual_df = keep_core_columns(annual_master, metric_cols)
    seasonal_df = keep_core_columns(seasonal_master, metric_cols)
    return annual_df, seasonal_df


################## Seasonal Table Prep ###################
def add_season_label(
    df: pd.DataFrame,
    wet_months: list[int] = [3, 4, 5],
    dry_months: list[int] = [7, 8, 9, 10],
    month_col: str = "month",
) -> pd.DataFrame:
    """
    Add a season label to monthly data using the project wet and dry month definitions.
    Months outside the defined wet/dry windows are labeled as 'other' so they remain visible
    but are excluded easily from seasonal summaries.
    """
    out = df.copy()
    out["season"] = "other"
    out.loc[out[month_col].isin(wet_months), "season"] = "wet"
    out.loc[out[month_col].isin(dry_months), "season"] = "dry"
    return out


def add_valid_value_flag(
    df: pd.DataFrame,
    value_columns: list[str],
) -> pd.DataFrame:
    """
    Add compact flags describing whether a row has complete analytical values.
    This preserves incomplete rows for auditing while making it easy to filter to
    valid monthly observations for aggregation.
    """
    out = df.copy()
    out["has_all_values"] = out[value_columns].notna().all(axis=1)
    out["has_any_value"] = out[value_columns].notna().any(axis=1)
    return out


def summarize_missing_by_site_year(
    df: pd.DataFrame,
    value_columns: list[str],
) -> pd.DataFrame:
    """
    Summarize missing analytical rows by site and year.
    This is a compact diagnostic table for identifying whether missingness is concentrated
    in particular sites, years, or seasonal windows.
    """
    out = add_valid_value_flag(df, value_columns=value_columns)

    summary = (
        out.groupby(
            ["site_id", "site_name", "site_category", "year"], dropna=False
        )
        .agg(
            n_rows=("year", "size"),
            n_complete_rows=("has_all_values", "sum"),
            n_incomplete_rows=("has_all_values", lambda s: (~s).sum()),
        )
        .reset_index()
    )

    summary["pct_incomplete_rows"] = (
        summary["n_incomplete_rows"] / summary["n_rows"]
    ) * 100.0

    return summary.sort_values(
        ["pct_incomplete_rows", "site_category", "site_id", "year"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)


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


def aggregate_monthly_to_seasonal(
    df: pd.DataFrame,
    value_columns: list[str],
    season_col: str = "season",
    min_valid_months: int = 2,
) -> pd.DataFrame:
    """
    Aggregate monthly site values into per-year seasonal summaries for wet and dry seasons.
    A seasonal value is computed only when at least the minimum number of valid monthly
    observations are available, and the output keeps counts needed for audit and filtering.
    """
    out = add_valid_value_flag(df, value_columns=value_columns)
    out = out.loc[out[season_col].isin(["wet", "dry"])].copy()

    rows = []

    group_cols = ["site_id", "site_name", "site_category", "year", season_col]

    for keys, g in out.groupby(group_cols, dropna=False):
        row = {
            "site_id": keys[0],
            "site_name": keys[1],
            "site_category": keys[2],
            "year": keys[3],
            "season": keys[4],
            "n_rows": len(g),
            "n_complete_rows": int(g["has_all_values"].sum()),
            "n_incomplete_rows": int((~g["has_all_values"]).sum()),
            "image_count_sum": (
                g["image_count"].sum() if "image_count" in g.columns else pd.NA
            ),
        }

        for col in value_columns:
            valid = g[col].dropna()
            row[f"{col}_n_valid_months"] = int(valid.shape[0])
            row[col] = (
                valid.mean() if valid.shape[0] >= min_valid_months else pd.NA
            )

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(["site_category", "site_id", "year", "season"])
        .reset_index(drop=True)
    )


def aggregate_monthly_to_seasonal_with_thresholds(
    df: pd.DataFrame,
    value_columns: list[str],
    season_col: str = "season",
    min_valid_months_by_season: dict[str, int] | None = None,
) -> pd.DataFrame:
    """
    Aggregate monthly site values into annual wet and dry seasonal summaries using
    season-specific minimum valid-month thresholds. This keeps the seasonal summaries
    flexible while preserving counts needed to judge data support.
    """
    if min_valid_months_by_season is None:
        min_valid_months_by_season = {"wet": 2, "dry": 3}

    out = add_valid_value_flag(df, value_columns=value_columns)
    out = out.loc[out[season_col].isin(["wet", "dry"])].copy()

    rows = []
    group_cols = ["site_id", "site_name", "site_category", "year", season_col]

    for keys, g in out.groupby(group_cols, dropna=False):
        season = keys[4]
        min_valid = min_valid_months_by_season[season]

        row = {
            "site_id": keys[0],
            "site_name": keys[1],
            "site_category": keys[2],
            "year": keys[3],
            "season": season,
            "n_rows": len(g),
            "n_complete_rows": int(g["has_all_values"].sum()),
            "n_incomplete_rows": int((~g["has_all_values"]).sum()),
            "min_valid_months_required": min_valid,
        }

        for col in value_columns:
            valid = g[col].dropna()
            row[f"{col}_n_valid_months"] = int(valid.shape[0])
            row[col] = valid.mean() if valid.shape[0] >= min_valid else pd.NA

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(["site_category", "site_id", "year", "season"])
        .reset_index(drop=True)
    )


################## Monthly Table Preperation ###################
def build_site_month_grid(
    sites_df: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """
    Build the full expected site-year-month grid for the monthly study period.
    This creates an explicit panel of all months that should exist so missing rows
    in the exported monthly table can be identified and tracked.
    """
    site_cols = ["site_id", "site_name", "site_category"]
    site_meta = sites_df.loc[:, site_cols].drop_duplicates().copy()

    years = pd.DataFrame({"year": range(start_year, end_year + 1)})
    months = pd.DataFrame({"month": range(1, 13)})

    grid = (
        site_meta.merge(years, how="cross")
        .merge(months, how="cross")
        .sort_values(["site_category", "site_id", "year", "month"])
        .reset_index(drop=True)
    )

    return grid


def merge_monthly_to_full_grid(
    monthly_df: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """
    Merge the exported monthly table onto the full expected site-year-month grid.
    This makes absent site-month rows explicit and allows downstream seasonal summaries
    to distinguish missing rows from rows with missing analytical values.
    """
    grid = build_site_month_grid(
        sites_df=monthly_df,
        start_year=start_year,
        end_year=end_year,
    )

    key_cols = ["site_id", "site_name", "site_category", "year", "month"]

    out = grid.merge(
        monthly_df,
        on=key_cols,
        how="left",
        suffixes=("", "_raw"),
    )

    out["row_was_missing"] = (
        out["date"].isna() if "date" in out.columns else out.isna().all(axis=1)
    )
    return out


def summarize_monthly_row_completeness(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize whether expected monthly rows are present for each site and year.
    This is a structural completeness check that should be reviewed before any
    seasonal interpretation or trend statistics.
    """
    summary = (
        df.groupby(
            ["site_id", "site_name", "site_category", "year"], dropna=False
        )
        .agg(
            expected_months=("month", "size"),
            observed_rows=("row_was_missing", lambda s: (~s).sum()),
            missing_rows=("row_was_missing", "sum"),
        )
        .reset_index()
    )

    summary["pct_missing_rows"] = (
        summary["missing_rows"] / summary["expected_months"]
    ) * 100.0

    return summary.sort_values(
        ["pct_missing_rows", "site_category", "site_id", "year"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)


def aggregate_monthly_to_seasonal_with_support(
    df: pd.DataFrame,
    value_columns: list[str],
    min_valid_months_by_season: dict[str, int] | None = None,
) -> pd.DataFrame:
    """
    Aggregate monthly site values into annual wet and dry seasonal summaries while
    preserving structural support metrics. This reports expected months, observed rows,
    missing rows, and valid analytical months so seasonal outputs remain auditable.
    """
    if min_valid_months_by_season is None:
        min_valid_months_by_season = {"wet": 2, "dry": 3}

    out = df.copy()
    out = add_season_label(out)
    out = add_valid_value_flag(out, value_columns=value_columns)
    out = out.loc[out["season"].isin(["wet", "dry"])].copy()

    rows = []

    for keys, g in out.groupby(
        ["site_id", "site_name", "site_category", "year", "season", "period"],
        dropna=False,
    ):
        season = keys[4]
        period = keys[5]
        min_valid = min_valid_months_by_season[season]
        expected_months = 3 if season == "wet" else 4

        row = {
            "site_id": keys[0],
            "site_name": keys[1],
            "site_category": keys[2],
            "year": keys[3],
            "season": season,
            "period": period,
            "expected_months_in_season": expected_months,
            "observed_rows_in_season": (
                int((~g["row_was_missing"]).sum())
                if "row_was_missing" in g.columns
                else len(g)
            ),
            "missing_rows_in_season": (
                int(g["row_was_missing"].sum())
                if "row_was_missing" in g.columns
                else 0
            ),
            "min_valid_months_required": min_valid,
        }

        for col in value_columns:
            valid = g[col].dropna()
            row[f"{col}_n_valid_months"] = int(valid.shape[0])
            row[col] = valid.mean() if valid.shape[0] >= min_valid else pd.NA

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(["site_category", "site_id", "year", "season"])
        .reset_index(drop=True)
    )


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
        df_long.groupby(group_cols + ["index_name"], dropna=False)["value"]
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


def build_category_series(
    df_long: pd.DataFrame,
    category: str,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Extract the trajectory for a specific site category in long format.
    """
    return (
        df_long.loc[df_long["site_category"].eq(category)]
        .sort_values(["index_name", year_col])
        .reset_index(drop=True)
    )


def build_focal_series(
    df_long: pd.DataFrame,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Extract the focal trajectory in long format for each year and index.
    """
    return build_category_series(
        df_long=df_long, category="focal", year_col=year_col
    )


def build_corridor_series(
    df_long: pd.DataFrame,
    year_col: str = "year",
) -> pd.DataFrame:
    """
    Extract the bio corridor trajectory in long format for each year and index.
    """
    return build_category_series(
        df_long=df_long,
        category="corridor",
        year_col=year_col,
    )


def join_category_series_to_envelope(
    category_long: pd.DataFrame,
    envelope_df: pd.DataFrame,
    year_col: str = "year",
    envelope_label: str = "reference",
) -> pd.DataFrame:
    """
    Join a category trajectory to a category envelope so each observation
    carries the comparison range for the same year and index.
    """
    cols = [
        year_col,
        "index_name",
        "mean",
        "median",
        "min",
        "max",
        "q25",
        "q75",
        "n_sites",
    ]
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
    return category_long.merge(env, on=[year_col, "index_name"], how="left")


def join_focal_to_envelope(
    focal_long: pd.DataFrame,
    envelope_df: pd.DataFrame,
    year_col: str = "year",
    envelope_label: str = "reference",
) -> pd.DataFrame:
    """
    Join the focal series to a category envelope.
    """
    return join_category_series_to_envelope(
        category_long=focal_long,
        envelope_df=envelope_df,
        year_col=year_col,
        envelope_label=envelope_label,
    )


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
    base = baseline_ranges.loc[
        :, ["index_name", "baseline_mean", "baseline_std"]
    ].copy()
    base = base.rename(
        columns={
            "baseline_mean": f"{label}_baseline_mean",
            "baseline_std": f"{label}_baseline_std",
        }
    )
    out = focal_long.merge(base, on="index_name", how="left")
    out[f"{label}_baseline_anomaly"] = (
        out["value"] - out[f"{label}_baseline_mean"]
    )
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
        df_long.groupby(
            ["site_category", "period", "index_name"], dropna=False
        )["value"]
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
            return pd.Series(
                {"n_obs": mask.sum(), "slope": np.nan, "intercept": np.nan}
            )
        slope, intercept = np.polyfit(x[mask], y[mask], 1)
        return pd.Series(
            {"n_obs": mask.sum(), "slope": slope, "intercept": intercept}
        )

    return (
        df_long.groupby(
            ["site_id", "site_name", "site_category", "index_name"],
            dropna=False,
        )
        .apply(_fit)
        .reset_index()
    )
