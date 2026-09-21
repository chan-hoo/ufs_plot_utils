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
cd ufs_plot_utils
./setup_env.sh
```

- If you have already set it up, activate it:
```bash
source .venv/bin/activate
```

### 3. Run a sample script:
```bash
cd configs
./run_plot_task.py -i config_[case].yaml -l INFO
```

### 4. Deactivate the python environment:
```bash
deactivate
```

## Installed Usage

```bash
ufs-plot -i configs/config.yaml
```

## Read-the-Docs User's Guide
User's guide: [click this link](https://ufs-plot-utils.readthedocs.io/en/latest/)
