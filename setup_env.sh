#!/bin/bash

set -e

module purge
module load python

echo "Python:"
python3 --version

echo "Creating virtual environment..."
python3 -m venv .venv

source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing ufs_plot_utils..."
python -m pip install -e ".[dev]"
# If you don't want to install the optional packages in pyproject.toml, run the following instead:
# python -m pip install .

echo
echo "Installation complete."
echo
echo "Activate the environment with:"
echo "    source .venv/bin/activate"
echo
echo "Check installation with:"
echo "    ufs-plot --help"
