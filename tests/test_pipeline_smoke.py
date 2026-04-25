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
    
    expected_attrs = ["Pipeline"]
    for attr in expected_attrs:
        has_attr = hasattr(p, attr)
        assert has_attr, f'''Pipeline module should have '{attr}' component'''


def test_pipeline_class_has_methods():
    """
    Verify Pipeline class has expected methods
    """
    import ufs_plot_utils.pipeline as p
    
    expected_methods = ["run_plot_tiles", "run_differences"]
    for method in expected_methods:
        has_method = hasattr(p.Pipeline, method)
        assert has_method, f'''Pipeline class should have '{method}' method, got missing method'''


def test_pipeline_initialization_requires_config():
    """
    Test pipeline initialization with config parameter
    """
    import ufs_plot_utils.pipeline as p
    from unittest.mock import MagicMock
    
    try:
        # Mock config object
        mock_cfg = MagicMock()
        mock_cfg.get.return_value = [{"name": "test_ds"}]
        
        pipeline = p.Pipeline(mock_cfg)
        assert pipeline is not None, f'''Pipeline instance should be created with config'''
        assert hasattr(pipeline, "cfg"), f'''Pipeline should store config'''
    except TypeError as e:
        pytest.fail(f'''Pipeline initialization failed: {str(e)}''')
