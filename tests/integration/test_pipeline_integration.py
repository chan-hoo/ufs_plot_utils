import pytest
from unittest.mock import patch
from ufs_plot_utils.pipeline import Pipeline


def make_cfg(cfg):
    """
    Ensure datasets always exist for pipeline.
    """
    cfg["input"]["datasets"] = [
        {
            "name": "ds",
            "data_kind": "analysis",
            "path": ".",
            "filename": "f.nc",
            "file_type": "file",
            "var_list": ["var"],
            "geo": {
                "path": ".",
                "filename": "geo.nc",
                "file_type": "file"
            }
        }
    ]
    return cfg


def test_pipeline_builds_tasks(cfg_dict):
    cfg_dict = make_cfg(cfg_dict)

    with patch("ufs_plot_utils.geo.GeoReader.get_geo", return_value=(
        [[[0, 0], [0, 0]]],
        [[[0, 0], [0, 0]]]
    )):

        pipeline = Pipeline(cfg_dict)
        tasks = pipeline.build_tasks()

        assert isinstance(tasks, list)
