from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import ee

from tgbs_rs.metrics.temporal import build_period_composites
from tgbs_rs.utils import (
    geojson_to_ee_geometry,
    _clip_and_mask_image,
    load_ks_rehab_blocks_featurecollection,
)


def _safe_path(path_like: Any) -> Path:
    """Return a normalized pathlib.Path."""
    return path_like if isinstance(path_like, Path) else Path(path_like)


def _load_geojson_as_ee_featurecollection(
    path_like: Any,
) -> ee.FeatureCollection:
    """
    Load a local GeoJSON file into an ee.FeatureCollection.

    Notes
    -----
    - This is intended for local GeoJSON files.
    - It does not support GeoPackage inputs.
    - Features and properties are preserved from the input GeoJSON.
    """
    path = _safe_path(path_like)
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        gj = json.load(f)

    gj_type = gj.get("type")
    if gj_type == "FeatureCollection":
        return ee.FeatureCollection(gj)
    if gj_type == "Feature":
        return ee.FeatureCollection([gj])
    if gj_type in {
        "Polygon",
        "MultiPolygon",
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
    }:
        return ee.FeatureCollection(
            [{"type": "Feature", "geometry": gj, "properties": {}}]
        )

    raise ValueError(
        f"Unsupported GeoJSON top-level type: {gj_type}. "
        "Expected FeatureCollection, Feature, or a GeoJSON geometry."
    )


def _clip_if_requested(
    image: ee.Image, clip_geom: Optional[ee.Geometry]
) -> ee.Image:
    """Apply explicit AOI mask and clip if a geometry is provided."""
    return (
        _clip_and_mask_image(image, clip_geom)
        if clip_geom is not None
        else image
    )


def _ensure_nonzero_std(std_image: ee.Image, eps: float = 1e-6) -> ee.Image:
    """Replace zero std pixels with a small epsilon to avoid divide-by-zero."""
    return std_image.where(std_image.eq(0), ee.Image.constant(eps))


def _annual_collection_has_data(
    annual_collection: ee.ImageCollection,
) -> ee.ImageCollection:
    """
    Filter out annual composite images where image_count == 0 if that property exists.
    """
    return ee.ImageCollection(
        ee.Algorithms.If(
            ee.Algorithms.ObjectType(annual_collection.first())
            .compareTo("Image")
            .eq(0),
            annual_collection.filter(ee.Filter.gt("image_count", 0)),
            annual_collection,
        )
    )


def _add_year_band(img: ee.Image) -> ee.Image:
    """Add a numeric year band derived from system:time_start."""
    year_num = ee.Number(ee.Date(img.get("system:time_start")).get("year"))
    year_band = ee.Image.constant(year_num).rename("year").float()
    return img.addBands(year_band)


def _set_image_properties(
    image: ee.Image,
    index_name: str,
    **props: Any,
) -> ee.Image:
    """Attach common metadata properties to an image."""
    base_props = {"index_name": index_name}
    base_props.update(props)
    return image.set(base_props)


def get_focal_buffered_geometry(
    focal_path: Any,
    buffer_m: float = 500,
) -> Tuple[ee.Geometry, ee.Geometry]:
    """
    Load the focal site geometry and return both the original and buffered geometry.

    Parameters
    ----------
    focal_path : str | Path
        Path to the focal site GeoJSON.
    buffer_m : float, default 500
        Buffer distance in meters.

    Returns
    -------
    tuple[ee.Geometry, ee.Geometry]
        (focal_geom, focal_buffer_geom)
    """
    focal_geom = geojson_to_ee_geometry(focal_path)
    focal_buffer_geom = focal_geom.buffer(buffer_m)
    return focal_geom, focal_buffer_geom


def build_window_mean_image(
    collection: ee.ImageCollection,
    index_name: str,
    start_date: str,
    end_date: str,
    clip_geom: Optional[ee.Geometry] = None,
) -> ee.Image:
    """
    Build a mean image for a single index over a date window.

    Parameters
    ----------
    collection : ee.ImageCollection
        Collection containing the requested index band.
    index_name : str
        Band name to summarize.
    start_date : str
        Inclusive start date, e.g. '2019-01-01'.
    end_date : str
        Exclusive end date, e.g. '2022-01-01' or a practical window end.
    clip_geom : ee.Geometry, optional
        Geometry to clip the output image.

    Returns
    -------
    ee.Image
    """
    window_col = collection.filterDate(start_date, end_date).select(index_name)
    image_count = window_col.size()

    mean_img = window_col.mean().rename(f"{index_name}_mean")
    mean_img = _set_image_properties(
        mean_img,
        index_name=index_name,
        start_date=start_date,
        end_date=end_date,
        summary_stat="mean",
        image_count=image_count,
    )

    return _clip_if_requested(mean_img, clip_geom)


def build_baseline_current_delta(
    collection: ee.ImageCollection,
    index_name: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
    clip_geom: Optional[ee.Geometry] = None,
) -> Tuple[ee.Image, ee.Image, ee.Image]:
    """
    Build baseline mean, current mean, and current-minus-baseline delta images.

    Returns
    -------
    tuple[ee.Image, ee.Image, ee.Image]
        (baseline_img, current_img, delta_img)
    """
    baseline_img = build_window_mean_image(
        collection=collection,
        index_name=index_name,
        start_date=baseline_start,
        end_date=baseline_end,
        clip_geom=clip_geom,
    ).rename(f"{index_name}_baseline_mean")

    current_img = build_window_mean_image(
        collection=collection,
        index_name=index_name,
        start_date=current_start,
        end_date=current_end,
        clip_geom=clip_geom,
    ).rename(f"{index_name}_current_mean")

    delta_img = current_img.subtract(baseline_img).rename(f"{index_name}_delta")
    delta_img = _set_image_properties(
        delta_img,
        index_name=index_name,
        baseline_start=baseline_start,
        baseline_end=baseline_end,
        current_start=current_start,
        current_end=current_end,
        summary_stat="current_minus_baseline",
    )

    delta_img = _clip_if_requested(delta_img, clip_geom)

    return baseline_img, current_img, delta_img


def build_annual_single_index_collection(
    collection: ee.ImageCollection,
    index_name: str,
    start_date: str,
    end_date: str,
    composite_stat: str = "median",
    clip_geom: Optional[ee.Geometry] = None,
) -> ee.ImageCollection:
    """
    Build annual composites for one index using the existing temporal workflow.

    Parameters
    ----------
    collection : ee.ImageCollection
        Input collection containing the requested index band.
    index_name : str
        Band name to composite.
    start_date : str
    end_date : str
    composite_stat : {'median', 'mean'}
    clip_geom : ee.Geometry, optional

    Returns
    -------
    ee.ImageCollection
    """
    annual_col = build_period_composites(
        collection=collection,
        bands=[index_name],
        start_date=start_date,
        end_date=end_date,
        temporal_scale="annual",
        composite_stat=composite_stat,
    )

    annual_col = _annual_collection_has_data(annual_col)

    if clip_geom is not None:
        annual_col = annual_col.map(lambda img: ee.Image(img).clip(clip_geom))

    return annual_col


def build_trend_slope_image(
    annual_collection: ee.ImageCollection,
    index_name: str,
    clip_geom: Optional[ee.Geometry] = None,
) -> ee.Image:
    """
    Build a per-pixel linear slope image from annual composites.

    Parameters
    ----------
    annual_collection : ee.ImageCollection
        Annual composite collection for a single index.
    index_name : str
        Band name to fit.
    clip_geom : ee.Geometry, optional

    Returns
    -------
    ee.Image
        A slope image named '<index_name>_slope_per_year'.
    """
    fit = (
        annual_collection.map(_add_year_band)
        .select(["year", index_name])
        .reduce(ee.Reducer.linearFit())
    )

    slope_img = fit.select("scale").rename(f"{index_name}_slope_per_year")
    slope_img = _set_image_properties(
        slope_img,
        index_name=index_name,
        summary_stat="linear_slope_per_year",
    )

    return _clip_if_requested(slope_img, clip_geom)


def build_reference_site_composite_stack(
    collection: ee.ImageCollection,
    reference_fc: ee.FeatureCollection,
    index_name: str,
    start_date: str,
    end_date: str,
    summary_stat: str = "mean",
) -> ee.ImageCollection:
    """
    Build one composite image per reference site for a given time window.

    Each output image is masked/clipped to its own reference geometry and retains
    site metadata properties.

    Parameters
    ----------
    collection : ee.ImageCollection
        Input collection containing the requested index band.
    reference_fc : ee.FeatureCollection
        Reference sites with site_id/site_name/site_category properties.
    index_name : str
        Band name to summarize.
    start_date : str
    end_date : str
    summary_stat : {'mean', 'median'}

    Returns
    -------
    ee.ImageCollection
    """
    reference_list = reference_fc.toList(reference_fc.size())

    def _site_img(i: ee.Number) -> ee.Image:
        feat = ee.Feature(reference_list.get(i))
        geom = feat.geometry()

        site_col = (
            collection.filterDate(start_date, end_date)
            .select(index_name)
            .filterBounds(geom)
        )

        site_img = (
            ee.Image(
                ee.Algorithms.If(
                    ee.String(summary_stat).compareTo("median").eq(0),
                    site_col.median(),
                    site_col.mean(),
                )
            )
            .rename(index_name)
            .clip(geom)
        )

        site_img = _set_image_properties(
            site_img,
            index_name=index_name,
            start_date=start_date,
            end_date=end_date,
            summary_stat=summary_stat,
            site_id=feat.get("site_id"),
            site_name=feat.get("site_name"),
            site_category=feat.get("site_category"),
            image_count=site_col.size(),
        )
        return site_img

    images = ee.List.sequence(0, reference_fc.size().subtract(1)).map(_site_img)
    return ee.ImageCollection.fromImages(images)


def build_reference_stats_images(
    reference_img_collection: ee.ImageCollection,
    index_name: str,
) -> Tuple[ee.Image, ee.Image]:
    """
    Build per-pixel reference mean and std-dev images from a reference composite stack.

    Parameters
    ----------
    reference_img_collection : ee.ImageCollection
        One image per reference site.
    index_name : str

    Returns
    -------
    tuple[ee.Image, ee.Image]
        (reference_mean, reference_std)
    """
    ref_mean = reference_img_collection.mean().rename(
        f"{index_name}_reference_mean"
    )

    ref_std = reference_img_collection.reduce(ee.Reducer.stdDev()).rename(
        f"{index_name}_reference_std"
    )

    ref_mean = _set_image_properties(
        ref_mean, index_name=index_name, summary_stat="reference_mean"
    )
    ref_std = _set_image_properties(
        ref_std, index_name=index_name, summary_stat="reference_std"
    )

    return ref_mean, ref_std


def build_reference_z_anomaly_image(
    focal_current_img: ee.Image,
    reference_mean_img: ee.Image,
    reference_std_img: ee.Image,
    index_name: str,
    clip_geom: Optional[ee.Geometry] = None,
) -> ee.Image:
    """
    Build a z-score anomaly image:
        (focal_current - reference_mean) / reference_std

    Parameters
    ----------
    focal_current_img : ee.Image
    reference_mean_img : ee.Image
    reference_std_img : ee.Image
    index_name : str
    clip_geom : ee.Geometry, optional

    Returns
    -------
    ee.Image
    """
    std_safe = _ensure_nonzero_std(reference_std_img)

    z_img = (
        focal_current_img.subtract(reference_mean_img)
        .divide(std_safe)
        .rename(f"{index_name}_z_anomaly")
    )

    z_img = _set_image_properties(
        z_img,
        index_name=index_name,
        summary_stat="z_anomaly",
    )

    return _clip_if_requested(z_img, clip_geom)


def build_reference_percentile_image(
    reference_img_collection: ee.ImageCollection,
    focal_current_img: ee.Image,
    index_name: str,
    clip_geom: Optional[ee.Geometry] = None,
) -> ee.Image:
    """
    Build a percentile-rank image comparing focal current values to reference-site values.

    For each pixel:
        percentile = 100 * (# reference images <= focal_current) / N_reference_images

    Parameters
    ----------
    reference_img_collection : ee.ImageCollection
        One image per reference site.
    focal_current_img : ee.Image
    index_name : str
    clip_geom : ee.Geometry, optional

    Returns
    -------
    ee.Image
    """
    n = ee.Number(reference_img_collection.size())

    le_count = reference_img_collection.map(
        lambda img: ee.Image(img).lte(focal_current_img).rename("le")
    ).sum()

    pct_img = (
        le_count.divide(n)
        .multiply(100)
        .rename(f"{index_name}_percentile_anomaly")
    )
    pct_img = _set_image_properties(
        pct_img,
        index_name=index_name,
        summary_stat="reference_percentile_rank",
    )

    return _clip_if_requested(pct_img, clip_geom)


def build_fire_dnbr_image(
    collection: ee.ImageCollection,
    pre_start: str,
    pre_end: str,
    post_start: str,
    post_end: str,
    clip_geom: Optional[ee.Geometry] = None,
    summary_stat: str = "median",
) -> Tuple[ee.Image, ee.Image, ee.Image]:
    """
    Build pre-fire NBR, post-fire NBR, and dNBR images.

    dNBR is computed as:
        pre_fire_nbr - post_fire_nbr

    Parameters
    ----------
    collection : ee.ImageCollection
        Input collection containing the NBR band.
    pre_start, pre_end, post_start, post_end : str
    clip_geom : ee.Geometry, optional
    summary_stat : {'median', 'mean'}

    Returns
    -------
    tuple[ee.Image, ee.Image, ee.Image]
        (pre_nbr, post_nbr, dnbr)
    """
    pre_col = collection.filterDate(pre_start, pre_end).select("NBR")
    post_col = collection.filterDate(post_start, post_end).select("NBR")

    pre_nbr = ee.Image(
        ee.Algorithms.If(
            ee.String(summary_stat).compareTo("mean").eq(0),
            pre_col.mean(),
            pre_col.median(),
        )
    ).rename("NBR_pre_fire")

    post_nbr = ee.Image(
        ee.Algorithms.If(
            ee.String(summary_stat).compareTo("mean").eq(0),
            post_col.mean(),
            post_col.median(),
        )
    ).rename("NBR_post_fire")

    dnbr = pre_nbr.subtract(post_nbr).rename("dNBR")

    pre_nbr = _set_image_properties(
        pre_nbr,
        index_name="NBR",
        start_date=pre_start,
        end_date=pre_end,
        summary_stat=f"pre_fire_{summary_stat}",
        image_count=pre_col.size(),
    )
    post_nbr = _set_image_properties(
        post_nbr,
        index_name="NBR",
        start_date=post_start,
        end_date=post_end,
        summary_stat=f"post_fire_{summary_stat}",
        image_count=post_col.size(),
    )
    dnbr = _set_image_properties(
        dnbr,
        index_name="NBR",
        pre_start=pre_start,
        pre_end=pre_end,
        post_start=post_start,
        post_end=post_end,
        summary_stat="dNBR",
    )

    pre_nbr = _clip_if_requested(pre_nbr, clip_geom)
    post_nbr = _clip_if_requested(post_nbr, clip_geom)
    dnbr = _clip_if_requested(dnbr, clip_geom)

    return pre_nbr, post_nbr, dnbr


def split_old_new_restoration_blocks(
    focal_blocks_path: Any,
) -> tuple[ee.FeatureCollection, ee.FeatureCollection]:
    """
    Split KS Rehab block features into old and new cohorts using the preserved
    per-feature year property.
    """
    blocks_fc = load_ks_rehab_blocks_featurecollection(
        focal_blocks_path,
        year_field="year",
        drop_null_year=True,
    )

    old_blocks_fc = blocks_fc.filter(ee.Filter.eq("restoration_cohort", "old"))
    new_blocks_fc = blocks_fc.filter(ee.Filter.eq("restoration_cohort", "new"))

    return old_blocks_fc, new_blocks_fc


def summarize_image_by_block_group(
    image: ee.Image,
    blocks_fc: ee.FeatureCollection,
    group_name: str,
    index_name: str,
    reducer: Optional[ee.Reducer] = None,
    scale: int = 10,
    max_pixels: float = 1e13,
    tile_scale: int = 4,
) -> Dict[str, Any]:
    """
    Summarize an image over a block group geometry.

    Parameters
    ----------
    image : ee.Image
    blocks_fc : ee.FeatureCollection
    group_name : str
    index_name : str
    reducer : ee.Reducer, optional
        Defaults to ee.Reducer.mean().
    scale : int, default 10
    max_pixels : float, default 1e13
    tile_scale : int, default 4

    Returns
    -------
    dict
        Dictionary with the group name, index name, band name, and reducer result object.
        Values are Earth Engine objects until evaluated with getInfo() downstream.
    """
    reducer = reducer or ee.Reducer.mean()
    band_name = ee.String(image.bandNames().get(0))

    stats = image.reduceRegion(
        reducer=reducer,
        geometry=blocks_fc.geometry(),
        scale=scale,
        maxPixels=max_pixels,
        tileScale=tile_scale,
    )

    return {
        "group_name": group_name,
        "index_name": index_name,
        "band_name": band_name,
        "stats": stats,
    }
