from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Patch

from tgbs_rs.config import (
    DEM_VIS,
    DEM_VIS_HYPSO,
    DEM_VIS_MUTED,
    SLOPE_VIS,
    SLOPE_VIS_DARK_TO_ORANGE,
    CANOPY_VIS,
    SOIL_CARBON_VIS,
    BII_VIS,
    ESA_WORLDCOVER_VIS,
    ESA_CLASS_VALUES,
    ESA_CLASS_NAMES,
)


def _read_raster_as_array(raster_path):
    """
    Read raster as a masked array using rasterio's internal mask.
    This preserves valid zeros and only masks true nodata.
    """
    raster_path = Path(raster_path)

    with rasterio.open(raster_path) as src:
        arr = src.read(1, masked=True).astype("float32")
        profile = src.profile

    return arr, profile


def _crop_to_common_shape(arrays_dict):
    """
    Crop all arrays to the minimum shared shape.
    """
    shapes = [arr.shape for arr in arrays_dict.values()]
    min_rows = min(shape[0] for shape in shapes)
    min_cols = min(shape[1] for shape in shapes)

    cropped = {
        name: arr[:min_rows, :min_cols] for name, arr in arrays_dict.items()
    }

    return cropped, (min_rows, min_cols)


def _mask_background(arr, mask_zero=False):
    """
    Return a masked array with NaNs masked, and optionally zero values masked.

    Parameters
    ----------
    arr : np.ndarray or np.ma.MaskedArray
        Input raster array.
    mask_zero : bool, default False
        If True, also mask values equal to 0.
    """
    data = np.asanyarray(arr).astype("float32")

    masked = np.ma.masked_invalid(data)

    if mask_zero:
        masked = np.ma.masked_where(masked == 0, masked)

    return masked


def _hex_palette_to_cmap(hex_list, name="custom_cmap"):
    """
    Convert hex palette to ListedColormap with transparent masked values.
    """
    fixed = [
        f"#{c}" if isinstance(c, str) and not c.startswith("#") else c
        for c in hex_list
    ]

    cmap = ListedColormap(fixed, name=name)
    cmap = cmap.copy()
    cmap.set_bad((0, 0, 0, 0))

    return cmap


def _plot_continuous_with_hillshade(
    ax,
    hillshade,
    data,
    title,
    vis_params,
    alpha=0.65,
    data_mask_zero=False,
):
    """
    Plot a continuous raster over a hillshade baselayer.
    """
    cmap = _hex_palette_to_cmap(vis_params["palette"], name=f"{title}_cmap")
    norm = Normalize(vmin=vis_params["min"], vmax=vis_params["max"])

    hillshade_masked = _mask_background(hillshade, mask_zero=True)
    data_masked = _mask_background(data, mask_zero=data_mask_zero)

    ax.imshow(hillshade_masked, cmap="gray", vmin=0, vmax=255)
    im = ax.imshow(data_masked, cmap=cmap, norm=norm, alpha=alpha)

    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])

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
    Plot a categorical raster over hillshade and add a legend.
    """
    if exclude_legend_values is None:
        exclude_legend_values = []

    cmap = _hex_palette_to_cmap(palette, name=f"{title}_cmap")

    remapped = np.full(data.shape, np.nan, dtype="float32")
    for idx, class_value in enumerate(class_values):
        remapped[data == class_value] = idx

    hillshade_masked = _mask_background(hillshade, mask_zero=True)
    remapped_masked = np.ma.masked_invalid(remapped)

    ax.imshow(hillshade_masked, cmap="gray", vmin=0, vmax=255)
    ax.imshow(
        remapped_masked,
        cmap=cmap,
        vmin=0,
        vmax=len(class_values) - 1,
        alpha=alpha,
    )

    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])

    legend_handles = []
    for i, class_value in enumerate(class_values):
        if class_value in exclude_legend_values:
            continue
        legend_handles.append(
            Patch(
                facecolor=palette[i],
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


def plot_baseline_panels_from_rasters(
    raster_dir,
    figsize=(12, 14),
    alpha_continuous=0.65,
    alpha_categorical=0.75,
):
    """
    Read exported baseline rasters from disk and plot a 2 x 3 figure.

    Expected files in raster_dir:
    - hillshade.tif
    - kwale_dem.tif
    - kwale_slope.tif
    - kwale_canopy_height.tif
    - kwale_land_cover.tif
    - kwale_soil_carbon.tif
    - kwale_bii_all.tif
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
        arr, profile = _read_raster_as_array(path)
        arrays[name] = arr
        profiles[name] = profile

    arrays, common_shape = _crop_to_common_shape(arrays)

    hillshade = arrays["hillshade"]
    dem = arrays["dem"]
    slope = arrays["slope"]
    canopy = arrays["canopy_height"]
    land_cover = arrays["land_cover"]
    soil = arrays["soil_carbon"]
    bii = arrays["bii_all"]

    fig, axes = plt.subplots(3, 2, figsize=figsize)

    im0 = _plot_continuous_with_hillshade(
        axes[0, 0],
        hillshade,
        dem,
        "Elevation",
        DEM_VIS_MUTED,
        alpha=alpha_continuous,
        data_mask_zero=False,
    )
    cbar0 = fig.colorbar(im0, ax=axes[0, 0], fraction=0.046, pad=0.04)
    cbar0.set_label("(m)", fontsize=8, labelpad=6)

    im1 = _plot_continuous_with_hillshade(
        axes[0, 1],
        hillshade,
        slope,
        "Slope",
        SLOPE_VIS_DARK_TO_ORANGE,
        alpha=alpha_continuous,
        data_mask_zero=False,
    )
    cbar1 = fig.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)
    cbar1.set_label("(deg)", fontsize=8, labelpad=6)

    im2 = _plot_continuous_with_hillshade(
        axes[1, 0],
        hillshade,
        canopy,
        "Canopy Height",
        CANOPY_VIS,
        alpha=alpha_continuous,
        data_mask_zero=False,
    )
    cbar2 = fig.colorbar(im2, ax=axes[1, 0], fraction=0.046, pad=0.04)
    cbar2.set_label("(m)", fontsize=8, labelpad=6)

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

    im4 = _plot_continuous_with_hillshade(
        axes[2, 0],
        hillshade,
        soil,
        "Mean Soil Carbon 0-20cm Depth",
        SOIL_CARBON_VIS,
        alpha=alpha_continuous,
        data_mask_zero=True,
    )
    cbar4 = fig.colorbar(im4, ax=axes[2, 0], fraction=0.046, pad=0.04)
    cbar4.set_label("(g/kg)", fontsize=8, labelpad=6)

    im5 = _plot_continuous_with_hillshade(
        axes[1, 1],
        hillshade,
        bii,
        "Biodiversity Intactness Index",
        BII_VIS,
        alpha=alpha_continuous,
        data_mask_zero=False,
    )
    fig.colorbar(im5, ax=axes[1, 1], fraction=0.046, pad=0.04)

    plt.tight_layout(rect=[0.05, 0, 1, 1])
    return fig, axes
