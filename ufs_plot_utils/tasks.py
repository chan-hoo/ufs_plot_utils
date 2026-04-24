import logging
import copy
import xarray as xr
import numpy as np

from .data import DataReader
from .geo import GeoReader
from .cmap import PlotStyleResolver
from .utils import normalize_tile_dims

logger = logging.getLogger(__name__)


# ======================================================================================= CHJ =====
class BaseTask:
    def run(self):
        raise NotImplementedError


# ======================================================================================= CHJ =====
class PlotTask(BaseTask):
    """
    Single plotting unit
    """

    def __init__(
        self,
        dataset,
        varname,
        data_reader,
        geo,
        plotter,
        output,
        namer,
        context=None,
    ):
        self.dataset = dataset
        self.varname = varname
        self.data_reader = data_reader
        self.lat, self.lon = geo
        self.plotter = plotter
        self.output = output
        self.namer = namer
        self.context = context or {}

    def run(self):
        logger.info(f'''PlotTask:: {self.dataset.name} :: {self.varname} :: {self.context}''')

        # -------------------------
        # Read data
        # -------------------------
        da = self.data_reader.get_data(
            self.varname,
            fhr=self.context.get("fhr"),
            rtag=self.context.get("rtag"),
        )

        # -------------------------
        # Title
        # -------------------------
        title = self.namer.build_title(
            varname=self.varname,
            dataset_name=self.dataset.name,
            z_index=self.dataset.z_index,
            dataset=self.dataset,
        )

        if "fhr" in self.context:
            title = f'''{title} :: f{self.context["fhr"]}'''

        if "rtag" in self.context:
            title = f'''{title} :: {self.context["rtag"]}'''

        # -------------------------
        # Filename
        # -------------------------
        filename = self.namer.build_filename(
            varname=self.varname,
            dataset_name=self.dataset.name,
            z_index=self.dataset.z_index,
        )

        if "fhr" in self.context:
            filename = f'''{filename}_f{self.context["fhr"]}'''

        if "rtag" in self.context:
            safe_rtag = self.context["rtag"].replace(".", "")
            filename = f'''{filename}_{safe_rtag}'''

        # -------------------------
        # Plot
        # -------------------------
        fig = self.plotter.plot_data_tiles(
            lat=self.lat,
            lon=self.lon,
            da=da,
            varname=self.varname,
            output_title=title,
            dataset=self.dataset,
        )

        # -------------------------
        # Save
        # -------------------------
        self.output.save_figure(fig, filename)


# ======================================================================================= CHJ =====
class DifferenceTask(BaseTask):
    """
    Difference plotting unit
    """

    def __init__(
        self,
        base_ds,
        minus_ds,
        var_base,
        var_minus,
        readers,
        geo,
        plotter,
        output,
        namer,
        diff_cfg,
    ):
        self.base_ds = base_ds
        self.minus_ds = minus_ds
        self.var_base = var_base
        self.var_minus = var_minus
        self.reader_base, self.reader_minus = readers
        self.lat, self.lon = geo
        self.plotter = plotter
        self.output = output
        self.namer = namer
        self.diff_cfg = diff_cfg

    def run(self):
        logger.info(
            f'''DifferenceTask:: {self.var_base} ({self.base_ds.name} - {self.minus_ds.name})'''
        )
    
        # -------------------------
        # Read
        # -------------------------
        da_base = self.reader_base.get_data(self.var_base)
        da_minus = self.reader_minus.get_data(self.var_minus)
    
        logger.info(f'''Original:: base  dims={da_base.dims}, shape={da_base.shape}''')
        logger.info(f'''Original:: minus dims={da_minus.dims}, shape={da_minus.shape}''')
    
        # -------------------------
        # Normalize + Align
        # -------------------------
        da_base  = normalize_tile_dims(da_base)
        da_minus = normalize_tile_dims(da_minus)
    
        da_base, da_minus = xr.align(da_base, da_minus, join="override")
    
        # -------------------------
        # Compute difference (B - A)
        # -------------------------
        da_diff = da_minus - da_base
    
        vals = da_diff.values
        logger.info(
            f'''Difference:: ({self.minus_ds.name} - {self.base_ds.name}) {self.var_base} '''
            f'''min={np.nanmin(vals):.6g}, max={np.nanmax(vals):.6g}'''
        )
    
        # ============================================================
        # 1. PLOT BASE (A)
        # ============================================================
        self.plotter.set_style_resolver(
            PlotStyleResolver(self.base_ds)
        )
    
        title_base = self.namer.build_title(
            varname=self.var_base,
            dataset_name=self.base_ds.name,
            z_index=self.base_ds.z_index,
            dataset=self.base_ds,
        )
    
        filename_base = self.namer.build_filename(
            varname=self.var_base,
            dataset_name=self.base_ds.name,
            z_index=self.base_ds.z_index,
        )
    
        fig_base = self.plotter.plot_data_tiles(
            lat=self.lat,
            lon=self.lon,
            da=da_base,
            varname=self.var_base,
            output_title=title_base,
            dataset=self.base_ds,
        )
    
        self.output.save_figure(fig_base, filename_base)
    
        # ============================================================
        # 2. PLOT MINUS (B)
        # ============================================================
        self.plotter.set_style_resolver(
            PlotStyleResolver(self.minus_ds)
        )
    
        title_minus = self.namer.build_title(
            varname=self.var_minus,
            dataset_name=self.minus_ds.name,
            z_index=self.minus_ds.z_index,
            dataset=self.minus_ds,
        )
    
        filename_minus = self.namer.build_filename(
            varname=self.var_minus,
            dataset_name=self.minus_ds.name,
            z_index=self.minus_ds.z_index,
        )
    
        fig_minus = self.plotter.plot_data_tiles(
            lat=self.lat,
            lon=self.lon,
            da=da_minus,
            varname=self.var_minus,
            output_title=title_minus,
            dataset=self.minus_ds,
        )
    
        self.output.save_figure(fig_minus, filename_minus)
    
        # ============================================================
        # 3. PLOT DIFFERENCE (B - A)
        # ============================================================
        diff_ds = copy.copy(self.base_ds)
        diff_ds.data_kind = "increment"
    
        resolver = PlotStyleResolver(
            dataset=diff_ds,
            cmap_cfg=self.diff_cfg.get("colormap"),
            range_cfg=self.diff_cfg.get("range"),
            is_difference=True,
        )
    
        self.plotter.set_style_resolver(resolver)
    
        title_diff = self.namer.build_title(
            varname=self.var_base,
            dataset_name=self.diff_cfg["name"],
            z_index=diff_ds.z_index,
            dataset=None,
        )
    
        filename_diff = self.namer.build_filename(
            varname=self.var_base,
            dataset_name=self.diff_cfg["name"],
            z_index=diff_ds.z_index,
        )
    
        fig_diff = self.plotter.plot_data_tiles(
            lat=self.lat,
            lon=self.lon,
            da=da_diff,
            varname=self.var_base,
            output_title=title_diff,
            dataset=None,
        )
    
        self.output.save_figure(fig_diff, filename_diff)


# ======================================================================================= CHJ =====
class TaskBuilder:
    """
    Build all tasks for pipeline
    """

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def build_plot_tasks(self):
        tasks = []

        for ds in self.pipeline.datasets:
            logger.info(f'''TaskBuilder:: dataset = {ds.name}''')

            geo = GeoReader(ds).get_geo()
            reader = DataReader(ds)

            self.pipeline.plotter.set_style_resolver(
                PlotStyleResolver(ds)
            )

            # -------------------------
            # FORECAST
            # -------------------------
            if ds.data_kind == "forecast":
                fhrs = reader.detect_forecast_hours()

                for fhr in fhrs:
                    for var in ds.var_list:
                        tasks.append(
                            PlotTask(
                                dataset=ds,
                                varname=var,
                                data_reader=reader,
                                geo=geo,
                                plotter=self.pipeline.plotter,
                                output=self.pipeline.output,
                                namer=self.pipeline.names,
                                context={"fhr": fhr},
                            )
                        )

            # -------------------------
            # RESTART
            # -------------------------
            elif ds.data_kind == "restart":
                rtags = reader.detect_restart_tags()

                for rtag in rtags:
                    for var in ds.var_list:
                        tasks.append(
                            PlotTask(
                                dataset=ds,
                                varname=var,
                                data_reader=reader,
                                geo=geo,
                                plotter=self.pipeline.plotter,
                                output=self.pipeline.output,
                                namer=self.pipeline.names,
                                context={"rtag": rtag},
                            )
                        )

            # -------------------------
            # DEFAULT
            # -------------------------
            else:
                for var in ds.var_list:
                    tasks.append(
                        PlotTask(
                            dataset=ds,
                            varname=var,
                            data_reader=reader,
                            geo=geo,
                            plotter=self.pipeline.plotter,
                            output=self.pipeline.output,
                            namer=self.pipeline.names,
                        )
                    )

        return tasks
