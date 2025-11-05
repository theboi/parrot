__all__ = ["ChromeController", "WindowDetector", "InteractionHandler"]
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("parrot")
except PackageNotFoundError:
    __version__ = "0.0.0"
    
print(__version__)

from .chrome_controller import ChromeController
from .window_detector import WindowDetector
from .interaction import InteractionHandler