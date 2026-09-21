# ufs_plot_utils
Plotting tools for UFS applications

---

## Quick Start Guide

### 1. Clone repository:

**SSH:**
```bash
git clone git@github.com/chan-hoo/ufs_plot_utils.git
```

**HTTPS:**
```bash
git clone https://github.com/chan-hoo/ufs_plot_utils.git
```

### 2. Set up python environment:
```bash
cd ufs_plot_utils
./setup_env.sh
```

- If you have already set it up, activate it:
```bash
source .venv/bin/activate
```

### 3. Run sample script:
- Run with script:
```bash
cd configs
./run_plot_task.py -i config_[case].yaml -l INFO
```

- Run with executable:
```bash
ufs-plot -i configs/config.yaml
```

### 4. Deactivate python environment:
```bash
deactivate
```

## Read-the-Docs User's Guide
User's guide: [click this link](https://ufs-plot-utils.readthedocs.io/en/latest/)
