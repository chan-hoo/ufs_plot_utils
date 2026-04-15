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
        prefix = getattr(self.cfg, "output_file_prefix")
        parts.append(prefix)

        # Variable name
        parts.append(varname)

        # Vertical level
        if z_index is not None:
            parts.append(f'''z{int(z_index):03d}''')

        # Date
        pdy = getattr(self.cfg, "PDY", None)
        if pdy:
            parts.append(str(pdy))

        # Cycle
        cycle = getattr(self.cfg, "cycle", None)
        if cycle:
            parts.append(cycle)

        filename = "_".join(parts)

        logger.info(f'''Output filename: {filename}''')

        return filename


# ======================================================================================= CHJ =====
    def build_title(self, varname, z_index=None):
        """
        Build plot title:
        prefix var (levXXX) PDY cyc
        """    
        parts = []
    
        # Prefix
        prefix = getattr(self.cfg, "output_file_prefix")
        prefix = prefix.upper()
        parts.append(prefix)
    
        # Variable name
        parts.append(varname)
    
        # Vertical level
        if z_index is not None:
            parts.append(f'''z{int(z_index)}''')
    
        # Date
        pdy = getattr(self.cfg, "PDY", None)
        if pdy:
            parts.append(str(pdy))
    
        # Cycle
        cycle = getattr(self.cfg, "cycle", None)
        if cycle:
            parts.append(cycle)
    
        title = " :: ".join(parts)
    
        logger.info(f'''Plot title: {title}''')
    
        return title
