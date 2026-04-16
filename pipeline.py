import logging

from .get_data import GetData
from .plot_data import PlotData
from .output_manager import OutputManager
from .set_names import SetNames

logger = logging.getLogger(__name__)

class PlotPipeline:
    """
    Full plotting pipeline
    """
    def __init__(self, cfg):
        self.cfg = cfg

        self.data = GetData(cfg)
        self.plotter = PlotData(cfg)
        self.output = OutputManager(cfg)
        self.names = SetNames(cfg)

# ======================================================================================= CHJ =====
    def run_tiles_inc(self):
        """
        Execute full pipeline for tiled data of increment
        """
        # Get geo
        lat, lon = self.data.get_geo_file()

        # Loop variables
        for varname in self.cfg.var_list:
            logger.info(f'''Processing: {varname}''')
            # Get data
            data_var, label = self.data.get_data(varname)
            # Set title
            title = self.names.build_title(
                varname,
                z_index=self.cfg.z_index
            )
            # Set filename
            filename = self.names.build_filename(
                varname,
                z_index=self.cfg.z_index
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
