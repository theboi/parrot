from .window_detector import WindowDetector
from ..interaction import InteractionHandler
from abc import ABC, abstractmethod
from typing import Callable, Union


class Screen(ABC):
    def __init__(self):
        self.detector = WindowDetector()
        self.interaction = InteractionHandler()

    def get_bounds(self) -> dict:
        """Get the first window's bounds for this screen's PID.
        
        Returns:
            dict with keys: title, x, y, width, height
        """
        bounds_list = self.detector.get_window_bounds(self.pid)
        if bounds_list and len(bounds_list) > 0:
            return bounds_list[0]
        return None

    def get_all_window_bounds(self) -> list[dict]:
        """Get bounds for all windows belonging to this screen's PID.
        
        Returns:
            List of dicts, each with keys: title, x, y, width, height
        """
        return self.detector.get_window_bounds(self.pid)

    def get_size(self) -> tuple[float, float]:
        """Get the window size (width, height).
        
        Returns:
            Tuple of (width, height) in pixels, or None if window not found.
        """
        bounds = self.get_bounds()
        if bounds:
            return (bounds["width"], bounds["height"])
        return None

    def get_position(self) -> tuple[float, float]:
        """Get the window position (x, y) on screen.
        
        Returns:
            Tuple of (x, y) representing top-left corner in screen coordinates.
        """
        bounds = self.get_bounds()
        if bounds:
            return (bounds["x"], bounds["y"])
        return None

    def click(
        self,
        coord: Union[tuple[float, float], Callable[[dict], tuple[float, float]]],
        button: str = 'left',
        clicks: int = 1
    ):
        """Click at window-relative coordinates.
        
        Translates the given (x, y) position within the window's local
        coordinate system to absolute macOS screen coordinates.
        
        Args:
            coord: Either a (x, y) tuple relative to window's top-left corner,
                   OR a callable that receives bounds dict and returns (x, y) tuple.
                   Example: (100, 200) or lambda b: (b['width'] / 2, b['height'] / 2)
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks (1 for single, 2 for double)
            
        Raises:
            ValueError: If coordinates are outside window bounds
            RuntimeError: If window bounds cannot be determined
        """
        bounds = self.get_bounds()
        if not bounds:
            raise RuntimeError("Could not get window bounds")
        
        # Handle callable overload
        if callable(coord):
            coord_x, coord_y = coord(bounds)
        else:
            coord_x, coord_y = coord
        
        # Validate coordinates are within window
        if coord_x < 0 or coord_x > bounds["width"]:
            raise ValueError(f"x={coord_x} is outside window width (0-{bounds['width']})")
        if coord_y < 0 or coord_y > bounds["height"]:
            raise ValueError(f"y={coord_y} is outside window height (0-{bounds['height']})")
        
        # Translate to absolute screen coordinates
        abs_x = bounds["x"] + coord_x
        abs_y = bounds["y"] + coord_y
        
        self.interaction.click(abs_x, abs_y, button=button, clicks=clicks)

    def double_click(self, coord: tuple[float, float]):
        """Double-click at window-relative coordinates."""
        self.click(coord, clicks=2)

    def right_click(self, coord: tuple[float, float]):
        """Right-click at window-relative coordinates."""
        self.click(coord, button='right')

    def move_to(self, coord: tuple[float, float]):
        """Move cursor to window-relative coordinates without clicking.
        
        Args:
            coord: (x, y) tuple relative to window's top-left corner
        """
        bounds = self.get_bounds()
        if not bounds:
            raise RuntimeError("Could not get window bounds")
        
        abs_x = bounds["x"] + coord[0]
        abs_y = bounds["y"] + coord[1]
        
        import pyautogui
        pyautogui.moveTo(abs_x, abs_y)

    def click_center(self):
        """Click at the center of the window."""
        size = self.get_size()
        if size:
            self.click((size[0] / 2, size[1] / 2))

    def close(self):
        """Close/cleanup the screen. Override in subclasses as needed."""
        pass

    @property
    @abstractmethod
    def pid(self):
        pass
