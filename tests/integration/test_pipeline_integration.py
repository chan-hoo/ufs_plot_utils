import tempfile
import yaml
from ufs_plot_utils.config import Config
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


def test_pipeline_builds_tasks():
    cfg_dict = make_cfg()

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(cfg_dict, f)
        cfg_file = f.name

    cfg = Config(cfg_file)

    pipeline = Pipeline(cfg)
    tasks = pipeline.run_plot_tiles()

    assert tasks is None  # smoke test only
