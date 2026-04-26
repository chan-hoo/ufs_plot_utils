import pytest

def test_pipeline_builds_tasks_from_config(tmp_path):
    """
    Integration test: YAML -> Config -> Pipeline -> execution
    """

    from ufs_plot_utils.config import Config
    from ufs_plot_utils.pipeline import Pipeline

    cfg_yaml = """
    input:
      datasets:
        - name: base
          data_kind: increment
          data:
            path: /tmp
            filename: dummy.nc
            file_type: file
            var_list: ["T", "Q"]
          geo:
            path: /tmp
            filename: geo.nc

    plot:
      channels:
        base:
          T: [1, 3]
    """

    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(cfg_yaml)

    cfg = Config(str(cfg_file))
    pipeline = Pipeline(cfg)

    # This is the real integration test
    try:
        pipeline.run_plot_tiles()
    except Exception as e:
        pytest.fail(f'''Pipeline execution failed: {e}''')


# ======================================================================================= CHJ =====
def test_pipeline_runs_with_mock_data(tmp_path, monkeypatch):
    """
    Integration test: Pipeline executes with mocked data sources
    """
    import numpy as np
    import xarray as xr

    from ufs_plot_utils.config import Config
    from ufs_plot_utils.pipeline import Pipeline

    # mock DataReader
    def mock_read_data(self, var_name):
        return xr.DataArray(
            np.random.rand(6, 10, 10),
            dims=("tile", "y", "x"),
            name=var_name
        )

    # mock GeoReader
    def mock_get_geo(self):
        lon = np.zeros((6, 10, 10))
        lat = np.zeros((6, 10, 10))
        return lon, lat

    monkeypatch.setattr(
        "ufs_plot_utils.data.DataReader.read_data",
        mock_read_data
    )

    monkeypatch.setattr(
        "ufs_plot_utils.geo.GeoReader.get_geo",
        mock_get_geo
    )

    # config
    cfg_yaml = """
    input:
      datasets:
        - name: test
          data_kind: increment
          data:
            path: /tmp
            filename: dummy.nc
            var_list: ["T"]
          geo:
            path: /tmp
            filename: geo.nc
    """

    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(cfg_yaml)

    cfg = Config(str(cfg_file))
    pipeline = Pipeline(cfg)

    # This is the real integration step
    pipeline.run_plot_tiles()

    # Basic sanity: pipeline ran without crashing
    assert True
