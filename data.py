import logging
import numpy as np
import xarray as xr
import os
import re
from .utils import extract_tile_prefix

logger = logging.getLogger(__name__)

class DataReader:
    """
    Read NetCDF data and extract 2D fields or 2D with tiles.
    """
    def __init__(self, dataset):
        self.dataset = dataset

        self.path = dataset.path
        self.filename = dataset.filename
        self.file_type = dataset.file_type
        self.z_index = dataset.z_index
        self.time_index = dataset.time_index

        self.ds = None


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
    def get_data(self, varname, z_index=None, time_index=0):
        """
        Choose geo data reading method based on config
        """
        z_index = z_index if z_index is not None else self.z_index

        if self.file_type == "file":
            return self.get_data_file(varname, z_index, time_index)
        else:
            return self.get_data_tiles(varname, z_index, time_index)


# ======================================================================================= CHJ =====
    def get_data_file(self, varname, z_index=None, time_index=0):
        """
        Extract 2D or 2D+tile data for a given variable from a single NetCDF file.
        """
        self._open_dataset()

        logger.info(f'''Reading variable: {varname}''')
        z_index = z_index if z_index is not None else getattr(self, "z_index", 0)

        da = self.ds[varname]

        logger.info(f'''{varname}:: dims = {da.dims}''')
        logger.debug(f'''{varname}:: shape = {da.shape}''')

        # Slice time and z-level
        da = self._slice_data(da, z_index, time_index)

        # Ensure 2D or 2D with 6 tiles
        if "tile" in da.dims:
            if da.ndim != 3:
                raise ValueError(f'''{varname} is not 2D + tile after slicing, dims={da.dims}''')
            logger.info(f'''{varname} is 2D + tile, dims={da.dims}''')
        else:
            if da.ndim != 2:
                raise ValueError(f'''{varname} is not 2D after slicing, dims={da.dims}''')

        logger.info(f'''{varname}:: final shape = {da.shape}''')

        data_min = np.nanmin(da.values)
        data_max = np.nanmax(da.values)
        logger.info(f"{varname}:: min={data_min}, max={data_max}")

        return da, da.values


# ======================================================================================= CHJ =====
    def get_data_tiles(self, varname, z_index=None, time_index=0):
        """
        Read tiled NetCDF files using xarray (fast, lazy loading)
            input_file: prefix of input tiled files (Ex. {input_file}.tile#.nc)
        """    
        import glob
    
        input_file = self.filename
        logger.debug(f'''Tiles:: input_file = {input_file}''')

        # Remove file extension and tile#
        prefix = extract_tile_prefix(input_file)
        logger.info(f'''Tiles:: prefix = {prefix}''')

        input_path = self.path
        z_index = z_index if z_index is not None else getattr(self, "z_index", 0)
    
        # Collect files
        pattern = os.path.join(input_path, f"{prefix}.tile*.nc")
        logger.debug(f'''Tiles:: pattern = {pattern}''')
        file_list = sorted(glob.glob(pattern))
        logger.debug(f'''Tiles:: file_list = {file_list}''')
        if len(file_list) != 6:
            raise ValueError(f'''Expected 6 tiles, found {len(file_list)}''')
    
        logger.info(f'''Opening tiled dataset (6 files)''')
    
        datasets = []
        for f in file_list:
            ds = xr.open_dataset(f)
            datasets.append(ds)
        
        ds = xr.concat(datasets, dim="tile")

        if varname not in ds:
            raise ValueError(f'''{varname} not found in tiled dataset''')
    
        da = ds[varname]

        logger.info(f'''{varname}:: dims = {da.dims}''')
        logger.debug(f'''{varname}:: shape = {da.shape}''')
    
        # Slice time and z-level
        da = self._slice_data(da, z_index, time_index)

        # Ensure (tile, y, x)
        if da.ndim != 3:
            raise ValueError(f"{varname} is not (tile, y, x), dims={da.dims}")
   
        ds.close()

        data_min = np.nanmin(da.values)
        data_max = np.nanmax(da.values)
        logger.info(f"{varname}:: min={data_min}, max={data_max}")

        return da, da.values


# ======================================================================================= CHJ =====
    def _slice_data(self, da, z_index, time_index):
        """
        Apply time + vertical slicing
        """    
        # time
        time_dim = next((d for d in ["time", "Time"] if d in da.dims), None)
        if time_dim:
            if da.sizes[time_dim] > 1:
                logger.warning(f'''{time_dim} dimension > 1, using index {time_index}''')
            da = da.isel({time_dim: time_index})
    
        # vertical
        # pfull (1->127: high->low altitude: 127=near-surface, 76=505.65mb)
        z_dims = ["pfull", "zaxis_1", "zaxis_2", "zaxis_3",
                  "zaxis_4", "lev", "level", "depth", "z"]
        z_dim = next((d for d in z_dims if d in da.dims), None)
        if z_dim:
            da = da.isel({z_dim: z_index})
    
        return da

