import xarray as xr
import numpy as np
from ufs_plot_utils.tasks import PlotTask
from ufs_plot_utils.tasks import TaskBuilder

class DummyReader:
    def get_data(self, *args, **kwargs):
        return xr.DataArray(
            np.random.rand(6, 5, 5),
            dims=("tile", "y", "x")
        )


class DummyPlotter:
    def plot_data_tiles(self, *args, **kwargs):
        class Fig:
            pass
        return Fig()


class DummyOutput:
    def save_figure(self, *args, **kwargs):
        return "ok"


class DummyNamer:
    def build_title(self, *a, **k): return "title"
    def build_filename(self, *a, **k): return "file"


def test_plot_task_runs():
    task = PlotTask(
        dataset=type("D", (), {"name":"ds","z_index":None}),
        varname="var",
        data_reader=DummyReader(),
        geo=(None, None),
        plotter=DummyPlotter(),
        output=DummyOutput(),
        namer=DummyNamer(),
    )

    task.run()


class FakePipeline:
    def __init__(self):
        self.datasets = []


def test_task_builder_empty():
    builder = TaskBuilder(FakePipeline())
    tasks = builder.build_plot_tasks()

    assert isinstance(tasks, list)
