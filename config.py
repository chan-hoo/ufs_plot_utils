import yaml
import logging
from .utils import to_plain_dict

logger = logging.getLogger(__name__)

class Config:
    """
    Read input YAML file and get configuration parameters.
    """
    def __init__(self, yaml_file):
        """
        Read input YAML file.
        """
        logger.info(f'''Loading configuration YAML file: {yaml_file}''')

        with open(yaml_file, "r") as f:
            raw = yaml.safe_load(f)

        obj = self.from_dict(raw)   # return Config
        self._config = obj._config  # unwrap

        logger.debug("===== Configuration loaded successfully =====")


# ======================================================================================= CHJ =====
    def __getattr__(self, name):
        """
        Get configuration parameters by dot-style access
        Usage:
          input YAML: config.yaml
            params:
              model_option: A
            paths:
              input_path: ./

        cfg = Config("config.yaml")
        model_option = cfg.params.model_option
        input_path = cfg.paths.input_path
        """
        if name in self._config:
            return self._config[name]
        raise AttributeError(f'''{name} not found in config''')


    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj._config = {}
    
        for k, v in d.items():
            if isinstance(v, dict):
                obj._config[k] = cls.from_dict(v)  # recursive
            else:
                obj._config[k] = v
    
        return obj


# ======================================================================================= CHJ =====
    def log_config(self):
        logger.info(f'''Input YAML Configuration:''')
        plain_cfg = to_plain_dict(self._config)
    
        for line in yaml.dump(plain_cfg, sort_keys=True).splitlines():
            logger.info(line)

