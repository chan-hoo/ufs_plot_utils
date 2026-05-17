class Dataset:
    def __init__(self, cfg):
        # -------------------------
        # Top-level
        # -------------------------
        self.name = cfg.get("name")
        self.data_kind = cfg.get("data_kind", "increment")
        self.data_model = cfg.get("data_model", "fv3")
        self.title = cfg.get("title")

        # -------------------------
        # GEO (FLATTEN)
        # -------------------------
        geo_cfg = cfg.get("geo", {}) or {}

        self.geo_path = geo_cfg.get("path")
        self.geo_filename = geo_cfg.get("filename")
        self.geo_file_type = geo_cfg.get("file_type", "file")

        # -------------------------
        # Data block (FLATTEN HERE)
        # -------------------------
        data_cfg = cfg.get("data", {})

        self.path = data_cfg.get("path")
        self.filename = data_cfg.get("filename")
        self.file_type = data_cfg.get("file_type", "file")
        self.group = data_cfg.get("group")
        self.var_list = data_cfg.get("var_list", [])
        self.channels = data_cfg.get("channels", None)
        self.z_index = data_cfg.get("z_index")
        self.time_index = data_cfg.get("time_index", 0)

        # -------------------------
        # Style (top-level)
        # -------------------------
        self.colormap = cfg.get("colormap", {})
        self.range = cfg.get("range", {})

        # -------------------------
        # Validation
        # -------------------------
        if not self.filename:
            raise ValueError(f'''Dataset "{self.name}" missing filename''')

        if not self.var_list:
            raise ValueError(f'''Dataset "{self.name}" missing var_list''')

        if not self.path:
            raise ValueError(f'''Dataset "{self.path}" missing path''')

        if self.channels:
            if any(c < 1 for c in self.channels):
                raise ValueError("channels must be 1-based positive integers")
