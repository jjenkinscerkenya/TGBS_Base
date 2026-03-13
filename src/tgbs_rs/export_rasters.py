import ee


def export_image_to_drive(
    image: ee.Image,
    aoi: ee.Geometry,
    description: str,
    folder: str,
    file_prefix: str,
    scale=10,
    crs=None,
):
    """Export an ee.Image prediction layer to Google Drive as a GeoTIFF."""
    task = ee.batch.Export.image.toDrive(
        image=image.clip(aoi),
        description=description,
        folder=folder,
        fileNamePrefix=file_prefix,
        region=aoi,
        scale=scale,
        crs=crs,
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    task.start()
    print("Export started:", task.status())


def export_image_to_asset(
    image: ee.Image,
    aoi: ee.Geometry,
    asset_id: str,
    description: str,
    scale=10,
    crs=None,
):
    """Export an image to an Earth Engine asset."""
    task = ee.batch.Export.image.toAsset(
        image=image,
        description=description,
        assetId=asset_id,
        region=aoi,
        scale=scale,
        maxPixels=1e13,
        crs=crs,
    )
    task.start()
    print("Export started:", task.status())
