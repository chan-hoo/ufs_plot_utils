import xarray as xr
import numpy as np
from ufs_plot_utils.data import DataReader


class Dummy:
    def __init__(self):
        self.path = "."
        self.filename = "x.nc"
        self.file_type = "file"
        self.z_index = None
        self.time_index = 0


def test_slice_time():
    ds = xr.Dataset({
        "var": (("time", "y", "x"), np.random.rand(2, 4, 4))
    })

    r = DataReader(Dummy())
    da = r._slice_data(ds["var"], None, 0)

    assert "time" not in da.dims
