Configuration
=============

Example:

.. code-block:: yaml

   input:
     datasets:
       - name: base
         data_kind: increment
         data:
           path: /data
           filename: file.nc
           var_list: ["T"]

   plot:
     channels:
       base:
         T: [1, 3]
