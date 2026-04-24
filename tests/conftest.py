import pytest
import numpy as np
import xarray as xr
import yaml
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ufs_plot_utils.config import Config


# ============================================================
# CONFIG FIXTURES
# ============================================================

@pytest.fixture
def cfg_dict():
    return {
        "input": {"datasets": []},
        "output": {"path": "./out"},
        "plot": {}
    }


@pytest.fixture
def cfg_file(cfg_dict):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        yield f.name


@pytest.fixture
def cfg(cfg_file):
    return Config(cfg_file)


# ============================================================
# DATA FIXTURES
# ============================================================

@pytest.fixture
def sample_da_tile():
    data = np.random.rand(6, 10, 10)
    return xr.DataArray(data, dims=("tile", "yaxis_1", "xaxis_1"))


@pytest.fixture
def sample_da_grid():
    data = np.random.rand(6, 10, 10)
    return xr.DataArray(data, dims=("tile", "grid_yt", "grid_xt"))


@pytest.fixture
def zero_da():
    return xr.DataArray(np.zeros((6, 10, 10)), dims=("tile", "y", "x"))


# ============================================================
# FAKE PIPELINE (for TaskBuilder)
# ============================================================

@pytest.fixture
def fake_pipeline():
    class Fake:
        def __init__(self):
            self.datasets = []
            self.plotter = None
            self.output = None
            self.names = None
    return Fake()


# ============================================================
# DATASET CONFIG (VALID STRUCTURE)
# ============================================================

@pytest.fixture
def dataset_cfg():
    return {
        "name": "ds",
        "data_kind": "analysis",
        "title": "Test",

        "geo": {
            "path": ".",
            "filename": "geo.nc",
            "file_type": "file"
        },

        "data": {
            "path": ".",
            "filename": "f.nc",
            "file_type": "file",
            "var_list": ["var"],
            "z_index": None,
            "time_index": 0
        },

        "colormap": {},
        "range": {}
    }
