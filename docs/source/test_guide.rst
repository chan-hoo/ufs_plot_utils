Testing Guide
=============

This document describes the testing strategy used in
``ufs_plot_utils``.

Testing Philosophy
------------------

The testing suite emphasizes:

- isolated unit tests
- lightweight smoke tests
- minimal external dependencies
- synthetic datasets
- reproducible behavior

Test Layout
-----------

Example structure:

.. code-block:: text

   tests/
   ├── conftest.py
   ├── unit/
   └── integration/

Shared Fixtures
---------------

``tests/conftest.py`` provides reusable fixtures.

Common fixtures:

- ``sample_da_tile``
- ``sample_da_grid``
- ``zero_da``

Unit Tests
----------

Config Tests
^^^^^^^^^^^^

Verify:

- YAML parsing
- nested access
- missing-key handling

DataReader Tests
^^^^^^^^^^^^^^^^

Verify:

- slicing behavior
- tiled datasets
- forecast detection
- restart detection
- observation handling

GeoReader Tests
^^^^^^^^^^^^^^^

Verify:

- file-based geo loading
- tiled geometry handling
- MOM6/CICE coordinate mapping
- observation lon/lat detection

Utility Tests
^^^^^^^^^^^^^

Verify:

- tile dimension normalization
- filename normalization
- staggered-grid mapping

Pipeline Smoke Tests
--------------------

Smoke tests validate end-to-end execution.

Typical workflow:

1. Generate temporary YAML config
2. Mock xarray readers
3. Build pipeline
4. Execute plotting tasks
5. Verify successful completion

Running Tests
-------------

Run the full suite:

.. code-block:: bash

   pytest

Run a subset:

.. code-block:: bash

   pytest tests/unit

Run with verbose logging:

.. code-block:: bash

   pytest -v

Recommended CI Checks
---------------------

Suggested automated checks:

- pytest
- flake8
- black --check
- isort --check-only

Example:

.. code-block:: bash

   pytest && flake8 ufs_plot_utils

Future Improvements
-------------------

Potential enhancements:

- coverage enforcement
- benchmark tests
- image regression tests
- Dask integration tests
- cloud-storage mocking
