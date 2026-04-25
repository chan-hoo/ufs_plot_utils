import pytest
from ufs_plot_utils.geo import GeoReader


class DummyGeoConfig:
    """
    Mock geo configuration object for testing GeoReader
    """
    def __init__(self, geo_file_type="file", geo_path=".", geo_filename="dummy.nc"):
        self.geo_file_type = geo_file_type
        self.geo_path = geo_path
        self.geo_filename = geo_filename


def test_geo_reader_init():
    """
    Test GeoReader initialization
    """
    config = DummyGeoConfig()
    g = GeoReader(config)
    assert g.dataset is not None, f'''GeoReader dataset should be initialized, got {g.dataset}'''


def test_geo_reader_file_type_validation():
    """
    Test GeoReader with different file types
    """
    for file_type in ["file", "s3", "url"]:
        config = DummyGeoConfig(geo_file_type=file_type)
        g = GeoReader(config)
        assert g.dataset is not None, f'''GeoReader should handle file_type: {file_type}'''


def test_geo_reader_config_attributes():
    """
    Test GeoReader respects configuration attributes
    """
    path = "/path/to/data"
    filename = "geo_data.nc"
    config = DummyGeoConfig(geo_path=path, geo_filename=filename)
    
    g = GeoReader(config)
    assert g.dataset is not None, f'''GeoReader should successfully initialize with path={path}, filename={filename}'''

