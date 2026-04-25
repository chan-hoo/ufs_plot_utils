import numpy as np
import xarray as xr
import pytest
from ufs_plot_utils.data import DataReader


class DummyDataset:
    """
    Mock dataset object for testing DataReader
    """
    def __init__(self, path=".", filename="dummy.nc", file_type="file"):
        self.path = path
        self.filename = filename
        self.file_type = file_type
        self.z_index = None
        self.time_index = 0


def test_slice_time():
    """
    Test time dimension slicing
    """
    ds = xr.Dataset({
        "var": (("time", "y", "x"), np.random.rand(2, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], None, 0)

    assert "time" not in da.dims, f'''Time dimension should be removed, remaining dims: {da.dims}'''
    assert da.shape == (10, 10), f'''Expected shape (10, 10), got {da.shape}'''


def test_slice_z_dimension():
    """
    Test z dimension slicing
    """
    ds = xr.Dataset({
        "var": (("z", "y", "x"), np.random.rand(5, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], 2, None)

    assert "z" not in da.dims, f'''Z dimension should be removed, remaining dims: {da.dims}'''
    assert da.shape == (10, 10), f'''Expected shape (10, 10), got {da.shape}'''


def test_slice_time_only_from_4d():
    """
    Test slicing only time dimension from 4D array
    """
    ds = xr.Dataset({
        "var": (("time", "z", "y", "x"), np.random.rand(3, 5, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], None, 0)

    assert "time" not in da.dims, f'''Time dimension should be removed, dims: {da.dims}'''
    assert "z" in da.dims, f'''Z dimension should be preserved, dims: {da.dims}'''
    assert da.ndim == 3, f'''Expected 3D result (z, y, x), got {da.ndim}D with shape {da.shape}'''
    assert da.shape == (5, 10, 10), f'''Expected shape (5, 10, 10), got {da.shape}'''


def test_slice_z_only_from_4d():
    """
    Test slicing only z dimension from 4D array
    """
    ds = xr.Dataset({
        "var": (("time", "z", "y", "x"), np.random.rand(3, 5, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], 2, None)

    assert "z" not in da.dims, f'''Z dimension should be removed, dims: {da.dims}'''
    assert "time" in da.dims, f'''Time dimension should be preserved, dims: {da.dims}'''
    assert da.ndim == 3, f'''Expected 3D result (time, y, x), got {da.ndim}D with shape {da.shape}'''
    assert da.shape == (3, 10, 10), f''''Expected shape (3, 10, 10), got {da.shape}'''


def test_slice_both_time_and_z_from_4d():
    """
    Test slicing both time and z dimensions from 4D array
    """
    ds = xr.Dataset({
        "var": (("time", "z", "y", "x"), np.random.rand(3, 5, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], 1, 2)

    assert "time" not in da.dims, f'''Time dimension should be removed, dims: {da.dims}'''
    assert "z" not in da.dims, f'''Z dimension should be removed, dims: {da.dims}'''
    assert da.ndim == 2, f'''Expected 2D result (y, x), got {da.ndim}D with shape {da.shape}'''
    assert da.shape == (10, 10), f'''Expected shape (10, 10), got {da.shape}'''


@pytest.mark.parametrize("time_idx,z_idx,expected_ndim", [(0, 1, 2), (1, 0, 2), (None, 0, 3), (0, None, 3)])
def test_slice_parametrized(time_idx, z_idx, expected_ndim):
    """
    Test slicing with various index combinations and verify expected dimensionality
    """
    ds = xr.Dataset({
        "var": (("time", "z", "y", "x"), np.random.rand(3, 5, 10, 10))
    })

    reader = DataReader(DummyDataset())
    da = reader._slice_data(ds["var"], z_idx, time_idx)

    assert da.ndim == expected_ndim, f'''Expected {expected_ndim}D result, got {da.ndim}D with shape {da.shape}'''
