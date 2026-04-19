import logging
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

from .utils import to_dict, to_plain

logger = logging.getLogger(__name__)


class PlotStyleResolver:
    """
    Unified handler for colormap, range, and label.
    """

    def __init__(self, dataset):
        self.dataset = dataset

        # Normalize configs ONCE
        self.cmap_cfg = to_dict(getattr(dataset, "colormap", {}))
        self.range_cfg = to_dict(getattr(dataset, "range", {}))


# ======================================================================================= CHJ =====
    def resolve(self, varname, data_var, da):
        cmap = self._resolve_cmap(varname)
        vmin, vmax = self._resolve_range(varname, data_var)
        label = self._build_label(da, varname)

        logger.info(
            f'''{varname}:: cmap={getattr(cmap, 'name', type(cmap).__name__)}, '''
            f'''vmin={vmin}, vmax={vmax}'''
        )

        return cmap, vmin, vmax, label


# ======================================================================================= CHJ =====
    def _resolve_cmap(self, varname):
        logger.debug(f'''colormap in config: {to_plain(self.cmap_cfg)}''')

        cmap = self.cmap_cfg.get(varname, self.cmap_cfg.get("default"))

        # User-defined string -> cmap
        if isinstance(cmap, str):
            try:
                cmap = plt.get_cmap(cmap)
            except Exception:
                logger.warning(f'''Invalid cmap "{cmap}", fallback to viridis''')
                cmap = plt.get_cmap("viridis")

        # Meteorology defaults
        if cmap is None:
            var = varname.lower()

            if any(v in var for v in ["tmp", "temp", "t_inc"]):
                colors = [
                    "#4B0082", "#0000FF", "#00BFFF", "#00FF00",
                    "#FFFF00", "#FFA500", "#FF4500", "#FF0000"
                ]
                cmap = LinearSegmentedColormap.from_list("nws_temp", colors)
                logger.info(f'''{varname}:: using NWS temperature colormap''')

            elif any(v in var for v in ["ugrd", "vgrd", "wind"]):
                cmap = plt.get_cmap("RdBu_r")
                logger.info(f'''{varname}:: using wind diverging colormap''')

            else:
                cmap = plt.get_cmap("viridis")
                logger.info(f'''{varname}:: using default colormap (viridis)''')

        return cmap


# ======================================================================================= CHJ =====
    def _resolve_range(self, varname, data_var):
        logger.debug(f'''range in config: {to_plain(self.range_cfg)}''')

        var_range = self.range_cfg.get(varname, self.range_cfg.get("default", {}))

        vmin = var_range.get("vmin")
        vmax = var_range.get("vmax")

        if vmin is None or vmax is None:
            if self._is_increment():
                vmax_auto = np.nanpercentile(np.abs(data_var), 98)
                vmin, vmax = -vmax_auto, vmax_auto
            else:
                vmin = np.nanpercentile(data_var, 2)
                vmax = np.nanpercentile(data_var, 98)

        return vmin, vmax


# ======================================================================================= CHJ =====
    def _build_label(self, da, varname):
        long_name = da.attrs.get("long_name", varname)
        units = da.attrs.get("units", "")

        label = f"{long_name} ({units})" if units else long_name

        if self._is_increment():
            label = f"Δ{label}"

        return label


# ======================================================================================= CHJ =====
    def _is_increment(self):
        return getattr(self.dataset, "data_kind", "") == "increment"
