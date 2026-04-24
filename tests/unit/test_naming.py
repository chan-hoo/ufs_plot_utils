from ufs_plot_utils.naming import NameBuilder


def test_build_filename():
    cfg = {
        "input": {},
        "output": {"prefix": "p"},
    }

    nb = NameBuilder(cfg)
    name = nb.build_filename("temp", "ds", 10)

    assert "temp" in name
    assert "ds" in name
