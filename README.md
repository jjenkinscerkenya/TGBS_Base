# TGBS Remote Sensing Analysis Framework

## Overview

**TGBS_Base** is a Python remote sensing framework for monitoring landscape metrics, vegetation dynamics, and ecological disturbance in Kwale County, Kenya. It provides workflows for collecting satellite imagery from Google Earth Engine, calculating spectral indices, and generating time-series comparisons between a restoration site (KS Rehab) and reference ecosystems.

- **Temporal Scope**: 2014–2025 (baseline: 2014–2017; current: 2018–2025)
- **Study Sites**: Focal site (KS Rehab, restoration), Reference sites (Buda, Gogoni, Shimba Hills), Degraded sites (Degraded 1–3)
- **Data Sources**: Google Earth Engine (HLS 30m, 2014–2025; Sentinel-2 10m, 2019–2025)
- **Outputs**: Time-series metrics, comparison tables, anomaly detection, visualizations

---

## Repository Organization

```
TGBS_Base/
├── src/tgbs_rs/                    # Main Python package
│   ├── config/                     # Configuration and specifications
│   │   ├── config.py              # File paths, Earth Engine datasets, constants
│   │   ├── specs.py               # Metric and visualization specifications
│   │   └── config_vis.py           # Visualization theming and color schemes
│   ├── data/                       # Data loading and preprocessing
│   │   ├── baseline.py            # Global baseline datasets (forest, biodiversity)
│   │   ├── topography.py          # Terrain analysis (elevation, slope, aspect)
│   │   └── sensors/               # Sensor-specific data pipelines
│   │       ├── chirps/            # CHIRPS Precipitation Daily Reanalysis (5km, 2014–2025)
│   │       ├── dynamic_world/     # Dynamic World V1 (10m, 2015–2025)
│   │       ├── hls/               # Harmonized Landsat-Sentinel (30m, 2014–2025)
│   │       └── sentinel/          # Sentinel-2 processing (10m, 2019–2025)
│   ├── metrics/                    # Metrics calculation and aggregation
│   │   └── temporal.py            # Core module: temporal compositing and site-level analysis
│   ├── visualization/              # Output generation
│   │   ├── plots.py               # Matplotlib figure generation
│   │   └── tables.py              # Data transformations for tables and comparisons
│   ├── io.py                       # File I/O utilities
│   └── utils.py                    # General utility functions
├── notebooks/                      # Jupyter analysis notebooks
│   ├── landscape_metrics.r        # Calculate landscape metrics from dynamic world rasters
│   ├── ee_notebooks/              # Earth Engine data preparation workflows
│   │   ├── baseline_data.ipynb     # Load baseline markers (forest cover, biodiversity)
│   │   ├── chirps_precip.ipynb     # Generate annual and monthly total rainfall tables
│   │   ├── composites.ipynb        # Build annual and seasonal composites
│   │   ├── landscape_metrics.ipynb # Generate woody vs. non-woody cover rasters
│   │   ├── spatial_change.ipynb    # Calculate spatial change metrics for focal site
│   │   └── site_aois.ipynb         # Define and visualize study site boundaries
│   └── plotting_notebooks/        # Result visualization and interpretation
│       ├── baseline_plots.ipynb
│       ├── disturbance_metrics_plots.ipynb
│       ├── landscape_metrics_plots.ipynb
│       ├── moisture_metrics_plots.ipynb
│       ├── productivity_metrics_plots.ipynb
│       ├── rainfall_plots.ipynb
│       └── veg_cover_metrics_plots.ipynb
├── aoi/                            # Study site boundary files (GeoJSON/GeoPackage)
├── outputs/                        # Analysis results (maps, tables, rasters)
│   ├── plots/                     # Figure outputs organized by metric type
│   ├── tables/                    # CSV time-series tables
│   └── rasters/                   # GeoTIFF output rasters
├── references/                     # Documentation and literature
├── pyproject.toml                 # Package configuration and dependencies
├── uv.lock                        # Locked dependency versions (reproducibility)
└── README.md                      # This file
```

---

## Installation & Environment Setup

This section guides you through setting up a reproducible Python environment and installing the `tgbs_rs` package.

### Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)
- A terminal/command prompt

### Step 1: Install uv (Package Manager)

`uv` is a fast Python package installer and resolver that manages dependencies and virtual environments. Install it once on your system:

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows (using PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, verify that `uv` is available:
```bash
uv --version
```

### Step 2: Clone the Repository

```bash
git clone <repository-url>
cd TGBS_Base
```

### Step 3: Set Up the Virtual Environment with Dependencies

The `uv.lock` file contains locked versions of all dependencies, ensuring reproducible environments across machines. Use it to create an isolated Python environment:

```bash
uv sync --all-groups
```

This command:
- Creates a `.venv` virtual environment in the repository
- Installs all core dependencies (earthengine-api, geemap, geopandas, pandas, numpy, matplotlib)
- Installs optional development dependencies (jupyter, pytest, black, ruff) specified in `--all-groups`

After syncing, repository modules should be importable in notebooks and scripts, for example:
```bash
from tgbs_rs.data.sensors.hls import get_hls_merged_collection
```

### Step 4: Activate the Virtual Environment (Optional)

Activation is only needed if you want your shell session to use the repo environment directly. The activation method depends on your operating system:

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

After activation, you should see `(.venv)` prepended to your terminal prompt.

### Step 5: Verify the Setup

Test that the environment is configured correctly:

```bash
python --version  # Should show Python 3.10+
python -c "import tgbs_rs; print('tgbs_rs imported successfully')"
```

### Using Jupyter Notebooks

Once the environment is set up and activated, launch Jupyter from the repository root:

```bash
jupyter notebook
```

Or use JupyterLab:
```bash
jupyter lab
```

The Jupyter kernel will automatically use the `.venv` Python interpreter, allowing access to all installed packages and the `tgbs_rs` modules.

### Using Jupyter Notebooks with VSCode

In VS Code, select the Python interpreter (Ctrl + Shift + P) and notebook kernel from the repository .venv
Ensure that both point to `.venv/Scripts/python.exe`.

### Reproducibility

The combination of `uv.lock` and `uv sync` ensures that anyone cloning the repository and following these steps will have the **exact same versions** of all dependencies, creating a reproducible analysis environment. This is critical for long-term maintainability and collaboration.

---

## Core Modules Overview

Key modules in the `tgbs_rs` package:

- **`config/`** — Configuration files defining paths, Earth Engine datasets, temporal windows, and masking parameters
- **`data/`** — Data loading from Google Earth Engine
  - `baseline.py` — Global baseline datasets (forest cover, biodiversity, elevation)
  - `sensors/hls/` — Harmonized Landsat-Sentinel processing (30m, 2014–2025)
  - `sensors/sentinel/` — Sentinel-2 processing (10m, 2019–2025)
- **`metrics/temporal.py`** — Core engine: temporal compositing, spatial reduction, and metrics calculation
- **`visualization/`** — Figure and table generation (Matplotlib and Pandas)
- **`io.py`, `utils.py`** — File I/O and utility functions

---

## Analysis Workflow

The framework progresses through these stages:

1. **Data Collection** — Query satellite imagery from Earth Engine for study sites and date range
2. **Temporal Compositing** — Aggregate daily images into annual/monthly composites using median filtering
3. **Spatial Reduction** — Extract site-level statistics by reducing composites to polygon boundaries
4. **Metrics Calculation** — Build time-series comparisons: focal vs. reference sites, anomalies, trends
5. **Visualization** — Generate plots and export comparison tables to `outputs/`

### Key Concept: Focal vs. Reference Analysis

- **Focal Site (KS Rehab)** — Restoration area being monitored
- **Reference Sites (Buda, Gogoni, Shimba Hills)** — Undisturbed ecosystems representing healthy baseline
- **Interpretation**: If focal metrics increase toward reference levels → restoration signal; if they remain below → incomplete recovery

---

## Running the Notebooks

### Before Running Notebooks

1. Complete installation (see previous section)
2. Activate environment: `source .venv/bin/activate`
3. Authenticate Earth Engine (first time only):
   ```bash
   earthengine authenticate
   ```

### Data Preparation (Earth Engine Notebooks)

Run these notebooks first from `notebooks/ee_notebooks/`:

1. **`site_aois.ipynb`** — Verify study site boundaries are correctly configured
2. **`baseline_data.ipynb`** — Load and validate baseline reference datasets
3. **`composites.ipynb`** — Build annual/monthly satellite composites and extract site-level time-series (10–30 min)
4. **`landscape_metrics.ipynb`** — Optional: calculate landscape-scale pattern metrics

### Analysis & Visualization (Plotting Notebooks)

After data preparation, run notebooks from `notebooks/plotting_notebooks/`:

- **`veg_cover_metrics_plots.ipynb`** — Analysis of vegetation indices (NDVI, EVI, SAVI)
- **`moisture_metrics_plots.ipynb`** — Water stress and moisture analysis (NDMI, NDWI)
- **`landscape_metrics_plots.ipynb`** — Landscape metrics 
- **`disturbance_metrics_plots.ipynb`** — Disturbance detection (NBR) and productivity (NIRv)
- **`baseline_plots.ipynb`** — Reference layers and site context
- **`rainfall_plots.ipynb`** — Precipitation trends (CHIRPS)
- **`table_prep.ipynb`** — Data quality checks and formatting

Each plotting notebook:
1. Loads time-series data from `outputs/tables/`
2. Calls `tgbs_rs.metrics.temporal` functions to compute focal-vs-reference comparisons
3. Generates publication-ready figures and exports tables

### Quick Start Example

```bash
# 1. Setup
source .venv/bin/activate
earthengine authenticate

# 2. Open Jupyter
jupyter notebook

# 3. Run in order:
#    - ee_notebooks/site_aois.ipynb
#    - ee_notebooks/composites.ipynb
#    - plotting_notebooks/veg_cover_metrics_plots.ipynb
```

### Customization

- Change focal site in `config.py`
- Adjust temporal windows in notebooks
- Add new spectral indices from `tgbs_rs.data.sensors`
- Modify figure export settings (resolution, format)

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `uv pip install -e .` and verify `(.venv)` is active |
| "Authentication failed" | Re-run `earthengine authenticate` |
| Notebook hangs | Earth Engine queues are slow; try off-peak hours |
| CSV export fails | Check `outputs/tables/` exists and you have write permissions |

---