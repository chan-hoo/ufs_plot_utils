import numpy as np
import xarray as xr


def test_difference_math():
    a = xr.DataArray(np.ones((6, 5, 5)), dims=("tile","y","x"))
    b = xr.DataArray(np.ones((6, 5, 5))*2, dims=("tile","y","x"))

    diff = b - a

    assert diff.min() == 1
    assert diff.max() == 1
