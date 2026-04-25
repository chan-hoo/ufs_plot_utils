import tempfile
import yaml
from unittest.mock import patch
from ufs_plot_utils.pipeline import Pipeline


def make_cfg():
    return {
        "input": {
            "datasets": [
                {
                    "name": "ds",
                    "data_kind": "analysis",

                    "geo": {
                        "path": ".",
                        "filename": "geo.nc",
                        "file_type": "file"
                    },

                    "data": {
                        "path": ".",
                        "filename": "f.nc",
                        "file_type": "file",
                        "var_list": ["var"]
                    }
                }
            ]
        },
        "output": {"path": "./out"},
        "plot": {}
    }


def test_pipeline_builds_tasks(cfg):
    with patch("ufs_plot_utils.geo.GeoReader.get_geo") as mock_geo:
        mock_geo.return_value = (
            [[[0]], [[0]]],  # fake lat
            [[[0]], [[0]]]   # fake lon
        )

        pipeline = Pipeline(cfg)
        pipeline.run_plot_tiles()

