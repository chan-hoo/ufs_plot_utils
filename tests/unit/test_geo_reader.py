import pytest
import xarray as xr
import numpy as np
from ufs_plot_utils.geo import GeoReader


class DummyGeoConfig:
    def __init__(self, geo_file_type="file", geo_path=".", geo_filename="dummy.nc"):
        self.geo_file_type = geo_file_type
        self.geo_path = geo_path
        self.geo_filename = geo_filename


# ======================================================================================= CHJ =====
def test_geo_reader_init(monkeypatch):
    """
    Unit test: GeoReader initializes without real file access
    """

    def mock_open_dataset(*args, **kwargs):
        return xr.Dataset({
            "lon": (("tile", "y", "x"), [[[0]]]),
            "lat": (("tile", "y", "x"), [[[0]]])
        })

    monkeypatch.setattr(
        "xarray.open_dataset",
        mock_open_dataset
    )

    config = DummyGeoConfig()
    g = GeoReader(config)

    assert g.dataset is not None


# ======================================================================================= CHJ =====
@pytest.mark.parametrize("file_type", ["file", "s3", "url"])
def test_geo_reader_file_types(monkeypatch, file_type):
    """
    Unit test: GeoReader handles different file types
    """

    def mock_open_dataset(*args, **kwargs):
        return xr.Dataset()

    monkeypatch.setattr("xarray.open_dataset", mock_open_dataset)

    config = DummyGeoConfig(geo_file_type=file_type)
    g = GeoReader(config)

    assert g.dataset is not None


# ======================================================================================= CHJ =====
def test_geo_reader_path_join(monkeypatch):

    called_paths = []

    def mock_open_dataset(path, *args, **kwargs):
        called_paths.append(path)
        return xr.Dataset({
            "lat": (("x",), np.array([0, 1])),
            "lon": (("x",), np.array([0, 1]))
        })

    monkeypatch.setattr(
        "ufs_plot_utils.geo.xr.open_dataset",
        mock_open_dataset
    )

    class DummyGeoConfig:
        def __init__(self):
            self.geo_file_type = "file"
            self.geo_path = "/data"
            self.geo_filename = "geo.nc"
            self.data_kind = "analysis"

    config = DummyGeoConfig()

    g = GeoReader(config)
    g.get_geo()

    assert called_paths, "open_dataset was not called"
    assert "/data/geo.nc" in called_paths[0]
