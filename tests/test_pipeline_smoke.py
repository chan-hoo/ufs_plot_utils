import pytest


def test_pipeline_import():
    """
    Smoke test: Verify pipeline module can be imported
    """
    import ufs_plot_utils.pipeline as p
    assert p is not None, f'''Pipeline module should be importable'''


def test_pipeline_has_main_components():
    """
    Verify pipeline module contains expected components
    """
    import ufs_plot_utils.pipeline as p
    
    expected_attrs = ["Pipeline", "run", "execute"]
    for attr in expected_attrs:
        has_attr = hasattr(p, attr)
        assert has_attr, f'''Pipeline module should have "{attr}" component, missing components'''


def test_pipeline_initialization():
    """
    Test basic pipeline initialization
    """
    try:
        import ufs_plot_utils.pipeline as p
        pipeline = p.Pipeline()
        assert pipeline is not None, f'''Pipeline instance should be created'''
    except Exception as e:
        pytest.fail(f'''Pipeline initialization failed: {str(e)}''')

