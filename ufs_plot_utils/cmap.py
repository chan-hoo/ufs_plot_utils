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
    def __init__(self, dataset, cmap_cfg=None, range_cfg=None, is_difference=False):
        self.dataset = dataset
        self.is_difference = is_difference

        self.cmap_cfg = cmap_cfg or getattr(dataset, "colormap", {}) or {}
        self.range_cfg = range_cfg or getattr(dataset, "range", {}) or {}


# =================================================================== CHJ ===
    def resolve(self, varname, da):

        data_var = da.values

        cmap = self._resolve_cmap(varname)
        vmin, vmax = self._resolve_range(varname, data_var)
        label = self._build_label(da, varname)
    
        logger.info(
            f'''{varname}:: '''
            f'''cmap={getattr(cmap, 'name', type(cmap).__name__)}, '''
            f'''vmin={vmin}, vmax={vmax}'''
        )
 
        return PlotStyle(
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            label=label
        )


# =================================================================== CHJ ===
    def _resolve_cmap(self, varname):
        """
        Set up colormap
        """

        cmap = self.cmap_cfg.get(varname)
        if cmap is None:
            cmap = self.cmap_cfg.get("default")

        # -------------------------
        # string -> cmap
        # -------------------------
        if isinstance(cmap, str):
            try:
                cmap = plt.get_cmap(cmap)
            except Exception:
                logger.warning(f'''Invalid cmap "{cmap}", fallback to viridis''')
                cmap = plt.get_cmap("viridis")

        # -------------------------
        # meteorology fallback
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


# =================================================================== CHJ ===
    def _resolve_range(self, varname, data_var):

        # -------------------------
        # 1. dataset config
        # -------------------------
        var_range = self.range_cfg.get(varname, self.range_cfg.get("default", {})) or {}

        vmin = var_range.get("vmin")
        vmax = var_range.get("vmax")

        # -------------------------
        # 2. auto fallback
        # -------------------------
        if vmin is None or vmax is None:
            is_increment = (
                self.is_difference
                or self.dataset.data_kind == "increment"
            )

            if is_increment:
                vmax_auto = np.nanpercentile(np.abs(data_var), 98)

                # fallback if data is tiny / all zeros
                if vmax_auto == 0 or np.isnan(vmax_auto):
                    vmax_auto = np.nanmax(np.abs(data_var))

                vmin, vmax = -vmax_auto, vmax_auto

            else:
                vmin = np.nanpercentile(data_var, 2)
                vmax = np.nanpercentile(data_var, 98)

        # Enforce symmetry for differences
        if self.is_difference:
            vmax = max(abs(vmin), abs(vmax))
            vmin = -vmax

        # Final safeguard
        if vmin == vmax:
            scale = np.nanmax(np.abs(data_var))
            if scale == 0 or np.isnan(scale):
                scale = 1e-6
            else:
                scale *= 0.01

            logger.warning(f'''{varname}:: degenerate range -> using ±{scale}''')
            vmin, vmax = -scale, scale

        return vmin, vmax


# =================================================================== CHJ ===
    def _build_label(self, da, varname):

        long_name = da.attrs.get("long_name", varname)
        units = da.attrs.get("units", "")

        label = f'''{long_name} ({units})''' if units else long_name

        if self.dataset.data_kind == "increment":
            label = f'''Δ{label}'''

        return label

