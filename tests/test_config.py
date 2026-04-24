import tempfile
import yaml
from ufs_plot_utils.config import Config


def test_config_load():
    data = {"input": {"datasets": []}}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(data, f)
        cfg = Config(f.name)

    assert cfg.get("input") is not None


def test_config_nested():
    data = {"input": {"datasets": [{"name": "x"}]}}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(data, f)
        cfg = Config(f.name)

    assert isinstance(cfg.get("input", "datasets"), list)

