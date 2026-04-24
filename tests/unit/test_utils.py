import numpy as np
from ufs_plot_utils.utils import normalize_tile_dims


def test_normalize(sample_da_tile):
    da = normalize_tile_dims(sample_da_tile)
    assert da.dims == ("tile", "y", "x")
    assert da.shape == (6, 10, 10)


def test_preserve_values(sample_da_tile):
    da = normalize_tile_dims(sample_da_tile)
    assert np.allclose(sample_da_tile.values, da.values)
