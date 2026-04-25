from ufs_plot_utils.config import Config
import tempfile
import yaml


def test_config_load():
    cfg_dict = {
        "input": {
            "datasets": []
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        fname = f.name

    cfg = Config(fname)

    assert cfg.get("input") is not None


def test_config_nested_get():
    cfg_dict = {
        "input": {
            "datasets": [{"name": "fv3"}]
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        fname = f.name

    cfg = Config(fname)

    datasets = cfg.get("input", "datasets")
    assert isinstance(datasets, list)
