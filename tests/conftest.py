# tests/conftest.py
import pytest
from types import SimpleNamespace
from ufs_plot_utils.config import Config


@pytest.fixture
def raw_cfg():
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
def cfg(raw_cfg):
    """
    Real Config object used by Pipeline.
    """
    return Config(raw_cfg)


@pytest.fixture
def cfg_dict(raw_cfg):
    """
    Plain dict version for unit tests that bypass Config.
    """
    return raw_cfg


@pytest.fixture
def fake_dataset_cfg():
    return {
        "name": "ds",
        "data_kind": "analysis",
        "path": ".",
        "filename": "f.nc",
        "file_type": "file",
        "var_list": ["var"]
    }

