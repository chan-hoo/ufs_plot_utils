import numpy as np
import xarray as xr
from ufs_plot_utils.data import DataReader


class DummyDataset:
    def __init__(self):
        self.path = "."
        self.filename = "dummy.nc"
        self.file_type = "file"
        self.z_index = None
        self.time_index = 0


def test_slice_time():
    ds = xr.Dataset({
        "var": (("time", "y", "x"), np.random.rand(2, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], None, 0)

    assert "time" not in da.dims
