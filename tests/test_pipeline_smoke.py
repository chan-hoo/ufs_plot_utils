import tempfile
import yaml
from ufs_plot_utils.config import Config
from ufs_plot_utils.pipeline import Pipeline


def make_cfg():
    data = {
        "input": {
            "datasets": [{
                "name": "ds",
                "data_kind": "analysis",
                "path": ".",
                "filename": "f.nc",
                "file_type": "file",
                "var_list": ["var"]
            }]
        },
        "output": {
            "path": "./out"
        },
        "plot": {}
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump(data, f)
        return Config(f.name)


def test_pipeline_instantiation():
    cfg = make_cfg()

    pipeline = Pipeline(cfg)

    assert len(pipeline.datasets) == 1
    assert pipeline.datasets[0].name == "ds"
