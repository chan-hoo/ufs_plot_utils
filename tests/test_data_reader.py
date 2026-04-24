import xarray as xr
import numpy as np
from ufs_plot_utils.data import DataReader


class DummyDataset:
    def __init__(self):
        self.path = "."
        self.filename = "file.nc"
        self.file_type = "file"
        self.z_index = None
        self.time_index = 0
        self.data_kind = "analysis"


def test_slice_time():
    ds = xr.Dataset({
        "var": (("time", "y", "x"), np.random.rand(2, 5, 5))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], None, 0)

    assert "time" not in da.dims


def test_open_dataset_mock(monkeypatch):
    import xarray as xr

    def fake_open(*args, **kwargs):
        return xr.Dataset({"var": (("y", "x"), np.ones((2, 2)))})

    monkeypatch.setattr(xr, "open_dataset", fake_open)

    reader = DataReader(DummyDataset())
    reader._open_dataset()

    assert reader.xr_ds is not None

