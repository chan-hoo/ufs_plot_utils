import tempfile
import yaml
from ufs_plot_utils.pipeline import Pipeline


def make_cfg():
    return {
        "input": {
            "datasets": [
                {
                    "name": "ds",
                    "data_kind": "analysis",

                    "data": {
                        "path": ".",
                        "filename": "f.nc",
                        "file_type": "file",
                        "var_list": ["var"],
                        "z_index": None,
                        "time_index": 0
                    },

                    "geo": {
                        "path": ".",
                        "filename": "geo.nc",
                        "file_type": "file"
                    },

                    "colormap": {},
                    "range": {}
                }
            ]
        },
        "plot": {},
        "output": {
            "path": "./out"
        }
    }


def test_pipeline_builds_tasks():
    cfg = make_cfg()
    pipeline = Pipeline(cfg)

    builder = pipeline._build_dataset_map()

    assert "ds" in builder
