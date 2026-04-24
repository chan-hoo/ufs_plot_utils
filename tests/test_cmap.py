import numpy as np
import xarray as xr
from ufs_plot_utils.cmap import PlotStyleResolver


class Dummy:
    data_kind = "analysis"
    colormap = {}
    range = {}


def test_resolve_basic():
    da = xr.DataArray(np.random.rand(10, 10), dims=("y", "x"))

    r = PlotStyleResolver(Dummy())
    style = r.resolve("temp", da)

    assert style.vmin < style.vmax
    assert style.cmap is not None


def test_difference_mode():
    da = xr.DataArray(np.random.randn(10, 10), dims=("y", "x"))

    r = PlotStyleResolver(Dummy(), is_difference=True)
    style = r.resolve("temp", da)

    assert style.vmin < 0
    assert style.vmax > 0
