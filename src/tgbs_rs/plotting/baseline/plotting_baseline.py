from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize, LinearSegmentedColormap
from matplotlib.patches import Patch
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask

from tgbs_rs.config.config import (
    ESA_CLASS_VALUES,
    ESA_CLASS_NAMES,
    DATA_DIR,
    RASTER_DIR,
)
from tgbs_rs.config.config_vis import BASELINE_VIS_PARAMS


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
        ms=vp.get("markersize", 1.5),
        mfc=vp.get("facecolor", "red"),
        mec=vp.get("edgecolor", "black"),
        mew=vp.get("linewidth", 0.5),
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
    raster_dir: RASTER_DIR,
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
    raster_dir: RASTER_DIR,
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
