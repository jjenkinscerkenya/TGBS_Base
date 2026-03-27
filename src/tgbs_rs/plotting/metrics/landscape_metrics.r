library(terra)
library(dplyr)
library(stringr)
library(purrr)
library(readr)
library(tidyr)
library(landscapemetrics)

project_root <- "."
raster_dir <- file.path(project_root, "outputs", "rasters", "landscape_metrics")
out_dir <- file.path(project_root, "outputs", "tables")

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

if (!dir.exists(raster_dir)) {
  stop("Raster directory not found: ", raster_dir)
}

target_crs <- "EPSG:32737"

# Helpers

reproject_landscape_raster <- function(r, target_crs = "EPSG:32737") {
  if (is.na(terra::crs(r)) || terra::crs(r) == "") {
    stop("Raster has no CRS defined.")
  }

  current_crs <- terra::crs(r, proj = TRUE)
  message("Original CRS: ", current_crs)

  if (grepl("32737", current_crs)) {
    message("Raster already in EPSG:32737")
    return(r)
  }

  r_proj <- terra::project(r, target_crs, method = "near")
  message("Reprojected CRS: ", terra::crs(r_proj, proj = TRUE))
  r_proj
}

parse_raster_metadata <- function(filepath) {
  fname <- basename(filepath)
  fname_noext <- tools::file_path_sans_ext(fname)

  year_match <- stringr::str_extract(fname_noext, "(?<!\\d)(20\\d{2})(?!\\d)")
  year_val <- suppressWarnings(as.integer(year_match))

  site_id <- fname_noext |>
    stringr::str_remove("_(20\\d{2}).*$")

  tibble(
    file_name = fname,
    site_id = site_id,
    year = year_val
  )
}

safe_check_landscape <- function(r, raster_name = NA_character_) {
  tryCatch(
    landscapemetrics::check_landscape(r),
    error = function(e) {
      warning("check_landscape() failed for ", raster_name, ": ", e$message)
      NULL
    }
  )
}

calc_metrics_for_raster <- function(r, raster_name) {
  lsm_landscape <- tryCatch(
    {
      landscapemetrics::calculate_lsm(
        landscape = r,
        what = c(
          "lsm_l_np",
          "lsm_l_pd",
          "lsm_l_ed",
          "lsm_l_lpi",
          "lsm_l_shdi",
          "lsm_l_ai"
        )
      ) %>%
        mutate(metric_level = "landscape")
    },
    error = function(e) {
      warning("Landscape metrics failed for ", raster_name, ": ", e$message)
      tibble()
    }
  )

  lsm_class <- tryCatch(
    {
      landscapemetrics::calculate_lsm(
        landscape = r,
        what = c(
          "lsm_c_ca",
          "lsm_c_pland",
          "lsm_c_np",
          "lsm_c_pd",
          "lsm_c_ed",
          "lsm_c_lpi"
        )
      ) %>%
        mutate(metric_level = "class")
    },
    error = function(e) {
      warning("Class metrics failed for ", raster_name, ": ", e$message)
      tibble()
    }
  )

  bind_rows(lsm_landscape, lsm_class)
}

clean_metrics_table <- function(df) {
  df %>%
    select(-any_of(c("crs", "id", "raster_name", "parsed_label"))) %>%
    relocate(file_name, site_id, year)
}

# Find rasters

raster_files <- list.files(
  raster_dir,
  pattern = "\\.tif$",
  full.names = TRUE
)

if (length(raster_files) == 0) {
  stop("No .tif files found in: ", raster_dir)
}

message("Found ", length(raster_files), " raster(s).")

# Process rasters

all_metrics <- purrr::map_dfr(raster_files, function(raster_path) {
  message("--------------------------------------------------")
  message("Processing: ", raster_path)

  meta <- parse_raster_metadata(raster_path)

  r <- terra::rast(raster_path)
  r <- reproject_landscape_raster(r, target_crs = target_crs)

  safe_check_landscape(r, raster_name = meta$file_name)

  metrics_df <- calc_metrics_for_raster(r, raster_name = meta$file_name)

  metrics_df %>%
    mutate(
      file_name = meta$file_name,
      site_id = meta$site_id,
      year = meta$year,
      resolution_x = terra::res(r)[1],
      resolution_y = terra::res(r)[2]
    ) %>%
    relocate(file_name, site_id, year, resolution_x, resolution_y)
})

all_metrics <- clean_metrics_table(all_metrics)

landscape_metrics <- all_metrics %>%
  filter(level == "landscape" | metric_level == "landscape") %>%
  clean_metrics_table()

class_metrics <- all_metrics %>%
  filter(level == "class" | metric_level == "class") %>%
  clean_metrics_table()

# Write outputs

all_metrics_path <- file.path(out_dir, "landscape_metrics_all.csv")
landscape_metrics_path <- file.path(out_dir, "landscape_metrics_landscape_level.csv")
class_metrics_path <- file.path(out_dir, "landscape_metrics_class_level.csv")

readr::write_csv(all_metrics, all_metrics_path)
readr::write_csv(landscape_metrics, landscape_metrics_path)
readr::write_csv(class_metrics, class_metrics_path)

message("Done.")
message("Wrote: ", all_metrics_path)
message("Wrote: ", landscape_metrics_path)
message("Wrote: ", class_metrics_path)