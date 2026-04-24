from ufs_plot_utils.geo import GeoReader


class Dummy:
    geo_file_type = "file"
    geo_path = "."
    geo_filename = "x.nc"


def test_init():
    g = GeoReader(Dummy())
    assert g.dataset.geo_filename == "x.nc"
