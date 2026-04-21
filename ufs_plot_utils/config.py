import yaml
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Lightweight YAML configuration wrapper.
    Provides safe nested access without magic.
    """

    def __init__(self, yaml_file):
        logger.info(f'''Loading configuration YAML file: {yaml_file}''')
        with open(yaml_file, "r") as f:
            self.data = yaml.safe_load(f)

        logger.debug(f'''Configuration loaded successfully''')


# ======================================================================================= CHJ =====
    def get(self, *keys, default=None):
        """
        Safe nested access:
        cfg.get("input", "datasets")
        """
        d = self.data
        for k in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(k)

        return d if d is not None else default


# ======================================================================================= CHJ =====
    def log_config(self):
        logger.info(f'''Input YAML Configuration:''')
        for line in yaml.dump(self.data, sort_keys=True).splitlines():
            logger.info(line)

