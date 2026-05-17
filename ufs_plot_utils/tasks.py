import logging
import copy
import xarray as xr
import numpy as np

from .data import DataReader
from .geo import GeoReader
from .cmap import PlotStyleResolver
from .utils import normalize_tile_dims

logger = logging.getLogger(__name__)


class BaseTask:
    def run(self):
        raise NotImplementedError


# =================================================================== CHJ ===

class PlotTask(BaseTask):
    """
    Single plotting unit
    """

    def __init__(
        self,
        dataset,
        varname,
        data_reader,
        plotter,
        output,
        namer,
        context=None,
    ):
        self.dataset = dataset
        self.varname = varname
        self.data_reader = data_reader
        self.plotter = plotter
        self.output = output
        self.namer = namer
        self.context = context or {}

    # =============================================================== CHJ ===

    def run(self):
        logger.info(
            f'''PlotTask:: {self.dataset.name} :: {self.varname} :: '''
            f'''{self.context}'''
        )

        # Set resolver per task
        self.plotter.set_style_resolver(
            PlotStyleResolver(self.dataset)
        )

        # -------------------------
        # Read data
        # -------------------------
        da = self.data_reader.get_data(
            self.varname,
            fhr=self.context.get("fhr"),
            rtag=self.context.get("rtag"),
        )

        # -------------------------
        # GEO data
        # -------------------------
        geo_reader = GeoReader(self.dataset)
        lat, lon = geo_reader.get_geo(da)

        # -------------------------
        # Skip empty channels
        # -------------------------
        if np.all(np.isnan(da.values)):
            logger.warning(f'''Skipping NaN-only field: {self.varname}''')
            return

        # -------------------------
        # Channel slicing (OBS)
        # -------------------------
        if "channel" in self.context:
            ch = self.context["channel_idx"]
            ch_dim = next(
                (
                    d
                    for d in da.dims
                    if d.lower() in ["channel", "chan", "nchan", "band"]
                ),
                None,
            )
            if ch_dim is not None:
                da = da.isel({ch_dim: ch})

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

        if "channel" in self.context:
            title = f'''{title} :: ch{self.context["channel"]:02d}'''

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

        if "channel" in self.context:
            filename = f'''{filename}_ch{self.context["channel"]:02d}'''

        # -------------------------
        # Plot
        # -------------------------
        if self.dataset.data_kind == "observation":
            fig = self.plotter.plot_data_scatter(
                lat=lat,
                lon=lon,
                da=da,
                varname=self.varname,
                output_title=title,
                dataset=self.dataset,
            )

        elif self.dataset.data_model in ["mom6", "cice"]:
            fig = self.plotter.plot_data_grid(
                lat=lat,
                lon=lon,
                da=da,
                varname=self.varname,
                output_title=title,
                dataset=self.dataset,
            )

        else:
            fig = self.plotter.plot_data_tiles(
                lat=lat,
                lon=lon,
                da=da,
                varname=self.varname,
                output_title=title,
                dataset=self.dataset,
            )

        # -------------------------
        # Save
        # -------------------------
        self.output.save_figure(fig, filename)


# =================================================================== CHJ ===

class DifferenceTask(BaseTask):
    """
    Difference plotting unit
    """

    def __init__(
        self,
        base_ds,
        target_ds,
        var_base,
        var_target,
        readers,
        plotter,
        output,
        namer,
        diff_cfg,
    ):
        self.base_ds = base_ds
        self.target_ds = target_ds
        self.var_base = var_base
        self.var_target = var_target
        self.reader_base, self.reader_target = readers
        self.plotter = plotter
        self.output = output
        self.namer = namer
        self.diff_cfg = diff_cfg

    # =============================================================== CHJ ===

    def run(self):
        logger.info(
            f'''DifferenceTask:: {self.var_base} ({self.target_ds.name} '''
            f'''- {self.base_ds.name})'''
        )

        # -------------------------
        # Read data sets
        # -------------------------
        da_base = self.reader_base.get_data(self.var_base)
        da_target = self.reader_target.get_data(self.var_target)

        logger.info(
            f'''Original:: base dims={da_base.dims}, shape={da_base.shape}'''
        )
        logger.info(
            f'''Original:: target dims={da_target.dims}, '''
            f'''shape={da_target.shape}'''
        )

        # -------------------------
        # Geo data: base
        # -------------------------
        geo_reader = GeoReader(self.base_ds)
        lat, lon = geo_reader.get_geo(da_base)

        # -------------------------
        # Normalize + Align
        # -------------------------
        da_base = normalize_tile_dims(da_base)
        da_target = normalize_tile_dims(da_target)

        da_base, da_target = xr.align(da_base, da_target, join="override")

        # -------------------------
        # Compute difference (B - A)
        # -------------------------
        da_diff = da_target - da_base

        vals = da_diff.values
        logger.info(
            f'''Difference:: ({self.target_ds.name} - '''
            f'''{self.base_ds.name}) {self.var_base} '''
            f'''min={np.nanmin(vals):.6g}, '''
            f'''max={np.nanmax(vals):.6g}'''
        )

        # ==============================
        # 1. PLOT BASE (A)
        # ==============================
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

        if self.base_ds.data_model in ["mom6", "cice"]:
            fig_base = self.plotter.plot_data_grid(
                lat=lat,
                lon=lon,
                da=da_base,
                varname=self.var_base,
                output_title=title_base,
                dataset=self.base_ds,
            )

        else:
            fig_base = self.plotter.plot_data_tiles(
                lat=lat,
                lon=lon,
                da=da_base,
                varname=self.var_base,
                output_title=title_base,
                dataset=self.base_ds,
            )

        self.output.save_figure(fig_base, filename_base)

        # ==============================
        # 2. PLOT TARGET (B)
        # ==============================
        self.plotter.set_style_resolver(
            PlotStyleResolver(self.target_ds)
        )

        title_target = self.namer.build_title(
            varname=self.var_target,
            dataset_name=self.target_ds.name,
            z_index=self.target_ds.z_index,
            dataset=self.target_ds,
        )

        filename_target = self.namer.build_filename(
            varname=self.var_target,
            dataset_name=self.target_ds.name,
            z_index=self.target_ds.z_index,
        )

        if self.target_ds.data_model in ["mom6", "cice"]:
            fig_target = self.plotter.plot_data_grid(
                lat=lat,
                lon=lon,
                da=da_target,
                varname=self.var_target,
                output_title=title_target,
                dataset=self.target_ds,
            )

        else:
            fig_target = self.plotter.plot_data_tiles(
                lat=lat,
                lon=lon,
                da=da_target,
                varname=self.var_target,
                output_title=title_target,
                dataset=self.target_ds,
            )

        self.output.save_figure(fig_target, filename_target)

        # ==============================
        # 3. PLOT DIFFERENCE (B - A)
        # ==============================
        diff_ds = copy.copy(self.base_ds)
        diff_ds.data_kind = "increment"
        diff_ds.title = self.diff_cfg.get("title")
        diff_ds.name = self.diff_cfg.get("name")

        resolver = PlotStyleResolver(
            dataset=diff_ds,
            cmap_cfg=self.diff_cfg.get("colormap"),
            range_cfg=self.diff_cfg.get("range"),
            is_difference=True,
        )

        self.plotter.set_style_resolver(resolver)

        title_diff = self.namer.build_title(
            varname=self.var_base,
            dataset_name=diff_ds.name,
            z_index=diff_ds.z_index,
            dataset=diff_ds,
        )

        filename_diff = self.namer.build_filename(
            varname=self.var_base,
            dataset_name=diff_ds.name,
            z_index=diff_ds.z_index,
        )

        if self.base_ds.data_model in ["mom6", "cice"]:
            fig_diff = self.plotter.plot_data_grid(
                lat=lat,
                lon=lon,
                da=da_diff,
                varname=self.var_base,
                output_title=title_diff,
                dataset=None,
            )

        else:
            fig_diff = self.plotter.plot_data_tiles(
                lat=lat,
                lon=lon,
                da=da_diff,
                varname=self.var_base,
                output_title=title_diff,
                dataset=None,
            )

        self.output.save_figure(fig_diff, filename_diff)


# =================================================================== CHJ ===

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
                                plotter=self.pipeline.plotter,
                                output=self.pipeline.output,
                                namer=self.pipeline.names,
                                context={"rtag": rtag},
                            )
                        )

            # -------------------------
            # OBSERVATION
            # -------------------------
            elif ds.data_kind == "observation":
                reader = DataReader(ds)
                self.pipeline.plotter.set_style_resolver(
                    PlotStyleResolver(ds)
                )

                for var in ds.var_list:
                    ch_dim, ch_list = reader.get_observation_channels(var)
                    channels_cfg = ds.channels  # now dataset-local

                    if ch_dim is None:
                        logger.info(
                            f'''{ds.name}:{var} has NO channel dimension'''
                        )
                        tasks.append(
                            PlotTask(
                                dataset=ds,
                                varname=var,
                                data_reader=reader,
                                plotter=self.pipeline.plotter,
                                output=self.pipeline.output,
                                namer=self.pipeline.names,
                                context={},   # IMPORTANT: no channel
                            )
                        )
                        continue

                    else:
                        selected_channels = ch_list
                        if channels_cfg:
                            max_ch = len(ch_list)
                            channels_cfg = [
                                c for c in channels_cfg if 1 <= c <= max_ch
                            ]
                            channels_cfg = [c - 1 for c in channels_cfg]
                            selected_channels = [
                                ch for ch in ch_list if ch in channels_cfg
                            ]

                        for ch in selected_channels:
                            context = {
                                "channel_idx": ch,
                                "channel": ch + 1,
                            }

                            tasks.append(
                                PlotTask(
                                    dataset=ds,
                                    varname=var,
                                    data_reader=reader,
                                    plotter=self.pipeline.plotter,
                                    output=self.pipeline.output,
                                    namer=self.pipeline.names,
                                    context=context,
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
                            plotter=self.pipeline.plotter,
                            output=self.pipeline.output,
                            namer=self.pipeline.names,
                        )
                    )

        return tasks
