import logging
import numpy as np
import xarray as xr
import os
import re
from .utils import extract_tile_prefix

logger = logging.getLogger(__name__)

class DataReader:
    """
    Read NetCDF data and extract fields (I/O layer only).
    """

    def __init__(self, dataset):
        self.dataset = dataset
        self.ds = None

        # I/O only shortcuts (safe + clean)
        self.path = dataset.dataset.path
        self.filename = dataset.dataset.filename
        self.file_type = dataset.dataset.file_type

        self.var_list = dataset.dataset.var_list
        self.z_index = getattr(dataset.dataset, "z_index", None)
        self.time_index = getattr(dataset.dataset, "time_index", 0)


    def _open_dataset(self):
        """
        Open dataset only when needed (lazy loading)
        """
        if self.ds is None:
            self.file_path = os.path.join(self.path, self.filename)
            logger.info(f'''Opening dataset: {self.file_path}''')
            try:
                self.ds = xr.open_dataset(self.file_path)
            except Exception as e:
                raise FileNotFoundError(f'''Could NOT open file: {self.file_path}''') from e


    def close(self):
        if self.ds is not None:
            self.ds.close()
            self.ds = None


# ======================================================================================= CHJ =====
    def get_data(self, varname):
        """
        Return raw DataArray (NO styling, NO plotting logic).
        """
    
        if self.file_type == "tile":
            return self._get_data_tiles(varname)
    
        elif self.file_type == "file":
            return self._get_data_file(varname)
    
        else:
            raise ValueError(f'''Unsupported file_type: {self.file_type}''')


# ======================================================================================= CHJ =====
    def _get_data_file(self, varname, z_index=None, time_index=0):
        """
        Read single NetCDF file and return DataArray.
        """
    
        self._open_dataset()
    
        logger.info(f'''Reading variable: {varname}''')
    
        if varname not in self.ds:
            raise ValueError(f'''{varname} not found in dataset''')
    
        da = self.ds[varname]
    
        logger.debug(f'''{varname} dims = {da.dims}''')
        logger.debug(f'''{varname} shape = {da.shape}''')
    
        # apply slicing (data-layer only)
        da = self._slice_data(da, self.z_index, self.time_index)
    
        # -------------------------
        # validation
        # -------------------------
        if "tile" in da.dims:
            if da.ndim != 3:
                raise ValueError(f'''{varname} expected (tile,y,x), got {da.dims}''')
        else:
            if da.ndim != 2:
                raise ValueError(f'''{varname} expected 2D, got {da.dims}''')
    
        logger.info(f'''{varname} final shape = {da.shape}''')
        logger.info(f'''{varname} min={np.nanmin(da.values)}, max={np.nanmax(da.values)}''')
    
        return da


# ======================================================================================= CHJ =====
    def _get_data_tiles(self, varname, z_index=None, time_index=0):
        """
        Read 6-tile NetCDF and return DataArray (tile, y, x).
        """    
        import glob
   
        prefix = extract_tile_prefix(self.filename)
        pattern = os.path.join(self.path, f'''{prefix}.tile*.nc''')
    
        file_list = sorted(glob.glob(pattern))
    
        if len(file_list) != 6:
            raise ValueError(f'''Expected 6 tiles, found {len(file_list)}''')
    
        logger.info(f'''Opening 6 tiles for variable: {varname}''')
        logger.debug(f'''Tile pattern: {pattern}''')
        logger.debug(f'''Files found: {file_list}''')
    
        datasets = []
    
        try:
            for f in file_list:
                datasets.append(xr.open_dataset(f))
    
            ds = xr.concat(datasets, dim="tile")
    
            if varname not in ds:
                raise ValueError(f'''{varname} not found in tiled dataset''')
    
            da = ds[varname]
    
            logger.debug(f'''{varname} dims = {da.dims}''')
            logger.debug(f'''{varname} shape = {da.shape}''')
    
            # apply slicing (data layer only)
            da = self._slice_data(da, self.z_index, self.time_index)
    
            if da.ndim != 3:
                raise ValueError(f'''{varname} expected (tile, y, x), got {da.dims}''')
    
            logger.info(f'''{varname} final shape = {da.shape}''')
            logger.info(f'''{varname} min={np.nanmin(da.values)}, max={np.nanmax(da.values)}''')
    
            return da
    
        finally:
            for d in datasets:
                try:
                    d.close()
                except Exception:
                    pass


# ======================================================================================= CHJ =====
    def _slice_data(self, da, z_index=None, time_index=0):
        """
        Apply time + vertical slicing (data-layer only).
        """
    
        # -------------------------
        # time slicing
        # -------------------------
        time_dim = next((d for d in ["time", "Time"] if d in da.dims), None)
        if time_dim is not None:
            if da.sizes.get(time_dim, 1) > 1:
                logger.debug(f'''{time_dim} > 1, selecting index {time_index}''')
            da = da.isel({time_dim: time_index})
    
        # -------------------------
        # vertical slicing
        # -------------------------
        z_dims = [
            "pfull", "zaxis_1", "zaxis_2", "zaxis_3",
            "zaxis_4", "lev", "level", "depth", "z"
        ]
    
        z_dim = next((d for d in z_dims if d in da.dims), None)
    
        if z_dim is not None and z_index is not None:
            da = da.isel({z_dim: z_index})
    
        return da

