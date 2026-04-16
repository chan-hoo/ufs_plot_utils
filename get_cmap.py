import logging
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

logger = logging.getLogger(__name__)

class GetCmap:
    """
    Handle colormap selection logic.
    """
    def __init__(self, cfg):
        self.cfg = cfg


# ======================================================================================= CHJ =====
    def select_cmap(self, varname, data_var):
        """
        Central logic for choosing colormap
        """
        increment_flag = str(getattr(self.cfg.flags, "INCREMENT_PLOT", "NO")).upper()
        is_increment = increment_flag in ["YES", "TRUE", "1", "ON"]

        if is_increment:
            return self.choose_colormap(varname, data_var)
        else:
            return self.get_met_cmap(varname, data_var)


# ======================================================================================= CHJ =====
    def get_met_cmap(self, varname, data_var):
        """
        Return meteorology-specific colormap and range
        """
        var = varname.lower()

        # Temperature (NWS-style)
        if "tmp" in var or "temp" in var:
            colors = [
                "#4B0082", "#0000FF", "#00BFFF", "#00FF00",
                "#FFFF00", "#FFA500", "#FF4500", "#FF0000"
            ]
            cmap = LinearSegmentedColormap.from_list("nws_temp", colors)
            vmin = np.nanpercentile(data_var, 2)
            vmax = np.nanpercentile(data_var, 98)
            logger.info(f'''{varname}: using NWS temperature colormap''')

        # Wind / vector fields
        elif any(v in var for v in ["ugrd", "vgrd", "wind", "u", "v"]):
            cmap = "RdBu_r"
            abs_max = np.nanmax(np.abs(data_var))
            vmin, vmax = -abs_max, abs_max
            logger.info(f'''{varname}: using diverging wind colormap''')

        # Default fallback
        else:
            cmap = "viridis"
            vmin = np.nanpercentile(data_var, 2)
            vmax = np.nanpercentile(data_var, 98)

            logger.info(f'''{varname}: using default colormap''')

        return cmap, vmin, vmax


# ======================================================================================= CHJ =====
    def choose_colormap(self, varname, data_var):
        """
        Automatically choose colormap and vmin/vmax.
        """
        if np.all(np.isnan(data_var)):
            logger.warning(f'''{varname}: all NaN values''')
            return "viridis", None, None

        data_min = np.nanmin(data_var)
        data_max = np.nanmax(data_var)
        logger.info(f'''{varname}:: data_min={data_min}, data_max={data_max}''')

        # Diverging case
        if data_min < 0 and data_max > 0:
            cmap = "RdBu_r"   # standard diverging
            abs_max = np.nanmax(np.abs(data_var))
            vmin = -abs_max
            vmax = abs_max
            logger.info(f'''{varname}: using diverging colormap''')

        # Sequential case
        else:
            cmap = "viridis"
            # robust range (avoid outliers)
            vmin = np.nanpercentile(data_var, 2)
            vmax = np.nanpercentile(data_var, 98)
            logger.info(f'''{varname}: using sequential colormap''')

        logger.info(f'''{varname}:: cmap={cmap}, vmin={vmin}, vmax={vmax}''')

        return cmap, vmin, vmax

