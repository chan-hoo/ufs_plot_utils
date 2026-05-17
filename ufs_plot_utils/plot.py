import logging
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable

logger = logging.getLogger(__name__)


class Plotter:
    """
    Plot data using Cartopy.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        plot_cfg = cfg.get("plot", default={})
        self.proj_cfg = plot_cfg.get("projection", {})
        self.fig_cfg = plot_cfg.get("figure", {})
        self.cb_cfg = plot_cfg.get("colorbar", {})
        self.title_cfg = plot_cfg.get("title", {})
        self.scatter_cfg = plot_cfg.get("scatter", {})
        self.bg_cfg = plot_cfg.get("background", {})
        self.style_resolver = None

        # Set Cartopy Natural Earth data path
        cartopy_ne_path = plot_cfg.get("cartopy_ne_path")
        if cartopy_ne_path:
            cartopy.config['data_dir'] = cartopy_ne_path
            logger.info(f'''Cartopy data_dir set to: {cartopy_ne_path}''')

    # =============================================================== CHJ ===

    def set_style_resolver(self, resolver):
        self.style_resolver = resolver

    # =============================================================== CHJ ===

    def plot_data_tiles(
        self,
        lat,
        lon,
        da,
        varname,
        output_title,
        dataset
    ):
        """
        Plot cubed-sphere tiled data.
        """

        logger.info("Plotting seamless global map")
        if self.style_resolver is None:
            raise RuntimeError("StyleResolver not set.")

        if lat.shape != da.shape:
            raise ValueError(
                f'''Geo/data mismatch: lat={lat.shape}, data={da.shape}'''
            )

        # -------------------------
        # Tiles (dynamic, not hardcoded)
        # -------------------------
        if "tile" not in da.dims:
            raise ValueError(f'''Expected "tile" dimension, got {da.dims}''')

        num_tiles = da.sizes["tile"]

        # -------------------------
        # Projection
        # -------------------------
        projection = self.build_projection()

        # -------------------------
        # Figure
        # -------------------------
        figsize = self.fig_cfg.get("figsize", [10, 5])
        dpi = self.fig_cfg.get("dpi", 150)

        fig, ax = plt.subplots(
            1, 1,
            figsize=figsize,
            dpi=dpi,
            subplot_kw=dict(projection=projection)
        )

        ax.set_global()
        # -------------------------
        # Optional regional extent
        # -------------------------
        self.apply_extent(ax)
        # -------------------------
        # Background
        # -------------------------
        self.plot_background(ax)

        # -------------------------
        # Style
        # -------------------------
        style = self.style_resolver.resolve(
            varname,
            da
        )
        cmap = style.cmap
        vmin = style.vmin
        vmax = style.vmax
        cbar_label = style.label

        # -------------------------
        # Title
        # -------------------------
        title_fs = self.title_cfg.get("fontsize", 8)
        ax.set_title(output_title, fontsize=title_fs)

        # -------------------------
        # Plot tiles
        # -------------------------
        cs = None

        for it in range(num_tiles):
            lon_tile = np.asarray(lon[it, :, :])
            lat_tile = np.asarray(lat[it, :, :])

            # Extract from xarray (not pre-converted numpy)
            var_tile = da.isel(tile=it).values

            # Wrap longitude
            lon_tile = (lon_tile + 180) % 360 - 180

            # Mask invalid
            var_tile = np.ma.masked_invalid(var_tile)

            cs = ax.pcolormesh(
                lon_tile,
                lat_tile,
                var_tile,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                transform=ccrs.PlateCarree(),
                shading="auto"
            )

        # -------------------------
        # Colorbar
        # -------------------------
        cb_extend = self.cb_cfg.get("extend", "both")
        cb_size = self.cb_cfg.get("size", "3%")
        cb_pad = self.cb_cfg.get("pad", 0.1)
        cb_label_fs = self.cb_cfg.get("label_fontsize", 7)
        cb_tick_fs = self.cb_cfg.get("tick_fontsize", 6)

        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(
                    size=cb_size, pad=cb_pad, axes_class=plt.Axes
                )
        fig.add_axes(ax_cb)

        cbar = plt.colorbar(cs, cax=ax_cb, extend=cb_extend)
        cbar.ax.tick_params(labelsize=cb_tick_fs)
        cbar.set_label(cbar_label, fontsize=cb_label_fs)

        return fig

    # =============================================================== CHJ ===

    def plot_data_scatter(
        self,
        lat,
        lon,
        da,
        varname,
        output_title,
        dataset
    ):
        """
        Scatter plot for observation data
        """

        logger.info("Plotting observation scatter")

        if self.style_resolver is None:
            raise RuntimeError("StyleResolver not set.")

        # -------------------------
        # Projection
        # -------------------------
        projection = self.build_projection()

        # -------------------------
        # Figure
        # -------------------------
        figsize = self.fig_cfg.get("figsize", [10, 5])
        dpi = self.fig_cfg.get("dpi", 150)

        fig, ax = plt.subplots(
            1, 1,
            figsize=figsize,
            dpi=dpi,
            subplot_kw=dict(projection=projection)
        )

        ax.set_global()
        # -------------------------
        # Optional regional extent
        # -------------------------
        self.apply_extent(ax)
        # -------------------------
        # Background
        # -------------------------
        self.plot_background(ax)

        # -------------------------
        # Style
        # -------------------------
        style = self.style_resolver.resolve(
            varname,
            da
        )
        cmap = style.cmap
        vmin = style.vmin
        vmax = style.vmax
        cbar_label = style.label

        # -------------------------
        # Title
        # -------------------------
        title_fs = self.title_cfg.get("fontsize", 8)
        ax.set_title(output_title, fontsize=title_fs)

        # -------------------------
        # Scatter
        # -------------------------
        cs = ax.scatter(
            lon,
            lat,
            c=da.values,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            s=self.scatter_cfg.get("marker_size", 5),
            transform=ccrs.PlateCarree()
        )

        # -------------------------
        # Colorbar
        # -------------------------
        cb_extend = self.cb_cfg.get("extend", "both")
        cb_size = self.cb_cfg.get("size", "3%")
        cb_pad = self.cb_cfg.get("pad", 0.1)
        cb_label_fs = self.cb_cfg.get("label_fontsize", 7)
        cb_tick_fs = self.cb_cfg.get("tick_fontsize", 6)

        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(
            size=cb_size,
            pad=cb_pad,
            axes_class=plt.Axes,
        )
        fig.add_axes(ax_cb)

        cbar = plt.colorbar(cs, cax=ax_cb, extend=cb_extend)
        cbar.ax.tick_params(labelsize=cb_tick_fs)
        cbar.set_label(cbar_label, fontsize=cb_label_fs)

        return fig

    # =============================================================== CHJ ===

    def plot_data_grid(
            self,
            lat,
            lon,
            da,
            varname,
            output_title,
            dataset
    ):
        """
        Plot regular/curvilinear 2D grid data.
        """

        logger.info("Plotting structured grid map")

        if self.style_resolver is None:
            raise RuntimeError("StyleResolver not set.")

        # -------------------------
        # Projection
        # -------------------------
        projection = self.build_projection()

        # -------------------------
        # Figure
        # -------------------------
        figsize = self.fig_cfg.get("figsize", [10, 5])
        dpi = self.fig_cfg.get("dpi", 150)

        fig, ax = plt.subplots(
            1,
            1,
            figsize=figsize,
            dpi=dpi,
            subplot_kw=dict(projection=projection)
        )

        ax.set_global()
        # -------------------------
        # Optional regional extent
        # -------------------------
        self.apply_extent(ax)
        # -------------------------
        # Background
        # -------------------------
        self.plot_background(ax)

        # -------------------------
        # Style
        # -------------------------
        style = self.style_resolver.resolve(varname, da)

        cs = ax.pcolormesh(
            lon,
            lat,
            np.ma.masked_invalid(da.values),
            cmap=style.cmap,
            vmin=style.vmin,
            vmax=style.vmax,
            transform=ccrs.PlateCarree(),
            shading="auto"
        )

        # -------------------------
        # Title
        # -------------------------
        title_fs = self.title_cfg.get("fontsize", 8)
        ax.set_title(output_title, fontsize=title_fs)

        # -------------------------
        # Colorbar
        # -------------------------
        divider = make_axes_locatable(ax)

        ax_cb = divider.new_horizontal(
            size=self.cb_cfg.get("size", "3%"),
            pad=self.cb_cfg.get("pad", 0.1),
            axes_class=plt.Axes,
        )

        fig.add_axes(ax_cb)

        cbar = plt.colorbar(
            cs,
            cax=ax_cb,
            extend=self.cb_cfg.get("extend", "both")
        )

        cbar.ax.tick_params(
            labelsize=self.cb_cfg.get("tick_fontsize", 6)
        )

        cbar.set_label(
            style.label,
            fontsize=self.cb_cfg.get("label_fontsize", 7)
        )

        return fig

    # =============================================================== CHJ ===

    def build_projection(self):

        proj_name = self.proj_cfg.get("name", "Robinson")

        central_lon = self.proj_cfg.get(
            "central_longitude",
            -77.0369
        )

        proj_map = {
            "Robinson": ccrs.Robinson,
            "PlateCarree": ccrs.PlateCarree,
            "Mollweide": ccrs.Mollweide,
            "NorthPolarStereo": ccrs.NorthPolarStereo,
            "SouthPolarStereo": ccrs.SouthPolarStereo,
            "Stereographic": ccrs.Stereographic,
        }

        proj_class = proj_map.get(
            proj_name,
            ccrs.Robinson
        )

        if proj_name == "PlateCarree":
            return ccrs.PlateCarree()

        elif proj_name == "Stereographic":
            return ccrs.Stereographic(
                central_longitude=central_lon,
                central_latitude=self.proj_cfg.get(
                    "central_latitude",
                    90,
                ),
            )

        else:
            return proj_class(
                central_longitude=central_lon
            )

    # =============================================================== CHJ ===

    def apply_extent(self, ax):

        extent_cfg = self.cfg.get("plot", "extent")
        if not extent_cfg:
            return

        ax.set_extent(
            [
                extent_cfg["lon"][0],
                extent_cfg["lon"][1],
                extent_cfg["lat"][0],
                extent_cfg["lat"][1],
            ],
            crs=ccrs.PlateCarree(),
        )

    # =============================================================== CHJ ===

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
