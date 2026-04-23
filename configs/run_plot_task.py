#!/usr/bin/env python3

import sys
import os
from pathlib import Path
# Get the path one level up
parent_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(parent_dir))

import ufs_plot_utils as ufs
import logging

def main():
    """
    Plot test.
    Requires two arguments for input file and logging level.
    Usage:
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

        ## Select type of pipeline based on configuration
        input_cfg = cfg.get("input")
        if input_cfg and input_cfg.get("differences"):
            pipeline.run_differences()
        else:
            pipeline.run_plot_tiles()

    except Exception:
        logging.exception(f'''Pipeline failed''')
        sys.exit(1)


# Main call ========================================================= CHJ =====
if __name__ == "__main__":
    main()
