def test_config_get(cfg):
    assert cfg.get("input") is not None


def test_config_nested(cfg):
    assert cfg.get("input", "datasets") == []
