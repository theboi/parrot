from .window_detector import WindowDetector
from ..interaction import InteractionHandler
from ..detector import UIDetector
from abc import ABC, abstractmethod
from typing import Callable, Union, Generator, List
import threading
import time
import mss
import numpy as np
from PIL import Image
import cv2


class Screen(ABC):
    def __init__(self):
        self.detector = WindowDetector()
        self.interaction = InteractionHandler()
        self._recording = False
        self._record_thread = None
        self._video_writer = None
        self._ui_detector = None  # Lazy-loaded

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
        self.stop_recording()

    def capture(self) -> Image.Image:
        """Capture a single frame of the window.
        
        Returns:
            PIL.Image in RGB format, or None if bounds unavailable.
        """
        bounds = self.get_bounds()
        if not bounds:
            return None
        
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

    def frames(self, fps: float = 30) -> Generator[Image.Image, None, None]:
        """Generator that yields frames at the specified FPS.
        
        Args:
            fps: Target frames per second (default 30)
            
        Yields:
            PIL.Image frames in RGB format
        """
        interval = 1.0 / fps
        with mss.mss() as sct:
            while True:
                start = time.time()
                
                bounds = self.get_bounds()
                if not bounds:
                    break
                
                monitor = {
                    "left": int(bounds["x"]),
                    "top": int(bounds["y"]),
                    "width": int(bounds["width"]),
                    "height": int(bounds["height"]),
                }
                shot = sct.grab(monitor)
                img = np.array(shot)[:, :, :3][:, :, ::-1]
                
                yield Image.fromarray(img)
                
                # Maintain target FPS
                elapsed = time.time() - start
                if elapsed < interval:
                    time.sleep(interval - elapsed)

    def start_recording(self, output_path: str, fps: float = 30, codec: str = 'mp4v'):
        """Start recording the window to a video file.
        
        Args:
            output_path: Path to output video file (e.g., 'output.mp4')
            fps: Frames per second (default 30)
            codec: FourCC codec code (default 'mp4v' for .mp4)
        """
        if self._recording:
            raise RuntimeError("Already recording")
        
        import cv2
        
        bounds = self.get_bounds()
        if not bounds:
            raise RuntimeError("Could not get window bounds")
        
        width = int(bounds["width"])
        height = int(bounds["height"])
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self._video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        self._recording = True
        
        def record_loop():
            interval = 1.0 / fps
            with mss.mss() as sct:
                while self._recording:
                    start = time.time()
                    
                    bounds = self.get_bounds()
                    if not bounds:
                        break
                    
                    monitor = {
                        "left": int(bounds["x"]),
                        "top": int(bounds["y"]),
                        "width": int(bounds["width"]),
                        "height": int(bounds["height"]),
                    }
                    shot = sct.grab(monitor)
                    # mss returns BGRA, OpenCV expects BGR
                    frame = np.array(shot)[:, :, :3]
                    self._video_writer.write(frame)
                    
                    elapsed = time.time() - start
                    if elapsed < interval:
                        time.sleep(interval - elapsed)
            
            self._video_writer.release()
            self._video_writer = None
        
        self._record_thread = threading.Thread(target=record_loop, daemon=True)
        self._record_thread.start()

    def stop_recording(self):
        """Stop the current recording."""
        if not self._recording:
            return
        
        self._recording = False
        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def _get_ui_detector(self) -> UIDetector:
        """Lazy-load the UI detector (model loading is expensive)."""
        if self._ui_detector is None:
            self._ui_detector = UIDetector()
        return self._ui_detector

    def detect_ui(self, labels: List[str] = None, score_thresh: float = 0.3) -> List[dict]:
        """Detect UI elements in the current window.
        
        Args:
            labels: List of UI element labels to detect. 
                    Default: ['button', 'input', 'checkbox', 'link', 'dropdown']
            score_thresh: Minimum confidence score (0-1)
            
        Returns:
            List of detections, each with keys: label, score, bbox=(x1,y1,x2,y2)
        """
        if labels is None:
            labels = ['button', 'input', 'checkbox', 'link', 'dropdown']
        
        frame = self.capture()
        if frame is None:
            return []
        
        detector = self._get_ui_detector()
        return detector.detect(frame, labels, score_thresh)

    def frames_with_detection(
        self,
        labels: List[str] = None,
        fps: float = 10,
        score_thresh: float = 0.3
    ) -> Generator[tuple[Image.Image, List[dict]], None, None]:
        """Generator that yields frames with UI detection results.
        
        Args:
            labels: UI element labels to detect
            fps: Target frames per second (default 10, lower due to model inference)
            score_thresh: Minimum confidence score
            
        Yields:
            Tuple of (PIL.Image frame, list of detections)
        """
        if labels is None:
            labels = ['button', 'input', 'checkbox', 'link', 'dropdown']
        
        detector = self._get_ui_detector()
        interval = 1.0 / fps
        
        with mss.mss() as sct:
            while True:
                start = time.time()
                
                bounds = self.get_bounds()
                if not bounds:
                    break
                
                monitor = {
                    "left": int(bounds["x"]),
                    "top": int(bounds["y"]),
                    "width": int(bounds["width"]),
                    "height": int(bounds["height"]),
                }
                shot = sct.grab(monitor)
                img = np.array(shot)[:, :, :3][:, :, ::-1]
                frame = Image.fromarray(img)
                
                # Run detection
                detections = detector.detect(frame, labels, score_thresh)
                
                yield frame, detections
                
                # Maintain target FPS
                elapsed = time.time() - start
                if elapsed < interval:
                    time.sleep(interval - elapsed)

    def record_with_detection(
        self,
        output_path: str,
        labels: List[str] = None,
        fps: float = 10,
        score_thresh: float = 0.3,
        codec: str = 'mp4v'
    ):
        """Start recording with real-time UI detection overlays.
        
        Captures frames, runs OWL-ViT detection, draws bounding boxes,
        and writes to video file.
        
        Args:
            output_path: Path to output video file (e.g., 'output.mp4')
            labels: UI element labels to detect
            fps: Target frames per second (default 10, lower due to model inference)
            score_thresh: Minimum confidence score
            codec: FourCC codec code (default 'mp4v' for .mp4)
        """
        if self._recording:
            raise RuntimeError("Already recording")
        
        if labels is None:
            labels = ['button', 'input', 'checkbox', 'link', 'dropdown']
        
        bounds = self.get_bounds()
        if not bounds:
            raise RuntimeError("Could not get window bounds")
        
        width = int(bounds["width"])
        height = int(bounds["height"])
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self._video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        self._recording = True
        
        # Pre-load the detector in main thread to avoid issues
        detector = self._get_ui_detector()
        
        def record_loop():
            interval = 1.0 / fps
            with mss.mss() as sct:
                while self._recording:
                    start = time.time()
                    
                    bounds = self.get_bounds()
                    if not bounds:
                        break
                    
                    monitor = {
                        "left": int(bounds["x"]),
                        "top": int(bounds["y"]),
                        "width": int(bounds["width"]),
                        "height": int(bounds["height"]),
                    }
                    shot = sct.grab(monitor)
                    img = np.array(shot)[:, :, :3][:, :, ::-1]
                    frame = Image.fromarray(img)
                    
                    # Run detection and draw boxes
                    detections = detector.detect(frame, labels, score_thresh)
                    annotated = UIDetector.draw_detections(frame, detections)
                    
                    self._video_writer.write(annotated)
                    
                    elapsed = time.time() - start
                    if elapsed < interval:
                        time.sleep(interval - elapsed)
            
            self._video_writer.release()
            self._video_writer = None
        
        self._record_thread = threading.Thread(target=record_loop, daemon=True)
        self._record_thread.start()

    def capture_with_detection(
        self,
        labels: List[str] = None,
        score_thresh: float = 0.3,
        draw_boxes: bool = True
    ) -> tuple[Image.Image, List[dict]]:
        """Capture a single frame with UI detection.
        
        Args:
            labels: UI element labels to detect
            score_thresh: Minimum confidence score
            draw_boxes: If True, return image with bounding boxes drawn
            
        Returns:
            Tuple of (PIL.Image, list of detections)
        """
        if labels is None:
            labels = ['button', 'input', 'checkbox', 'link', 'dropdown']
        
        frame = self.capture()
        if frame is None:
            return None, []
        
        detector = self._get_ui_detector()
        detections = detector.detect(frame, labels, score_thresh)
        
        if draw_boxes and detections:
            annotated_bgr = UIDetector.draw_detections(frame, detections)
            # Convert BGR back to RGB PIL Image
            annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(annotated_rgb)
        
        return frame, detections

    @property
    @abstractmethod
    def pid(self):
        pass
