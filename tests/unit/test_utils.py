import numpy as np
import pytest
from ufs_plot_utils.utils import (
    normalize_tile_dims,
    normalize_geo_dims,
)


def test_normalize_yaxis(sample_da_tile):
    """
    Test normalizing yaxis_1/xaxis_1 dimensions to y/x
    """

    da = normalize_tile_dims(sample_da_tile)

    assert da.dims == ("tile", "y", "x"), (
        f'''Expected dims ("tile", "y", "x"), got {da.dims}'''
    )
    assert da.shape == (6, 96, 96), (
        f'''Expected shape (6, 96, 96), got {da.shape}'''
    )


# =================================================================== CHJ ===

def test_normalize_grid(sample_da_grid):
    """
    Test normalizing grid_yt/grid_xt dimensions to y/x
    """

    da = normalize_tile_dims(sample_da_grid)

    assert da.dims == ("tile", "y", "x"), (
        f'''Expected normalized dims ("tile", "y", "x"), got {da.dims}'''
    )
    assert da.shape == (6, 96, 96), (
        f'''Expected shape (6, 96, 96), got {da.shape}'''
    )


# =================================================================== CHJ ===

def test_normalize_preserves_values(sample_da_tile):
    """
    Test that normalization preserves data values
    """

    da2 = normalize_tile_dims(sample_da_tile)

    assert np.allclose(sample_da_tile.values, da2.values), (
        "Normalized data should preserve original values"
    )
    assert np.array_equal(sample_da_tile.values, da2.values), (
        "Expected exact value preservation for all elements"
    )


# =================================================================== CHJ ===

def test_normalize_already_normalized():
    """
    Test normalizing already normalized dimensions
    """

    import xarray as xr
    data = np.random.rand(6, 96, 96)
    da = xr.DataArray(
        data,
        dims=("tile", "y", "x"),
        name="test_var"
    )

    da_normalized = normalize_tile_dims(da)
    assert da_normalized.dims == ("tile", "y", "x"), (
        "Already normalized dims should remain unchanged"
    )


# =================================================================== CHJ ===

def test_normalize_geo_dims_fv3():
    """
    FV3 tiled normalization
    """

    lat = np.random.rand(6, 96, 96)
    lon = np.random.rand(6, 96, 96)

    lat2, lon2 = normalize_geo_dims(lat, lon)

    assert lat2.shape == (6, 96, 96)
    assert lon2.shape == (6, 96, 96)


# =================================================================== CHJ ===

def test_normalize_geo_dims_mom6():
    """
    MOM6 structured-grid normalization
    """

    lat = np.random.rand(320, 360)
    lon = np.random.rand(320, 360)

    lat2, lon2 = normalize_geo_dims(
        lat,
        lon,
        add_tile_dim=False,
    )

    assert lat2.shape == (320, 360)
    assert lon2.shape == (320, 360)


# =================================================================== CHJ ===

def test_normalize_geo_dims_mismatch():
    """
    Shape mismatch should fail
    """

    lat = np.random.rand(320, 360)
    lon = np.random.rand(300, 360)

    with pytest.raises(ValueError):
        normalize_geo_dims(
            lat,
            lon,
            add_tile_dim=False,
        )


# =================================================================== CHJ ===
@pytest.mark.parametrize("shape", [(1, 96, 96), (6, 48, 48), (12, 192, 192)])
def test_normalize_various_shapes(shape):
    """
    Test normalizing dimensions with various array shapes
    """

    import xarray as xr
    data = np.random.rand(*shape)
    da = xr.DataArray(
        data,
        dims=("tile", "grid_yt", "grid_xt"),
        name="test_var"
    )

    da_normalized = normalize_tile_dims(da)
    assert da_normalized.shape == shape, (
        f'''Shape {shape} should be preserved after normalization, '''
        f'''but got {da_normalized.shape}'''
    )
    assert da_normalized.dims == ("tile", "y", "x"), (
        f'''Dims should be normalized to ("tile", "y", "x") for {shape}'''
    )
