# FrankenBlast-Host 🚀

[![Python](https://img.shields.io/badge/python-3.10.15-blue.svg)](https://www.python.org/downloads/release/python-31015/)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17555070.svg)](https://doi.org/10.5281/zenodo.17555070)

Code for **rapid transient host association**, **photometry**, and **stellar population modeling**.

## 📖 Citation
If you use **FrankenBlast**, please cite:

- **Nugent et al. 2025** (FrankenBlast)
  [ADS link](https://ui.adsabs.harvard.edu/abs/2025arXiv250908874N/abstract)
- **Jones et al. 2024** ([BLAST web application](https://blast.scimma.org/))  
  [ADS link](https://ui.adsabs.harvard.edu/abs/2024arXiv241017322J/abstract)

---

## ⚙️ Installation

### Environment
The exact conda environment is specified in `requirements.txt`.

FrankenBlast requires **Python 3.10.15**.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/anugent96/frankenblast-host.git
   cd frankenblast-host
   ```

2. Create the environment:
   ```bash
   conda create --name frankenblast python=3.10
   conda activate frankenblast
   pip install -r requirements.txt
   ```

3. Add custom paths from `settings.sh` to your shell configuration file (`.zshrc`, `.bashrc`, or `.bash_profile`).

### Dependencies
Make sure the following packages are installed via `pip` or `conda`:
```
numpy, scipy, astro-prospector, python-fsps (and FSPS), sedpy, astro-prost, astroquery, 
corner, dustmaps, extinction, jupyter, pandas, sbi, seaborn, tensorflow, matplotlib
```

---

## 📂 Data Access

The **SBI++ trained models** for host SED fitting are too large for GitHub.  
Please download them from:

[Zenodo link](https://doi.org/10.5281/zenodo.16953205)

Files to download:
- `sbipp_phot.zip`
- `sbi_training_sets.zip`

Place these in the `./data/` directory and unzip.

---

## 📓 Tutorials

- **[FrankenBlast Tutorial.ipynb](./FrankenBlast%20Tutorial.ipynb)** — step-by-step guide to using FrankenBlast.  
- SBI++ host SED fitting with LSST data — *tutorial coming soon*, although all trained models are currently available.

---

## 🛠️ Known Issues

We are currently experiencing issues with the **astro_prost** PanSTARRS host association.  

### Workarounds:
1. **Edit `astro_prost`**  
   Comment out lines **2829–2830** in `helpers.py`:
   ```python
   # galaxies["redshift_mean"] = np.nan
   # galaxies["redshift_std"] = np.nan
   ```
   ⚠️ This will return `"0"` as the redshift of the host.

2. **Disable PanSTARRS**  
   In `get_host.py` (line 278), remove `"panstarrs"` from the `catalogs` dictionary.

---

## 📬 Contact

Questions or comments?  
Reach out to **Anya Nugent** → anya.nugent[at]cfa.harvard.edu

---
