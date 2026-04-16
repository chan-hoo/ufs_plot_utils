import yaml
import logging

logger = logging.getLogger(__name__)

class GetConfig:
    """
    Read input YAML file and get configuration parameters.
    """
    def __init__(self, yaml_file):
        """
        Read input YAML file.
        """
        logger.info(f'''Loading configuration YAML file: {yaml_file}''')

        with open(yaml_file, 'r') as f:
            self._config = yaml.safe_load(f)

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

        cfg = GetConfig("config.yaml")
        model_option = cfg.params.model_option
        input_path = cfg.paths.input_path
        """
        # Top-level
        if name in self._config:
            value = self._config[name]
            if isinstance(value, dict):
                return GetConfig.from_dict(value)
            return value
    
        # Fallback search
        for section in ["paths", "filenames", "params", "flags"]:
            if section in self._config:
                sub = self._config[section]
                if name in sub:
                    return sub[name]
    
        raise AttributeError(f'''{name} not found in config''')


    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj._config = d
        return obj


# ======================================================================================= CHJ =====
    def log_config(self):
        logger.info(f'''Input YAML Configuration:''')
        for line in yaml.dump(self._config, sort_keys=True).splitlines():
            logger.info(line)

