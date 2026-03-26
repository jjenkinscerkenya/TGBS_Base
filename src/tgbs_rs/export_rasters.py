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


def _image_export_suffix(
    image: ee.Image,
    index: int,
    date_property: str = "date",
    fallback_property: str = "year",
) -> str:
    """Build a compact suffix for one image export.

    Prefers an existing image property such as `date` or `year`. If neither
    is present, falls back to the zero-padded collection index.
    """
    props = image.toDictionary([date_property, fallback_property]).getInfo()
    if props.get(date_property) is not None:
        return str(props[date_property]).replace(":", "-")
    if props.get(fallback_property) is not None:
        return str(props[fallback_property])
    return f"{index:03d}"


def export_image_collection_to_drive(
    collection: ee.ImageCollection,
    aoi: ee.Geometry,
    folder: str,
    file_prefix: str,
    scale: int,
    crs: str = "EPSG:4326",
    band_names: list[str] | None = None,
    sort_property: str = "system:time_start",
    description_prefix: str | None = None,
    date_property: str | None = None,
    fallback_property: str = "year",
    file_suffix: str | None = None,
) -> list:
    """Export every image in an ImageCollection to Google Drive.

    Sorts the collection, optionally selects specific bands, then launches one
    Drive export task per image using a property-based filename suffix.
    """
    collection = ee.ImageCollection(collection).sort(sort_property)
    if band_names is not None:
        collection = collection.select(band_names)

    n = collection.size().getInfo()
    images = collection.toList(n)
    tasks = []

    for i in range(n):
        image = ee.Image(images.get(i))

        props_to_get = (
            [fallback_property]
            if date_property is None
            else [date_property, fallback_property]
        )
        props = image.toDictionary(props_to_get).getInfo()

        if date_property is not None and props.get(date_property) is not None:
            suffix = str(props[date_property]).replace(":", "-")
        elif props.get(fallback_property) is not None:
            suffix = str(props[fallback_property])
        else:
            suffix = f"{i:03d}"

        description = f"{description_prefix or file_prefix}_{suffix}"
        prefix = (
            f"{file_prefix}_{suffix}"
            if file_suffix is None
            else f"{file_prefix}_{suffix}_{file_suffix}"
        )

        task = export_image_to_drive(
            image=image,
            aoi=aoi,
            description=description,
            folder=folder,
            file_prefix=prefix,
            scale=scale,
            crs=crs,
        )
        tasks.append(task)

    return tasks


def export_site_collections_to_drive(
    site_collections: dict[str, dict],
    folder: str,
    scale: int,
    crs: str = "EPSG:4326",
    band_names: list[str] | None = None,
    sort_property: str = "system:time_start",
    date_property: str = "date",
    fallback_property: str = "year",
    file_suffix: str = "dw_woody_cover",
) -> dict[str, list]:
    """
    Export one ImageCollection per site from a site dictionary to Google Drive.

    Expects a dictionary like `site_dw_dict` where each entry contains at least
    `aoi` and `collection`. Returns a dictionary of export task lists keyed by site_id.
    """
    tasks_by_site = {}

    for site_id, site_info in site_collections.items():
        tasks_by_site[site_id] = export_image_collection_to_drive(
            collection=site_info["collection"],
            aoi=site_info["aoi"],
            folder=folder,
            file_prefix=site_id,
            scale=scale,
            crs=crs,
            band_names=band_names,
            sort_property=sort_property,
            description_prefix=f"{site_id}_{file_suffix}",
            date_property=date_property,
            fallback_property=fallback_property,
            file_suffix=file_suffix,
        )

    return tasks_by_site


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


def export_table_to_drive(
    collection: ee.FeatureCollection,
    description: str,
    folder: str,
    fileNamePrefix: str,
    fileFormat: str = "CSV",
):
    """Export an Earth Engine image to Google Drive"""
    task = ee.batch.Export.table.toDrive(
        collection=collection,
        description=description,
        folder=folder,
        fileNamePrefix=fileNamePrefix,
        fileFormat="CSV",
    )
    task.start()
    print("Export started:", task.status())


def check_ee_task_status(task_id):
    """
    Query an Earth Engine batch task by ID and return its current status.
    Prints state, progress, and error message (if any).
    """
    tasks = ee.batch.Task.list()

    for task in tasks:
        if task.id == task_id:
            status = task.status()
            print("Task ID:", task_id)
            print("State:", status.get("state"))
            print("Description:", status.get("description"))
            print("Progress:", status.get("progress", "N/A"))
            print("Error Message:", status.get("error_message", "None"))
            return status

    print("Task ID not found.")
    return None
