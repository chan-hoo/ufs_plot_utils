import logging
import sys

class LoggerConfig:
    """
    Dedicated logging module.
    """
    @staticmethod
    def setup(log_level_str="INFO", log_file=None):
        """
        Set up basic configuration for logging.
        Usage:
          plt.LoggerConfig.setup(args.log_level)
          logger = logging.getLogger(__name__)
        """
        log_level_str = log_level_str.upper()
        try:
            log_level = getattr(logging, log_level_str)
        except AttributeError:
            log_level = logging.INFO
            sys.stderr.write(f'''WARNING: Invalid log level "{log_level_str}", set to INFO.''')
            log_level_str = "INFO"

        handlers = [logging.StreamHandler()]

        if log_file:
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] [%(filename)s:L%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
            force=True
        )

        logger = logging.getLogger(__name__)
        logger.info(f'''Python Log Level = {log_level_str} ({log_level})''')

