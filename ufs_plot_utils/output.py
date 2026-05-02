import os
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class OutputManager:
    """
    Handle saving figures.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.output_path = self.cfg.get("output", "path", default="./")

    # =============================================================== CHJ ===

    def save_figure(self, fig, filename, dpi=300, close=True):

        os.makedirs(self.output_path, exist_ok=True)

        # -------------------------
        # Ensure extension
        # -------------------------
        root, ext = os.path.splitext(filename)

        if ext == "":
            filename = f'''{filename}.png'''

        full_path = os.path.join(self.output_path, filename)

        if os.path.exists(full_path):
            logger.warning(f'''Overwriting existing file: {full_path}''')

        fig.savefig(full_path, dpi=dpi, bbox_inches="tight")

        logger.info(f'''Saved figure: {full_path}''')

        if close:
            plt.close(fig)

        return full_path
