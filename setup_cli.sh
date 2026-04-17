#!/bin/bash

# FrankenBlast CLI Setup Script
# This script prepares the FrankenBlast CLI tools for use

echo "========================================="
echo "FrankenBlast CLI Setup"
echo "========================================="
echo ""

# Make scripts executable
echo "Making CLI scripts executable..."
chmod +x frankenblast_cli.py 2>/dev/null || echo "  Warning: frankenblast_cli.py not found"
chmod +x frankenblast.py 2>/dev/null || echo "  Warning: frankenblast.py not found"
chmod +x batch_process.py 2>/dev/null || echo "  Warning: batch_process.py not found"
echo "✓ Scripts made executable"
echo ""

# Check for required environment variables
echo "Checking environment variables..."
MISSING_VARS=()

if [ -z "$PROST_PATH" ]; then
    MISSING_VARS+=("PROST_PATH")
fi

if [ -z "$SBIPP_ROOT" ]; then
    MISSING_VARS+=("SBIPP_ROOT")
fi

if [ -z "$SBIPP_PHOT_ROOT" ]; then
    MISSING_VARS+=("SBIPP_PHOT_ROOT")
fi

if [ -z "$SBIPP_TRAINING_ROOT" ]; then
    MISSING_VARS+=("SBIPP_TRAINING_ROOT")
fi

if [ -z "$SED_OUTPUT_ROOT" ]; then
    MISSING_VARS+=("SED_OUTPUT_ROOT")
fi

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "✓ All required environment variables are set"
else
    echo "✗ Missing environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please run: source settings.sh"
fi
echo ""

# Check for Python and required packages
echo "Checking Python environment..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "✓ Python found: $PYTHON_VERSION"
    
    # Check for required packages
    echo "  Checking required packages..."
    PACKAGES=("numpy" "astropy" "pandas" "prospect" "astro_prost")
    MISSING_PACKAGES=()
    
    for package in "${PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            echo "    ✓ $package"
        else
            MISSING_PACKAGES+=("$package")
            echo "    ✗ $package (missing)"
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        echo ""
        echo "  Missing packages. Install with:"
        echo "  pip install -r requirements.txt"
    fi
else
    echo "✗ Python not found in current environment"
    echo "  Please activate the frankenblast conda environment:"
    echo "  conda activate frankenblast"
fi
echo ""

# Check for SBI model files
echo "Checking for SBI model files..."
if [ -d "data/SBI" ]; then
    if [ -f "data/SBI/SBI_model_zfree_GPD2W_global.pt" ] && [ -f "data/SBI/SBI_model_zfix_GPD2W_global.pt" ]; then
        echo "✓ SBI model files found"
    else
        echo "✗ SBI model files not found"
        echo "  Please download from Zenodo (see README.md)"
        echo "  https://doi.org/10.5281/zenodo.16953205"
    fi
else
    echo "✗ data/SBI directory not found"
    echo "  Please download SBI models from Zenodo"
fi
echo ""

# Create necessary directories
echo "Creating output directories..."
mkdir -p cutouts 2>/dev/null
mkdir -p prostdb 2>/dev/null
mkdir -p data/sed_output 2>/dev/null
mkdir -p batch_results 2>/dev/null
echo "✓ Output directories created"
echo ""

# Display quick start guide
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Quick Start Commands:"
echo ""
echo "1. Test with a single transient:"
echo "   ./frankenblast_cli.py full --name SN2019ulo --ra 20.509 --dec -60.571"
echo ""
echo "2. Use configuration file:"
echo "   ./frankenblast_cli.py full --config config_examples/full_pipeline.yaml"
echo ""
echo "3. Batch process multiple transients:"
echo "   ./batch_process.py config_examples/transient_list.csv"
echo ""
echo "4. Python interface:"
echo "   python"
echo "   >>> from frankenblast import FrankenBlast"
echo "   >>> fb = FrankenBlast('SN2019ulo', ra=20.509, dec=-60.571)"
echo "   >>> fb.run_full_pipeline()"
echo ""
echo "For full documentation, see CLI_USAGE.md"
echo ""