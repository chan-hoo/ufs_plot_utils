class Dataset:
    def __init__(self, cfg):
        # -------------------------
        # Top-level
        # -------------------------
        self.name = cfg.get("name")
        self.data_kind = cfg.get("data_kind", "analysis")

        # -------------------------
        # GEO (FLATTEN)
        # -------------------------
        geo_cfg = cfg.get("geo", {}) or {}
        
        self.geo_path = geo_cfg.get("path")
        self.geo_filename = geo_cfg.get("filename")
        self.geo_file_type = geo_cfg.get("file_type", "file")

        # -------------------------
        # Dataset block (FLATTEN HERE)
        # -------------------------
        ds_cfg = cfg.get("dataset", {})

        self.path = ds_cfg.get("path")
        self.filename = ds_cfg.get("filename")
        self.file_type = ds_cfg.get("file_type", "file")

        self.var_list = ds_cfg.get("var_list", [])
        self.z_index = ds_cfg.get("z_index")
        self.time_index = ds_cfg.get("time_index", 0)

        # -------------------------
        # Style (top-level)
        # -------------------------
        self.colormap = cfg.get("colormap", {})
        self.range = cfg.get("range", {})

        # -------------------------
        # Validation (VERY IMPORTANT)
        # -------------------------
        if not self.filename:
            raise ValueError(f'''Dataset "{self.name}" missing filename''')

        if not self.var_list:
            raise ValueError(f'''Dataset "{self.name}" missing var_list''')
