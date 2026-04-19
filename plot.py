import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .cmap import PlotStyleResolver
from .utils import to_dict

logger = logging.getLogger(__name__)

class Plotter:
    """
    Plot data using Cartopy.
    """
    def __init__(self, cfg):
        self.cfg = cfg

        plot_cfg = to_dict(getattr(cfg, "plot", {}))

        self.proj_cfg  = plot_cfg.get("projection", {})
        self.fig_cfg   = plot_cfg.get("figure", {})
        self.cb_cfg    = plot_cfg.get("colorbar", {})
        self.title_cfg = plot_cfg.get("title", {})
        self.bg_cfg    = plot_cfg.get("background", {})

        # Set Cartopy Natural Earth data path
        cartopy_ne_path = plot_cfg.get("cartopy_ne_path")
        if cartopy_ne_path:
            cartopy.config['data_dir'] = cartopy_ne_path
            logger.info(f'''Cartopy data_dir set to: {cartopy_ne_path}''')


# ======================================================================================= CHJ =====
    def plot_data_tiles(
        self,
        data_var,
        lat,
        lon,
        da,
        varname,
        dataset,
        output_title
    ):
        """
        Plot cubed-sphere tiled data.
        """
        logger.info("Plotting seamless global map")

        num_tiles = 6
        central_lon=-77.0369

        fig,ax=plt.subplots(1,1,subplot_kw=dict(projection=ccrs.Robinson(central_lon)))
        ax.set_global()

        # Background plot
        self.plot_background(ax)

        # Colormap
        resolver = PlotStyleResolver(dataset)        
        cmap, vmin, vmax, cbar_label = resolver.resolve(
            varname,
            data_var,
            da
        )

        # Title
        ax.set_title(output_title, fontsize=8)

        cs = None
        for it in range(num_tiles):
            lon_tile = np.array(lon[it, :, :])
            lat_tile = np.array(lat[it, :, :])
            var_tile = np.array(data_var[it, :, :])

            # Wrap longitude consistently
            lon_tile = (lon_tile + 180) % 360 - 180
            # Mask invalid values
            var_tile = np.ma.masked_invalid(var_tile)

            cs = ax.pcolormesh(
                lon_tile,
                lat_tile,
                var_tile,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                transform=ccrs.PlateCarree(),
                shading="auto"   # important for seamless edges
            )

        # Colorbar
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="3%", pad=0.1, axes_class=plt.Axes)
        fig.add_axes(ax_cb)
        cbar = plt.colorbar(cs, cax=ax_cb, extend="both")
        cbar.ax.tick_params(labelsize=6)
        cbar.set_label(cbar_label, fontsize=7)

        return fig


# ======================================================================================= CHJ =====
    def plot_background(self, ax):
        """
        Add background features (config-driven)
        """
        features = set(self.bg_cfg.get("features", []))
        res = self.bg_cfg.get("resolution", "50m")
        lw = self.bg_cfg.get("linewidth", 0.5)
        alpha = self.bg_cfg.get("alpha", 0.7)
    
        logger.info(f'''Background features: {features}''')
    
        if "coastline" in features:
            ax.add_feature(
                cfeature.COASTLINE.with_scale(res),
                linewidth=lw,
                alpha=alpha
            )
    
        if "borders" in features:
            ax.add_feature(
                cfeature.BORDERS.with_scale(res),
                linewidth=lw,
                alpha=alpha
            )
    
        if "states" in features:
            ax.add_feature(
                cfeature.STATES.with_scale(res),
                linewidth=lw,
                linestyle=":",
                alpha=alpha
            )
    
        if "lakes" in features:
            ax.add_feature(
                cfeature.LAKES.with_scale(res),
                linewidth=lw,
                facecolor="none",
                edgecolor="blue",
                alpha=alpha
            )
    
        if "land" in features:
            ax.add_feature(
                cfeature.LAND.with_scale(res),
                facecolor=cfeature.COLORS["land"],
                edgecolor="face",
                alpha=alpha
            )
