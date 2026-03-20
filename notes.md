## References

Tolan, J., Yang, H.I., Nosarzewski, B., Couairon, G., Vo, H.V., Brandt, J., Spore, J., Majumdar, S., Haziza, D., Vamaraju, J. and Moutakanni, T.,
2024. Very high resolution canopy height maps from RGB imagery using self-supervised vision transformer and convolutional decoder trained on aerial
lidar. Remote Sensing of Environment, 300, p.113888.

Hansen, M. C., P. V. Potapov, R. Moore, M. Hancher, S. A. Turubanova, A. Tyukavina, D. Thau, S. V. Stehman, S. J. Goetz, T. R. Loveland, A. Kommareddy, A. Egorov, L. Chini, C. O. Justice, and J. R. G. Townshend. 2013. "High-Resolution Global Maps of 21st-Century Forest Cover Change." Science 342 (15 November): 850-53. 10.1126/science.1244693 Data available on-line at: https://glad.earthengine.app/view/global-forest-change.

Brown, C.F., Brumby, S.P., Guzder-Williams, B. et al. Dynamic World, Near real-time global 10 m land use land cover mapping. Sci Data 9, 251 (2022). doi:10.1038/s41597-022-01307-4

Hengl, T., Miller, M.A.E., Križan, J., et al. African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Sci Rep 11, 6130 (2021). doi:10.1038/s41598-021-85639-y

Clements, H.S., Biggs, R., De Vos, A. et al. A place-based assessment of biodiversity intactness in sub-Saharan Africa.
Nature (2025). https://doi.org/10.1038/s41586-025-09781-7

## Development Notes

1. Site model completion
Add at least one degraded site and make site_category formally constrained to focal | reference | degraded. This is foundational for every later comparison step. TGBS explicitly expects all three site types in the remote sensing survey design.

2. Comparison layer
Add a new module centered on grouped comparisons, something like comparisons.py, with functions for:
focal vs reference envelopes
focal vs degraded envelopes
reference baseline ranges
site-category grouped summaries
standardized baseline-to-current deltas
This is where the repo becomes explicitly TGBS-oriented rather than just a general EO workflow.

3. Temporal products layer
Your monthly composites are a good core product, but TGBS interpretation will benefit from additional derived summaries:
baseline period summaries
current period summaries
annual dry-season summaries
annual wet-season summaries
trend statistics per site
TGBS stresses distinguishing real ecological trajectories from normal seasonal variation, especially through interpretation relative to reference-site temporal patterns.

4. Spatial change layer
Add explicit raster outputs for:
baseline mean
current mean
current minus baseline
trend slope
z-score or percentile anomaly relative to reference behavior
This will satisfy the TGBS requirement for spatial analysis and heat maps of where change is strongest.

5. Interpretation and limitations layer
Add a reporting schema or markdown generator that records:
indicator type
ecological interpretation
whether it is direct or indirect
spatial/spectral/temporal resolution considerations
seasonal caveats
known limitations for the site
TGBS explicitly requires these limitations to be identified and considered before assessment conclusions are made.

6. Audit package layer
Create a reproducible export bundle for each analytical component:
source AOIs
parameter settings
sensor used
date ranges
exported tables
exported rasters
figure-ready summaries
processing notes
Section 4 says the remote sensing survey must generate a report for assessors and support comparison with field results.



Sentinel-2 SR vs Landsat-8
For TGBS reporting, I would document the workflow like this:
Core long-term optical archive: Landsat 8 C2 L2 SR (2013–2017) + Sentinel-2 SR Harmonized (2017–present)
Common analytical support: 30 m, matched seasonal windows, matched site categories
Cross-sensor harmonization step: overlap-year regression / bias analysis per metric
Metric eligibility table: “fully comparable,” “proxy comparable,” or “Sentinel-era only”
Audit note: trend breaks attributable to sensor transition explicitly tested and documented