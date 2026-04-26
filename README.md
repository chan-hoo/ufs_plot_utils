# ufs_plot_utils
Plotting utilities for UFS applications

## Quick-start-guide

1. Set up the conda/python environment:
```
cd env

vim build_conda_env.sh
(or)
vim build_venv.sh
(follow the steps)
```

- If you have already set it up, activate it:
```
module load miniconda3
conda activate plot_pyenv
(or)
source env/plot_pyenv/bin/activate
```

2. Run a sample script:
```
cd ../configs
./run_plot_task.py -i config_[case].yaml -l INFO
```

3. Deactivate the conda/python environment:
```
conda deactivate
(or)
deactivate
```

## Read-the-Docs User's Guide
User's guide: [click this link](https://ufs-plot-utils.readthedocs.io/en/latest/) (under development)
