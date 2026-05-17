# ufs_plot_utils
Plotting tools for UFS applications

---

## Developer Usage (without installation)

### 1. Clone this repository:

**SSH:**
```bash
git clone git@github.com/chan-hoo/ufs_plot_utils.git
```

**HTTPS:**
```bash
git clone https://github.com/chan-hoo/ufs_plot_utils.git
```

### 2. Set up the conda/python environment:
```bash
cd env

vim build_conda_env.sh
# or
vim build_venv.sh
```
Follow the steps inside the script.

- If you have already set it up, activate it:
```bash
module load miniconda3

conda activate plot_pyenv
# or
source env/plot_pyenv/bin/activate
```

### 3. Run a sample script:
```bash
cd ../configs
./run_plot_task.py -i config_[case].yaml -l INFO
```

### 4. Deactivate the conda/python environment:
```bash
conda deactivate
# or
deactivate
```

## Installed Usage

```bash
pip install -e .

ufs-plot -i configs/config.yaml
```

## Read-the-Docs User's Guide
User's guide: [click this link](https://ufs-plot-utils.readthedocs.io/en/latest/)
