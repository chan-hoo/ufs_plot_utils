import pytest
import numpy as np
import xarray as xr
import yaml
import tempfile
import sys
from pathlib import Path

# Ensure package import works in CI
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ufs_plot_utils.config import Config


# ============================================================
# CONFIG FIXTURES
# ============================================================

@pytest.fixture
def dummy_cfg_dict():
    """
    Raw dict config (for unit tests only).
    """
    return {
        "input": {
            "datasets": []
        },
        "output": {
            "path": "./out"
        },
        "plot": {}
    }


@pytest.fixture
def dummy_cfg_file(dummy_cfg_dict):
    """
    Temporary YAML file for Config() integration testing.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(dummy_cfg_dict, f)
        yield f.name


@pytest.fixture
def dummy_cfg(dummy_cfg_file):
    """
    Real Config object (used in integration-style tests).
    """
    return Config(dummy_cfg_file)


# ============================================================
# FAKE PIPELINE (for TaskBuilder unit tests)
# ============================================================

@pytest.fixture
def fake_pipeline():
    """
    Minimal pipeline stub for TaskBuilder unit tests.
    """
    class FakePipeline:
        def __init__(self):
            self.datasets = []
            self.plotter = None
            self.output = None
            self.names = None

    return FakePipeline()


# ============================================================
# XARRAY TEST DATA
# ============================================================

@pytest.fixture
def sample_da_tile():
    """
    Standard tile dataset: (tile, y, x)
    """
    data = np.random.rand(6, 96, 96)

    return xr.DataArray(
        data,
        dims=("tile", "yaxis_1", "xaxis_1"),
        name="test_var"
    )


@pytest.fixture
def sample_da_grid():
    """
    Alternative grid naming: (tile, grid_yt, grid_xt)
    """
    data = np.random.rand(6, 96, 96)

    return xr.DataArray(
        data,
        dims=("tile", "grid_yt", "grid_xt"),
        name="test_var"
    )


@pytest.fixture
def zero_da():
    """
    All-zero dataset for edge-case testing.
    """
    return xr.DataArray(
        np.zeros((6, 96, 96)),
        dims=("tile", "y", "x"),
        name="zero"
    )


# ============================================================
# SMALL UTILITY FIXTURES
# ============================================================

@pytest.fixture
def simple_dataset_config():
    """
    Minimal valid Dataset config for Dataset() unit tests.
    """
    return {
        "name": "ds",
        "data_kind": "analysis",
        "path": ".",
        "filename": "f.nc",
        "file_type": "file",
        "var_list": ["var"],
        "z_index": None,
        "time_index": 0
    }


@pytest.fixture
def sample_dataset_cfg():
    """
    Full dataset config (useful for Dataset + Pipeline integration tests).
    """
    return {
        "name": "ds",
        "data_kind": "forecast",
        "title": "Test Dataset",
        "geo": {
            "path": ".",
            "filename": "geo.nc",
            "file_type": "file"
        },
        "data": {
            "path": ".",
            "filename": "f*.tile*.nc",
            "file_type": "file",
            "var_list": ["var"],
            "z_index": None,
            "time_index": 0
        },
        "colormap": {},
        "range": {}
    }
