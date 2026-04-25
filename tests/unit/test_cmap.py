from ufs_plot_utils.cmap import PlotStyleResolver


def test_plot_style_resolver_exists():
    resolver = PlotStyleResolver({})
    assert resolver is not None
