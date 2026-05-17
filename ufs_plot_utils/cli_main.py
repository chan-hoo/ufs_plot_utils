import sys
import logging
import ufs_plot_utils as ufs


def main():
    """
    Requires two arguments for input file and logging level.
    Usage:
    ./[python_script] -i [config.yaml] -l [logging_level]
    ./[python_script] --help
    """
    # Read input arguments
    args = ufs.CLI().parse()

    # Set logger configuration
    ufs.LoggerSetup.setup(args.log_level)

    try:
        # Read input configuration YAML file
        cfg = ufs.Config(args.input_config)
        # Print out configuration parameters
        cfg.log_config()
        # Run pipeline
        pipeline = ufs.Pipeline(cfg)

        # Select type of pipeline based on configuration
        input_cfg = cfg.get("input")
        if input_cfg and input_cfg.get("differences"):
            pipeline.run_differences()
        else:
            pipeline.run_plot_data()

    except FileNotFoundError as e:
        logging.error("Configuration file not found: %s", e)
        sys.exit(1)

    except ValueError as e:
        logging.error("Invalid configuration: %s", e)
        sys.exit(1)
