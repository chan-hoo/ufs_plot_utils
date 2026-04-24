from ufs_plot_utils.tasks import TaskBuilder


def test_task_builder_empty(fake_pipeline):
    builder = TaskBuilder(fake_pipeline)
    tasks = builder.build_plot_tasks()

    assert isinstance(tasks, list)
    assert len(tasks) == 0
