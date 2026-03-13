import json
from pathlib import Path
import ee


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
