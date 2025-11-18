import mss
import numpy as np
from PIL import Image

def capture_region(bounds: dict) -> Image.Image:
    """Capture a screen region defined by bounds dict with keys x,y,width,height.

    Returns a PIL.Image in RGB.
    """
    monitor = {
        "left": int(bounds["x"]),
        "top": int(bounds["y"]),
        "width": int(bounds["width"]),
        "height": int(bounds["height"]),
    }
    with mss.mss() as sct:
        shot = sct.grab(monitor)
        # mss returns BGRA; convert to RGB
        img = np.array(shot)[:, :, :3][:, :, ::-1]
        return Image.fromarray(img)