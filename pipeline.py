import logging

from .data import DataReader
from .geo import GeoData
from .naming import NameBuilder
from .plot import Plotter
from .output import OutputManager

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Full plotting pipeline
    """
    def __init__(self, cfg):
        self.cfg = cfg

        self.datasets = [
            DataReader(ds_cfg)
            for ds_cfg in self.cfg.input.datasets
        ]
        self.geo = GeoData(cfg)
        self.names = NameBuilder(cfg)
        self.plotter = Plotter(cfg)
        self.output = OutputManager(cfg)

        # Geo data
        self.lat, self.lon = self.geo.get_geo()
        

# ======================================================================================= CHJ =====
    def run_plot_tiles(self):
        """
        Execute pipeline for multiple datasets (no comparison yet)
        """
    
        for ds in self.datasets:
            logger.info(f'''Processing dataset: {ds.cfg.name}''')
    
            for varname in ds.var_list:
                logger.info(f'''Processing: {varname}''')
    
                # Get data
                da = ds.get_data(varname)
    
                # Title
                title = self.names.build_title(
                    varname,
                    dataset_name=ds.cfg.name,
                    z_index=ds.z_index
                )
    
                # Filename
                filename = self.names.build_filename(
                    varname,
                    dataset_name=ds.cfg.name,
                    z_index=ds.z_index
                )
    
                # Plot
                fig = self.plotter.plot_data_tiles(
                    da,
                    self.lat,
                    self.lon,
                    varname=varname,
                    output_title=title
                )
    
                # Save
                self.output.save_figure(fig, filename)
    
        # Close all datasets
        for ds in self.datasets:
            ds.close()

