from ufs_plot_utils.pipeline import Pipeline


def test_pipeline_instantiation(dummy_cfg):
    dummy_cfg["input"]["datasets"] = [{
        "name": "ds",
        "data_kind": "analysis",
        "path": ".",
        "filename": "f.nc",
        "file_type": "file",
        "var_list": ["var"]
    }]

    pipeline = Pipeline(type("C", (), {"get": lambda self,*a,**k: dummy_cfg})())

    assert pipeline.datasets

