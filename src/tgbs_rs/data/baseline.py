import ee

from tgbs_rs.config.config import (
    BII_1KM,
    BII_MASK,
    ESA,
    CANOPY,
    ISDA,
    DEM,
    BII_BANDS,
    BII_MAIN_BAND,
    ESA_MAP_BAND,
    ISDA_TOPSOIL_MEAN_BAND,
    GL_FOREST_CHANGE,
    ESA_CLASS_VALUES,
)
from tgbs_rs.data.topography import calc_terrain
from tgbs_rs.utils import _clip_and_mask_image


# Global Forest Change
def get_forest_2000(aoi: ee.Geometry):
    """
    Return a clipped image of tree canopy cover for year 2000.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest_2000 = gfc.select("treecover2000")
    return _clip_and_mask_image(forest_2000, aoi)


def get_forest_loss_image(aoi: ee.Geometry, tree_cover_threshold=10):
    """
    Return a clipped binary forest loss image for the provided AOI.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest2000 = gfc.select("treecover2000").gte(tree_cover_threshold)
    loss = gfc.select("loss")

    forest_loss = forest2000.And(loss).rename("forest_loss")

    return _clip_and_mask_image(forest_loss, aoi)


def get_forest_loss_year_image(aoi: ee.Geometry, tree_cover_threshold=10):
    """
    Return a clipped forest loss year image for the provided AOI.
    """
    gfc = ee.Image(GL_FOREST_CHANGE)

    forest2000 = gfc.select("treecover2000").gte(tree_cover_threshold)
    lossyear = gfc.select("lossyear").updateMask(forest2000).rename("lossyear")

    return _clip_and_mask_image(lossyear, aoi)


# BII


def load_bii_image():
    """
    Load the BII stack and rename bands using BII_BANDS.

    Assumes the asset is an ImageCollection that should be converted to bands.
    """
    bii_ic = ee.ImageCollection(BII_1KM)
    bii_img = bii_ic.toBands().rename(BII_BANDS)
    return bii_img


def process_bii_image():
    """
    Process BII into:
    - BII bands only (self-masked)
    - Land Use
    - Land Use Intensity masked to non-target classes
    - BII mask applied
    """
    bii_img = load_bii_image()

    bii_mask = ee.Image(BII_MASK)
    bii_bands = bii_img.select("^BII.*").selfMask()

    lc_mask = (
        bii_img.select("Land Use").neq(2).And(bii_img.select("Land Use").neq(5))
    )

    lui = bii_img.select("Land Use Intensity").updateMask(lc_mask)

    processed = (
        bii_bands.addBands(bii_img.select("Land Use"))
        .addBands(lui.rename("Land Use Intensity"))
        .updateMask(bii_mask)
    )

    return processed


def get_bii_all(aoi):
    """Return the processed BII All band clipped to AOI."""
    bii = process_bii_image().select(BII_MAIN_BAND)
    return _clip_and_mask_image(bii, aoi).rename("BII_All")


# ESA WorldCover


def get_esa_landcover(aoi):
    """
    Return the raw ESA WorldCover categorical Map band clipped to AOI.
    """
    esa_img = ee.ImageCollection(ESA).first().select(ESA_MAP_BAND)
    return _clip_and_mask_image(esa_img, aoi).rename("Land_Cover")


# Canopy Height


def get_canopy_height(aoi):
    """
    Return the canopy height mosaic clipped to AOI with an explicit AOI mask.
    """
    canopy = ee.ImageCollection(CANOPY).mosaic().rename("Canopy_Height")
    return _clip_and_mask_image(canopy, aoi)


# iSDA Total Soil Carbon


def load_isda_image():
    """
    Load the iSDA total soil carbon image.
    """
    return ee.Image(ISDA)


def get_isda_topsoil_mean(aoi):
    """
    Return the configured iSDA topsoil mean carbon band clipped to AOI.
    """
    soil = (
        load_isda_image().select(ISDA_TOPSOIL_MEAN_BAND).rename("Soil_Carbon")
    )
    return _clip_and_mask_image(soil, aoi)


# DEM / Terrain


def load_dem_collection():
    """Load the Copernicus GLO30 DEM ImageCollection."""
    return ee.ImageCollection(DEM)


def get_terrain_layers(aoi):
    """
    Build terrain layers from the DEM collection and clip to AOI.

    Returns a multiband ee.Image with:
    - ELEVATION
    - SLOPE
    - ASPECT
    - HILLSHADE
    """
    dem_ic = load_dem_collection()
    terrain = calc_terrain(dem_ic)
    return _clip_and_mask_image(terrain, aoi)


def get_dem(aoi):
    """Return DEM clipped to AOI."""
    return get_terrain_layers(aoi).select("ELEVATION").rename("DEM")


def get_slope(aoi):
    """Return slope clipped to AOI."""
    return get_terrain_layers(aoi).select("SLOPE")


def get_hillshade(aoi):
    """Return hillshade clipped to AOI."""
    return get_terrain_layers(aoi).select("HILLSHADE")


# Baseline orchestration


def build_baseline_layers(aoi):
    """
    Build all requested baseline layers and return them as a dictionary of ee.Images.
    """
    terrain = get_terrain_layers(aoi)

    layers = {
        "dem": terrain.select("ELEVATION").rename("DEM"),
        "slope": terrain.select("SLOPE"),
        "hillshade": terrain.select("HILLSHADE"),
        "canopy_height": get_canopy_height(aoi),
        "land_cover": get_esa_landcover(aoi),
        "soil_carbon": get_isda_topsoil_mean(aoi),
        "bii_all": get_bii_all(aoi),
        "forest_2000": get_forest_2000(aoi),
        "forest_loss": get_forest_loss_image(aoi),
    }

    return layers


def build_continuous_baseline_stack(layers_dict):
    """
    Combine continuous baseline layers into a single multiband image.
    """
    return ee.Image.cat(
        [
            layers_dict["dem"].rename("DEM"),
            layers_dict["slope"].rename("SLOPE"),
            layers_dict["hillshade"].rename("HILLSHADE"),
            layers_dict["canopy_height"].rename("CANOPY_HEIGHT"),
            layers_dict["soil_carbon"].rename("SOIL_CARBON"),
            layers_dict["bii_all"].rename("BII_ALL"),
        ]
    )


def build_continuous_reducer():
    """
    Build a combined reducer for continuous raster summaries.
    """
    reducer = ee.Reducer.mean()
    reducer = reducer.combine(reducer2=ee.Reducer.median(), sharedInputs=True)
    reducer = reducer.combine(reducer2=ee.Reducer.min(), sharedInputs=True)
    reducer = reducer.combine(reducer2=ee.Reducer.max(), sharedInputs=True)
    reducer = reducer.combine(reducer2=ee.Reducer.stdDev(), sharedInputs=True)
    return reducer


def summarize_continuous_baseline_layers(
    sites_fc,
    baseline_layers,
    scale=30,
    crs="EPSG:4326",
    tile_scale=4,
):
    """
    Reduce continuous baseline layers over each site polygon.
    """
    image = build_continuous_baseline_stack(baseline_layers)
    reducer = build_continuous_reducer()

    return image.reduceRegions(
        collection=sites_fc,
        reducer=reducer,
        scale=scale,
        crs=crs,
        tileScale=tile_scale,
    )


def build_esa_class_map():
    """
    Build a dict of export-friendly ESA class names to integer class values.
    """
    clean_names = [
        "tree_cover",
        "shrubland",
        "grassland",
        "cropland",
        "built_up",
        "bare_sparse_vegetation",
        "snow_ice",
        "permanent_water_bodies",
        "herbaceous_wetland",
        "mangroves",
        "moss_lichen",
    ]

    return dict(zip(clean_names, ESA_CLASS_VALUES))


def summarize_landcover_classes(
    sites_fc,
    land_cover_img,
    class_map,
    scale=10,
    crs="EPSG:4326",
    tile_scale=4,
):
    """
    Summarize ESA land-cover class areas by site.

    Parameters
    ----------
    sites_fc : ee.FeatureCollection
        Site polygons with site metadata.
    land_cover_img : ee.Image
        ESA land-cover image.
    class_map : dict
        Example:
        {
            "tree_cover": 10,
            "shrubland": 20,
            ...
        }
    """
    class_area_bands = []

    # Use the first band of the ESA image explicitly.
    lc_band = land_cover_img.select(0).unmask(-9999)

    for class_name, class_value in class_map.items():
        class_area = (
            ee.Image.pixelArea()
            .multiply(lc_band.eq(class_value))
            .rename(f"lc_{class_name}_area_m2")
        )
        class_area_bands.append(class_area)

    area_stack = ee.Image.cat(class_area_bands)

    return area_stack.reduceRegions(
        collection=sites_fc,
        reducer=ee.Reducer.sum(),
        scale=scale,
        crs=crs,
        tileScale=tile_scale,
    )


def merge_site_summaries(
    sites_fc,
    continuous_fc,
    landcover_fc,
):
    """
    Merge continuous and land-cover summary properties back onto one feature per site.
    """

    def merge_one_site(site):
        site_id = site.get("site_id")

        continuous_feat = ee.Feature(
            continuous_fc.filter(ee.Filter.eq("site_id", site_id)).first()
        )

        landcover_feat = ee.Feature(
            landcover_fc.filter(ee.Filter.eq("site_id", site_id)).first()
        )

        # Copy summary properties onto the original site feature.
        merged = ee.Feature(site)

        merged = merged.copyProperties(continuous_feat)
        merged = merged.copyProperties(landcover_feat)

        return merged

    return ee.FeatureCollection(sites_fc.map(merge_one_site))


def summarize_baseline_layers_by_site(
    sites_fc,
    scale_continuous=30,
    scale_landcover=10,
    crs="EPSG:4326",
    tile_scale=4,
):
    """
    Summarize baseline layers by site and return one feature per site.
    """
    all_sites_geom = sites_fc.geometry()
    baseline_layers = build_baseline_layers(all_sites_geom)

    # Drop unwanted layers after building the dictionary.
    baseline_layers.pop("forest_2000", None)
    baseline_layers.pop("forest_loss", None)

    esa_class_map = build_esa_class_map()

    continuous_fc = summarize_continuous_baseline_layers(
        sites_fc=sites_fc,
        baseline_layers=baseline_layers,
        scale=scale_continuous,
        crs=crs,
        tile_scale=tile_scale,
    )

    landcover_fc = summarize_landcover_classes(
        sites_fc=sites_fc,
        land_cover_img=baseline_layers["land_cover"],
        class_map=esa_class_map,
        scale=scale_landcover,
        crs=crs,
        tile_scale=tile_scale,
    )

    merged_fc = merge_site_summaries(
        sites_fc=sites_fc,
        continuous_fc=continuous_fc,
        landcover_fc=landcover_fc,
    )

    return merged_fc
