import logging
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from .config import to_dict, to_plain

logger = logging.getLogger(__name__)

class CmapManager:
    """
    Handle colormap selection logic.
    """
    def __init__(self, cfg):
        self.cfg = cfg


# ======================================================================================= CHJ =====
    def get_cmap_and_range(self, varname, data_var, is_increment=False):
        """
        Get colormap and range:
        1. User-defined (YAML)
        2. Meteorology-specific defaults
        3. Generic fallback (e.g., viridis)
        """
        import matplotlib.pyplot as plt
    
        # =========================
        # 1. User-defined colormap
        # =========================
        cmap_cfg = self.cfg.plot.colormap
        logger.debug(f'''colormap in config: {to_plain(cmap_cfg)}''')
        cmap_name = getattr(
            cmap_cfg,
            varname,
            getattr(cmap_cfg, "default", "viridis")
        )
    
        if cmap_name:
            try:
                cmap = plt.get_cmap(cmap_name)
                logger.info(f'''{varname}:: using user-defined colormap: {cmap_name}''')
            except Exception:
                logger.warning(f'''{varname}:: invalid cmap "{cmap_name}"''')
                cmap = None
        else:
            cmap = None
    
        # =========================
        # 2. Meteorology defaults
        # =========================
        if cmap is None:
            var = varname.lower()
    
            # Temperature (NWS-style)
            if any(v in var for v in ["tmp", "temp", "t_inc"]):
                colors = [
                    "#4B0082", "#0000FF", "#00BFFF", "#00FF00",
                    "#FFFF00", "#FFA500", "#FF4500", "#FF0000"
                ]
                cmap = LinearSegmentedColormap.from_list("nws_temp", colors)
                logger.info(f'''{varname}:: using NWS temperature colormap''')
    
            # Wind / vector fields
            elif any(v in var for v in ["ugrd", "vgrd", "wind"]):
                cmap = plt.get_cmap("RdBu_r")
                logger.info(f'''{varname}:: using wind diverging colormap''')
    
            # Generic fallback
            else:
                cmap = plt.get_cmap("viridis")
                logger.info(f'''{varname}:: using default colormap (viridis)''')
    
        # =========================
        # 3. Range handling
        # =========================
        range_cfg = self.cfg.plot.range
        logger.debug(f'''range in config: {to_plain(range_cfg)}''') 
        var_range = getattr(
            range_cfg,
            varname,
            getattr(range_cfg, "default", None)
        )
        vmin = getattr(var_range, "vmin", None)
        vmax = getattr(var_range, "vmax", None)
    
        if vmin is None or vmax is None:
            if is_increment:
                vmax_auto = np.nanpercentile(np.abs(data_var), 98)
                vmin, vmax = -vmax_auto, vmax_auto
            else:
                vmin = np.nanpercentile(data_var, 2)
                vmax = np.nanpercentile(data_var, 98)

        logger.info(
            f"{varname}:: cmap={getattr(cmap, 'name', type(cmap).__name__)}, "
            f"vmin={vmin}, vmax={vmax}"
        )
    
        return cmap, vmin, vmax

