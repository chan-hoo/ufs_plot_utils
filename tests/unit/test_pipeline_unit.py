from ufs_plot_utils.pipeline import Pipeline


class FakeDataset:
    def __init__(self):
        self.name = "ds"
        self.data_kind = "analysis"
        self.var_list = ["var"]


class FakeConfig:
    def get(self, *keys, default=None):
        if keys == ("input", "datasets"):
            return [{
                "name": "ds",
                "data_kind": "analysis",
                "path": ".",
                "filename": "f.nc",
                "file_type": "file",
                "var_list": ["var"]
            }]
        return default


def test_pipeline_dataset_loading():
    pipeline = Pipeline(FakeConfig())

    assert len(pipeline.datasets) == 1
    assert pipeline.datasets[0].name == "ds"
