import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable

logger = logging.getLogger(__name__)

class PlotData:
    """
    Plot data using Cartopy.
    """
    def __init__(self, cfg):
        self.cfg = cfg

        # Set Cartopy Natural Earth data path
        cartopy_ne_path = getattr(cfg, "cartopy_ne_path", None)
        if cartopy_ne_path:
            cartopy.config['data_dir'] = cartopy_ne_path
            logger.info(f'''Cartopy data_dir set to: {cartopy_ne_path}''')


# ======================================================================================= CHJ =====
#    def plot_data_single(self):


# ======================================================================================= CHJ =====
    def plot_data_tiles(
        self,
        data_var,
        lat,
        lon,
        varname,
        var_cbar_label="Test label",
        output_title="Test Title",
        output_file="test_plot.png"
    ):
        """
        Plot cubed-sphere tiled data.
        """
        logger.info("Plotting seamless global map")

        num_tiles = 6
        central_lon=-77.0369

        fig,ax=plt.subplots(1,1,subplot_kw=dict(projection=ccrs.Robinson(central_lon)))
        ax.set_global()
        ax.set_title(output_title, fontsize=8)

        # Background plot
        self.plot_background(ax)
        # Colormap
        cmap, vmin, vmax = self.select_cmap(varname, data_var)

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
        cbar.set_label(var_cbar_label, fontsize=7)

        # Save figure
        self.out_file(output_file, ndpi=300, fmt="png", fig=fig)


# ======================================================================================= CHJ =====
    def select_cmap(self, varname, data_var):
        """
        Central logic for choosing colormap
        """
        increment_flag = str(getattr(self.cfg, "INCREMENT_PLOT", "NO")).upper()
        is_increment = increment_flag in ["YES", "TRUE", "1"]
    
        if is_increment:
            return self.choose_colormap(varname, data_var)
        else:
            return self.get_met_cmap(varname, data_var)


# ======================================================================================= CHJ =====
    def get_met_cmap(self, varname, data_var):
        """
        Return meteorology-specific colormap and range
        """
        from matplotlib.colors import LinearSegmentedColormap
    
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


# ======================================================================================= CHJ =====
    def plot_background(self, ax):
        """
        Add background features (land, coastlines, borders, etc.)
        """
        logger.info(f'''Adding background features''')

        back_res = '50m'   # '110m' (faster) or '50m' (better)
        fline_wd = 0.5
        falpha = 0.7

        land = cfeature.NaturalEarthFeature(
            'physical', 'land', back_res,
            edgecolor='face',
            facecolor=cfeature.COLORS['land'],
            alpha=falpha
        )

        lakes = cfeature.NaturalEarthFeature(
            'physical', 'lakes', back_res,
            edgecolor='blue',
            facecolor='none',
            linewidth=fline_wd,
            alpha=falpha
        )

        coastline = cfeature.NaturalEarthFeature(
            'physical', 'coastline', back_res,
            edgecolor='black',
            facecolor='none',
            linewidth=fline_wd,
            alpha=falpha
        )

        states = cfeature.NaturalEarthFeature(
            'cultural', 'admin_1_states_provinces', back_res,
            edgecolor='green',
            facecolor='none',
            linewidth=fline_wd,
            linestyle=':',
            alpha=falpha
        )

        borders = cfeature.NaturalEarthFeature(
            'cultural', 'admin_0_countries', back_res,
            edgecolor='red',
            facecolor='none',
            linewidth=fline_wd,
            alpha=falpha
        )

        #ax.add_feature(land)
        #ax.add_feature(lakes)
        #ax.add_feature(states)
        #ax.add_feature(borders)
        ax.add_feature(coastline)


# ======================================================================================= CHJ =====
    def out_file(self, output_file, ndpi=300, fmt="png", fig=None):
        """
        Save figure to output directory.
    
        Parameters:
            output_file (str): file name (without extension or with .png)
            ndpi (int): resolution
            fmt: file extension
            fig (matplotlib.figure.Figure): optional figure object
        """
    
        work_dir = getattr(self.cfg, "output_path", ".")
    
        # Full name of output file
        output_file = f'''{output_file}.{fmt}'''
    
        fp_out = os.path.join(work_dir, output_file)
    
        logger.info(f'''Saving figure to: {fp_out}''')
    
        if fig is not None:
            fig.savefig(fp_out, dpi=ndpi, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.savefig(fp_out, dpi=ndpi, bbox_inches='tight')
            plt.close('all')
