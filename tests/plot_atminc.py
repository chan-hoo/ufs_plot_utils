#!/usr/bin/env python3

import sys
from pathlib import Path
# Get the path two levels up
parent_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(parent_dir))

import ufs_plot_utils as plt
import logging

def main():
    """
    Plot test.
    Requires two arguments for input file and logging level.
    Usage:
    ./[python_script] --help
    """
    # Read input arguments
    args = plt.CLI().parse()

    # Set logger configuration
    plt.LoggerSetup.setup(args.log_level)
    #logger = logging.getLogger(__name__)

    # Read input configuration YAML file
    cfg = plt.Config(args.input_config)

    # Print out configuration parameters
    cfg.log_config()

    # Run pipeline
    pipeline = plt.Pipeline(cfg)
    pipeline.run_inc_tiles()


# Main call ========================================================= CHJ =====
if __name__ == "__main__":
    main()
