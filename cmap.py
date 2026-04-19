import logging
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from matplotlib.colors import Colormap
from matplotlib.colors import LinearSegmentedColormap

logger = logging.getLogger(__name__)

@dataclass
class PlotStyle:
    cmap: Colormap
    vmin: float
    vmax: float
    label: str


class PlotStyleResolver:
    """
    Unified handler for colormap, range, and label.
    """

    def __init__(self, dataset):
        self.dataset = dataset

        self.cmap_cfg = dataset.get("colormap", default={})
        self.range_cfg = dataset.get("range", default={})


# ======================================================================================= CHJ =====
    def resolve(self, varname, data_var, da, dataset_cfg=None):
        cmap = self._resolve_cmap(varname, dataset_cfg)
        vmin, vmax = self._resolve_range(varname, data_var, dataset_cfg)
        label = self._build_label(da, varname, dataset_cfg)

        logger.info(
            f'''{varname}:: cmap={getattr(cmap, 'name', type(cmap).__name__)}, '''
            f'''vmin={vmin}, vmax={vmax}'''
            )

        return PlotStyle(
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            label=label
        )


# ======================================================================================= CHJ =====
    def _resolve_cmap(self, varname, dataset_cfg=None):
    
        # -------------------------
        # 1. dataset override
        # -------------------------
        if dataset_cfg is not None:
            ds_cmap_cfg = getattr(dataset_cfg, "colormap", {})
            cmap = ds_cmap_cfg.get(varname, ds_cmap_cfg.get("default"))
        else:
            cmap = None
    
        # -------------------------
        # 2. global fallback
        # -------------------------
        if cmap is None:
            cmap = self.cmap_cfg.get(varname, self.cmap_cfg.get("default"))
    
        # -------------------------
        # 3. string -> cmap
        # -------------------------
        if isinstance(cmap, str):
            try:
                cmap = plt.get_cmap(cmap)
            except Exception:
                logger.warning(f'''Invalid cmap "{cmap}", fallback to viridis''')
                cmap = plt.get_cmap("viridis")
    
        # -------------------------
        # 4. meteorology fallback
        # -------------------------
        if cmap is None:
            var = varname.lower()
    
            if any(v in var for v in ["tmp", "temp", "t_inc"]):
                colors = [
                    "#4B0082", "#0000FF", "#00BFFF", "#00FF00",
                    "#FFFF00", "#FFA500", "#FF4500", "#FF0000"
                ]
                cmap = LinearSegmentedColormap.from_list("nws_temp", colors)
    
            elif any(v in var for v in ["ugrd", "vgrd", "wind"]):
                cmap = plt.get_cmap("RdBu_r")
    
            else:
                cmap = plt.get_cmap("viridis")
    
        return cmap


# ======================================================================================= CHJ =====
    def _resolve_range(self, varname, data_var, dataset_cfg=None):
    
        # -------------------------
        # 1. dataset override (HIGHEST PRIORITY)
        # -------------------------
        if dataset_cfg is not None:
            ds_range_cfg = getattr(dataset_cfg, "range", {})
            var_range = ds_range_cfg.get(varname, ds_range_cfg.get("default", {}))
        else:
            var_range = {}
    
        vmin = var_range.get("vmin")
        vmax = var_range.get("vmax")
    
        # -------------------------
        # 2. global fallback if missing
        # -------------------------
        if vmin is None or vmax is None:
            global_range = self.range_cfg.get(varname, self.range_cfg.get("default", {}))
    
            if vmin is None:
                vmin = global_range.get("vmin")
            if vmax is None:
                vmax = global_range.get("vmax")
    
        # -------------------------
        # 3. auto-range fallback
        # -------------------------
        if vmin is None or vmax is None:
            if self._is_increment():
                vmax_auto = np.nanpercentile(np.abs(data_var), 98)
                vmin, vmax = -vmax_auto, vmax_auto
            else:
                vmin = np.nanpercentile(data_var, 2)
                vmax = np.nanpercentile(data_var, 98)
    
        return vmin, vmax


# ======================================================================================= CHJ =====
    def _build_label(self, da, varname, dataset_cfg=None):
    
        long_name = da.attrs.get("long_name", varname)
        units = da.attrs.get("units", "")
    
        label = f"{long_name} ({units})" if units else long_name
    
        # dataset-aware increment flag
        is_increment = False
        if dataset_cfg is not None:
            is_increment = getattr(dataset_cfg, "data_kind", None) == "increment"
    
        if is_increment:
            label = f"Δ{label}"
    
        return label


# ======================================================================================= CHJ =====
    def _is_increment(self):
        return getattr(self.dataset, "data_kind", "") == "increment"
