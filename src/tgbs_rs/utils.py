import ee
import json
from pathlib import Path

from tgbs_rs.config.config import AOI_PATHS


def _clip_and_mask_image(image, geometry):
    """
    Clip image to AOI and apply an explicit AOI mask while preserving
    the image's existing mask.
    """
    aoi_mask = ee.Image.constant(1).clip(geometry).mask()
    return image.updateMask(aoi_mask).clip(geometry)


def clip_collection_to_aoi(
    collection: ee.ImageCollection,
    aoi: ee.Geometry,
) -> ee.ImageCollection:
    """
    Clip every image in an ImageCollection to a single AOI geometry.

    This is useful when filtering by AOI is not enough and you want each
    output raster trimmed to the exact site boundary.
    """
    aoi = ee.Geometry(aoi)
    return ee.ImageCollection(collection).map(
        lambda img: ee.Image(img).clip(aoi)
    )


def geojson_to_ee_geometry(path) -> ee.Geometry:
    """Read a local GeoJSON file and return its contents as a single ee.Geometry."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        geojson = json.load(f)

    if geojson["type"] == "FeatureCollection":
        features = geojson.get("features", [])
        if not features:
            raise ValueError("GeoJSON FeatureCollection contains no features.")
        geometries = [ee.Geometry(feature["geometry"]) for feature in features]
        return ee.FeatureCollection(
            [ee.Feature(g) for g in geometries]
        ).geometry()

    if geojson["type"] == "Feature":
        return ee.Geometry(geojson["geometry"])

    return ee.Geometry(geojson)


def build_site_feature(
    geometry, site_id, site_name, site_category, source_file=None
):
    """
    Build an ee.Feature from an ee.Geometry and standard site metadata.
    """
    properties = {
        "site_id": site_id,
        "site_name": site_name,
        "site_category": site_category,
    }

    if source_file is not None:
        properties["source_file"] = source_file

    return ee.Feature(geometry, properties)


def load_site_feature(path, site_id, site_name, site_category):
    """
    Load a local GeoJSON boundary file and convert it to a metadata-rich ee.Feature.
    """
    path = Path(path).resolve()
    geometry = geojson_to_ee_geometry(path)

    return build_site_feature(
        geometry=geometry,
        site_id=site_id,
        site_name=site_name,
        site_category=site_category,
        source_file=path.name,
    )


def build_default_sites_featurecollection():
    """
    Build the standard TGBS site FeatureCollection from the current repo AOI files.
    """
    ks_rehab_feature = load_site_feature(
        path=AOI_PATHS["ks_rehab_blocks"],
        site_id="ks_rehab",
        site_name="KS Rehab",
        site_category="focal",
    )

    buda_feature = load_site_feature(
        path=AOI_PATHS["buda"],
        site_id="buda",
        site_name="Buda",
        site_category="reference",
    )

    gogoni_feature = load_site_feature(
        path=AOI_PATHS["gogoni"],
        site_id="gogoni",
        site_name="Gogoni",
        site_category="reference",
    )

    shimba_hills_feature = load_site_feature(
        path=AOI_PATHS["shimba_hills"],
        site_id="shimba_hills",
        site_name="Shimba Hills",
        site_category="reference",
    )

    degraded_1_feature = load_site_feature(
        path=AOI_PATHS["degraded_1"],
        site_id="degraded_1",
        site_name="degraded_1",
        site_category="degraded",
    )

    degraded_2_feature = load_site_feature(
        path=AOI_PATHS["degraded_2"],
        site_id="degraded_2",
        site_name="degraded_2",
        site_category="degraded",
    )

    degraded_3_feature = load_site_feature(
        path=AOI_PATHS["degraded_3"],
        site_id="degraded_3",
        site_name="degraded_3",
        site_category="degraded",
    )

    return ee.FeatureCollection(
        [
            ks_rehab_feature,
            buda_feature,
            gogoni_feature,
            shimba_hills_feature,
            degraded_1_feature,
            degraded_2_feature,
            degraded_3_feature,
        ]
    )


def load_ks_rehab_blocks_featurecollection(
    geojson_path: str | Path,
    id_field: str = "id",
    area_field: str = "area",
    year_field: str = "year",
    drop_null_year: bool = True,
    drop_null_geometry: bool = True,
) -> ee.FeatureCollection:
    """
    Load ks_rehab_blocks.geojson as an ee.FeatureCollection while preserving
    original per-feature properties such as id, area, and year.

    This loader is intended specifically for block-level analyses where the
    original GeoJSON features must remain separate. It also handles null id/year
    values safely.

    Returns
    -------
    ee.FeatureCollection
        FeatureCollection with one feature per GeoJSON feature and preserved
        properties.

    """
    path = Path(geojson_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        gj = json.load(f)

    if gj.get("type") != "FeatureCollection":
        raise ValueError(
            f"Expected a GeoJSON FeatureCollection, got: {gj.get('type')}"
        )

    ee_features = []

    for i, feat in enumerate(gj.get("features", [])):
        geometry = feat.get("geometry")
        properties = feat.get("properties", {}) or {}

        if geometry is None:
            if drop_null_geometry:
                continue
            else:
                raise ValueError(f"Feature index {i} has null geometry.")

        # Pull original properties safely
        raw_id = properties.get(id_field, None)
        raw_area = properties.get(area_field, None)
        raw_year = properties.get(year_field, None)

        # Skip null-year features if requested
        if drop_null_year and raw_year is None:
            continue

        # Build a clean property dict that preserves originals and adds helpers
        clean_props = dict(properties)

        # Explicit normalized helper fields
        clean_props["block_id"] = raw_id
        clean_props["block_area"] = raw_area
        clean_props["block_year"] = raw_year

        # Convenience cohort field for later filtering
        if raw_year is None:
            clean_props["restoration_cohort"] = None
        elif raw_year <= 2020:
            clean_props["restoration_cohort"] = "old"
        elif raw_year >= 2022:
            clean_props["restoration_cohort"] = "new"
        else:
            clean_props["restoration_cohort"] = "other"

        ee_feat = ee.Feature(geometry, clean_props)
        ee_features.append(ee_feat)

    if not ee_features:
        raise ValueError(
            "No valid features were loaded. Check whether all features had null "
            "geometry or null year values that were dropped."
        )

    return ee.FeatureCollection(ee_features)


def get_sites_geometry(sites_fc):
    """
    Return the merged geometry of a site FeatureCollection.
    """
    return ee.FeatureCollection(sites_fc).geometry()


def buffer_sites_fc(
    sites_fc: ee.FeatureCollection,
    buffer_m: float = 500,
) -> ee.FeatureCollection:
    """Return a site FeatureCollection with each feature buffered by a fixed distance.

    Buffers every site geometry by `buffer_m` meters while preserving the
    original site properties for later naming, export, and grouping.
    """
    sites_fc = ee.FeatureCollection(sites_fc)
    return sites_fc.map(
        lambda f: ee.Feature(ee.Feature(f).buffer(buffer_m)).copyProperties(
            ee.Feature(f)
        )
    )


def get_image_min_max(
    image,
    geometry,
    scale=10,
    band_name=None,
    max_pixels=1e13,
    tile_scale=4,
):
    """
    Print the min and max of an ee.Image band within a geometry.
    Returns a dictionary with band_name, min, and max.
    """
    if hasattr(geometry, "geometry"):
        geometry = geometry.geometry()

    if band_name is None:
        band_name = image.bandNames().get(0).getInfo()

    stats = (
        image.select([band_name])
        .reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=geometry,
            scale=scale,
            maxPixels=max_pixels,
            tileScale=tile_scale,
        )
        .getInfo()
    )

    min_val = stats.get(f"{band_name}_min")
    max_val = stats.get(f"{band_name}_max")

    print(f"{band_name} min: {min_val}")
    print(f"{band_name} max: {max_val}")

    return {
        "band_name": band_name,
        "min": min_val,
        "max": max_val,
    }
