Usage
=====

Basic example:

.. code-block:: python

   from ufs_plot_utils.pipeline import Pipeline
   from ufs_plot_utils.config import Config

   cfg = Config("config.yaml")
   pipeline = Pipeline(cfg)
   pipeline.run_plot_tiles()
