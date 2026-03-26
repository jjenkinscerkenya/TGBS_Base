############# Visualization parameters #########################
SITES_VIS_PARAMS = {
    "color": "#FF0000",
    "width": 2,
    "lineType": "solid",
    "fillColor": "#FF00006F",
}

# Sentinel-2 SR
S2_VIS_PARAMS = {
    "TrueColor": {
        "bands": ["B4", "B3", "B2"],
        "min": 0.02,
        "max": 0.35,
        "gamma": 1.2,
    },
    "NDVI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#0000FF",  # water / very low
            "#FFFFFF",  # bare / neutral
            "#CE7E45",
            "#DF923D",
            "#F1B555",
            "#FCD163",
            "#99B718",
            "#74A901",
            "#66A000",
            "#529400",
            "#3E8601",
            "#207401",
            "#056201",
            "#004C00",  # dense vegetation
        ],
    },
    "EVI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#000080",
            "#0000FF",
            "#FFFFFF",
            "#FDE725",
            "#5DC863",
            "#21918C",
            "#3B528B",
            "#004C00",
        ],
    },
    "NDWI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#8B4513",  # dry / non-water
            "#F5F5F5",
            "#B0E0E6",
            "#87CEFA",
            "#1E90FF",
            "#0000FF",  # strong water
        ],
    },
    "MNDWI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#654321",
            "#D2B48C",
            "#F7F7F7",
            "#BFEFFF",
            "#4DA6FF",
            "#0033CC",
        ],
    },
    "SAVI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#440154",
            "#3B528B",
            "#21918C",
            "#5DC863",
            "#FDE725",
            "#FFFFCC",
            "#006400",
        ],
    },
    "NDMI": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#A52A2A",  # dry
            "#F5DEB3",
            "#FFFFBF",
            "#C7E9B4",
            "#7FCDBB",
            "#41B6C4",
            "#225EA8",  # moist
        ],
    },
    "NBR": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#0000FF",
            "#FFFFFF",
            "#FFFFB2",
            "#FECC5C",
            "#FD8D3C",
            "#E31A1C",
            "#800026",
        ],
    },
    "NIRv": {
        "min": 0.0,
        "max": 0.5,
        "palette": [
            "#F7FCF5",
            "#E5F5E0",
            "#C7E9C0",
            "#A1D99B",
            "#74C476",
            "#41AB5D",
            "#238B45",
            "#005A32",
        ],
    },
    "NDRE": {
        "min": -1.0,
        "max": 1.0,
        "palette": [
            "#542788",
            "#998EC3",
            "#F7F7F7",
            "#F1A340",
            "#D73027",
            "#7F0000",
            "#004C00",
        ],
    },
}

# Landsat-8 OLI
L8_VIS_PARAMS = {
    "TrueColor": {
        "bands": ["SR_B4", "SR_B3", "SR_B2"],
        "min": 0.0,
        "max": 0.3,
        "gamma": 1.2,
    },
}

# HLS
HLS_VIS_PARAMS = {
    "TrueColor": {
        "bands": ["RED", "GREEN", "BLUE"],
        "min": 0.02,
        "max": 0.35,
        "gamma": 1.2,
    },
}

DW_BINARY_VIS_PARAMS = {
    "min": 0,
    "max": 1,
    "palette": ["#F57C00", "#2E7D32"],  # 0 = Non-Woody LC  # 1 = Woody LC
}

BASELINE_VIS_PARAMS = {
    # Forest Cover
    "FOREST_COVER_VIS": {
        "min": 0,
        "max": 100,
        "palette": ["#000000", "#1F951F"],
    },
    "FOREST_LOSS_VIS": {
        "min": 0,
        "max": 1,
        "palette": ["#ffffff", "#ff0000"],
    },
    "LOSS_YEAR_VIS": {
        "min": 0,
        "max": 24,
        "palette": [
            "#ffffcc",
            "#ffeda0",
            "#fed976",
            "#feb24c",
            "#fd8d3c",
            "#fc4e2a",
            "#e31a1c",
            "#bd0026",
            "#800026",
        ],
    },
    # Tree Canopy
    "CANOPY_VIS": {
        "min": 0,
        "max": 15,
        "palette": [
            "#440154",
            "#482775",
            "#3E4A89",
            "#31688E",
            "#26828E",
            "#1F9E89",
            "#67C165",
            "#B8D73D",
            "#FDE623",
        ],
    },
    # Elevation
    "DEM_VIS": {
        "min": 0,
        "max": 800,
        "palette": ["#334e68", "#7b9e87", "#b7b7a4", "#d4a373", "#f1faee"],
    },
    # Slope
    "SLOPE_VIS": {
        "min": 0,
        "max": 45,
        "palette": [
            "#071424",
            "#14324f",
            "#4fa3c4",
            "#fdae61",
            "#d94801",
        ],
    },
    # Hillshade
    "HILLSHADE_VIS": {"min": 0, "max": 255, "palette": ["#000000", "#ffffff"]},
    # Soil Carbon
    "SOIL_CARBON_VIS": {
        "min": 0,
        "max": 40,
        "palette": [
            "#fff7ec",
            "#fee8c8",
            "#fdd49e",
            "#fdbb84",
            "#e34a33",
            "#7f0000",
        ],
    },
    # Biodiversity Intactness Index
    "BII_VIS": {
        "min": 0,
        "max": 1,
        "palette": ["#d73027", "#fee08b", "#d9ef8b", "#1a9850"],
    },
    # ESA WorldCover
    "ESA_WORLDCOVER_VIS": {
        "min": 10,
        "max": 100,
        "palette": [
            "#006400",  # 10 Tree cover
            "#ffbb22",  # 20 Shrubland
            "#ffff4c",  # 30 Grassland
            "#f096ff",  # 40 Cropland
            "#fa0000",  # 50 Built-up
            "#b4b4b4",  # 60 Bare/sparse vegetation
            "#f0f0f0",  # 70 Snow and ice
            "#0064c8",  # 80 Permanent water bodies
            "#0096a0",  # 90 Herbaceous wetland
            "#00cf75",  # 95 Mangroves
            "#fae6a0",  # 100 Moss and lichen
        ],
    },
    # KS Rehab Point
    "KS_REHAB_POINT_VIS": {
        "facecolor": "#FF0000",  # red
        "edgecolor": "#000000",  # black
        "linewidth": 0.5,
        "markersize": 6,
    },
}
