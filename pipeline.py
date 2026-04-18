import logging

from .data import DataReader
from .plot import Plotter
from .output import OutputManager
from .naming import NameBuilder

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Full plotting pipeline
    """
    def __init__(self, cfg):
        self.cfg = cfg

        self.data = DataReader(cfg)
        self.plotter = Plotter(cfg)
        self.output = OutputManager(cfg)
        self.names = NameBuilder(cfg)

# ======================================================================================= CHJ =====
    def run_plot_tiles(self):
        """
        Execute full pipeline for FV3 tiled domain
        """
        # Get geo
        lat, lon = self.data.get_geo()

        # Loop variables
        for varname in self.cfg.input.data_file.var_list:
            logger.info(f'''Processing: {varname}''')
            # Get data
            data_var, label = self.data.get_data(varname)
            # Set title
            title = self.names.build_title(
                varname,
                z_index=self.cfg.input.data_file.z_index
            )
            # Set filename
            filename = self.names.build_filename(
                varname,
                z_index=self.cfg.input.data_file.z_index
            )
            # Plot data
            fig = self.plotter.plot_data_tiles(
                data_var=data_var,
                lat=lat,
                lon=lon,
                varname=varname,
                var_cbar_label=label,
                output_title=title
            )
            # Save file
            self.output.save_figure(fig, filename)

        self.data.close()

