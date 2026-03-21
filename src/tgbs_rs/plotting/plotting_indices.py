from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


CATEGORY_STYLES = {
    "focal": {"linestyle": "-", "linewidth": 1.5},
    "reference": {"linestyle": "--", "linewidth": 1.8},
    "degraded": {"linestyle": ":", "linewidth": 1.5},
}


def _require_cols(df: pd.DataFrame, cols: list[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _subset(
    long_df: pd.DataFrame, band_name: str, period_type: str | None = None
) -> pd.DataFrame:
    _require_cols(
        long_df, ["band", "site_category", "site_name", "year", "value"]
    )
    df = long_df[long_df["band"] == band_name].copy()
    return (
        df
        if period_type is None or "period_type" not in df.columns
        else df[df["period_type"] == period_type].copy()
    )


def _quantile_summary(x: pd.Series, prefix: str = "") -> pd.Series:
    return pd.Series(
        {
            f"{prefix}mean": x.mean(),
            f"{prefix}median": x.median(),
            f"{prefix}std": x.std(),
            f"{prefix}min": x.min(),
            f"{prefix}max": x.max(),
            f"{prefix}q10": x.quantile(0.10),
            f"{prefix}q90": x.quantile(0.90),
            f"{prefix}n": x.count(),
        }
    )


def table_to_long_df(
    input_table,
    index_bands: list[str],
    period_type: str = "annual",
    extra_id_vars: list[str] | None = None,
) -> pd.DataFrame:
    df = (
        pd.read_csv(input_table)
        if isinstance(input_table, (str, Path))
        else input_table.copy()
    )
    id_vars = ["site_id", "site_name", "site_category", "year"]
    extras = [
        c
        for c in (extra_id_vars or ["source_file", "date", "image_count"])
        if c in df.columns
    ]
    _require_cols(df, id_vars + [c for c in index_bands if c in df.columns])
    long_df = df.melt(
        id_vars=id_vars + extras,
        value_vars=index_bands,
        var_name="band",
        value_name="value",
    )
    long_df["year"] = long_df["year"].astype(int)
    long_df["period_type"] = period_type
    return long_df.sort_values(
        ["band", "period_type", "site_category", "site_name", "year"]
    ).reset_index(drop=True)


def add_period_label(
    long_df: pd.DataFrame,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> pd.DataFrame:
    out = long_df.copy()
    b0, b1 = pd.Timestamp(baseline_start).year, pd.Timestamp(baseline_end).year
    c0, c1 = pd.Timestamp(current_start).year, pd.Timestamp(current_end).year
    out["period_label"] = np.select(
        [out["year"].between(b0, b1), out["year"].between(c0, c1)],
        ["baseline", "current"],
        default="other",
    )
    return out


def build_site_category_summary(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    df = _subset(long_df, band_name, period_type)
    return (
        df.groupby(
            ["band", "period_type", "year", "site_category"], dropna=False
        )["value"]
        .apply(_quantile_summary)
        .unstack()
        .reset_index()
        .sort_values(["year", "site_category"])
        .reset_index(drop=True)
    )


def build_reference_envelope(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    df = _subset(long_df, band_name, period_type)
    df = df[df["site_category"] == "reference"]
    out = (
        df.groupby(["band", "period_type", "year"], dropna=False)["value"]
        .apply(lambda x: _quantile_summary(x, "reference_"))
        .unstack()
        .reset_index()
        .sort_values("year")
        .reset_index(drop=True)
    )
    return out


def build_degraded_envelope(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    df = _subset(long_df, band_name, period_type)
    df = df[df["site_category"] == "degraded"]
    out = (
        df.groupby(["band", "period_type", "year"], dropna=False)["value"]
        .apply(lambda x: _quantile_summary(x, "degraded_"))
        .unstack()
        .reset_index()
        .sort_values("year")
        .reset_index(drop=True)
    )
    return out


def build_focal_comparison_table(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    subdf = _subset(long_df, band_name, period_type)
    focal = subdf[subdf["site_category"] == "focal"][
        ["year", "site_name", "value"]
    ].rename(columns={"site_name": "focal_site", "value": "focal_value"})
    reference_mean = (
        subdf[subdf["site_category"] == "reference"]
        .groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "reference_mean"})
    )
    degraded_mean = (
        subdf[subdf["site_category"] == "degraded"]
        .groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "degraded_mean"})
    )
    out = focal.merge(reference_mean, on="year", how="left").merge(
        degraded_mean, on="year", how="left"
    )
    out["focal_minus_reference"] = out["focal_value"] - out["reference_mean"]
    out["focal_minus_degraded"] = out["focal_value"] - out["degraded_mean"]
    out["band"] = band_name
    if period_type is not None:
        out["period_type"] = period_type
    return out.sort_values(["focal_site", "year"]).reset_index(drop=True)


def compare_focal_to_reference(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    focal = _subset(long_df, band_name, period_type)
    focal = focal[focal["site_category"] == "focal"][
        ["band", "period_type", "year", "site_id", "site_name", "value"]
    ]
    ref = build_reference_envelope(long_df, band_name, period_type)
    out = focal.merge(ref, on=["band", "period_type", "year"], how="left")
    out["focal_minus_reference_mean"] = out["value"] - out["reference_mean"]
    out["within_reference_q10_q90"] = out["value"].between(
        out["reference_q10"], out["reference_q90"]
    )
    out["above_reference_q90"] = out["value"] > out["reference_q90"]
    out["below_reference_q10"] = out["value"] < out["reference_q10"]
    return out.sort_values(["site_name", "year"]).reset_index(drop=True)


def compare_focal_to_degraded(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    focal = _subset(long_df, band_name, period_type)
    focal = focal[focal["site_category"] == "focal"][
        ["band", "period_type", "year", "site_id", "site_name", "value"]
    ]
    deg = build_degraded_envelope(long_df, band_name, period_type)
    out = focal.merge(deg, on=["band", "period_type", "year"], how="left")
    out["focal_minus_degraded_mean"] = out["value"] - out["degraded_mean"]
    out["within_degraded_q10_q90"] = out["value"].between(
        out["degraded_q10"], out["degraded_q90"]
    )
    out["above_degraded_q90"] = out["value"] > out["degraded_q90"]
    out["below_degraded_q10"] = out["value"] < out["degraded_q10"]
    return out.sort_values(["site_name", "year"]).reset_index(drop=True)


def compute_baseline_current_delta(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    df = _subset(long_df, band_name, period_type)
    _require_cols(df, ["period_label"])
    df = df[df["period_label"].isin(["baseline", "current"])]
    out = (
        df.groupby(
            [
                "band",
                "period_type",
                "site_id",
                "site_name",
                "site_category",
                "period_label",
            ],
            dropna=False,
        )["value"]
        .mean()
        .unstack("period_label")
        .reset_index()
    )
    out["delta"] = out["current"] - out["baseline"]
    out["pct_change"] = np.where(
        out["baseline"].eq(0), np.nan, 100 * out["delta"] / out["baseline"]
    )
    return out.sort_values(["site_category", "site_name"]).reset_index(
        drop=True
    )


def compute_standardized_delta(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
) -> pd.DataFrame:
    delta = compute_baseline_current_delta(long_df, band_name, period_type)
    df = _subset(long_df, band_name, period_type)
    _require_cols(df, ["period_label"])
    ref = df[
        (df["site_category"] == "reference")
        & (df["period_label"] == "baseline")
    ]["value"]
    ref_mean, ref_std = ref.mean(), ref.std()
    delta["reference_baseline_mean"] = ref_mean
    delta["reference_baseline_std"] = ref_std
    delta["standardized_delta"] = (
        delta["delta"] / ref_std
        if pd.notna(ref_std) and ref_std != 0
        else np.nan
    )
    delta["baseline_offset_from_reference"] = (
        (delta["baseline"] - ref_mean) / ref_std
        if pd.notna(ref_std) and ref_std != 0
        else np.nan
    )
    delta["current_offset_from_reference"] = (
        (delta["current"] - ref_mean) / ref_std
        if pd.notna(ref_std) and ref_std != 0
        else np.nan
    )
    return delta


def compute_trend_stats(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
    min_years: int = 4,
) -> pd.DataFrame:
    df = _subset(long_df, band_name, period_type)
    rows = []
    for keys, g in df.groupby(
        ["band", "period_type", "site_id", "site_name", "site_category"],
        dropna=False,
    ):
        g = g.sort_values("year")
        x, y = g["year"].to_numpy(float), g["value"].to_numpy(float)
        if len(g) < min_years or np.all(~np.isfinite(y)):
            rows.append(
                dict(
                    zip(
                        [
                            "band",
                            "period_type",
                            "site_id",
                            "site_name",
                            "site_category",
                        ],
                        keys,
                    ),
                    n_years=len(g),
                    slope=np.nan,
                    intercept=np.nan,
                    r2=np.nan,
                    start_year=g["year"].min(),
                    end_year=g["year"].max(),
                    start_value=np.nan,
                    end_value=np.nan,
                    absolute_change=np.nan,
                    pct_change=np.nan,
                )
            )
            continue
        slope, intercept = np.polyfit(x, y, 1)
        yhat = slope * x + intercept
        ss_res, ss_tot = np.sum((y - yhat) ** 2), np.sum((y - y.mean()) ** 2)
        rows.append(
            dict(
                zip(
                    [
                        "band",
                        "period_type",
                        "site_id",
                        "site_name",
                        "site_category",
                    ],
                    keys,
                ),
                n_years=len(g),
                slope=slope,
                intercept=intercept,
                r2=np.nan if ss_tot == 0 else 1 - ss_res / ss_tot,
                start_year=int(g["year"].iloc[0]),
                end_year=int(g["year"].iloc[-1]),
                start_value=float(g["value"].iloc[0]),
                end_value=float(g["value"].iloc[-1]),
                absolute_change=float(g["value"].iloc[-1] - g["value"].iloc[0]),
                pct_change=(
                    np.nan
                    if g["value"].iloc[0] == 0
                    else 100
                    * (g["value"].iloc[-1] - g["value"].iloc[0])
                    / g["value"].iloc[0]
                ),
            )
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["site_category", "site_name"])
        .reset_index(drop=True)
    )


def save_table(df: pd.DataFrame, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def plot_site_timeseries(
    long_df: pd.DataFrame, band_name: str, period_type: str | None = None
):
    subdf = _subset(long_df, band_name, period_type)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for site_name in subdf["site_name"].unique():
        site_df = subdf[subdf["site_name"] == site_name].sort_values("year")
        ax.plot(
            site_df["year"],
            site_df["value"],
            label=f"{site_name} ({site_df['site_category'].iloc[0]})",
            **CATEGORY_STYLES.get(site_df["site_category"].iloc[0], {}),
        )
    ax.set_title(f"{period_type.capitalize() or 'all'} {band_name} by Site")
    ax.set_xlabel("Year")
    ax.set_ylabel(band_name)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_focal_vs_groups(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
    envelope: str = "quantile",
):
    subdf = _subset(long_df, band_name, period_type)
    focal_df = subdf[subdf["site_category"] == "focal"].copy()
    ref_env = build_reference_envelope(long_df, band_name, period_type)
    deg_env = build_degraded_envelope(long_df, band_name, period_type)
    fig, ax = plt.subplots(figsize=(11, 4.5))

    if not ref_env.empty:
        lo, hi = (
            ("reference_q10", "reference_q90")
            if envelope == "quantile"
            else ("reference_min", "reference_max")
        )
        ax.fill_between(
            ref_env["year"],
            ref_env[lo],
            ref_env[hi],
            alpha=0.15,
            label=f"Reference {envelope} envelope",
        )
        ax.plot(
            ref_env["year"],
            ref_env["reference_mean"],
            linestyle="--",
            linewidth=2.2,
            label="Reference mean",
        )

    if not deg_env.empty:
        lo, hi = (
            ("degraded_q10", "degraded_q90")
            if envelope == "quantile"
            else ("degraded_min", "degraded_max")
        )
        ax.fill_between(
            deg_env["year"],
            deg_env[lo],
            deg_env[hi],
            alpha=0.15,
            label=f"Degraded {envelope} envelope",
        )
        ax.plot(
            deg_env["year"],
            deg_env["degraded_mean"],
            linestyle=":",
            linewidth=2.2,
            label="Degraded mean",
        )

    for site_name in focal_df["site_name"].unique():
        site_sub = focal_df[focal_df["site_name"] == site_name].sort_values(
            "year"
        )
        ax.plot(
            site_sub["year"],
            site_sub["value"],
            linestyle="-",
            linewidth=2.8,
            label=f"{site_name} (focal)",
        )

    ax.set_title(
        f"{period_type.capitalize() or 'all'} {band_name}: Focal vs Reference vs Degraded"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel(band_name)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_baseline_current_bars(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
):
    df = compute_baseline_current_delta(
        long_df, band_name, period_type
    ).sort_values(["site_category", "site_name"])
    x = np.arange(len(df))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x - w / 2, df["baseline"], width=w, label="Baseline")
    ax.bar(x + w / 2, df["current"], width=w, label="Current")
    ax.set_xticks(x)
    ax.set_xticklabels(df["site_name"], rotation=45, ha="right")
    ax.set_ylabel(band_name)
    ax.set_title(
        f"{period_type.capitalize() or 'all'} {band_name}: Baseline vs Current"
    )
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_standardized_deltas(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
):
    df = compute_standardized_delta(
        long_df, band_name, period_type
    ).sort_values(["site_category", "site_name"])
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(df["site_name"], df["standardized_delta"])
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_ylabel("Standardized delta (SD units)")
    ax.set_title(
        f"{period_type.capitalize() or 'all'} {band_name}: Standardized Baseline-to-Current Delta"
    )
    ax.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_trend_slopes(
    long_df: pd.DataFrame,
    band_name: str,
    period_type: str | None = None,
):
    df = compute_trend_stats(long_df, band_name, period_type).sort_values(
        ["site_category", "site_name"]
    )
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(df["site_name"], df["slope"])
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_ylabel("Slope per year")
    ax.set_title(
        f"{period_type.capitalize() or 'all'} {band_name}: Trend Slopes by Site"
    )
    ax.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
