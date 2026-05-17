import pytest
import numpy as np
import xarray as xr
import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


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
    """
    Create a zero-filled DataArray for testing
    """
    return xr.DataArray(
        np.zeros((6, 96, 96)),
        dims=("tile", "y", "x")
    )


@pytest.fixture(autouse=True)
def disable_plotting(monkeypatch):

    monkeypatch.setattr(
        "ufs_plot_utils.plot.Plotter.plot_data_tiles",
        lambda *a, **k: None
    )

    monkeypatch.setattr(
        "ufs_plot_utils.plot.Plotter.plot_data_grid",
        lambda *a, **k: None
    )

    monkeypatch.setattr(
        "ufs_plot_utils.plot.Plotter.plot_data_scatter",
        lambda *a, **k: None
    )


# Automatically applies to all tests
@pytest.fixture(autouse=True)
def disable_plot_saving(monkeypatch):
    monkeypatch.setattr(
        "ufs_plot_utils.output.OutputManager.save_figure",
        lambda *a, **k: None
    )
