import ee
import json
from pathlib import Path

from tgbs_rs.config import AOI_PATHS


def _clip_and_mask_image(image, geometry):
    """
    Clip image to AOI and apply an explicit AOI mask while preserving
    the image's existing mask.
    """
    aoi_mask = ee.Image.constant(1).clip(geometry).mask()
    return image.updateMask(aoi_mask).clip(geometry)


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
        path=AOI_PATHS["ks_rehab"],
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

    return ee.FeatureCollection(
        [
            ks_rehab_feature,
            buda_feature,
            gogoni_feature,
            shimba_hills_feature,
            degraded_1_feature,
            degraded_2_feature,
        ]
    )


def get_sites_geometry(sites_fc):
    """
    Return the merged geometry of a site FeatureCollection.
    """
    return ee.FeatureCollection(sites_fc).geometry()
