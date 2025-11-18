from typing import TypedDict
import subprocess
import json
import re
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
from Quartz import CGPoint, CGSize


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

    def get_chrome_bounds_with_applescript(self, pid: str):
        """Get the bounding box of the Chrome window with PID of `pid`.

        Alternative method to get_window_bounds() for Chrome which uses AppleScript instead (more reliable than pyobjc in some cases)

        """
        apps_found = [
            app
            for app in self.workspace.runningApplications()
            if app.processIdentifier() == pid
        ]

        if not apps_found:
            print(f"No Chrome application with PID of {pid} found.")
            return None

        apps_found = apps_found[0]

        try:
            script = """
            tell application "Google Chrome"
                try
                    if (count of windows) > 0 then
                        set frontWindow to window 1
                        set windowBounds to bounds of frontWindow
                        return windowBounds
                    end if
                on error error_message number error_number
                    display dialog error_message
                    return missing value
                end try
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, check=True
            )

            # Parse result: "x1, y1, x2, y2"
            bounds_str = result.stdout.strip()
            print(bounds_str)
            match = re.match(r"(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", bounds_str)

            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                return {
                    "x": x1,
                    "y": y1,
                    "width": x2 - x1,
                    "height": y2 - y1,
                    "x2": x2,
                    "y2": y2,
                }
            else:
                print(f"Could not parse bounds: {bounds_str}")
                return None

        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e.stderr}")
            return None
        except Exception as e:
            print(f"Error getting window bounds: {e}")
            return None

    def get_all_chrome_windows_with_applescript(self):
        """Get bounds for all Chrome windows (for multiple window support)."""
        try:
            script = """
            tell application "Google Chrome"
                set windowList to {}
                repeat with w in windows
                    set windowBounds to bounds of w
                    set end of windowList to windowBounds
                end repeat
                return windowList
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, check=True
            )

            # Parse multiple bounds
            bounds_list = []
            for line in result.stdout.strip().split("\n"):
                match = re.match(r"(\d+),\s*(\d+),\s*(\d+),\s*(\d+)", line)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    bounds_list.append(
                        {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}
                    )

            return bounds_list

        except Exception as e:
            print(f"Error getting all windows: {e}")
            return []
