import logging

from .data import DataReader
from .dataset import Dataset
from .geo import GeoReader
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

        # Dataset objects (NOT DataReader directly)
        self.datasets = [
            Dataset(ds_cfg)
            for ds_cfg in self.cfg.input.datasets
        ]

        # Shared utilities (these can stay global)
        self.names = NameBuilder(cfg)
        self.plotter = Plotter(cfg)
        self.output = OutputManager(cfg)
        

# ======================================================================================= CHJ =====
    def run_plot_tiles(self):
        """
        Execute pipeline for multiple datasets (no comparison yet)
        """
        for ds in self.datasets:
            logger.info(f'''Processing dataset: {ds.name}''')
    
            # GEO
            geo_reader = GeoReader(ds.geo)
            lat, lon = geo_reader.get_geo()
    
            # DATA
            data_reader = DataReader(ds)
    
            for varname in ds.var_list:
                logger.info(f'''{ds.name} :: {varname}''')
    
                da, data_var = data_reader.get_data(varname)
    
                # TITLE
                title = self.names.build_title(
                    varname,
                    z_index=ds.z_index,
                    dataset_name=ds.name
                )
    
                # FILENAME
                filename = self.names.build_filename(
                    varname,
                    z_index=ds.z_index,
                    dataset_name=ds.name
                )
    
                # PLOT
                fig = self.plotter.plot_data_tiles(
                    data_var,
                    lat,
                    lon,
                    da,
                    varname,
                    ds,
                    output_title=title
                )
    
                self.output.save_figure(fig, filename)
    
            data_reader.close()

