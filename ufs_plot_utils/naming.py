import logging
import re

logger = logging.getLogger(__name__)


class NameBuilder:
    """
    Handle naming conventions / labels
    """

    def __init__(self, cfg):
        self.cfg = cfg

# ======================================================================================= CHJ =====
    def _build_parts(self, varname, dataset_name, z_index):
        parts = []

        prefix = self.cfg.get("output", "prefix", default="")
        if prefix:
            parts.append(prefix)

        if dataset_name:
            parts.append(dataset_name)

        parts.append(varname)

        if z_index is not None:
            parts.append(f'''z{int(z_index):03d}''')

        params = self.cfg.get("input", "parameters", default="")
        cycle = params.get("cycle")
        pdy = str(params.get("PDY"))

        if pdy:
            parts.append(pdy)

        if cycle:
            parts.append(cycle)

        return parts


# ======================================================================================= CHJ =====
    def build_filename(self, varname, dataset_name, z_index=None):
        parts = self._build_parts(varname, dataset_name, z_index)

        filename = "_".join(parts)

        # sanitize filename
        filename = re.sub(r'''[^a-zA-Z0-9._-]''', "", filename)

        logger.info(f'''Output filename: {filename}''')

        return filename


# ======================================================================================= CHJ =====
    def build_title(self, varname, dataset_name, z_index=None):
        parts = self._build_parts(varname, dataset_name, z_index)

        title = " :: ".join(parts)

        logger.info(f'''Plot title: {title}''')

        return title

