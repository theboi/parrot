from typing import TypedDict
from AppKit import NSWorkspace
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXValueGetValue,
    kAXWindowsAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXTitleAttribute,
    kAXValueCGPointType,
    kAXValueCGSizeType,
)


class WindowBounds(TypedDict):
    title: str
    x: float
    y: float
    width: float
    height: float


class WindowDetector:
    def __init__(self):
        self.workspace = NSWorkspace.sharedWorkspace()

    def get_window_bounds(self, pid: str) -> list[WindowBounds]:
        """Get the bounding box of the window with PID of `pid`."""

        app_ref = AXUIElementCreateApplication(pid)

        # Get the windows attribute
        err, windows = AXUIElementCopyAttributeValue(app_ref, kAXWindowsAttribute, None)

        # err == 0 if there is no error
        if err != 0:
            print(f"Error getting windows: {err}")
            return None

        window_bounds = []

        for window in windows:
            title_err, title = AXUIElementCopyAttributeValue(
                window, kAXTitleAttribute, None
            )
            title = title if title_err == 0 else "Untitled"

            pos_err, pos_ref = AXUIElementCopyAttributeValue(
                window, kAXPositionAttribute, None
            )
            size_err, size_ref = AXUIElementCopyAttributeValue(
                window, kAXSizeAttribute, None
            )
            if pos_err != 0 or size_err != 0:
                print(f"Error getting windows: {pos_err}")
                return None

            # Unpack AXValue references to CGPoint and CGSize
            # AXValueGetValue returns (success, value) tuple in PyObjC
            pos_success, pos = AXValueGetValue(pos_ref, kAXValueCGPointType, None)
            size_success, size = AXValueGetValue(size_ref, kAXValueCGSizeType, None)
            if pos_success and size_success:
                window_info: WindowBounds = {
                    "title": title,
                    "x": pos.x,
                    "y": pos.y,
                    "width": size.width,
                    "height": size.height,
                }
                window_bounds.append(window_info)
        return window_bounds
