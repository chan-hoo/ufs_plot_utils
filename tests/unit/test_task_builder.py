from ufs_plot_utils.tasks import TaskBuilder


class FakePipeline:
    def __init__(self):
        self.datasets = []


def test_task_builder_empty():
    builder = TaskBuilder(FakePipeline())
    tasks = builder.build_plot_tasks()

    assert isinstance(tasks, list)
    assert tasks == []
