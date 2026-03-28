# Spatial Change Output Interpretation Guide

This document summarizes the key Sentinel-2 spatial change outputs for the KS Rehab focal-site workflow. These rasters are intended to support field targeting, interpretation of restoration response, and identification of fire- and moisture-related change within the focal site and its 500 m buffered context.

## Temporal windows used in this workflow

Unless otherwise noted, the standard focal-site change rasters use the following windows:

- **Baseline window:** 2019-01-01 to 2021-12-31
- **Current window:** 2023-01-01 to 2025-12-31

For these outputs, the workflow first builds a summary image for the baseline window and a summary image for the current window, then compares them. In most cases, the summary is a mean image derived from the Sentinel-2 index collection for that window.

The fire-specific product uses a separate pair of windows:

- **Pre-fire window:** 2024-07-01 to 2024-12-31
- **Post-fire window:** 2025-01-01 to 2025-06-30

## General guidance for interpreting these rasters

These are **spatial change products**, not site-level averages. Each pixel shows how local conditions changed through time or how current focal-site conditions compare to reference behavior.

In general:

- Positive values usually indicate improvement for vegetation- or productivity-related indices.
- Negative values usually indicate decline, disturbance, drying, or lagging recovery.
- For disturbance metrics such as NBR and dNBR, interpretation depends on whether the raster is a delta, slope, or fire-specific change layer.

All rasters should be interpreted together with:
- restoration block timing (older vs newer restoration blocks)
- the known January 2025 fire event
- site context from field observations

---

## NBR_delta

**What it measures**

`NBR_delta` is the difference between:

- **current mean NBR** for 2023-01-01 to 2025-12-31
- minus **baseline mean NBR** for 2019-01-01 to 2021-12-31

So each pixel answers:

> How has NBR changed between the earlier restoration-context period and the more recent period?

**What NBR represents**

NBR (Normalized Burn Ratio) uses the near-infrared and shortwave infrared bands and is sensitive to disturbance, burn effects, and broader vegetation structure and biomass condition.

**How to interpret the image**

- **Positive NBR_delta**
  - suggests improved vegetation condition, greater biomass, or reduced disturbance relative to the baseline window
  - may indicate restoration-linked recovery in blocks under active restoration

- **Negative NBR_delta**
  - suggests increased disturbance, fire impact, reduced biomass, or declining vegetation condition
  - may help highlight the fire-affected block or other degraded patches

**How to use it**

This is one of the strongest first-pass heatmaps for locating where the focal site has improved or declined since the earlier period.

---

## NBR_slope_per_year

**What it measures**

`NBR_slope_per_year` is the per-pixel linear trend in annual NBR through the Sentinel-2 analysis period. It is derived from annual composites built across the broader workflow period, then fit with a linear regression through time.

So each pixel answers:

> Is NBR generally increasing or decreasing over time, and how fast?

**How to interpret the image**

- **Positive slope**
  - indicates a long-term upward trend in NBR
  - suggests progressive recovery, reduced disturbance, or improving vegetation condition

- **Negative slope**
  - indicates a long-term downward trend in NBR
  - suggests recurring disturbance, fire effects, or worsening vegetation condition

- **Near-zero slope**
  - indicates relative stability through the Sentinel period

**How to use it**

This image is useful for distinguishing **persistent directional change** from one-off differences between two summary windows. It is especially helpful where a pixel may have improved gradually over several years or declined steadily before or after restoration.

---

## dNBR

**What it measures**

`dNBR` is the difference between:

- **pre-fire NBR** for 2024-07-01 to 2024-12-31
- minus **post-fire NBR** for 2025-01-01 to 2025-06-30

So each pixel answers:

> How much did vegetation condition change immediately across the fire period?

**What dNBR is for**

dNBR is a standard fire-change metric used to detect burn impact and post-fire severity patterns.

**How to interpret the image**

- **High positive dNBR**
  - strong drop in NBR from pre-fire to post-fire
  - indicates likely fire impact or strong burn severity

- **Low or near-zero dNBR**
  - little change across the fire window
  - suggests the area was likely unaffected or only weakly affected

- **Negative dNBR**
  - post-fire NBR exceeds pre-fire NBR
  - may reflect rapid regrowth, noise, cloud-window differences, or areas not actually affected by fire

**How to use it**

This is the main fire-event raster. It should be used to confirm the spatial footprint and relative intensity of the January 2025 fire and to guide field visits to the most affected blocks.

---

## NDMI_delta

**What it measures**

`NDMI_delta` is:

- **current mean NDMI** for 2023-01-01 to 2025-12-31
- minus **baseline mean NDMI** for 2019-01-01 to 2021-12-31

So each pixel answers:

> Has vegetation or surface moisture status improved or declined between the baseline and current windows?

**What NDMI represents**

NDMI (Normalized Difference Moisture Index) is sensitive to vegetation moisture and drying stress.

**How to interpret the image**

- **Positive NDMI_delta**
  - suggests increased moisture status, denser or healthier vegetation, or reduced stress
  - may indicate improving vegetation structure in restored blocks

- **Negative NDMI_delta**
  - suggests drying, stress, or lower vegetation moisture
  - may highlight degraded zones, fire-affected areas, or weak restoration response

**How to use it**

This is a strong complementary layer to NBR. It helps distinguish whether changes are associated with moisture stress, drying, or improved canopy condition.

---

## NIRv_delta

**What it measures**

`NIRv_delta` is:

- **current mean NIRv** for 2023-01-01 to 2025-12-31
- minus **baseline mean NIRv** for 2019-01-01 to 2021-12-31

So each pixel answers:

> Has vegetation productivity increased or decreased since the earlier period?

**What NIRv represents**

NIRv (Near-Infrared Reflectance of Vegetation) is a productivity proxy and often tracks vegetation activity more directly than simpler greenness indices.

**How to interpret the image**

- **Positive NIRv_delta**
  - suggests increased vegetation productivity
  - may indicate successful restoration response, especially in older restoration blocks

- **Negative NIRv_delta**
  - suggests lower productivity or reduced vegetation function
  - may indicate disturbance, stress, or fire effects

**How to use it**

This is one of the most important restoration-response layers. It is especially useful for identifying where vegetation function appears to be strengthening through time.

---

## NDVI_delta

**What it measures**

`NDVI_delta` is:

- **current mean NDVI** for 2023-01-01 to 2025-12-31
- minus **baseline mean NDVI** for 2019-01-01 to 2021-12-31

So each pixel answers:

> Has greenness or vegetation cover increased or decreased between the baseline and current windows?

**What NDVI represents**

NDVI is a standard vegetation greenness and cover index.

**How to interpret the image**

- **Positive NDVI_delta**
  - suggests increased greenness or vegetation cover
  - may indicate restoration gains or denser plant cover

- **Negative NDVI_delta**
  - suggests reduced greenness, vegetation loss, or disturbance
  - may highlight degraded or recently burned areas

**How to use it**

NDVI is an easy-to-interpret supporting layer that helps communicate vegetation change clearly, even though it may be less sensitive than some other indices in sparse or complex dryland conditions.

---

## SAVI_delta

**What it measures**

`SAVI_delta` is:

- **current mean SAVI** for 2023-01-01 to 2025-12-31
- minus **baseline mean SAVI** for 2019-01-01 to 2021-12-31

So each pixel answers:

> Has vegetation cover changed when soil-background effects are partially accounted for?

**What SAVI represents**

SAVI (Soil-Adjusted Vegetation Index) is similar to NDVI but is designed to reduce soil-background influence. This is especially useful in more open or sparsely vegetated systems.

**How to interpret the image**

- **Positive SAVI_delta**
  - suggests increased vegetation cover or vigor, adjusted for soil brightness effects
  - often supports interpretation of recovery in drier or more open patches

- **Negative SAVI_delta**
  - suggests reduced vegetation cover, increased bare ground influence, or disturbance

**How to use it**

SAVI is a useful supporting comparison to NDVI. Where NDVI and SAVI both show positive change, confidence in vegetation-cover recovery is stronger.

---

## NBR_z_anomaly

**What it measures**

`NBR_z_anomaly` compares the focal-site **current mean NBR** image to **reference-site current behavior** using:

> (focal current NBR - reference mean NBR) / reference standard deviation

The focal image is from **2023-01-01 to 2025-12-31**, and the reference mean/std are derived from reference-site composites over that same current window.

So each pixel answers:

> How far above or below reference behavior is the focal site, in units of reference variability?

**How to interpret the image**

- **Positive z-score**
  - focal pixel is above the reference mean
  - for NBR, this may suggest better vegetation condition or lower disturbance than reference behavior

- **Negative z-score**
  - focal pixel is below the reference mean
  - may indicate remaining degradation, disturbance, or fire effects relative to reference behavior

- **Magnitude matters**
  - around `0`: close to reference mean
  - around `+/-1`: about one standard deviation from the reference mean
  - larger magnitudes: stronger anomaly relative to reference behavior

**How to use it**

This raster is best used as a **reference-relative interpretation layer**, not as a simple change-through-time layer. It helps identify where the focal site is still lagging or exceeding the ecological behavior seen in the reference sites during the current period.

---

## NDMI_z_anomaly

**What it measures**

`NDMI_z_anomaly` compares focal-site **current mean NDMI** to reference-site current behavior for the same current window:

- **Current focal/reference window:** 2023-01-01 to 2025-12-31

Formula:

> (focal current NDMI - reference mean NDMI) / reference standard deviation

**How to interpret the image**

- **Positive z-score**
  - focal pixel is wetter or less moisture-stressed than the reference mean

- **Negative z-score**
  - focal pixel is drier or more moisture-stressed than the reference mean

- **Larger absolute values**
  - stronger departure from reference behavior

**How to use it**

This raster highlights where the focal site is currently moisture-limited relative to reference behavior, which is useful for identifying stressed blocks or patches where restoration may still be lagging.

---

## NIRv_z_anomaly

**What it measures**

`NIRv_z_anomaly` compares focal-site **current mean NIRv** to reference-site current behavior for the same current window:

- **Current focal/reference window:** 2023-01-01 to 2025-12-31

Formula:

> (focal current NIRv - reference mean NIRv) / reference standard deviation

**How to interpret the image**

- **Positive z-score**
  - focal pixel is more productive than the reference mean

- **Negative z-score**
  - focal pixel is less productive than the reference mean
  - may identify blocks still lagging in functional recovery

- **Large positive or negative magnitude**
  - strong departure from reference behavior

**How to use it**

This is one of the strongest reference-relative recovery layers. It helps show where current focal-site productivity is approaching, exceeding, or still falling short of the behavior seen in the reference sites.

---

## Final interpretation advice

These rasters are most informative when interpreted together rather than one at a time.

A practical reading sequence is:

1. **dNBR** to isolate fire-affected areas
2. **NBR_delta** and **NBR_slope_per_year** to assess broader disturbance/recovery patterns
3. **NDMI_delta** to assess moisture-related change
4. **NIRv_delta** to assess productivity response
5. **NDVI_delta** and **SAVI_delta** to assess vegetation cover response
6. **z-anomaly rasters** to compare current focal conditions to reference behavior

In general:

- Areas with **positive NIRv_delta**, **positive NDVI/SAVI delta**, and **positive or near-neutral NBR trends** are consistent with recovery.
- Areas with **high dNBR**, **negative NBR_delta**, and **negative NDMI_delta** are consistent with recent disturbance and moisture stress.
- Areas with **negative z-anomalies** indicate places where the focal site still lags reference behavior during the current period.

Because these are spatial heatmaps, they should be used to support field targeting: identify which blocks or within-block patches deserve closer inspection during field visits.
