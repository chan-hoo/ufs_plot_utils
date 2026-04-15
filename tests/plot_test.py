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
    plt.LoggerConfig.setup(args.log_level)
    logger = logging.getLogger(__name__)

    # Read input configuration YAML file
    cfg = plt.GetConfig(args.input_config)

    # Print out configuration parameters
    cfg.log_config()

    # Read NetCDF file(s)
    data_reader = plt.GetData(cfg)

    ## Read geo data (lat/lon)
    lat, lon = data_reader.get_geo_file()
    logger.info(f'''lat shape = {lat.shape}''')
    logger.info(f'''lon shape = {lon.shape}''')

    ## Plotter
    plotter = plt.PlotData(cfg)

    ## Name builder
    names = plt.SetNames(cfg)

    ## Read and plot data for variables
    for varname in cfg.var_list:
        logger.info(f'''=== Processing variable: {varname}''')
        ### Extract 2D data
        data_var, var_cbar_label = data_reader.get_data_file(varname)
        logger.debug(f'''{varname}:: shape = {data_var.shape}''')
        logger.debug(f'''{varname}:: colorbar label = {var_cbar_label}''')

        ### Set output file name
        output_file = names.build_filename(
            varname,
            z_index=cfg.z_index
        )

        ### Set title
        output_title = names.build_title(
            varname,
            z_index=cfg.z_index
        )

        ### Plot data
        plotter.plot_data_tiles(
            data_var=data_var,
            lat=lat,
            lon=lon,
            var_cbar_label=var_cbar_label,
            output_title=output_title,
            output_file=output_file
        )

    data_reader.close()



# Main call ========================================================= CHJ =====
if __name__ == "__main__":
    main()
