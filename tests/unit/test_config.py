from ufs_plot_utils.config import Config
import tempfile
import yaml
import pytest


def test_config_load():
    """
    Test loading a basic configuration file
    """
    cfg_dict = {
        "input": {
            "datasets": []
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        fname = f.name

    cfg = Config(fname)

    assert cfg.get("input") is not None, (
        "Config input section should not be None"
    )


# =================================================================== CHJ ===

def test_config_nested_get():
    """
    Test nested configuration retrieval
    """
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
    assert isinstance(datasets, list), (
        f'''Expected datasets to be a list, got {type(datasets).__name__}'''
    )
    assert len(datasets) == 1, (
        f'''Expected 1 dataset, got {len(datasets)}'''
    )
    assert datasets[0]["name"] == "fv3", (
        f'''Expected dataset name "fv3", got {datasets[0].get('name')}'''
    )


# =================================================================== CHJ ===

@pytest.mark.parametrize("missing_key", ["nonexistent", "missing_section"])
def test_config_missing_keys(missing_key):
    """
    Test handling of missing configuration keys
    """
    cfg_dict = {
        "input": {
            "datasets": []
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        fname = f.name

    cfg = Config(fname)
    result = cfg.get(missing_key)
    assert result is None, f'''Expected None for missing key "{missing_key}", got {result}'''
