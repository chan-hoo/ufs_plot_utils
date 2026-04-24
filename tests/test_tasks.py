import xarray as xr
import numpy as np
from ufs_plot_utils.tasks import PlotTask, DifferenceTask


class DummyReader:
    def get_data(self, *args, **kwargs):
        return xr.DataArray(np.random.rand(6, 5, 5), dims=("tile","y","x"))


def test_plot_task_run(monkeypatch, dummy_dataset):
    def fake_plot(*args, **kwargs):
        class Fig:
            pass
        return Fig()

    class DummyPlotter:
        def plot_data_tiles(self, *a, **k):
            return fake_plot()

    class DummyOutput:
        def save_figure(self, *a, **k):
            return "ok"

    class DummyNamer:
        def build_title(self, *a, **k): return "title"
        def build_filename(self, *a, **k): return "file"

    task = PlotTask(
        dataset=dummy_dataset,
        varname="var",
        data_reader=DummyReader(),
        geo=(np.zeros((6,5,5)), np.zeros((6,5,5))),
        plotter=DummyPlotter(),
        output=DummyOutput(),
        namer=DummyNamer(),
    )

    task.run()

