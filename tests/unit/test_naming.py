import pytest
from ufs_plot_utils.naming import NameBuilder


def test_build_filename(cfg_dict):
    nb = NameBuilder(cfg_dict)

    name = nb.build_filename("temp", "ds", 10)

    assert isinstance(name, str)
    assert "temp" in name
    assert "ds" in name
