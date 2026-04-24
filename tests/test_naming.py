import tempfile
import yaml
from ufs_plot_utils.config import Config
from ufs_plot_utils.naming import NameBuilder


def make_cfg(d):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(d, f)
        return Config(f.name)


def test_build_filename():
    cfg = make_cfg({
        "input": {"datasets": []},
        "output": {"prefix": "PFX"},
        "plot": {}
    })

    nb = NameBuilder(cfg)

    name = nb.build_filename("temp", "ds", 10)

    assert "temp" in name
    assert "ds" in name
    assert "z010" in name


def test_build_title_fallback(dummy_cfg):
    nb = NameBuilder(dummy_cfg)

    title = nb.build_title("temp", "ds", 0)

    assert "temp" in title

