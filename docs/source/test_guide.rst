Testing Guide
=============

This document provides an overview of the testing suite for the ``ufs_plot_utils`` package. The tests are located in the ``tests/`` directory and are divided into unit tests, integration tests, and shared configurations.

Test Directory Structure
------------------------

The directory is organized as follows:

* ``tests/conftest.py``: Contains shared pytest fixtures.
* ``tests/unit/``: Contains unit tests for individual modules.
* ``tests/integration/``: Contains high-level smoke tests for the entire pipeline.

Shared Fixtures (``conftest.py``)
---------------------------------

The ``conftest.py`` file defines reusable data structures that are automatically available to all tests. Key fixtures include:

* **sample_da_tile**: Creates a mock DataArray with dimensions ``(tile, yaxis_1, xaxis_1)``.
* **sample_da_grid**: Creates a mock DataArray with dimensions ``(tile, grid_yt, grid_xt)``.
* **zero_da**: A utility fixture providing a zero-filled array for baseline comparisons.

Unit Tests
----------

Unit tests verify the correctness of specific components in isolation.

Config Module (``test_config.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests the ``Config`` class to ensure it correctly parses YAML files, handles nested keys, and manages missing configuration sections gracefully.

Data Reader (``test_data_reader.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Focuses on the ``DataReader._slice_data`` method. It verifies that:
* Time dimensions are correctly sliced out of 3D and 4D arrays.
* Vertical levels (z-dimensions) are correctly extracted.
* Multiple dimensions can be sliced simultaneously to return a 2D spatial plane.

Geo Reader (``test_geo_reader.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests the ``GeoReader`` without requiring actual NetCDF files on disk. It uses ``monkeypatch`` to mock ``xarray.open_dataset``, verifying:
* Initialization and dataset loading.
* Support for different file protocols (file, s3, url).
* Correct path joining for file system access.

Utilities (``test_utils.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Verifies the ``normalize_tile_dims`` function. This ensures that various UFS/FV3 dimension naming conventions (like ``grid_yt`` or ``yaxis_1``) are consistently converted to a standard ``(tile, y, x)`` format while preserving data integrity.

Integration Tests
-----------------

Integration tests (smoke tests) verify that the different components of the library work together.

Pipeline Smoke Test (``test_pipeline_smoke.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These tests simulate a full execution of the plotting pipeline. They:
1.  Generate a temporary YAML configuration file.
2.  Mock the ``DataReader`` and ``GeoReader`` to return synthetic data instead of reading from disk.
3.  Instantiate a ``Pipeline`` and call ``run_plot_tiles()``.
4.  Ensure the entire process completes without errors, confirming the wiring between config, data loading, and processing is functional.

Running Tests
-------------

To run the full test suite, navigate to the project root and execute:

.. code-block:: bash

   pytest tests/

