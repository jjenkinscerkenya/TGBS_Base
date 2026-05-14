import ee


# Vegetation indices
def calc_ndvi(image: ee.Image):
    """Calculate NDVI as a standard proxy for green vegetation vigor and cover."""
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")


def calc_evi(image: ee.Image):
    """Calculate EVI for improved vegetation sensitivity in higher biomass and variable soil backgrounds."""
    return image.expression(
        "2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))",
        {
            "nir": image.select("B8"),
            "red": image.select("B4"),
            "blue": image.select("B2"),
        },
    ).rename("EVI")


def calc_savi(image: ee.Image, L=0.5):
    """Calculate SAVI to reduce soil background effects in sparsely vegetated landscapes."""
    return image.expression(
        "((nir - red) / (nir + red + L)) * (1 + L)",
        {"nir": image.select("B8"), "red": image.select("B4"), "L": L},
    ).rename("SAVI")


# Water/moisture indices
def calc_ndwi(image: ee.Image):
    """Calculate NDWI to highlight surface water and vegetation water-related contrast."""
    return image.normalizedDifference(["B3", "B8"]).rename("NDWI")


def calc_mndwi(image: ee.Image):
    """Calculate MNDWI using green and SWIR1 to enhance open-water detection against land surfaces."""
    return image.normalizedDifference(["B3", "B11"]).rename("MNDWI")


def calc_ndmi(image: ee.Image):
    """Calculate NDMI as a moisture-sensitive index for vegetation and surface dryness assessment."""
    return image.normalizedDifference(["B8", "B11"]).rename("NDMI")


# Disturbance / biomass proxy indices
def calc_nbr(image: ee.Image):
    """Calculate NBR for burn severity and broader disturbance screening."""
    return image.normalizedDifference(["B8", "B12"]).rename("NBR")


def calc_nirv(image: ee.Image):
    """Calculate NIRv as a vegetation productivity proxy combining NIR reflectance and NDVI."""
    return image.select("B8").multiply(calc_ndvi(image)).rename("NIRv")


def calc_ndre(image: ee.Image):
    """Calculate NDRE as a red-edge vegetation condition proxy sensitive to canopy chlorophyll and biomass variation."""
    return image.normalizedDifference(["B8A", "B5"]).rename("NDRE")


# Multi-index helpers
def calc_veg_indices(image: ee.Image):
    """Add the original vegetation and water indices discussed for the baseline Sentinel-2 workflow."""
    return image.addBands(
        [
            calc_ndvi(image),
            calc_evi(image),
            calc_ndwi(image),
            calc_mndwi(image),
            calc_savi(image),
        ]
    )


def calc_tgbs_indices(image: ee.Image):
    """Add the full TGBS-oriented Sentinel-2 index set for vegetation, moisture, disturbance, and biomass-proxy analysis."""
    return image.addBands(
        [
            calc_ndvi(image),
            calc_evi(image),
            calc_ndwi(image),
            calc_mndwi(image),
            calc_savi(image),
            calc_ndmi(image),
            calc_nbr(image),
            calc_nirv(image),
            calc_ndre(image),
        ]
    )


def select_base_s2_bands(image: ee.Image):
    """Select the core Sentinel-2 reflectance bands commonly used to derive the project indices."""
    return image.select(
        ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
    )
