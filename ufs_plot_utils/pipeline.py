import logging
import xarray as xr

from .cmap import PlotStyleResolver
from .data import DataReader
from .dataset import Dataset
from .geo import GeoReader
from .naming import NameBuilder
from .plot import Plotter
from .output import OutputManager
from .utils import normalize_tile_dims

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

                # Title
                title = self.names.build_title(varname,dataset_name=ds.name,z_index=ds.z_index)
    
                # Filename
                filename = self.names.build_filename(varname,dataset_name=ds.name,z_index=ds.z_index)
    
                # Plot
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


# ======================================================================================= CHJ =====
    def run_differences(self):
        import copy
        import numpy as np
    
        diff_cfgs = self.cfg.get("input", "differences", default=[])
        if not diff_cfgs:
            logger.info("No differences configured. Skipping.")
            return
    
        ds_map = self._build_dataset_map()
    
        for diff_cfg in diff_cfgs:
    
            name = diff_cfg["name"]
            base_name = diff_cfg["base"]
            minus_name = diff_cfg["minus"]
            var_map = diff_cfg.get("var_map", {})
    
            logger.info(f'''Running difference: {name}''')
    
            base_ds = ds_map[base_name]
            minus_ds = ds_map[minus_name]
    
            # -------------------------
            # GEO (use base as reference)
            # -------------------------
            geo_reader = GeoReader(base_ds)
            lat, lon = geo_reader.get_geo()
    
            # -------------------------
            # DATA READERS
            # -------------------------
            reader_base = DataReader(base_ds)
            reader_minus = DataReader(minus_ds)
    
            # -------------------------
            # STYLE
            # -------------------------
            self.plotter.set_style_resolver(PlotStyleResolver(base_ds))
    
            # -------------------------
            # LOOP VARIABLES
            # -------------------------
            for var_base in base_ds.var_list:
    
                var_minus = var_map.get(var_base, var_base)
    
                logger.info(f'''{var_base} (base) vs {var_minus} (minus)''')
    
                da_base = reader_base.get_data(var_base)
                da_minus = reader_minus.get_data(var_minus)
                logger.info(f'''Original:: da_base : {da_base.dims} = {da_base.shape}''')
                logger.info(f'''Original:: da_minus: {da_minus.dims} = {da_minus.shape}''')

                # Normalize BEFORE math
                da_base  = normalize_tile_dims(da_base)
                da_minus = normalize_tile_dims(da_minus)
                logger.info(f'''Normalized:: da_base : {da_base.dims} = {da_base.shape}''')
                logger.info(f'''Normalized:: da_minus: {da_minus.dims} = {da_minus.shape}''')

                # Align
                da_base, da_minus = xr.align(da_base, da_minus, join="override")
    
                # Difference
                da_diff = da_base - da_minus
                logger.info(f'''da_diff: {da_diff.dims} = {da_diff.shape}''')
                vals = da_diff.values
                logger.info(
                    f'''[{base_name} - {minus_name}] {var_base}:: '''
                    f'''min={np.nanmin(vals):.6g}, max={np.nanmax(vals):.6g}'''
                )
    
                # =========================
                # 1. PLOT BASE
                # =========================
                # Title
                title_base = self.names.build_title(varname=var_base,dataset_name=base_ds.name,z_index=base_ds.z_index)
                # Filename
                filename_base = self.names.build_filename(varname=var_base,dataset_name=base_ds.name,z_index=base_ds.z_index)
                # Plot
                fig1 = self.plotter.plot_data_tiles(
                    lat=lat,
                    lon=lon,
                    da=da_base,
                    varname=var_base,
                    output_title=title_base,
                    dataset=base_ds
                )
                # Save
                self.output.save_figure(fig1, filename_base)
    
                # =========================
                # 2. PLOT MINUS
                # =========================
                self.plotter.set_style_resolver(PlotStyleResolver(minus_ds))

                # Title
                title_minus = self.names.build_title(varname=var_minus,dataset_name=minus_ds.name,z_index=base_ds.z_index)
                # Filename
                filename_minus = self.names.build_filename(varname=var_minus,dataset_name=minus_ds.name,z_index=base_ds.z_index)

                fig2 = self.plotter.plot_data_tiles(
                    lat=lat,
                    lon=lon,
                    da=da_minus,
                    varname=var_minus,
                    output_title=title_minus,
                    dataset=minus_ds
                )
    
                self.output.save_figure(fig2, filename_minus)
    
                # =========================
                # 3. PLOT DIFFERENCE
                # =========================
                # use BASE style but force increment behavior
                diff_ds = copy.copy(base_ds)
                diff_ds.data_kind = "increment"

                diff_cmap = diff_cfg.get("colormap", {})
                diff_range = diff_cfg.get("range", {})                
                resolver = PlotStyleResolver(
                    dataset=diff_ds,          # needed for data_kind etc.
                    cmap_cfg=diff_cmap,
                    range_cfg=diff_range
                )
                resolver.is_difference = True
                self.plotter.set_style_resolver(resolver)

                # Title
                title_diff = self.names.build_title(varname=var_base,dataset_name=name,z_index=base_ds.z_index)
                # Filename
                filename_diff = self.names.build_filename(varname=var_base,dataset_name=name,z_index=base_ds.z_index)

                fig3 = self.plotter.plot_data_tiles(
                    lat=lat,
                    lon=lon,
                    da=da_diff,
                    varname=var_base,
                    output_title=title_diff,
                    dataset=diff_ds
                )
    
                self.output.save_figure(fig3, filename_diff)
    
            reader_base.close()
            reader_minus.close()


# ======================================================================================= CHJ =====
    def _build_dataset_map(self):
        return {ds.name: ds for ds in self.datasets}

