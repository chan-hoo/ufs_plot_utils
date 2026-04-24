import pytest
from ufs_plot_utils.dataset import Dataset


def test_dataset_valid(dataset_cfg):
    ds = Dataset(dataset_cfg)

    assert ds.name == "ds"
    assert ds.filename == "f.nc"
    assert ds.var_list == ["var"]


def test_dataset_missing_filename():
    cfg = {"name": "bad", "data": {}}

    with pytest.raises(ValueError):
        Dataset(cfg)
