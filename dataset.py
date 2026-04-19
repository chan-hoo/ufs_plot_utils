class Dataset:
    def __init__(self, ds_cfg):
        """
        ds_cfg is now a plain dictionary
        """

        self.name = ds_cfg.get("name")

        self.dataset = ds_cfg.get("dataset", {})
        self.geo = ds_cfg.get("geo", {})

        self.colormap = ds_cfg.get("colormap", {})
        self.range = ds_cfg.get("range", {})
        self.data_kind = ds_cfg.get("data_kind", "standard")

    # ===================================================================================
    @property
    def var_list(self):
        return self.dataset.get("var_list", [])

    @property
    def z_index(self):
        return self.dataset.get("z_index")

    @property
    def time_index(self):
        return self.dataset.get("time_index", 0)

    @property
    def path(self):
        return self.dataset.get("path")

    @property
    def filename(self):
        return self.dataset.get("filename")

    @property
    def file_type(self):
        return self.dataset.get("file_type")

