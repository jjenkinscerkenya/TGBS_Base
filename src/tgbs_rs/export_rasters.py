import ee


def export_image_to_drive(
    image: ee.Image,
    aoi: ee.Geometry,
    description: str,
    folder: str,
    file_prefix: str,
    scale: int,
    crs: str = "EPSG:4326",
):
    """
    Export an Earth Engine image to Google Drive with proper nodata handling.
    """

    no_data_value = -9999
    image = image.unmask(no_data_value)

    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=folder,
        fileNamePrefix=file_prefix,
        region=aoi,
        scale=scale,
        crs=crs,
        maxPixels=1e13,
        formatOptions={"noData": no_data_value},
    )

    task.start()
    return task


def build_baseline_export_config(scale_dict):
    """
    Build export metadata for the baseline layers dictionary.
    """
    return {
        "dem": {
            "description": "DEM",
            "prefix": "dem",
            "scale": scale_dict["dem"],
        },
        "slope": {
            "description": "Slope",
            "prefix": "slope",
            "scale": scale_dict["slope"],
        },
        "hillshade": {
            "description": "Hillshade",
            "prefix": "hillshade",
            "scale": scale_dict["hillshade"],
        },
        "canopy_height": {
            "description": "Canopy_Height",
            "prefix": "canopy_height",
            "scale": scale_dict["canopy_height"],
        },
        "land_cover": {
            "description": "Land_Cover",
            "prefix": "land_cover",
            "scale": scale_dict["land_cover"],
        },
        "soil_carbon": {
            "description": "Soil_Carbon",
            "prefix": "soil_carbon",
            "scale": scale_dict["soil_carbon"],
        },
        "bii_all": {
            "description": "BII_All",
            "prefix": "bii_all",
            "scale": scale_dict["bii_all"],
        },
        "forest_2000": {
            "description": "Forest_2000",
            "prefix": "forest_2000",
            "scale": scale_dict["forest_2000"],
        },
        "forest_loss": {
            "description": "Forest_Loss",
            "prefix": "forest_loss",
            "scale": scale_dict["forest_loss"],
        },
    }


def export_named_layer_to_drive(
    layers: dict,
    aoi: ee.Geometry,
    layer_name: str,
    folder: str,
    scale_dict: dict,
    crs: str = "EPSG:4326",
):
    """
    Export a single named layer from the layers dictionary.
    """
    export_config = build_baseline_export_config(scale_dict)

    if layer_name not in layers:
        raise KeyError(f"Layer '{layer_name}' not found in layers dictionary.")

    if layer_name not in export_config:
        raise KeyError(f"Layer '{layer_name}' not found in export config.")

    cfg = export_config[layer_name]

    task = export_image_to_drive(
        image=layers[layer_name],
        aoi=aoi,
        description=cfg["description"],
        folder=folder,
        file_prefix=cfg["prefix"],
        scale=cfg["scale"],
        crs=crs,
    )

    return task


def export_selected_layers_to_drive(
    layers: dict,
    aoi: ee.Geometry,
    layer_names: list,
    folder: str,
    scale_dict: dict,
    crs: str = "EPSG:4326",
):
    """
    Export a selected list of layer names from the layers dictionary.

    Returns
    -------
    dict
        Dictionary of {layer_name: ee.batch.Task}
    """
    tasks = {}

    for layer_name in layer_names:
        print(f"Starting export for layer: {layer_name}")
        task = export_named_layer_to_drive(
            layers=layers,
            aoi=aoi,
            layer_name=layer_name,
            folder=folder,
            scale_dict=scale_dict,
            crs=crs,
        )
        tasks[layer_name] = task

    return tasks


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
