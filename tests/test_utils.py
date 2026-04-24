import pytest
import numpy as np
import xarray as xr
from ufs_plot_utils.utils import (
    normalize_tile_dims,
    extract_tile_prefix,
    normalize_geo_dims
)


def test_normalize_tile_dims(sample_da_tile):
    da = normalize_tile_dims(sample_da_tile)
    assert da.dims == ("tile", "y", "x")


def test_normalize_grid(sample_da_grid):
    da = normalize_tile_dims(sample_da_grid)
    assert da.dims == ("tile", "y", "x")


def test_normalize_values_preserved(sample_da_tile):
    da = normalize_tile_dims(sample_da_tile)
    assert np.allclose(sample_da_tile.values, da.values)


def test_missing_tile_dim():
    da = xr.DataArray(np.ones((5, 5)), dims=("y", "x"))

    with pytest.raises(ValueError):
        normalize_tile_dims(da)


def test_extract_tile_prefix():
    assert extract_tile_prefix("abc.tile1.nc") == "abc"
    assert extract_tile_prefix("abc.tile.nc") == "abc"
    assert extract_tile_prefix("abc.nc") == "abc"


def test_normalize_geo_dims_2d():
    lat = np.random.rand(10, 10)
    lon = np.random.rand(10, 10)

    lat2, lon2 = normalize_geo_dims(lat, lon)

    assert lat2.shape == lon2.shape == (1, 10, 10)


def test_normalize_geo_dims_3d():
    lat = np.random.rand(6, 10, 10)
    lon = np.random.rand(6, 10, 10)

    lat2, lon2 = normalize_geo_dims(lat, lon)

    assert lat2.shape == (6, 10, 10)

