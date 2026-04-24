import logging
import xarray as xr

from types import SimpleNamespace

from .cmap import PlotStyleResolver
from .data import DataReader
from .dataset import Dataset
from .geo import GeoReader
from .naming import NameBuilder
from .plot import Plotter
from .output import OutputManager
from .utils import normalize_tile_dims, format_rtag
from .tasks import TaskBuilder, DifferenceTask

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
        Pipeline for multiple datasets
        """
        builder = TaskBuilder(self)
        tasks = builder.build_plot_tasks()
        for task in tasks:
            task.run()


# ======================================================================================= CHJ =====
    def run_differences(self):
        """
        Pipeline for difference plot of two datasets
        """
        diff_cfgs = self.cfg.get("input", "differences", default=[])
    
        if not diff_cfgs:
            logger.info(f'''No differences configured. Skipping.''')
            return
    
        ds_map = self._build_dataset_map()
    
        for diff_cfg in diff_cfgs:
    
            base_ds = ds_map[diff_cfg["base"]]
            minus_ds = ds_map[diff_cfg["minus"]]
    
            geo = GeoReader(base_ds).get_geo()
    
            reader_base = DataReader(base_ds)
            reader_minus = DataReader(minus_ds)
    
            for var_base in base_ds.var_list:
    
                var_minus = diff_cfg.get("var_map", {}).get(var_base, var_base)
    
                task = DifferenceTask(
                    base_ds,
                    minus_ds,
                    var_base,
                    var_minus,
                    readers=(reader_base, reader_minus),
                    geo=geo,
                    plotter=self.plotter,
                    output=self.output,
                    namer=self.names,
                    diff_cfg=diff_cfg,
                )
    
                task.run()
    
            reader_base.close()
            reader_minus.close()


# ======================================================================================= CHJ =====
    def _build_dataset_map(self):
        return {ds.name: ds for ds in self.datasets}


