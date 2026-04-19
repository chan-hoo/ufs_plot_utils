import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .cmap import CmapManager

logger = logging.getLogger(__name__)

class Plotter:
    """
    Plot data using Cartopy.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.cmap_helper = CmapManager(cfg)

        # Set Cartopy Natural Earth data path
        cartopy_ne_path = self.cfg.plot.cartopy_ne_path
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
        is_increment = dataset.data_kind == "increment"
        cmap, vmin, vmax = self.cmap_helper.get_cmap_and_range(
            varname,
            data_var,
            dataset.colormap,
            dataset.range,
            is_increment=is_increment
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
        var_cbar_label = self.build_cbar_label(da, varname, dataset)
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="3%", pad=0.1, axes_class=plt.Axes)
        fig.add_axes(ax_cb)
        cbar = plt.colorbar(cs, cax=ax_cb, extend="both")
        cbar.ax.tick_params(labelsize=6)
        cbar.set_label(var_cbar_label, fontsize=7)

        return fig


# ======================================================================================= CHJ =====
    def build_cbar_label(self, da, varname, dataset):
        long_name = da.attrs.get("long_name", varname)
        units = da.attrs.get("units", "")
    
        label = f"{long_name} ({units})" if units else long_name
    
        if dataset.data_kind == "increment":
            label = f"Δ{label}"
    
        return label


# ======================================================================================= CHJ =====
    def plot_background(self, ax):
        """
        Add background features (config-driven)
        """    
        bg_cfg = getattr(self.cfg.plot, "background", {})
        features = bg_cfg.get("features", []) if isinstance(bg_cfg, dict) else getattr(bg_cfg, "features", [])
        enabled = set(features)
        logger.info(f'''Background features: {enabled}''')

        back_res = "50m"
        fline_wd = 0.5
        falpha = 0.7
    
        def feature(geom, cat="physical", **kwargs):
            return cfeature.NaturalEarthFeature(
                cat, geom, back_res,
                **kwargs
            )
    
        if "land" in enabled:
            ax.add_feature(
                feature(
                    "land",
                    edgecolor="face",
                    facecolor=cfeature.COLORS["land"],
                    alpha=falpha
                )
            )
    
        if "lakes" in enabled:
            ax.add_feature(
                feature(
                    "lakes",
                    edgecolor="blue",
                    facecolor="none",
                    linewidth=fline_wd,
                    alpha=falpha
                )
            )
    
        if "coastline" in enabled:
            ax.add_feature(
                feature(
                    "coastline",
                    edgecolor="black",
                    facecolor="none",
                    linewidth=fline_wd,
                    alpha=falpha
                )
            )
    
        if "states" in enabled:
            ax.add_feature(
                feature(
                    "admin_1_states_provinces",
                    cat="cultural",
                    edgecolor="green",
                    facecolor="none",
                    linewidth=fline_wd,
                    linestyle=":",
                    alpha=falpha
                )
            )
    
        if "borders" in enabled:
            ax.add_feature(
                feature(
                    "admin_0_countries",
                    cat="cultural",
                    edgecolor="red",
                    facecolor="none",
                    linewidth=fline_wd,
                    alpha=falpha
                )
            )

