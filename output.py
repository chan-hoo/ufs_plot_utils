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
        self.output_path = self.cfg.output.path

    def save_figure(self, fig, filename, dpi=300):
        """
        Save figure to output_path
        """
        os.makedirs(self.output_path, exist_ok=True)

        full_path = os.path.join(self.output_path, filename)

        fig.savefig(full_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

        logger.info(f'''Saved figure: {full_path}''')
