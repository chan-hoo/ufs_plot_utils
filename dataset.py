class Dataset:
    def __init__(self, ds_cfg):
        self.cfg = ds_cfg

        self.name = ds_cfg.name

        # dataset block
        self.dataset = ds_cfg.dataset
        self.path = ds_cfg.dataset.path
        self.filename = ds_cfg.dataset.filename
        self.file_type = ds_cfg.dataset.file_type
        self.var_list = ds_cfg.dataset.var_list
        self.z_index = getattr(ds_cfg.dataset, "z_index", None)
        self.time_index = getattr(ds_cfg.dataset, "time_index", 0)

        # geo block
        self.geo = ds_cfg.geo

        # plot config
        self.colormap = getattr(ds_cfg, "colormap", {})
        self.range = getattr(ds_cfg, "range", {})
        self.data_kind = getattr(ds_cfg, "data_kind", "standard")
