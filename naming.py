import logging

logger = logging.getLogger(__name__)

class NameBuilder:
    """
    Handle naming conventions / labels
    """

    def __init__(self, cfg):
        self.cfg = cfg


# ======================================================================================= CHJ =====
    def build_filename(self, varname, dataset_name, z_index=None):
        """
        Build filename:
        prefix_dataset_var_levXXX_PDY_cyc
        """
        parts = []

        # File name prefix
        prefix = self.cfg.output.filename_prefix
        parts.append(prefix)

        # Dataset name
        if dataset_name:
            parts.append(dataset_name)

        # Variable name
        parts.append(varname)

        # Vertical level
        if z_index is not None:
            parts.append(f'''z{int(z_index):03d}''')

        # Date
        pdy = str(self.cfg.plot.PDY)
        if pdy:
            parts.append(pdy)

        # Cycle
        cycle = self.cfg.plot.cycle
        if cycle:
            parts.append(cycle)

        filename = "_".join(parts)

        logger.info(f'''Output filename: {filename}''')

        return filename


# ======================================================================================= CHJ =====
    def build_title(self, varname, dataset_name, z_index=None):
        """
        Build plot title:
        prefix::dataset::var::zXXX::PDY::cyc
        """    
        parts = []
    
        # Prefix
        prefix = self.cfg.output.filename_prefix.upper()
        parts.append(prefix)

        if dataset_name:
            parts.append(dataset_name)

        # Variable name
        parts.append(varname)
    
        # Vertical level
        if z_index is not None:
            parts.append(f'''z{int(z_index)}''')

        # Date
        pdy = str(self.cfg.plot.PDY)
        if pdy:
            parts.append(pdy)

        # Cycle
        cycle = self.cfg.plot.cycle
        if cycle:
            parts.append(cycle)
    
        title = " :: ".join(parts)
    
        logger.info(f'''Plot title: {title}''')
    
        return title
