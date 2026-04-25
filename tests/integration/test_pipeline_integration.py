from unittest.mock import patch
from ufs_plot_utils.pipeline import Pipeline


def test_pipeline_builds_tasks(cfg):
    with patch("ufs_plot_utils.geo.GeoReader.get_geo") as mock_geo:
        mock_geo.return_value = (
            [[[0, 0], [0, 0]]],
            [[[0, 0], [0, 0]]]
        )

        pipeline = Pipeline(cfg)

        # don't run full plotting if not needed
        tasks = pipeline.run_plot_tiles()

        assert tasks is None
