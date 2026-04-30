import logging
import xarray as xr

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
            target_ds = ds_map[diff_cfg["target"]]
    
            geo = GeoReader(base_ds).get_geo()
    
            reader_base = DataReader(base_ds)
            reader_target = DataReader(target_ds)

            var_pairs = diff_cfg.get("var_pairs", [])
            logger.info(f'''var_pairs = {var_pairs}''')
            
            # fallback
            if not var_pairs:
                var_pairs = [
                    {"base": v, "target": v}
                    for v in base_ds.var_list
                ]
                logger.warning(f'''No var_pairs defined for {name}, using identity mapping''')
            
            for pair in var_pairs:
                var_base = pair.get("base")
                var_target = pair.get("target")
            
                if not var_base or not var_target:
                    raise ValueError(f'''Invalid var_pairs entry: {pair}''')
                logger.info(f'''Running DifferenceTask:: base={var_base}, target={var_target}''')
            
                task = DifferenceTask(
                    base_ds,
                    target_ds,
                    var_base,
                    var_target,
                    readers=(reader_base, reader_target),
                    geo=geo,
                    plotter=self.plotter,
                    output=self.output,
                    namer=self.names,
                    diff_cfg=diff_cfg,
                )
            
                task.run()
    
            reader_base.close()
            reader_target.close()


# ======================================================================================= CHJ =====
    def _build_dataset_map(self):
        return {ds.name: ds for ds in self.datasets}


