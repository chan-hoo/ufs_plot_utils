import logging

logger = logging.getLogger(__name__)

class SetNames:
    """
    Handle naming conventions / labels
    """

    def __init__(self, cfg):
        self.cfg = cfg


# ======================================================================================= CHJ =====
    def build_filename(self, varname, z_index=None):
        """
        Build filename:
        prefix_var_levXXX_PDY_cyc
        """
        parts = []

        # File name prefix
        prefix = getattr(self.cfg, "output_file_prefix", None)
        if prefix:
            parts.append(prefix.rstrip("_"))  # avoid double underscore

        # Variable name
        parts.append(varname)

        # Vertical level
        if z_index is not None:
            parts.append(f"z{int(z_index):03d}")

        # Date
        pdy = getattr(self.cfg, "PDY", None)
        if pdy:
            parts.append(str(pdy))

        # Cycle
        cyc = getattr(self.cfg, "cyc", None)
        if cyc:
            parts.append(f"{int(cyc):02d}")

        filename = "_".join(parts)

        logger.info(f'''Output filename: {filename}''')

        return filename

