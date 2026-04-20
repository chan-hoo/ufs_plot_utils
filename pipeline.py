import logging

from .cmap import PlotStyleResolver
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
    
        datasets_cfg = self.cfg.get("input", "datasets", default=[])
    
        if not datasets_cfg:
            raise ValueError(f'''No datasets defined in config (input.datasets)''')
    
        self.datasets = [
            Dataset(ds_cfg)
            for ds_cfg in datasets_cfg
        ]
    
        self.names = NameBuilder(cfg)
        self.plotter = Plotter(cfg)
        self.output = OutputManager(cfg)


# ======================================================================================= CHJ =====
    def run_plot_tiles(self):
        """
        Execute pipeline for multiple datasets
        """

        for ds in self.datasets:
            logger.info(f'''Processing dataset: {ds.name}''')
            style_resolver = PlotStyleResolver(ds)
            self.plotter.set_style_resolver(style_resolver)
            # -------------------------
            # GEO (load once per dataset)
            # -------------------------
            geo_reader = GeoReader(ds)
            lat, lon = geo_reader.get_geo()

            # -------------------------
            # DATA (context-managed)
            # -------------------------
            data_reader = DataReader(ds)
    
            for varname in ds.var_list:
                logger.info(f'''{ds.name} :: {varname}''')
    
                da = data_reader.get_data(varname)
                data_var = da.values

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
                    lat=lat,
                    lon=lon,
                    da=da,
                    varname=varname,
                    output_title=title,
                    dataset=ds
                )
    
                self.output.save_figure(fig, filename)
    
            data_reader.close()

