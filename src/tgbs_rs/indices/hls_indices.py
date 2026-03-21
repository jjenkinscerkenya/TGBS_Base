import ee


# Vegetation indices
def calc_ndvi(image: ee.Image):
    """Calculate NDVI as a standard proxy for green vegetation vigor and cover."""
    return image.normalizedDifference(["NIR", "RED"]).rename("NDVI")


def calc_evi(image: ee.Image):
    """Calculate EVI for improved vegetation sensitivity in higher biomass and variable soil backgrounds."""
    return image.expression(
        "2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))",
        {
            "nir": image.select("NIR"),
            "red": image.select("RED"),
            "blue": image.select("BLUE"),
        },
    ).rename("EVI")


def calc_savi(image: ee.Image, L=0.5):
    """Calculate SAVI to reduce soil background effects in sparsely vegetated landscapes."""
    return image.expression(
        "((nir - red) / (nir + red + L)) * (1 + L)",
        {"nir": image.select("NIR"), "red": image.select("RED"), "L": L},
    ).rename("SAVI")


# Water/moisture indices
def calc_ndwi(image: ee.Image):
    """Calculate NDWI to highlight surface water and vegetation water-related contrast."""
    return image.normalizedDifference(["GREEN", "NIR"]).rename("NDWI")


def calc_mndwi(image: ee.Image):
    """Calculate MNDWI using green and SWIR1 to enhance open-water detection against land surfaces."""
    return image.normalizedDifference(["GREEN", "SWIR1"]).rename("MNDWI")


def calc_ndmi(image: ee.Image):
    """Calculate NDMI as a moisture-sensitive index for vegetation and surface dryness assessment."""
    return image.normalizedDifference(["NIR", "SWIR1"]).rename("NDMI")


# Disturbance / biomass proxy indices
def calc_nbr(image: ee.Image):
    """Calculate NBR for burn severity and broader disturbance screening."""
    return image.normalizedDifference(["NIR", "SWIR2"]).rename("NBR")


def calc_nirv(image: ee.Image):
    """Calculate NIRv as a vegetation productivity proxy combining NIR reflectance and NDVI."""
    return image.select("NIR").multiply(calc_ndvi(image)).rename("NIRv")


# Multi-index helpers
def calc_veg_indices(image: ee.Image):
    """Add the original vegetation and water indices discussed for the baseline HLS workflow."""
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
    """Add the full TGBS-oriented HLS index set for vegetation, moisture, disturbance, and biomass-proxy analysis."""
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
        ]
    )


def select_base_hls_bands(image: ee.Image):
    """Select the core shared HLS reflectance bands used to derive the merged cross-sensor indices."""
    return image.select(["BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2"])
