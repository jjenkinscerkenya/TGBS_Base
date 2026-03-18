from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Patch

from tgbs_rs.config import (
    DEM_VIS_MUTED,
    SLOPE_VIS_DARK_TO_ORANGE,
    CANOPY_VIS,
    SOIL_CARBON_VIS,
    BII_VIS,
    ESA_WORLDCOVER_VIS,
    ESA_CLASS_VALUES,
    ESA_CLASS_NAMES,
)


# -----------------------------------------------------------------------------
# Raster reading and masking helpers
# -----------------------------------------------------------------------------


def _ensure_masked_float_array(arr):
    """
    Return a float32 masked array with invalid values masked.
    """
    if np.ma.isMaskedArray(arr):
        out = np.ma.array(arr, copy=True)
        out = out.astype("float32")
        out = np.ma.masked_invalid(out)
        return out

    arr = np.asarray(arr, dtype="float32")
    return np.ma.masked_invalid(arr)


def _read_raster_as_array(raster_path, extra_nodata_values=None):
    """
    Read a raster band as a float32 masked array.

    This function does NOT rely only on rasterio's masked=True behavior.
    It explicitly masks:
    - src.nodata
    - NaN / inf
    - any values passed in extra_nodata_values

    Parameters
    ----------
    raster_path : str or Path
        Path to raster.
    extra_nodata_values : list or tuple, optional
        Additional pixel values to mask, e.g. [0] for hillshade if 0 is nodata.

    Returns
    -------
    arr : np.ma.MaskedArray
        Masked float32 array.
    profile : dict
        Raster profile.
    """
    raster_path = Path(raster_path)

    with rasterio.open(raster_path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile.copy()
        nodata = src.nodata

    mask = ~np.isfinite(arr)

    if nodata is not None:
        mask |= arr == nodata

    if extra_nodata_values is not None:
        for value in extra_nodata_values:
            mask |= arr == value

    arr = np.ma.array(arr, mask=mask, dtype="float32")
    arr = np.ma.masked_invalid(arr)

    return arr, profile


def _mask_array_with_vector(arr, profile, vector_path):
    """
    Mask a raster array to a polygon vector footprint.

    Pixels outside the polygon are masked, while preserving the existing mask.
    """
    vector_path = Path(vector_path)
    gdf = gpd.read_file(vector_path)

    raster_crs = profile["crs"]
    if gdf.crs != raster_crs:
        gdf = gdf.to_crs(raster_crs)

    inside_mask = geometry_mask(
        geometries=gdf.geometry,
        out_shape=arr.shape,
        transform=profile["transform"],
        invert=True,
    )

    arr = _ensure_masked_float_array(arr)
    combined_mask = np.ma.getmaskarray(arr) | ~inside_mask

    return np.ma.array(arr.data, mask=combined_mask, dtype="float32")


def _crop_to_common_shape(arrays_dict):
    """
    Crop all arrays to the minimum shared shape.
    """
    min_rows = min(arr.shape[0] for arr in arrays_dict.values())
    min_cols = min(arr.shape[1] for arr in arrays_dict.values())

    cropped = {
        name: arr[:min_rows, :min_cols] for name, arr in arrays_dict.items()
    }

    return cropped, (min_rows, min_cols)


def _combine_masks(*arrays):
    """
    Combine masks across multiple arrays so they share the same transparent background.

    Returns
    -------
    tuple of masked arrays
    """
    masked_arrays = [_ensure_masked_float_array(arr) for arr in arrays]
    combined_mask = np.zeros(masked_arrays[0].shape, dtype=bool)

    for arr in masked_arrays:
        combined_mask |= np.ma.getmaskarray(arr)

    out = [
        np.ma.array(arr.data, mask=combined_mask, dtype="float32")
        for arr in masked_arrays
    ]
    return tuple(out)


# -----------------------------------------------------------------------------
# Colormap helpers
# -----------------------------------------------------------------------------


def _transparent_gray_cmap():
    """
    Grayscale colormap with transparent masked pixels.
    """
    cmap = plt.cm.gray.copy()
    cmap.set_bad((0, 0, 0, 0))
    return cmap


def _hex_palette_to_cmap(hex_list, name="custom_cmap"):
    """
    Convert a hex palette to a ListedColormap with transparent masked pixels.
    """
    fixed = [
        f"#{c}" if isinstance(c, str) and not c.startswith("#") else c
        for c in hex_list
    ]

    cmap = ListedColormap(fixed, name=name).copy()
    cmap.set_bad((0, 0, 0, 0))
    return cmap


# -----------------------------------------------------------------------------
# Axis styling
# -----------------------------------------------------------------------------


def _style_axis(ax, title):
    """
    Apply consistent axis styling.
    """
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("none")
    ax.patch.set_alpha(0.0)

    for spine in ax.spines.values():
        spine.set_visible(False)


# -----------------------------------------------------------------------------
# Plotting helpers
# -----------------------------------------------------------------------------


def _plot_continuous_with_hillshade(
    ax,
    hillshade,
    data,
    title,
    vis_params,
    alpha=0.65,
):
    """
    Plot a continuous raster over hillshade.

    Important:
    Hillshade and data are given a shared combined mask so that any nodata area
    remains transparent in both layers.
    """
    hillshade, data = _combine_masks(hillshade, data)

    gray_cmap = _transparent_gray_cmap()
    data_cmap = _hex_palette_to_cmap(
        vis_params["palette"], name=f"{title}_cmap"
    )
    norm = Normalize(vmin=vis_params["min"], vmax=vis_params["max"])

    ax.imshow(hillshade, cmap=gray_cmap, vmin=0, vmax=255, interpolation="none")
    im = ax.imshow(
        data, cmap=data_cmap, norm=norm, alpha=alpha, interpolation="none"
    )

    _style_axis(ax, title)
    return im


def _plot_categorical_with_hillshade(
    ax,
    hillshade,
    data,
    title,
    class_values,
    class_names,
    palette,
    alpha=0.75,
    exclude_legend_values=None,
):
    """
    Plot a categorical raster over hillshade with legend.
    """
    if exclude_legend_values is None:
        exclude_legend_values = []

    hillshade = _ensure_masked_float_array(hillshade)
    data = _ensure_masked_float_array(data)

    data_filled = data.filled(np.nan)
    remapped = np.full(data_filled.shape, np.nan, dtype="float32")

    for idx, class_value in enumerate(class_values):
        remapped[data_filled == class_value] = idx

    remapped = np.ma.masked_invalid(remapped)
    hillshade, remapped = _combine_masks(hillshade, remapped)

    gray_cmap = _transparent_gray_cmap()
    cat_cmap = _hex_palette_to_cmap(palette, name=f"{title}_cmap")

    ax.imshow(hillshade, cmap=gray_cmap, vmin=0, vmax=255, interpolation="none")
    ax.imshow(
        remapped,
        cmap=cat_cmap,
        vmin=0,
        vmax=len(class_values) - 1,
        alpha=alpha,
        interpolation="none",
    )

    _style_axis(ax, title)

    legend_handles = []
    for i, class_value in enumerate(class_values):
        if class_value in exclude_legend_values:
            continue

        facecolor = palette[i]
        if isinstance(facecolor, str) and not facecolor.startswith("#"):
            facecolor = f"#{facecolor}"

        legend_handles.append(
            Patch(
                facecolor=facecolor,
                edgecolor="black",
                label=class_names[i],
            )
        )

    ax.legend(
        handles=legend_handles,
        loc="lower left",
        fontsize=7,
        frameon=True,
        ncol=1,
    )


# -----------------------------------------------------------------------------
# Main figure function
# -----------------------------------------------------------------------------


def plot_baseline_panels_from_rasters(
    raster_dir,
    figsize=(12, 14),
    alpha_continuous=0.65,
    alpha_categorical=0.75,
):
    """
    Read exported baseline rasters from disk and plot a 3 x 2 figure.

    Expected files in raster_dir:
    - kwale_hillshade.tif
    - kwale_dem.tif
    - kwale_slope.tif
    - kwale_canopy_height.tif
    - kwale_land_cover.tif
    - kwale_soil_carbon.tif
    - kwale_bii_all.tif

    Notes
    -----
    - Nodata is explicitly masked using raster metadata.
    - Hillshade can additionally mask 0 if 0 represents background/nodata.
    - Canopy height is further clipped to kwale_county.geojson.
    """
    raster_dir = Path(raster_dir)

    raster_paths = {
        "hillshade": raster_dir / "kwale_hillshade.tif",
        "dem": raster_dir / "kwale_dem.tif",
        "slope": raster_dir / "kwale_slope.tif",
        "canopy_height": raster_dir / "kwale_canopy_height.tif",
        "land_cover": raster_dir / "kwale_land_cover.tif",
        "soil_carbon": raster_dir / "kwale_soil_carbon.tif",
        "bii_all": raster_dir / "kwale_bii_all.tif",
    }

    missing = [str(path) for path in raster_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "The following raster files were not found:\n" + "\n".join(missing)
        )

    arrays = {}
    profiles = {}

    for name, path in raster_paths.items():
        extra_nodata_values = None

        # If hillshade background pixels are 0, mask them explicitly.
        if name == "hillshade":
            extra_nodata_values = [0]

        arr, profile = _read_raster_as_array(
            path,
            extra_nodata_values=extra_nodata_values,
        )
        arrays[name] = arr
        profiles[name] = profile

    arrays, _ = _crop_to_common_shape(arrays)

    hillshade = arrays["hillshade"]
    dem = arrays["dem"]
    slope = arrays["slope"]
    land_cover = arrays["land_cover"]
    soil = arrays["soil_carbon"]
    bii = arrays["bii_all"]

    # Manual vector mask for canopy layer
    vector_path = (
        Path(__file__).resolve().parents[2] / "data" / "kwale_county.geojson"
    )
    canopy = _mask_array_with_vector(
        arrays["canopy_height"],
        profiles["canopy_height"],
        vector_path,
    )

    # Make figure and axes transparent/white-friendly
    fig, axes = plt.subplots(3, 2, figsize=figsize)
    fig.patch.set_facecolor("white")
    fig.patch.set_alpha(1.0)

    for ax in axes.flat:
        ax.set_facecolor("none")
        ax.patch.set_alpha(0.0)

    # Panel 1: DEM
    im0 = _plot_continuous_with_hillshade(
        axes[0, 0],
        hillshade,
        dem,
        "Elevation",
        DEM_VIS_MUTED,
        alpha=alpha_continuous,
    )
    cbar0 = fig.colorbar(im0, ax=axes[0, 0], fraction=0.046, pad=0.04)
    cbar0.set_label("(m)", fontsize=8, labelpad=6)

    # Panel 2: Slope
    im1 = _plot_continuous_with_hillshade(
        axes[0, 1],
        hillshade,
        slope,
        "Slope",
        SLOPE_VIS_DARK_TO_ORANGE,
        alpha=alpha_continuous,
    )
    cbar1 = fig.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)
    cbar1.set_label("(deg)", fontsize=8, labelpad=6)

    # Panel 3: Canopy Height
    im2 = _plot_continuous_with_hillshade(
        axes[1, 0],
        hillshade,
        canopy,
        "Canopy Height",
        CANOPY_VIS,
        alpha=alpha_continuous,
    )
    cbar2 = fig.colorbar(im2, ax=axes[1, 0], fraction=0.046, pad=0.04)
    cbar2.set_label("(m)", fontsize=8, labelpad=6)

    # Panel 4: BII
    im3 = _plot_continuous_with_hillshade(
        axes[1, 1],
        hillshade,
        bii,
        "Biodiversity Intactness Index",
        BII_VIS,
        alpha=alpha_continuous,
    )
    cbar3 = fig.colorbar(im3, ax=axes[1, 1], fraction=0.046, pad=0.04)
    cbar3.set_label("(0–1)", fontsize=8, labelpad=6)

    # Panel 5: Soil Carbon
    im4 = _plot_continuous_with_hillshade(
        axes[2, 0],
        hillshade,
        soil,
        "Mean Soil Carbon 0-20cm Depth",
        SOIL_CARBON_VIS,
        alpha=alpha_continuous,
    )
    cbar4 = fig.colorbar(im4, ax=axes[2, 0], fraction=0.046, pad=0.04)
    cbar4.set_label("(g/kg)", fontsize=8, labelpad=6)

    # Panel 6: Land Cover
    _plot_categorical_with_hillshade(
        axes[2, 1],
        hillshade,
        land_cover,
        "Land Cover",
        ESA_CLASS_VALUES,
        ESA_CLASS_NAMES,
        ESA_WORLDCOVER_VIS["palette"],
        alpha=alpha_categorical,
        exclude_legend_values=[70],
    )

    plt.tight_layout(rect=[0.03, 0.02, 1, 1])
    return fig, axes
