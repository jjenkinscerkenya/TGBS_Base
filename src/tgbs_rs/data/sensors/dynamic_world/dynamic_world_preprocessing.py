import ee

from tgbs_rs.config.config import DYNAMIC_WORLD, DW_WOODY_BANDS
from tgbs_rs.metrics import build_period_composites


def add_dw_woody_bands(image: ee.Image) -> ee.Image:
    """Add compact woody probability bands to one Dynamic World image.

    Returns the original image plus `trees_prob` and `woody_prob`
    (`trees + shrub_and_scrub`) for later temporal compositing.
    """
    trees = image.select("trees").rename("trees_prob")
    woody = (
        image.select("trees")
        .add(image.select("shrub_and_scrub"))
        .rename("woody_prob")
    )
    return image.addBands([trees, woody]).copyProperties(
        image, ["system:time_start"]
    )


def get_dw_collection(
    aoi: ee.Geometry,
    start_date: str | ee.Date,
    end_date: str | ee.Date,
) -> ee.ImageCollection:
    """Build a Dynamic World collection with woody probability bands.

    Filters Dynamic World by AOI and date, then adds per-image woody
    probability bands needed for annual or monthly compositing.
    """
    return (
        ee.ImageCollection(DYNAMIC_WORLD)
        .filterBounds(aoi)
        .filterDate(ee.Date(start_date), ee.Date(end_date))
        .map(add_dw_woody_bands)
    )


def threshold_dw_woody_band(
    image: ee.Image,
    aoi: ee.Geometry,
    woody_threshold: float = 0.5,
    trees_threshold: float = 0.5,
    include_shrub: bool = True,
) -> ee.Image:
    """Return one masked binary woody-cover band for export."""
    aoi = ee.Geometry(aoi)

    prob = image.select("woody_prob" if include_shrub else "trees_prob")
    threshold = woody_threshold if include_shrub else trees_threshold
    out_band = "woody_cover" if include_shrub else "trees_cover"

    aoi_mask = ee.Image.constant(1).clip(aoi).mask()

    cover = (
        prob.gte(threshold)
        .rename(out_band)
        .toInt16()
        .updateMask(prob.mask())
        .updateMask(aoi_mask)
        .copyProperties(image, image.propertyNames())
    )

    return cover


def build_annual_dw_woody_cover_collection(
    aoi: ee.Geometry,
    start_date: str | ee.Date,
    end_date: str | ee.Date,
    composite_stat: str = "median",
    woody_threshold: float = 0.5,
    trees_threshold: float = 0.5,
    include_shrub: bool = True,
) -> ee.ImageCollection:
    """Return annual masked binary woody-cover rasters."""
    aoi = ee.Geometry(aoi)

    dw = get_dw_collection(aoi=aoi, start_date=start_date, end_date=end_date)

    annual_probs = build_period_composites(
        collection=dw,
        bands=DW_WOODY_BANDS,
        start_date=start_date,
        end_date=end_date,
        temporal_scale="annual",
        composite_stat=composite_stat,
    )

    annual_cover = annual_probs.map(
        lambda img: threshold_dw_woody_band(
            image=ee.Image(img),
            aoi=aoi,
            woody_threshold=woody_threshold,
            trees_threshold=trees_threshold,
            include_shrub=include_shrub,
        )
    )

    return annual_cover.set(
        {
            "source": "GOOGLE/DYNAMICWORLD/V1",
            "start_date": ee.Date(start_date).format("YYYY-MM-dd"),
            "end_date": ee.Date(end_date).format("YYYY-MM-dd"),
            "composite_stat": composite_stat,
            "include_shrub": include_shrub,
            "woody_threshold": woody_threshold,
            "trees_threshold": trees_threshold,
        }
    )
