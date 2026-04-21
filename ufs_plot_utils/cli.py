import argparse

class CLI:
    """
    CLI (Clean separation of Logic vs. Interface)
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Plot UFS-DA results"
        )
        self._add_arguments()

    def _add_arguments(self):
        """
        Read two arguments from a command line with python script.
        One is for the input YAML file,
        The other is for the logging level.
        Other parameters should be included in the input YAML file.
        """
        self.parser.add_argument(
            "-i", "--input_config",
            default="config.yaml",
            help="Path to YAML configuration file",
        )
        self.parser.add_argument(
            "-l", "--log-level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Logging level",
        )

    def parse(self):
        return self.parser.parse_args()

