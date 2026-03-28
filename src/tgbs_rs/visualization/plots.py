import pandas as pd
from pathlib import Path
import numpy as np
from matplotlib.colors import ListedColormap, Normalize, LinearSegmentedColormap
from matplotlib.patches import Patch
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from tgbs_rs.config.config import (
    ESA_CLASS_VALUES,
    ESA_CLASS_NAMES,
    DATA_DIR,
    RASTER_DIR,
)
from tgbs_rs.config.config_vis import BASELINE_VIS_PARAMS


sns.set_theme(style="whitegrid", context="talk")


############################ Baseline Data Plots ####################################

# I/O Helpers


def _read_band(path, extra_mask_vals=None):
    """Read band 1 as float32 masked array, masking nodata + optional extra values."""
    with rasterio.open(path) as src:
        arr = src.read(1, masked=True).astype(
            "float32"
        )  # uses internal mask + nodata
        profile = src.profile.copy()
    if extra_mask_vals:
        for v in extra_mask_vals:
            arr = np.ma.masked_where(arr == v, arr)
    return np.ma.masked_invalid(arr), profile


def _vector_mask(profile, vector_path):
    """Return a boolean array (True = inside polygon) aligned to raster grid."""
    gdf = gpd.read_file(vector_path)
    if gdf.crs != profile["crs"]:
        gdf = gdf.to_crs(profile["crs"])
    h, w = profile["height"], profile["width"]
    return geometry_mask(
        gdf.geometry,
        out_shape=(h, w),
        transform=profile["transform"],
        invert=True,
    )


def _apply_shared_mask(*arrays):
    """Union all masks, apply the combined mask to every array."""
    combined = np.zeros(arrays[0].shape, dtype=bool)
    for a in arrays:
        combined |= np.ma.getmaskarray(a)
    return tuple(np.ma.array(a.data, mask=combined) for a in arrays)


def _align_shapes(*arrays):
    """Trim all arrays to minimum shared shape (assumes co-registered origins)."""
    r = min(a.shape[0] for a in arrays)
    c = min(a.shape[1] for a in arrays)
    return tuple(a[:r, :c] for a in arrays)


# Colormap Helpers


def _make_cmap(colors, name="cmap", continuous=False):
    """Build a Listed or LinearSegmented colormap with transparent bad pixels."""
    cls = LinearSegmentedColormap.from_list if continuous else ListedColormap
    cmap = cls(name, colors) if continuous else cls(colors, name=name)
    cmap.set_bad((0, 0, 0, 0))
    return cmap


# Axis Helpers


def _style_axis(ax, title):
    ax.set(title=title, xticks=[], yticks=[])
    ax.set_title(title, fontsize=11, pad=10)
    ax.set_facecolor("none")
    ax.set_frame_on(False)


def _plot_points(ax, gdf, vp, transform):
    """Plot points using raster pixel coordinates derived from the geotransform."""
    rows, cols = rasterio.transform.rowcol(
        transform, gdf.geometry.x.values, gdf.geometry.y.values
    )
    ax.plot(
        cols,
        rows,
        "o",
        ms=vp.get("markersize"),
        mfc=vp.get("facecolor"),
        mec=vp.get("edgecolor"),
        mew=vp.get("linewidth"),
        zorder=100,
        ls="none",
    )


def _plot_vector_outline(
    ax, gdf, transform, edgecolor="black", linewidth=0.6, zorder=20
):
    """
    Plot polygon boundaries in raster pixel coordinates so they align with imshow().
    """
    for geom in gdf.geometry:
        if geom is None or geom.is_empty:
            continue

        geom_type = geom.geom_type

        if geom_type == "Polygon":
            polys = [geom]
        elif geom_type == "MultiPolygon":
            polys = list(geom.geoms)
        else:
            continue

        for poly in polys:
            x, y = poly.exterior.coords.xy
            rows, cols = rasterio.transform.rowcol(transform, x, y)
            ax.plot(
                cols, rows, color=edgecolor, linewidth=linewidth, zorder=zorder
            )

            for interior in poly.interiors:
                x, y = interior.coords.xy
                rows, cols = rasterio.transform.rowcol(transform, x, y)
                ax.plot(
                    cols,
                    rows,
                    color=edgecolor,
                    linewidth=linewidth,
                    zorder=zorder,
                )


def _mask_to_county(arr, profile, county_path):
    inside = _vector_mask(profile, county_path)[: arr.shape[0], : arr.shape[1]]
    return np.ma.array(arr.data, mask=np.ma.getmaskarray(arr) | ~inside)


def _add_colorbar(fig, ax, im, label):
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    cax = inset_axes(
        ax,
        width="5%",
        height="60%",
        loc="center left",
        bbox_to_anchor=(1.02, 0.0, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(label, fontsize=8, labelpad=6)
    # cb.outline.set_visible(False)
    cb.ax.tick_params(size=0)
    return cb


# Panel Renderers


def _render_continuous(ax, hillshade, data, vp, alpha=0.65):
    hs_plot = np.ma.array(
        hillshade.data,
        mask=np.ma.getmaskarray(hillshade) | np.ma.getmaskarray(data),
    )
    ax.imshow(hs_plot, cmap=plt.cm.gray, vmin=0, vmax=255, interpolation="none")
    im = ax.imshow(
        data,
        cmap=_make_cmap(vp["palette"], "data"),
        norm=Normalize(vp["min"], vp["max"]),
        alpha=alpha,
        interpolation="none",
    )
    return im


def _render_categorical(
    ax,
    hillshade,
    data,
    class_values,
    class_names,
    palette,
    alpha=0.75,
    exclude_values=None,
):
    exclude_values = exclude_values or []
    remapped = np.full(data.shape, np.nan, dtype="float32")
    for i, v in enumerate(class_values):
        remapped[data.data == v] = i
    remapped = np.ma.masked_invalid(remapped)

    hs_plot = np.ma.array(
        hillshade.data,
        mask=np.ma.getmaskarray(hillshade) | np.ma.getmaskarray(remapped),
    )

    ax.imshow(hs_plot, cmap=plt.cm.gray, vmin=0, vmax=255, interpolation="none")
    ax.imshow(
        remapped,
        cmap=_make_cmap(palette, "cat"),
        vmin=0,
        vmax=len(class_values) - 1,
        alpha=alpha,
        interpolation="none",
    )

    handles = [
        Patch(
            facecolor=f"#{c}" if not str(c).startswith("#") else c,
            edgecolor="black",
            label=class_names[i],
        )
        for i, (c, v) in enumerate(zip(palette, class_values))
        if v not in exclude_values
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=7, ncol=1)


# Main Figures


def plot_baseline_panels_from_rasters(
    raster_dir=RASTER_DIR,
    figsize=(12, 17),
    alpha_continuous=0.65,
    alpha_categorical=0.75,
):
    raster_dir = Path(raster_dir)
    vp = BASELINE_VIS_PARAMS
    county_path = DATA_DIR / "kwale_county.geojson"

    # ── load all rasters ──
    hs, hs_p = _read_band(
        raster_dir / "kwale_hillshade.tif", extra_mask_vals=[0]
    )
    dem, dem_p = _read_band(raster_dir / "kwale_dem.tif")
    slope, slope_p = _read_band(raster_dir / "kwale_slope.tif")
    canopy, canopy_p = _read_band(raster_dir / "kwale_canopy_height.tif")
    bii, bii_p = _read_band(raster_dir / "kwale_bii_all.tif")
    soil, soil_p = _read_band(raster_dir / "kwale_soil_carbon.tif")
    lc, lc_p = _read_band(raster_dir / "kwale_land_cover.tif")
    fc, fc_p = _read_band(raster_dir / "kwale_forest_2000.tif")
    fly, fly_p = _read_band(raster_dir / "kwale_forest_loss_years.tif")

    hs, dem, slope, canopy, bii, soil, lc, fc, fly = _align_shapes(
        hs, dem, slope, canopy, bii, soil, lc, fc, fly
    )

    # Apply one consistent county mask to all layers
    hs = _mask_to_county(hs, hs_p, county_path)
    dem = _mask_to_county(dem, dem_p, county_path)
    slope = _mask_to_county(slope, slope_p, county_path)
    canopy = _mask_to_county(canopy, canopy_p, county_path)
    bii = _mask_to_county(bii, bii_p, county_path)
    soil = _mask_to_county(soil, soil_p, county_path)
    lc = _mask_to_county(lc, lc_p, county_path)
    fc = _mask_to_county(fc, fc_p, county_path)

    # Keep only the visualization-specific mask for loss years
    fly = np.ma.masked_where(fly <= 0, fly)
    fly = _mask_to_county(fly, fly_p, county_path)

    point_gdf = gpd.read_file(DATA_DIR / "ks_rehab_point.geojson").to_crs(
        hs_p["crs"]
    )
    pt_vp = vp["KS_REHAB_POINT_VIS"]

    panels = [
        (
            0,
            0,
            dem,
            hs_p["transform"],
            vp["DEM_VIS"],
            "Elevation",
            "(m)",
            "cont",
        ),
        (
            0,
            1,
            slope,
            hs_p["transform"],
            vp["SLOPE_VIS"],
            "Slope",
            "(deg)",
            "cont",
        ),
        (
            1,
            0,
            canopy,
            hs_p["transform"],
            vp["CANOPY_VIS"],
            "Canopy Height",
            "(m)",
            "cont",
        ),
        (
            1,
            1,
            bii,
            hs_p["transform"],
            vp["BII_VIS"],
            "Biodiversity Intactness Index",
            "(0–1)",
            "cont",
        ),
        (
            2,
            0,
            soil,
            hs_p["transform"],
            vp["SOIL_CARBON_VIS"],
            "Mean Soil Carbon 0-20cm Depth",
            "(g/kg)",
            "cont",
        ),
        (2, 1, lc, hs_p["transform"], None, "Land Cover", None, "cat"),
    ]

    fig, axes = plt.subplots(3, 2, figsize=figsize, facecolor="white")
    for ax in axes.flat:
        ax.set_facecolor("none")

    for row, col, data, transform, layer_vp, title, cbar_label, kind in panels:
        ax = axes[row, col]

        if kind == "cont":
            im = _render_continuous(ax, hs, data, layer_vp, alpha_continuous)
            _style_axis(ax, title)
            _plot_points(ax, point_gdf, pt_vp, transform)
            _add_colorbar(fig, ax, im, cbar_label)

        elif kind == "cont_loss":
            im = _render_continuous(ax, hs, data, layer_vp, alpha=0.90)
            _style_axis(ax, title)
            _plot_points(ax, point_gdf, pt_vp, transform)
            cb = _add_colorbar(fig, ax, im, cbar_label)
            cb.set_ticks([1, 6, 12, 18, 24])
            cb.set_ticklabels(["2001", "2006", "2012", "2018", "2024"])

        elif kind == "cat":
            _render_categorical(
                ax,
                hs,
                data,
                ESA_CLASS_VALUES,
                ESA_CLASS_NAMES,
                vp["ESA_WORLDCOVER_VIS"]["palette"],
                alpha_categorical,
                exclude_values=[70],
            )
            _style_axis(ax, "Land Cover")
            _plot_points(ax, point_gdf, pt_vp, transform)

    fig.subplots_adjust(
        left=0.06,
        right=0.92,
        bottom=0.04,
        top=0.98,
        wspace=0.30,
        hspace=0.0,
    )

    return fig, axes


def plot_forest_panels_from_rasters(
    raster_dir=RASTER_DIR,
    data_dir=DATA_DIR,
    figsize=(12.5, 6.2),
    alpha_forest=0.70,
    alpha_loss=0.90,
):
    raster_dir = Path(raster_dir)
    vp = BASELINE_VIS_PARAMS
    county_path = data_dir / "kwale_county.geojson"

    hs, hs_p = _read_band(
        raster_dir / "kwale_hillshade.tif",
        extra_mask_vals=[0],
    )
    fc, fc_p = _read_band(raster_dir / "kwale_forest_2000.tif")
    fly, fly_p = _read_band(raster_dir / "kwale_forest_loss_years.tif")

    hs, fc, fly = _align_shapes(hs, fc, fly)

    # Common spatial mask
    hs = _mask_to_county(hs, hs_p, county_path)
    fc = _mask_to_county(fc, fc_p, county_path)

    # Keep only the visualization-specific mask for loss years
    fly = np.ma.masked_where(fly <= 0, fly)
    fly = _mask_to_county(fly, fly_p, county_path)

    county_gdf = gpd.read_file(county_path).to_crs(hs_p["crs"])
    point_gdf = gpd.read_file(data_dir / "ks_rehab_point.geojson").to_crs(
        hs_p["crs"]
    )
    pt_vp = vp["KS_REHAB_POINT_VIS"]

    fig, axes = plt.subplots(1, 2, figsize=figsize, facecolor="white")
    for ax in axes.flat:
        ax.set_facecolor("none")

    # Panel 1 — Forest Cover 2000
    ax = axes[0]
    fc_cmap = _make_cmap(
        vp["FOREST_COVER_VIS"]["palette"], "fc", continuous=True
    )
    hs_fc = np.ma.array(
        hs.data,
        mask=np.ma.getmaskarray(hs) | np.ma.getmaskarray(fc),
    )
    ax.imshow(hs_fc, cmap=plt.cm.gray, vmin=0, vmax=255, interpolation="none")
    im0 = ax.imshow(
        fc,
        cmap=fc_cmap,
        norm=Normalize(
            vp["FOREST_COVER_VIS"]["min"], vp["FOREST_COVER_VIS"]["max"]
        ),
        alpha=alpha_forest,
        interpolation="none",
    )
    _style_axis(ax, "Forest Cover (2000)")
    _plot_points(ax, point_gdf, pt_vp, fc_p["transform"])
    _add_colorbar(fig, ax, im0, "(tree cover %)")

    # Panel 2 — Forest Loss Year
    ax = axes[1]
    loss_cmap = _make_cmap(
        vp["LOSS_YEAR_VIS"]["palette"], "fly", continuous=True
    )
    hs_fly = np.ma.array(
        hs.data,
        mask=np.ma.getmaskarray(hs) | np.ma.getmaskarray(fly),
    )
    ax.imshow(hs_fly, cmap=plt.cm.gray, vmin=0, vmax=255, interpolation="none")
    im1 = ax.imshow(
        fly,
        cmap=loss_cmap,
        norm=Normalize(1, 24),
        alpha=alpha_loss,
        interpolation="none",
    )

    _plot_vector_outline(
        ax,
        county_gdf,
        fly_p["transform"],
        edgecolor="black",
        linewidth=0.6,
        zorder=10,
    )

    _style_axis(ax, "Forest Loss Year")
    _plot_points(ax, point_gdf, pt_vp, fly_p["transform"])
    cb1 = _add_colorbar(fig, ax, im1, "(year of loss)")
    cb1.set_ticks([1, 6, 12, 18, 24])
    cb1.set_ticklabels(["2001", "2006", "2012", "2018", "2024"])

    fig.subplots_adjust(
        left=0.05,
        right=0.93,
        bottom=0.08,
        top=0.94,
        wspace=0.28,
    )

    return fig, axes


############################ Timeseries Plots ####################################
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


############################ Landscape Metrics Plots ####################################
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
