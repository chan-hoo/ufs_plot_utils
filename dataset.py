class Dataset:
    def __init__(self, ds_cfg):
        self.name = ds_cfg.name

        self.dataset = ds_cfg.dataset
        self.geo = ds_cfg.geo

        self.colormap = getattr(ds_cfg, "colormap", {})
        self.range = getattr(ds_cfg, "range", {})
        self.data_kind = getattr(ds_cfg, "data_kind", "standard")

        # -------------------------
        # IMPORTANT FLATTENED ACCESS
        # -------------------------
        self.var_list = self.dataset.var_list
        self.z_index = getattr(self.dataset, "z_index", None)
        self.time_index = getattr(self.dataset, "time_index", 0)

        self.path = self.dataset.path
        self.filename = self.dataset.filename
        self.file_type = self.dataset.file_type
