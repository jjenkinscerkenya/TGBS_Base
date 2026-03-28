## References

Masek, J., Ju, J., Roger, J., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., Justice, C. (2021). HLS Operational Land Imager Surface Reflectance and TOA Brightness Daily Global 30m v2.0 [Data set]. NASA EOSDIS Land Processes Distributed Active Archive Center. Accessed 2023-09-12 from https://doi.org/10.5067/HLS/HLSL30.002

Tolan, J., Yang, H.I., Nosarzewski, B., Couairon, G., Vo, H.V., Brandt, J., Spore, J., Majumdar, S., Haziza, D., Vamaraju, J. and Moutakanni, T.,
2024. Very high resolution canopy height maps from RGB imagery using self-supervised vision transformer and convolutional decoder trained on aerial
lidar. Remote Sensing of Environment, 300, p.113888.

Hansen, M. C., P. V. Potapov, R. Moore, M. Hancher, S. A. Turubanova, A. Tyukavina, D. Thau, S. V. Stehman, S. J. Goetz, T. R. Loveland, A. Kommareddy, A. Egorov, L. Chini, C. O. Justice, and J. R. G. Townshend. 2013. "High-Resolution Global Maps of 21st-Century Forest Cover Change." Science 342 (15 November): 850-53. 10.1126/science.1244693 Data available on-line at: https://glad.earthengine.app/view/global-forest-change.

Brown, C.F., Brumby, S.P., Guzder-Williams, B. et al. Dynamic World, Near real-time global 10 m land use land cover mapping. Sci Data 9, 251 (2022). doi:10.1038/s41597-022-01307-4

Hengl, T., Miller, M.A.E., Križan, J., et al. African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Sci Rep 11, 6130 (2021). doi:10.1038/s41598-021-85639-y

Clements, H.S., Biggs, R., De Vos, A. et al. A place-based assessment of biodiversity intactness in sub-Saharan Africa.
Nature (2025). https://doi.org/10.1038/s41586-025-09781-7

## Handling Seasonal Tables
Seasonal information summary for documentation

Seasonal index information was derived from the cleaned monthly composite site tables rather than being computed directly as a single seasonal Earth Engine product. For each sensor, monthly composites were first generated and reduced over all focal, reference, and degraded site polygons. The monthly site tables were then standardized locally in pandas, expanded to a complete site–year–month panel, and labeled according to the project’s seasonal definitions: wet season (March–May) and dry season (July–October). This approach made missing months explicit, preserved auditability, and allowed seasonal summaries to be calculated using transparent quality-control rules.

For each site and year, wet- and dry-season productivity metrics were computed from the monthly values of the core indices. Seasonal values were only retained when a minimum number of valid monthly observations were available, ensuring that sparse months did not produce misleading seasonal summaries. The resulting seasonal tables include both the seasonal metric values and support information such as expected months, observed months, missing months, and valid-month counts.

These seasonal products will be used to distinguish interannual ecological change from normal seasonal variation. In particular, they support focal-versus-reference and focal-versus-degraded seasonal comparisons, help assess whether the focal site is moving toward or away from intact seasonal behavior, and provide an auditable basis for interpreting disturbance and recovery dynamics.


# Landscape Metrics Calculations
The shimba_hills 2022 site-year raster was excluded from the primary landscape-metrics analysis because valid pixel coverage was approximately 55%, substantially lower than the other site-years, which were near complete coverage. This level of masking was considered likely to distort patch configuration and fragmentation metrics by introducing artificial gaps and patch breaks, so the site-year was omitted under the study’s raster quality-control rule.

AI (Aggregation Index) measures how spatially clumped or aggregated patches of the same class are. Higher AI means cells of the same class are more often adjacent to one another, so the class is forming more continuous, consolidated areas rather than being broken into scattered pieces. In ecological terms, increasing AI often suggests stronger structural cohesion or connectivity within a class, while decreasing AI suggests that the class is becoming more dispersed or fragmented across the landscape.

ED (Edge Density) measures the amount of edge between patches per unit area of landscape. Higher ED means there is more boundary length relative to the total area, which usually indicates a more fragmented, irregular, or patchy landscape. A rise in ED often reflects increasing subdivision of cover types or more complex patch shapes, while lower ED generally indicates smoother, larger, and less fragmented patch structure.

LPI (Largest Patch Index) measures how dominant the single largest patch is relative to the total landscape area. A high LPI means one patch occupies a large share of the landscape, indicating strong dominance by a particular cover patch or class. If LPI increases through time, it often means one patch is expanding or consolidating; if it decreases, dominance is weakening and the landscape may be becoming more subdivided.

NP (Number Of Patches) measures the total count of distinct patches in the landscape or within a class. Higher NP usually indicates greater subdivision of the landscape into separate pieces, which is often associated with fragmentation, though it can also reflect increasing heterogeneity depending on context. Lower NP suggests fewer, larger, or more merged patches.

PD (Patch Density) measures the number of patches standardized by landscape area, making it easier to compare sites of different sizes. Like NP, higher PD usually reflects a more patchy or fragmented structure, but because it is area-adjusted it is often more comparable across site-years than raw patch counts alone. Increasing PD suggests a landscape is being broken into more separate units per area, while decreasing PD suggests patch consolidation.

SHDI (Shannon Diversity Index) measures compositional diversity by accounting for both the number of classes present and how evenly area is distributed among them. Higher SHDI means the landscape contains a richer and more even mixture of classes, while lower SHDI means the landscape is dominated by fewer classes or by one overwhelmingly dominant class. It is a composition metric rather than a configuration metric, so it says more about class diversity than patch arrangement.

CA (Class Area) measures the total area occupied by a given class. It tells you how much of the landscape that class covers in absolute terms, which makes it useful for tracking expansion or contraction of specific cover types over time. Changes in CA show whether a class is gaining or losing area, but by itself it does not describe whether that area is continuous or fragmented.

PLAND (Percent Of Landscape) measures the proportion of the total landscape occupied by a given class, expressed as a percentage. It is the relative version of class area, so it is especially useful for comparing class dominance across sites or years even when total mapped area differs slightly. Increasing PLAND means a class is taking up more of the landscape share; decreasing PLAND means it is losing relative dominance.

For class-level NP, the metric measures how many separate patches exist for one specific class. A high class-level NP means that class is broken into many distinct pieces, while a lower value means the class occurs in fewer pieces. Interpreting change in this metric helps show whether a particular class is becoming more fragmented or more consolidated.

For class-level PD, the metric measures how densely patches of one class occur per unit area. It is similar to class-level NP but standardized, so it is more comparable across landscapes. Higher class-level PD indicates a class is distributed among many separate patches relative to area, while lower values suggest fewer, larger, or more merged occurrences of that class.

For class-level ED, the metric measures the amount of edge associated with a specific class per unit area. Higher values indicate that the class has more boundary relative to landscape area, often meaning it occurs in more fragmented or irregularly shaped patches. Lower values generally indicate that the class occurs in larger, smoother, or less subdivided forms.

For class-level LPI, the metric measures how much of the landscape is occupied by the single largest patch of that specific class. A high value means one patch of that class is especially dominant, while a low value means the class is spread among smaller patches without one strongly dominant patch. This is useful for distinguishing whether increases in class area come from one major block or from many smaller pieces.


### Summary of Landscape Metrics Results:
AI (Aggregation Index). AI is highest and most stable at buda and shimba_hills, showing that those landscapes have the most spatially consolidated patch structure, with cells of the same class occurring in strongly clumped blocks. Gogoni is somewhat lower but still relatively aggregated. The degraded sites, especially degraded_3, have the lowest AI, indicating more broken and spatially dispersed patterning. Ks_rehab also trends downward, but with the mining context this should be interpreted differently: rather than simply worsening fragmentation, the decline in AI after 2021 likely reflects the site shifting from active mining surfaces into a more heterogeneous rehabilitation mosaic, where recovering woody patches and disturbed ground are interspersed.

ED (Edge Density). Edge density is lowest at buda and shimba_hills, which is consistent with smoother, less fragmented patch boundaries and a more cohesive woody landscape. Gogoni is intermediate, while all three degraded sites have much higher ED, especially degraded_3, indicating far more fragmented and edge-rich structure. Ks_rehab also shows elevated and increasing ED, but in this case the increase after the mining period is plausibly explained by rehabilitation creating many new boundaries between recovering vegetation, bare ground, and residual disturbed surfaces. So for ks_rehab, higher ED likely reflects early-stage landscape reorganization rather than just ecological decline.

LPI (Largest Patch Index). LPI is high at buda, gogoni, and shimba_hills, indicating that one dominant patch occupies a large share of each landscape, which is characteristic of more intact or consolidated woody cover. The degraded sites generally have lower LPI, meaning no single patch dominates as strongly and the landscape is more subdivided. Ks_rehab starts with relatively high LPI and then declines, which in light of the mine history likely reflects the breakup of one dominant landscape state—whether disturbed surface or remnant intact block—into a more mixed recovering pattern during rehabilitation.

NP (Number Of Patches). Absolute patch count is highest at shimba_hills, but because that site is larger, NP alone is less comparable there. Among the other sites, buda tends to have fewer patches, consistent with a simpler and more consolidated structure, while the degraded sites and ks_rehab often show higher patch counts. In the degraded sites this supports fragmentation. At ks_rehab, increasing NP after 2021 fits the expectation for a rehabilitating mine, where recovery often begins as scattered or uneven vegetation patches before coalescing into larger continuous cover.

PD (Patch Density). Patch density reinforces the fragmentation pattern while standardizing for area. It is lowest at buda and shimba_hills, moderate at gogoni, and highest at the degraded sites, especially degraded_2 and degraded_3, indicating much more patchy and subdivided landscapes. Ks_rehab is also relatively patch-dense and becomes more so over time, but with the rehabilitation context this is more consistent with early recovery dynamics: patchy revegetation and increasing structural complexity, not yet a return to a mature, contiguous woody landscape.

SHDI (Shannon Diversity Index). SHDI is lowest at buda and often also low at shimba_hills, showing that one class strongly dominates those landscapes. The degraded sites and ks_rehab tend to have higher SHDI, meaning woody and non-woody classes are more evenly represented. For the degraded sites, that higher diversity likely reflects reduced woody dominance and a more mixed, fragmented condition. For ks_rehab, high SHDI is especially consistent with a transitional rehabilitation phase in which woody cover, bare substrate, and recovering ground are all present in a shifting mosaic.

CA (Class Area). For class = 1, which appears to represent woody cover, class area is greatest and most stable at buda, gogoni, and shimba_hills, indicating strong persistence of woody cover. The degraded sites have lower woody area overall, especially where structural fragmentation is also high. Ks_rehab shows a notable decline in woody class area through time, which is consistent with the site’s disturbance history and indicates that by 2025 rehabilitation had not yet restored woody cover to the extent seen at the more reference-like sites.

PLAND (Percent Of Landscape). Woody PLAND is highest at buda, gogoni, and shimba_hills, where woody cover occupies a large majority of the landscape and remains dominant through time. The degraded sites have lower woody PLAND, especially degraded_2, indicating weaker woody dominance and more non-woody area. Ks_rehab also shows a substantial drop in woody PLAND, which is fully consistent with the mining-to-rehabilitation narrative: mining reduced woody dominance, and although rehabilitation began after 2021, the site still appears to be in an early restoration stage by 2025 rather than having recovered to a woody-dominated condition.

Class-level NP. For woody cover specifically, higher class-level NP means the woody class is broken into more separate pieces. Buda has relatively low woody NP, which aligns with its highly consolidated pattern. The degraded sites generally have higher woody NP, indicating more fragmented woody distribution. Ks_rehab also shows increasing woody NP over time, which, rather than simply indicating degradation, is consistent with woody recovery emerging in multiple smaller patches during early rehabilitation.

Class-level PD. Woody patch density tells the same story in standardized form. Lower woody PD at buda, gogoni, and shimba_hills indicates more contiguous woody structure, while higher values at the degraded sites indicate woody fragmentation. Ks_rehab shows increasing woody PD through time, which likely reflects the establishment of many smaller recovering woody patches rather than a single large restored block.

Class-level ED. Woody edge density is low where woody patches are large and smooth, and high where they are broken into smaller, irregular pieces. It is therefore lowest at the strongest reference-like sites and highest in the degraded landscapes. Ks_rehab also has elevated woody ED, but here the increase is consistent with an early rehabilitation mosaic where new woody patches have lots of edge relative to their area.

Class-level LPI. For woody cover, class-level LPI is high at buda, gogoni, and shimba_hills, showing that one large woody patch dominates each site. The degraded sites are generally lower, which indicates weaker woody dominance and greater subdivision. Ks_rehab declines over time as well, suggesting that the largest woody patch loses dominance through the mining and rehabilitation period. In context, that is compatible with a site shifting from a disturbed or simplified state into a more patchy recovering one, but not yet back to a consolidated woody landscape.

Overall, the cross-site pattern remains clear: buda and shimba_hills are the most spatially consolidated and woody-dominated landscapes, gogoni is somewhat intermediate but still relatively intact, and the degraded sites are more fragmented, less aggregated, and less woody-dominated. Ks_rehab is best understood separately from both the degraded and reference sites: its trends reflect a landscape that moved through active mining disturbance from 2018–2021 and then into an early rehabilitation phase from 2021–2025, producing increasing patchiness, edge, and class mixing that are consistent with landscape reorganization during recovery, not yet recovery completion.
########################################################################

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
Core long-term optical archive: Landsat 8 C2 L2 SR (2013–2017) + Sentinel-2 SR Harmonized (2019–present)
Common analytical support: 30 m, matched seasonal windows, matched site categories
Cross-sensor harmonization step: overlap-year regression / bias analysis per metric
Metric eligibility table: “fully comparable,” “proxy comparable,” or “Sentinel-era only”
Audit note: trend breaks attributable to sensor transition explicitly tested and documented



###########################################################

# 1. Ecosystem functionality / productivity trajectories

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project evaluates biodiversity outcome trajectories for:
- 1 focal site
- 3 reference sites
- 3 degraded sites

The assessment must support:
- focal vs reference vs degraded temporal comparisons
- baseline-to-current summaries
- spatial change products
- TGBS-style auditability and ecological interpretation

The current temporal windows are:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

Season definitions:
- `WET_MONTHS = [3, 4, 5]`
- `DRY_MONTHS = [7, 8, 9, 10]`

## Current repository capabilities
The repo already contains:

### Site inputs
A function:
- `build_default_sites_featurecollection()`

This returns the site polygons and metadata including:
- path
- site_id
- site_name
- site_category (`focal`, `reference`, `degraded`)

### Sensor-specific processed collection builders
These functions already exist and return multiband / multi-index collections:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

The official long-term 30 m trend product should use:
- `get_hls_merged_collection()`

### Collection processing utilities
The repo already contains collection-agnostic compositing and reduction functions:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`
- `reduce_image_over_sites()`
- `collection_to_site_timeseries()`
- `build_annual_index_timeseries()`
- `annual_collection_to_site_timeseries_df()`

These functions should be reused rather than rewritten.

## Analysis goal
Design and implement the ecosystem functionality / productivity trajectory layer.

Use the following indices:
- primary: `NIRv`
- secondary: `EVI`
- supporting: `NDVI`

The analysis must produce:
- focal vs reference envelopes
- focal vs degraded envelopes
- reference baseline ranges
- site-category grouped summaries
- standardized baseline-to-current deltas
- annual trajectories
- wet-season trajectories
- dry-season trajectories
- trend statistics per site

## Required implementation direction
Create or design a new module centered on grouped temporal comparisons, likely:
- `comparisons.py`

This module should operate mostly on long-format pandas DataFrames produced from existing Earth Engine outputs.

Focus on:
1. site-category grouped summaries
2. reference envelope generation
3. degraded envelope generation
4. focal-vs-reference comparison summaries
5. focal-vs-degraded comparison summaries
6. standardized focal anomalies relative to reference baseline
7. baseline vs current summaries
8. trend statistics per site

## Important design constraints
- Reuse existing collection builders and timeseries functions
- Assume HLS is the official long-term trend source at 30 m
- Keep outputs auditable and ecologically interpretable
- Prefer compact, modular functions
- Avoid overcomplicated abstractions
- Keep DataFrame outputs suitable for plotting and reporting

## Requested output
Please provide:
1. a concrete implementation plan for this analysis
2. the recommended function list for `comparisons.py`
3. the exact function signatures
4. concise but complete pandas-based code where appropriate
5. an explanation of how to generate:
   - annual site-level productivity summaries
   - wet/dry seasonal summaries
   - focal vs reference envelopes
   - standardized baseline-to-current deltas
6. guidance on which plots/tables should be generated first

Use the existing repo structure and function names exactly where relevant.



# 2. Vegetation cover change in dryland systems

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project compares:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Time windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

Season definitions:
- `WET_MONTHS = [3, 4, 5]`
- `DRY_MONTHS = [7, 8, 9, 10]`

## Current repository capabilities
Site polygons and metadata are provided through:
- `build_default_sites_featurecollection()`

Processed collections already exist:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Collection-agnostic temporal and site-reduction utilities already exist:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`
- `reduce_image_over_sites()`
- `collection_to_site_timeseries()`
- `build_annual_index_timeseries()`
- `annual_collection_to_site_timeseries_df()`

## Analysis goal
Design and implement the vegetation cover change workflow for dryland systems.

Use the following indices:
- primary: `NDVI`
- dryland support: `SAVI`
- optional support: `EVI`

This analysis must support:
- annual cover trajectories
- wet-season cover trajectories
- dry-season cover trajectories
- focal vs reference cover envelopes
- focal vs degraded cover envelopes
- baseline period summaries
- current period summaries
- baseline-to-current deltas
- standardized anomalies relative to reference behavior
- spatial change products and heatmaps

## Required implementation direction
This work should reuse the existing repo functions and likely extend:
- `comparisons.py` for grouped cover summaries
- a future `spatial_change.py` for raster outputs

The workflow should emphasize:
- dryland-appropriate vegetation cover interpretation
- avoiding confusion between seasonal variability and real ecological trajectory
- reference-relative interpretation

## Important design constraints
- Use `get_hls_merged_collection()` as the official long-term 30 m trend collection
- Keep Sentinel-2 available as a recent high-resolution support product if needed
- Prefer modular functions operating on DataFrames for summaries
- Keep spatial outputs exportable and heatmap-ready

## Requested output
Please provide:
1. a concrete implementation plan for the vegetation cover analysis
2. recommended function list additions for `comparisons.py`
3. any seasonal filtering helpers needed upstream of compositing
4. exact code or pseudo-code for:
   - annual NDVI/SAVI summaries
   - annual wet-season NDVI/SAVI summaries
   - annual dry-season NDVI/SAVI summaries
   - baseline/current site summaries
   - focal vs reference envelopes
   - standardized baseline-to-current cover anomalies
5. guidance on the most important raster products to generate first
6. guidance on the best first plots and tables for contract reporting

Use the existing repo structure and function names exactly where relevant.



# 3. Historical disturbance, degradation, and moisture trajectories

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project must evaluate biodiversity and ecological condition trajectories for:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Date windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

Season definitions:
- `WET_MONTHS = [3, 4, 5]`
- `DRY_MONTHS = [7, 8, 9, 10]`

Critical ecological context:
- major focal-site disturbance events occurred from `2018–2024`
- recovery efforts began in `2020` and continue to present

## Current repository capabilities
Site polygons come from:
- `build_default_sites_featurecollection()`

Processed sensor collections already exist:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Temporal aggregation and reduction utilities already exist:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`
- `reduce_image_over_sites()`
- `collection_to_site_timeseries()`
- `build_annual_index_timeseries()`
- `annual_collection_to_site_timeseries_df()`

## Analysis goal
Design and implement the disturbance / degradation / moisture trajectory workflow.

Use the following indices:
- primary moisture indicator: `NDMI`
- primary disturbance indicator: `NBR`
- contextual support: `NDVI`

The workflow must produce:
- annual NDMI trajectories
- annual NBR trajectories
- annual dry-season summaries
- annual wet-season summaries where useful
- disturbance-period summaries
- recovery-period summaries
- focal vs reference comparisons
- focal vs degraded comparisons
- trend statistics per site
- spatial change products and heatmaps

## Required implementation direction
Extend a grouped temporal summary module such as:
- `comparisons.py`

Potential function categories:
- disturbance-era summary
- recovery-era summary
- year-of-max-decline
- year-of-recovery-initiation
- focal anomaly relative to reference
- baseline/current deltas
- slope estimates

This analysis should clearly distinguish:
- disturbance decline
- post-2020 recovery
- persistent moisture stress
- reference-relative departure

## Important design constraints
- Use HLS as the official long-term trend collection
- Keep outputs interpretable for audit review
- Use compact, modular code
- Reuse existing compositing and site-timeseries functions rather than recreating them

## Requested output
Please provide:
1. a concrete implementation plan for this disturbance/moisture analysis
2. recommended function list for grouped temporal comparisons
3. suggested function signatures
4. code or pseudo-code for:
   - annual NDMI and NBR summaries
   - dry-season NDMI and NBR summaries
   - disturbance-period summaries
   - recovery-period summaries
   - slope calculations per site
   - focal vs reference anomaly summaries
5. guidance on which plots and summary tables to generate first
6. guidance on the most important raster change products for NDMI and NBR

Use the existing repo structure and function names exactly where relevant.



# 4. Aboveground biomass proxy analysis

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project compares:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Date windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

Season definitions:
- `WET_MONTHS = [3, 4, 5]`
- `DRY_MONTHS = [7, 8, 9, 10]`

Ecological context:
- focal disturbance: `2018–2024`
- recovery period: `2020–present`

## Current repository capabilities
Site polygons and metadata:
- `build_default_sites_featurecollection()`

Processed image collections:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Collection-agnostic utilities:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`
- `reduce_image_over_sites()`
- `collection_to_site_timeseries()`
- `build_annual_index_timeseries()`
- `annual_collection_to_site_timeseries_df()`

## Analysis goal
Design and implement the aboveground biomass proxy analysis.

Use the following indices:
- primary: `NIRv`
- secondary: `EVI`
- supporting context: `NDVI`

The workflow must produce:
- annual NIRv trajectories
- annual wet-season NIRv summaries
- annual dry-season NIRv summaries
- baseline period NIRv summaries
- current period NIRv summaries
- standardized baseline-to-current deltas
- focal vs reference envelopes
- focal vs degraded envelopes
- pre-2020 vs post-2020 trend comparisons
- raster change products for biomass-proxy interpretation

## Required implementation direction
This work should mainly reuse:
- `get_hls_merged_collection()`
- `build_period_composites()`
- `annual_collection_to_site_timeseries_df()`

Grouped summaries should likely live in:
- `comparisons.py`

Spatial raster products should likely live in:
- `spatial_change.py`

## Important design constraints
- Treat NIRv as the main biomass / productivity proxy
- Keep the workflow compact, modular, and auditable
- Prioritize HLS for the official long-term trend product
- Reuse current repo functions wherever possible

## Requested output
Please provide:
1. a concrete implementation plan for the biomass-proxy analysis
2. recommended `comparisons.py` functions for NIRv-based grouped summaries
3. code or pseudo-code for:
   - annual NIRv time series
   - wet-season and dry-season NIRv summaries
   - baseline/current NIRv summaries
   - standardized focal anomaly relative to reference baseline
   - pre-2020 vs post-2020 trend comparisons
4. recommended plots and summary tables
5. recommended raster products to generate first for this analysis

Use the existing repo structure and function names exactly where relevant.



# 5. Spectral diversity metrics (α and β)

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project compares:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Date windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

## Current repository capabilities
Site polygons and metadata:
- `build_default_sites_featurecollection()`

Processed collection builders:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Temporal aggregation functions:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`

Site-reduction and timeseries utilities:
- `reduce_image_over_sites()`
- `collection_to_site_timeseries()`
- `build_annual_index_timeseries()`
- `annual_collection_to_site_timeseries_df()`

Important note:
- `build_annual_multiband_composites()` already exists and is likely the key starting point for spectral diversity analysis.

## Analysis goal
Design and implement a practical, auditable spectral diversity workflow for TGBS.

Use the merged HLS reflectance stack as the main basis, with common 30 m bands:
- `BLUE`
- `GREEN`
- `RED`
- `NIR`
- `SWIR1`
- `SWIR2`

The workflow should support:
- alpha spectral diversity
- beta spectral diversity
- baseline period summaries
- current period summaries
- baseline-to-current deltas
- focal-to-reference comparisons
- focal-to-degraded comparisons
- spatial diversity surfaces and change maps

## Required implementation direction
Keep the methods simple, interpretable, and reproducible.

Possible implementation pathways include:
- local spectral variance / standard deviation
- neighborhood spectral heterogeneity
- PCA-based spectral dispersion
- inter-site spectral distance between focal and reference / degraded summaries

The answer should help decide which metric family is the most practical and defensible first implementation.

## Important design constraints
- Reuse `build_annual_multiband_composites()` if possible
- Prefer HLS as the official long-term 30 m product
- Avoid overly experimental methods that are hard to explain in audit documentation
- Keep code modular and practical

## Requested output
Please provide:
1. a concrete implementation plan for spectral diversity
2. the recommended first spectral diversity method to implement
3. recommended module structure and function list
4. code or pseudo-code for:
   - baseline multi-band composite generation
   - current multi-band composite generation
   - alpha diversity surface generation
   - beta diversity summary generation
   - site-level summary extraction
5. guidance on which outputs belong in:
   - a `spectral_diversity.py` module
   - `comparisons.py`
   - `spatial_change.py`
6. guidance on the best first tables, figures, and maps

Use the existing repo structure and function names exactly where relevant.



# 6. Spatial change layer and heatmap production

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project compares:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Time windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

The contract requires:
- spatial change products
- baseline vs current summaries
- heatmaps highlighting where change is strongest
- reference-relative interpretation where feasible

## Current repository capabilities
Site polygons and metadata:
- `build_default_sites_featurecollection()`

Processed collections:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Compositing functions:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`

The repo currently needs a dedicated spatial change layer.

## Analysis goal
Design and implement a `spatial_change.py` module that creates explicit raster outputs for:
- baseline mean
- current mean
- current minus baseline
- trend slope
- z-score anomaly relative to reference behavior
- percentile anomaly relative to reference behavior

Prioritized indices:
- `NDVI`
- `NIRv`
- `NDMI`
- `NBR`
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
1. a concrete implementation plan for `spatial_change.py`
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
6. the best naming conventions and export strategy for raster outputs

Use the existing repo structure and function names exactly where relevant.


# 7. Landscape structure and landscape metrics

You are a Remote Sensing and Google Earth Engine expert helping continue an existing TGBS biodiversity verification workflow for East African rangelands.

## Project context
The project compares:
- 1 focal site
- 3 reference sites
- 3 degraded sites

Date windows:
- `BASELINE_START = "2014-01-01"`
- `BASELINE_END = "2017-12-31"`
- `CURRENT_START = "2018-01-01"`
- `CURRENT_END = "2025-12-31"`

The contract requires landscape metrics including:
- connectivity
- fragmentation
- patch size
- edge effects

## Current repository capabilities
Site polygons and metadata:
- `build_default_sites_featurecollection()`

Processed collections:
- `get_s2_sr_collection()`
- `get_l8_sr_collection()`
- `get_hls_merged_collection()`

Compositing utilities:
- `build_period_composites()`
- `build_annual_band_composites()`
- `build_monthly_band_composites()`
- `build_annual_multiband_composites()`

There is not yet a dedicated module for structural landscape metrics.

## Analysis goal
Design a practical landscape-structure workflow using remote-sensing-derived vegetation masks and period summaries.

Likely base layers:
- thresholded `NDVI`
- thresholded `SAVI`
- optionally `NIRv` as a stricter support proxy

The workflow should support:
- baseline vegetation-state masks
- current vegetation-state masks
- patch metrics
- fragmentation metrics
- edge metrics
- focal vs reference comparisons
- focal vs degraded comparisons
- baseline-to-current structural deltas
- maps of structural change hotspots

## Required implementation direction
The analysis should make clear which steps occur:
- in Earth Engine
- in exported raster / GIS post-processing if needed

The answer should help determine the cleanest first implementation path and module structure.

Potential modules:
- `landscape_metrics.py`
- `spatial_change.py`
- `comparisons.py`

## Important design constraints
- Keep methods practical and defensible
- Avoid overengineering
- Build from existing composited products where possible
- Prioritize outputs that best satisfy the contract requirement for structure and fragmentation interpretation

## Requested output
Please provide:
1. a concrete implementation plan for landscape structure analysis
2. the recommended first vegetation mask strategy
3. the recommended module structure and function list
4. code or pseudo-code for:
   - baseline vegetation mask generation
   - current vegetation mask generation
   - patch-oriented summary workflow
   - baseline/current structural comparison summaries
5. guidance on which metrics are best done in Earth Engine vs downstream GIS
6. the best first tables, maps, and summary outputs for reporting

Use the existing repo structure and function names exactly where relevant.

