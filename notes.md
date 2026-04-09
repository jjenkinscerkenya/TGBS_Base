

## Spatial Change Interpretation
Positive delta values indicate that the index is higher in the current period than in the baseline period, which is interpreted as a relative increase in the biophysical property represented by that index at a given pixel, whereas negative delta values indicate that the index is lower in the current period than in the baseline period, reflecting a relative decline from baseline conditions. The ecological meaning of the sign depends on the index itself: for vegetation and productivity metrics such as NDVI, SAVI, and NIRv, positive deltas generally suggest increased vegetation cover, vigor, or productivity, while negative deltas suggest reduced cover or productivity; for NDMI, positive deltas generally indicate wetter or less water-stressed vegetation conditions, while negative deltas indicate drying or moisture loss; for NBR, positive deltas generally indicate recovery or increased vegetation condition, while negative deltas indicate disturbance, biomass loss, or burn-related decline. Accordingly, positive and negative delta values should not be interpreted as universally “good” or “bad” in isolation, but rather as directional measures of change whose significance must be evaluated in relation to the specific index, the local disturbance history, restoration timing, and corroborating spatial patterns such as known fire-affected or restoration-treatment blocks.


## Handling Seasonal Tables
Seasonal information summary for documentation

Seasonal index information was derived from the cleaned monthly composite site tables rather than being computed directly as a single seasonal Earth Engine product. For each sensor, monthly composites were first generated and reduced over all focal, reference, and degraded site polygons. The monthly site tables were then standardized locally in pandas, expanded to a complete site–year–month panel, and labeled according to the project’s seasonal definitions: wet season (March–May) and dry season (July–October). This approach made missing months explicit, preserved auditability, and allowed seasonal summaries to be calculated using transparent quality-control rules.

For each site and year, wet- and dry-season productivity metrics were computed from the monthly values of the core indices. Seasonal values were only retained when a minimum number of valid monthly observations were available, ensuring that sparse months did not produce misleading seasonal summaries. The resulting seasonal tables include both the seasonal metric values and support information such as expected months, observed months, missing months, and valid-month counts.

These seasonal products will be used to distinguish interannual ecological change from normal seasonal variation. In particular, they support focal-versus-reference and focal-versus-degraded seasonal comparisons, help assess whether the focal site is moving toward or away from intact seasonal behavior, and provide an auditable basis for interpreting disturbance and recovery dynamics.


## Landscape Metrics Calculations
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


## Summary of Landscape Metrics Results:
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


## Rainfall Data
The precipitation series shows a clear bimodal rainfall regime, which is consistent with the expected climate of coastal Kenya: a primary long-rains season in March–May and a secondary short-rains season in October–December.

At the annual scale, rainfall totals vary substantially across the 2014–2025 series, ranging from about 919 mm in 2022 to about 2,230 mm in 2023. The baseline years (2014–2017) were comparatively moderate and less variable, averaging about 1,277 mm/year, whereas the more recent complete current-period years (2018–2024) were wetter on average, about 1,578 mm/year, and considerably more variable. This suggests that the current-period environmental context was not simply wetter or drier overall, but more hydrologically volatile, with distinct wet and dry departures that could plausibly affect vegetation response and the interpretation of biodiversity-condition trajectories.

The monthly series reinforces this interpretation. The strongest and most recurrent rainfall peak occurs in April–May, with April averaging about 249 mm and May about 290 mm across 2018–2025. A second peak occurs in October–November, with particularly high interannual variability in November. This seasonal structure is ecologically important because it indicates that site condition should be interpreted against a background of pulsed moisture availability rather than uniform annual recharge. The monthly data also show that rainfall does not fall to zero for the entire dry season; instead, there is typically a weaker but still meaningful contribution through mid-year, which is consistent with coastal Kenya’s more humid maritime setting.

Several years stand out as notable anomalies. 2022 was the driest year in the annual record and appears to represent a pronounced rainfall deficit relative to both the baseline and the surrounding current-period years. In contrast, 2023 was an exceptionally wet year and is the clearest positive outlier in the record. The monthly series shows that this was driven especially strongly by the short rains, with November 2023 reaching about 810 mm, by far the wettest month in the dataset.

Other secondary anomalies are also evident. The long rains of 2020 were notably strong, with April 2020 and May 2020 both well above the multi-year monthly average, while 2019 combined a very wet May with an unusually strong October, producing one of the wetter years overall. Conversely, 2024 returned to a relatively dry annual total after the extreme wetness of 2023, indicating that the 2023 peak was not the start of a sustained upward trend so much as an episodic high-rainfall year within a highly variable recent period.

Overall, the rainfall record indicates that the study region experienced a seasonally coherent but highly variable hydroclimatic regime, with especially strong departures in 2022 and 2023. For interpretation of biodiversity and vegetation trajectories, this means that observed site-level change should not be attributed only to management or degradation history without considering the strong influence of interannual rainfall variability, particularly the intensity or failure of the MAM and OND seasons.


###############################################################

Project Overview 
Kwale County, Kenya's southernmost county is known for its white sand beaches which stretch for hundreds of kilometers along Kenya's southern coast. The county covers 8,270 km2 and is comprised of a mosaic of coastal plains, mangrove lagoons, coastal forests, and semi-arid grasslands. The county holds one of the largest coastal forest ecosystems in East Africa after the Arabuko-Sokoke forest. Kwale is home to several IUCN designated protected areas including the Shimba Hills National Reserve, Buda Forest, Gogoni Forest, and the Diani-Chale Marine National Reserve among others.  
 
The coastal forests of Kwale county play a crucial role in supporting high concentrations of both plant and animal biodiversity. For example, over 50% of the 159 rare plants in Kenya are found in the Shimba Hills National Reserve, including some endangered species of cycad and orchids. Furthermore, the reserve is home to Kenya's only population of sable antelope as well as containing the highest density of Elephants in the country. Birdlife is also abundant, with over 111 species recorded, of which 22 are coastal endemic.

However, these delicate ecosystems face increasing anthropogenic pressures from illegal logging, charcoal production, poaching, and changing climatic conditions. Community conservation and restoration efforts are crucial to preserving the ecological integrity and cultural heritage of these coastal ecosystems.


1.1 Objective
The objective of this report is to present the findings of a comprehensive remote sensing survey to support the assessment of restoration sites applying for the Global Biodiversity Standard. Wapi GIS Ltd used a variety of remote sensing and geoprocessing methods to understand baseline conditions and track signatures of ecological change throughout the restoration process.
By comparing these results with the same ecological change metrics from reference and degraded sites in the region, it is possible to evaluate and quantify the progress of current restoration efforts.  

1.2 Restoration Site
One of the key economic entities in Kwale county is the Kwale Mineral Sands Operation, operated by Base Resources, which was acquired in 2010 and commenced production in late 2013. In the 2022 financial year, the Kwale operation accounted for approximately 65% of Kenya’s mining industry by mineral output value, representing a significant contribution to Kenya’s export market. 

In 2020, mining operations transitioned from the Central Dune orebody to the South Dune orebody, an area roughly 4.5km2. The South Dune, hereafter referred to as the “focal” site, is located approximately 12km south of Shimba Hills National Reserve, between the Buda and Gogoni forests. Mining in the South Dune extension continued through the end of 2024. 

Following the depletion of each subsequent mining block of the South Dune orebody, environmental restoration efforts were undertaken to stabilize soil banks, improve soil health, and introduce a variety of pioneer plant species. The South Dune extension restoration efforts are composed of 14 main rehabilitation blocks with an additional 9 peripheral rehabilitation areas. 

For the purposes of this remote sensing survey, the rehabilitation blocks have been grouped into “old” rehabilitation blocks, those in which rehabilitation efforts have been taking place since 2020 - 2021, and “new” rehabilitation blocks, those in which rehabilitation efforts have been taking place since 2022 - 2024.





































########################################################################

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

Climate Hazards Center Infrared Precipitation with Stations version 3. CHIRPS3 Data Repository doi:10.15780/G2JQ0P (2025).