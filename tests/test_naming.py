from ufs_plot_utils.naming import NameBuilder


def test_build_filename(dummy_cfg):
    nb = NameBuilder(dummy_cfg)

    name = nb.build_filename("temp", "ds", 10)

    assert "temp" in name
    assert "ds" in name
    assert "z010" in name


def test_build_title_fallback(dummy_cfg):
    nb = NameBuilder(dummy_cfg)

    title = nb.build_title("temp", "ds", 0)

    assert "temp" in title

