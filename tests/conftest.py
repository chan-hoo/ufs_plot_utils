import pytest
import numpy as np
import xarray as xr
from types import SimpleNamespace


@pytest.fixture
def sample_da_tile():
    data = np.random.rand(6, 10, 10)
    return xr.DataArray(
        data,
        dims=("tile", "yaxis_1", "xaxis_1"),
        name="var"
    )


@pytest.fixture
def sample_da_grid():
    data = np.random.rand(6, 10, 10)
    return xr.DataArray(
        data,
        dims=("tile", "grid_yt", "grid_xt"),
        name="var"
    )


@pytest.fixture
def zero_da():
    return xr.DataArray(
        np.zeros((6, 10, 10)),
        dims=("tile", "y", "x")
    )


@pytest.fixture
def dummy_dataset():
    return SimpleNamespace(
        name="test_ds",
        data_kind="analysis",
        path=".",
        filename="file.nc",
        file_type="file",
        var_list=["var"],
        z_index=None,
        time_index=0,
        colormap={},
        range={}
    )


@pytest.fixture
def dummy_cfg():
    return {
        "input": {
            "datasets": []
        },
        "output": {
            "path": "./out"
        },
        "plot": {}
    }

