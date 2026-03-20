import pandas as pd
import matplotlib as plt


def table_to_long_df(input_table, index_bands: list):
    df = pd.read_csv(input_table)
    long_df = df.melt(
        id_vars=[
            "site_id",
            "site_name",
            "site_category",
            "source_file",
            "year",
            "date",
            "image_count",
        ],
        value_vars=index_bands,
        var_name="band",
        value_name="value",
    )

    long_df = long_df.sort_values(
        ["band", "site_category", "site_name", "year"]
    ).reset_index(drop=True)
    return long_df


CATEGORY_STYLES = {
    "focal": {"linestyle": "-", "linewidth": 2.8},
    "reference": {"linestyle": "--", "linewidth": 1.8},
    "degraded": {"linestyle": ":", "linewidth": 2.2},
}


def plot_site_timeseries(long_df: pd.DataFrame, band_name: str):
    subdf = long_df[long_df["band"] == band_name].copy()

    fig, ax = plt.subplots(figsize=(10, 6))

    for site_name in subdf["site_name"].unique():
        site_df = subdf[subdf["site_name"] == site_name].sort_values("year")
        category = site_df["site_category"].iloc[0]
        style = CATEGORY_STYLES.get(category, {})

        ax.plot(
            site_df["year"],
            site_df["value"],
            label=f"{site_name} ({category})",
            **style,
        )

    ax.set_title(f"Annual {band_name} by Site")
    ax.set_xlabel("Year")
    ax.set_ylabel(band_name)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_focal_vs_groups(long_df: pd.DataFrame, band_name: str):
    subdf = long_df[long_df["band"] == band_name].copy()

    focal_df = subdf[subdf["site_category"] == "focal"].copy()
    ref_df = subdf[subdf["site_category"] == "reference"].copy()
    deg_df = subdf[subdf["site_category"] == "degraded"].copy()

    ref_mean = (
        ref_df.groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "reference_mean"})
    )
    ref_range = ref_df.groupby("year", as_index=False)["value"].agg(
        reference_min="min", reference_max="max"
    )

    deg_mean = (
        deg_df.groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "degraded_mean"})
    )
    deg_range = deg_df.groupby("year", as_index=False)["value"].agg(
        degraded_min="min", degraded_max="max"
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    if not ref_range.empty:
        ax.fill_between(
            ref_range["year"],
            ref_range["reference_min"],
            ref_range["reference_max"],
            alpha=0.15,
            label="Reference range",
        )

    if not deg_range.empty:
        ax.fill_between(
            deg_range["year"],
            deg_range["degraded_min"],
            deg_range["degraded_max"],
            alpha=0.15,
            label="Degraded range",
        )

    if not ref_mean.empty:
        ax.plot(
            ref_mean["year"],
            ref_mean["reference_mean"],
            linestyle="--",
            linewidth=2.2,
            label="Reference mean",
        )

    if not deg_mean.empty:
        ax.plot(
            deg_mean["year"],
            deg_mean["degraded_mean"],
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

    ax.set_title(f"Annual {band_name}: Focal vs Reference vs Degraded")
    ax.set_xlabel("Year")
    ax.set_ylabel(band_name)
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def build_focal_comparison_table(long_df: pd.DataFrame, band_name: str):
    subdf = long_df[long_df["band"] == band_name].copy()

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

    return out.sort_values("year").reset_index(drop=True)
