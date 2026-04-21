module purge
module load python
rm -rf plot_pyenv
python3 -m venv plot_pyenv
source plot_pyenv/bin/activate
pip install --upgrade pip
pip install -r plot_env_list.txt
pip list
