import pytest
import numpy as np
import xarray as xr


@pytest.fixture
def sample_da_tile():
    """
    Create a fake tile dataset (tile, y, x)
    """
    data = np.random.rand(6, 96, 96)

    da = xr.DataArray(
        data,
        dims=("tile", "yaxis_1", "xaxis_1"),
        name="test_var"
    )
    return da


@pytest.fixture
def sample_da_grid():
    """
    Another format (grid_yt/grid_xt)
    """
    data = np.random.rand(6, 96, 96)

    da = xr.DataArray(
        data,
        dims=("tile", "grid_yt", "grid_xt"),
        name="test_var"
    )
    return da


@pytest.fixture
def zero_da():
    return xr.DataArray(
        np.zeros((6, 96, 96)),
        dims=("tile", "y", "x")
    )
