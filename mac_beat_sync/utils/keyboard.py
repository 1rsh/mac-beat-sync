import numpy as np
import subprocess
from tqdm import tqdm

from .utils import get_config

class BaseKeyboardController:
    def __init__(self):
        pass

    def set_brightness(self, level):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def close(self):
        pass

class MacKeyboardController:
    def __init__(self):
        config = get_config()
        self.cli_tool = config.driver.CLI_TOOL
        self.raw_bar = tqdm(
            total=1.0,
            desc="Raw Brightness",
            bar_format="{desc} |{bar}| {percentage:3.0f}%",
            ncols=50,
            leave=True,
            position=0,
        )
        self.smooth_bar = tqdm(
            total=1.0,
            desc="Smoothed Output",
            bar_format="{desc} |{bar}| {percentage:3.0f}%",
            ncols=50,
            leave=True,
            position=1,
        )

    def set_brightness(self, level):
        level = float(np.clip(level, 0, 1))
        self.smooth_bar.n = level
        self.smooth_bar.refresh()
        subprocess.run(
            [self.cli_tool, str(level)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def update_raw(self, value):
        value = float(value)
        self.raw_bar.n = value
        self.raw_bar.refresh()

    def close(self):
        self.raw_bar.close()
        self.smooth_bar.close()
