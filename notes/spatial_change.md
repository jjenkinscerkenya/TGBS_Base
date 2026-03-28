# Spatial change layer and heatmap production

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Analysis goal
Design and implement a `spatial_change.ipynb` that creates explicit raster outputs for:
- baseline mean
- current mean
- current minus baseline
- trend slope
- z-score anomaly relative to reference behavior
- percentile anomaly relative to reference behavior

Prioritized indices:
- `NBR`
- `NDMI`
- `NDVI`
- `NIRv`
- `SAVI`

These outputs should satisfy TGBS spatial comparison and heatmap requirements.

## Required implementation direction
The design should focus on compact Earth Engine functions that:
1. build baseline and current summary images
2. compute delta images
3. compute trend slope images
4. compute focal anomalies relative to reference behavior
5. remain compatible with export workflows

Assume HLS is the official long-term 30 m trend source.

## Important design constraints
- Reuse existing collection builders rather than rebuilding sensor preprocessing
- Keep the outputs easy to export as GeoTIFFs
- Use compact, modular function design
- Prioritize the highest-impact first products
- Keep the implementation auditable and ecologically interpretable

## Requested output
Please provide:
1. a concrete implementation plan for `spatial_change.ipynb`
2. the recommended function list and signatures
3. code or pseudo-code for:
   - baseline mean image
   - current mean image
   - delta image
   - trend slope image
   - reference z-score anomaly image
   - reference percentile anomaly image
4. guidance on how to derive reference-relative statistics from multiple reference sites
5. the recommended first raster products to generate for contract reporting
6. existing raster exporting functions will be used to export raster images to Google Drive for map production

Use the existing repo structure and function names exactly where relevant.

## Additional Add-Ons
For fire, Earth Engine has the ingredients for NBR/dNBR workflows and also hosts burned-area and burn-severity datasets such as MTBS and global burned-area products in the data catalog. If another dataset would add value to 
the repository please suggest it. 