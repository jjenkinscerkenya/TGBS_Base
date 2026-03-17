import ee


def calc_elevation(dem_collection):
    """
    Mosaic the DEM band from an ee.ImageCollection and rename it to ELEVATION.
    """
    dem_collection = ee.ImageCollection(dem_collection)

    projection = dem_collection.first().select("DEM").projection()

    dem = (
        dem_collection.select("DEM")
        .mosaic()
        .rename("ELEVATION")
        .setDefaultProjection(projection)
    )

    return dem


def calc_slope(dem_image):
    """Calculate slope in degrees from a DEM image."""
    return ee.Terrain.slope(ee.Image(dem_image)).rename("SLOPE")


def calc_aspect(dem_image):
    """Calculate aspect from a DEM image."""
    return ee.Terrain.aspect(ee.Image(dem_image)).rename("ASPECT")


def calc_hillshade(dem_image):
    """Calculate hillshade from a DEM image."""
    return ee.Terrain.hillshade(ee.Image(dem_image)).rename("HILLSHADE")


def calc_terrain(dem_collection):
    """
    Build a terrain stack from a DEM ImageCollection.
    """
    elev = calc_elevation(dem_collection)
    slope = calc_slope(elev)
    aspect = calc_aspect(elev)
    hillshade = calc_hillshade(elev)

    return elev.addBands([slope, aspect, hillshade])
