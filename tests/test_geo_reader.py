from ufs_plot_utils.geo import GeoReader


class Dummy:
    geo_file_type = "file"
    geo_path = "."
    geo_filename = "dummy.nc"


def test_geo_reader_init():
    g = GeoReader(Dummy())
    assert g.dataset is not None
