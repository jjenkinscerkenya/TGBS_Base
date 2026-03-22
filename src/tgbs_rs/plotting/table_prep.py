import pandas as pd


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
    Keep only the core metadata and requested analytical value columns.
    This is useful for creating small, analysis-focused tables from large exported
    band-rich CSV files.
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
            "date",
            "image_count",
            "temporal_scale",
            "composite_stat",
            "period",
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
