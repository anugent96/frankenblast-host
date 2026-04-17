# FrankenBlast Command Line Interface Documentation

## Overview

FrankenBlast now provides a comprehensive command-line interface for easy execution of host association, photometry, and SED fitting tasks. The CLI supports both individual commands and full pipeline execution.

## Installation

First, ensure all dependencies are installed and environment variables are set:

```bash
# Activate conda environment
conda activate frankenblast

# Source the settings file to set environment variables
source settings.sh
```

## Quick Start

### Basic Usage

```bash
# Make scripts executable
chmod +x frankenblast_cli.py
chmod +x frankenblast.py
chmod +x batch_process.py

# Run full pipeline for a single transient
./frankenblast_cli.py full --name SN2019ulo --ra 20.509 --dec -60.571

# Run with configuration file
./frankenblast_cli.py full --config config_examples/full_pipeline.yaml
```

## Command Line Interface (`frankenblast_cli.py`)

### Available Commands

#### 1. Full Pipeline
Run the complete FrankenBlast pipeline: host association, photometry, and SED fitting.

```bash
./frankenblast_cli.py full --name <NAME> --ra <RA> --dec <DEC> [options]
```

**Options:**
- `--redshift`: Transient redshift (optional)
- `--prost-samples`: Number of PROST MC samples (default: 1000)
- `--prost-catalogs`: Catalogs to query (default: panstarrs, glade, decals)
- `--aperture-type`: global or local (default: global)
- `--use-sbipp`: Use SBI++ for SED fitting (default: true)
- `--config`: Path to configuration file

**Example:**
```bash
./frankenblast_cli.py full \
    --name SN2019ulo \
    --ra 20.509 \
    --dec -60.571 \
    --redshift 0.05 \
    --aperture-type global \
    --verbose
```

#### 2. Host Association Only
Find the host galaxy for a transient.

```bash
./frankenblast_cli.py host --name <NAME> --ra <RA> --dec <DEC> [options]
```

**Example:**
```bash
./frankenblast_cli.py host \
    --name AT2021abc \
    --ra 150.123 \
    --dec 45.678 \
    --prost-samples 1000 \
    --save-prost \
    --prost-output-dir prostdb
```

#### 3. Photometry
Perform aperture photometry on a known host.

```bash
./frankenblast_cli.py photometry --name <NAME> --ra <RA> --dec <DEC> \
    --host-ra <HOST_RA> --host-dec <HOST_DEC> [options]
```

**Example:**
```bash
./frankenblast_cli.py photometry \
    --name SN2020xyz \
    --ra 180.5 \
    --dec -30.2 \
    --host-ra 180.502 \
    --host-dec -30.198 \
    --host-redshift 0.044 \
    --aperture-type global \
    --photometry-output sn2020xyz_phot.json
```

#### 4. SED Fitting
Fit the SED using existing photometry.

```bash
./frankenblast_cli.py sed --name <NAME> --ra <RA> --dec <DEC> \
    --photometry-file <FILE> [options]
```

**Example:**
```bash
./frankenblast_cli.py sed \
    --name SN2019ulo \
    --ra 20.509 \
    --dec -60.571 \
    --photometry-file photometry_results.json \
    --sbi-model zfree_GPD2W \
    --sed-mode production
```

#### 5. Download Cutouts
Download cutout images from various surveys.

```bash
./frankenblast_cli.py cutouts --name <NAME> --ra <RA> --dec <DEC> [options]
```

**Example:**
```bash
./frankenblast_cli.py cutouts \
    --name AT2021def \
    --ra 234.567 \
    --dec -15.432 \
    --surveys PanSTARRS DES WISE 2MASS GALEX \
    --size 120.0
```

### Global Options

All commands support these global options:
- `-v, --verbose`: Enable verbose output
- `--log-file`: Path to log file
- `--config`: Path to configuration file (YAML or JSON)

## Python Wrapper (`frankenblast.py`)

The Python wrapper provides a simplified interface for use in scripts and notebooks.

### Basic Usage

```python
from frankenblast import FrankenBlast

# Initialize for a transient
fb = FrankenBlast('SN2019ulo', ra=20.509, dec=-60.571, redshift=0.05)

# Run full pipeline
results = fb.run_full_pipeline()

# Or run individual steps
fb.find_host()              # Host association
fb.download_images()        # Download cutouts
fb.do_photometry()         # Aperture photometry
fb.fit_sed()               # SED fitting
```

### Quick Functions

```python
from frankenblast import quick_host_association, quick_photometry, quick_sed_fit

# Quick host association
host = quick_host_association('SN2019ulo', ra=20.509, dec=-60.571)

# Quick photometry with known host
photometry = quick_photometry(
    'SN2019ulo', 
    ra=20.509, 
    dec=-60.571,
    host_ra=20.510, 
    host_dec=-60.570,
    host_redshift=0.05
)

# Quick SED fit from saved photometry
sed_result = quick_sed_fit(
    'SN2019ulo',
    ra=20.509,
    dec=-60.571,
    photometry_file='photometry.json'
)
```

## Batch Processing (`batch_process.py`)

Process multiple transients from a CSV file.

### CSV Format

Create a CSV file with transient information:
```csv
name,ra,dec,redshift
SN2019ulo,20.509,-60.571,
SN2020abc,150.123,2.456,0.03
SN2019xyz,180.5,-30.2,0.045
```

### Running Batch Processing

```bash
# Process all transients in the CSV
./batch_process.py config_examples/transient_list.csv \
    --output-dir batch_results \
    --steps host photometry sed

# Run only host association
./batch_process.py transient_list.csv \
    --steps host \
    --output-dir host_results

# Use configuration file for additional parameters
./batch_process.py transient_list.csv \
    --config config_examples/full_pipeline.yaml \
    --parallel \
    --max-workers 4
```

## Configuration Files

Configuration files allow you to specify all parameters in advance.

### YAML Example (`config_examples/full_pipeline.yaml`)

```yaml
# Transient information
name: "SN2019ulo"
ra: 20.509
dec: -60.571
redshift: 0.05  # Optional

# Host association settings
prost_samples: 1000
prost_catalogs:
  - "glade"
  - "decals"

# Photometry settings
aperture_type: "global"
fwhm_correction: true
show_plots: false

# SED fitting settings
use_sbipp: true
sbi_model: "zfree_GPD2W"
sed_mode: "test"
```

### JSON Example (`config_examples/photometry_sed.json`)

```json
{
  "name": "SN2019xyz",
  "ra": 180.5,
  "dec": -30.2,
  "host_ra": 180.502,
  "host_dec": -30.198,
  "aperture_type": "global",
  "use_sbipp": true,
  "sbi_model": "zfix_GPD2W"
}
```

## Common Workflows

### 1. Complete Analysis for a New Transient

```bash
# Using command line
./frankenblast_cli.py full \
    --name SN2023abc \
    --ra 123.456 \
    --dec -45.678 \
    --verbose \
    --log-file sn2023abc.log

# Using Python
from frankenblast import FrankenBlast
fb = FrankenBlast('SN2023abc', ra=123.456, dec=-45.678)
results = fb.run_full_pipeline()
```

### 2. Rerun Photometry with Different Apertures

```bash
# First run with global aperture
./frankenblast_cli.py photometry \
    --name SN2023abc \
    --ra 123.456 \
    --dec -45.678 \
    --host-ra 123.457 \
    --host-dec -45.677 \
    --aperture-type global \
    --photometry-output global_phot.json

# Then run with local aperture
./frankenblast_cli.py photometry \
    --name SN2023abc \
    --ra 123.456 \
    --dec -45.678 \
    --host-ra 123.457 \
    --host-dec -45.677 \
    --aperture-type local \
    --photometry-output local_phot.json
```

### 3. Batch Processing Multiple Transients

```bash
# Create CSV file with transient list
cat > transients.csv << EOF
name,ra,dec,redshift
SN2023a,10.1,20.2,0.03
SN2023b,30.3,40.4,0.05
SN2023c,50.5,60.6,
EOF

# Run batch processing
./batch_process.py transients.csv \
    --output-dir results_2023 \
    --steps host photometry sed
```

### 4. Using Configuration Files

```bash
# Create custom configuration
cat > my_config.yaml << EOF
name: "SN2023xyz"
ra: 100.123
dec: -20.456
prost_samples: 2000
aperture_type: "global"
use_sbipp: true
sbi_model: "zfree_GPD2W"
verbose: true
EOF

# Run with configuration
./frankenblast_cli.py full --config my_config.yaml
```

## Environment Variables

Ensure these environment variables are set (via `settings.sh`):

```bash
export PROST_PATH="/path/to/prostdb"
export SBIPP_ROOT="/path/to/data/SBI"
export SBIPP_PHOT_ROOT="/path/to/data/sbipp_phot"
export SBIPP_TRAINING_ROOT="/path/to/data/sbi_training_sets"
export SED_OUTPUT_ROOT="/path/to/data/sed_output"
```

## Output Files

FrankenBlast generates several output files:

1. **Host Association**: `prostdb/hosts_YYYYMMDD.csv`
2. **Photometry Results**: `<name>_photometry.json`
3. **SED Fitting**: `data/sed_output/<name>/<name>_global.h5`
4. **Logs**: As specified with `--log-file`

## Troubleshooting

### Common Issues

1. **Missing SBI Models**
   ```
   Error: SBI model file not found
   Solution: Download models from Zenodo (see README)
   ```

2. **PanSTARRS Issues**
   ```
   Error: PanSTARRS host association failing
   Solution: Remove 'panstarrs' from catalog list or apply fix in README
   ```

3. **Environment Variables Not Set**
   ```
   Error: Missing required environment variables
   Solution: Run 'source settings.sh'
   ```

### Debug Mode

Run with verbose output for debugging:
```bash
./frankenblast_cli.py full --name SN2019ulo --ra 20.509 --dec -60.571 \
    --verbose --log-file debug.log
```

## Performance Tips

1. **Batch Processing**: Use `--parallel` with caution, as some operations may conflict
2. **SBI++ vs Prospector**: SBI++ is ~100x faster but less flexible
3. **Catalog Selection**: Excluding PanSTARRS can speed up host association
4. **Aperture Type**: Global apertures are generally more reliable for host galaxies

## Examples Repository

Find more examples in the `config_examples/` directory:
- `full_pipeline.yaml`: Complete pipeline configuration
- `host_only.yaml`: Host association only
- `photometry_sed.json`: Photometry and SED fitting
- `transient_list.csv`: Example CSV for batch processing

## Support

For issues or questions:
- Check the main README.md for known issues
- Contact: anya.nugent[at]cfa.harvard.edu