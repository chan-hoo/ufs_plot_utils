import matplotlib.pyplot as plt
from ufs_plot_utils.output import OutputManager


class DummyCfg:
    def get(self, *args, default=None):
        return "./out"


def test_save(tmp_path):
    cfg = DummyCfg()
    out = OutputManager(cfg)

    fig = plt.figure()

    path = out.save_figure(fig, "test.png", close=True)

    assert path.endswith("test.png")

