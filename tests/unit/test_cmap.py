from ufs_plot_utils.cmap import PlotStyleResolver


def test_resolver(sample_da_tile):
    class Dummy:
        colormap = {}
        range = {}

    r = PlotStyleResolver(Dummy())
    style = r.resolve("temp", sample_da_tile)

    assert style.cmap is not None
