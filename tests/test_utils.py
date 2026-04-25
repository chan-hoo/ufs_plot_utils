import numpy as np
from ufs_plot_utils.utils import normalize_tile_dims


def test_normalize_yaxis(sample_da_tile):
    da = normalize_tile_dims(sample_da_tile)

    assert da.dims == ("tile", "y", "x")
    assert da.shape == (6, 96, 96)


def test_normalize_grid(sample_da_grid):
    da = normalize_tile_dims(sample_da_grid)

    assert da.dims == ("tile", "y", "x")


def test_normalize_preserves_values(sample_da_tile):
    da2 = normalize_tile_dims(sample_da_tile)

    assert np.allclose(sample_da_tile.values, da2.values)
