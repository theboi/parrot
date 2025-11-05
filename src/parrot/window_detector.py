import subprocess
import json
import re
from AppKit import NSWorkspace, NSRunningApplication

class WindowDetector:
    """Detect Chrome window bounds on macOS."""
    
    def __init__(self):
        self.workspace = NSWorkspace.sharedWorkspace()
    
    def get_chrome_window_bounds(self):
        """Get the bounding box of the Chrome window."""
        # Find Chrome process
        chrome_apps = [
            app for app in self.workspace.runningApplications()
            if app.bundleIdentifier() == 'com.google.Chrome'
        ]
        
        if not chrome_apps:
            print("⚠️  Chrome not found in running applications")
            return None
        
        chrome_app = chrome_apps[0]
        
        # Use AppleScript to get window bounds (more reliable than pyobjc)
        try:
            script = '''
            tell application "Google Chrome"
                if (count of windows) > 0 then
                    set frontWindow to window 1
                    set windowBounds to bounds of frontWindow
                    return windowBounds
                end if
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse result: "x1, y1, x2, y2"
            bounds_str = result.stdout.strip()
            match = re.match(r'(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', bounds_str)
            
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                return {
                    'x': x1,
                    'y': y1,
                    'width': x2 - x1,
                    'height': y2 - y1,
                    'x2': x2,
                    'y2': y2
                }
            else:
                print(f"⚠️  Could not parse bounds: {bounds_str}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️  AppleScript error: {e.stderr}")
            return None
        except Exception as e:
            print(f"⚠️  Error getting window bounds: {e}")
            return None
    
    def get_all_chrome_windows(self):
        """Get bounds for all Chrome windows (for multiple window support)."""
        try:
            script = '''
            tell application "Google Chrome"
                set windowList to {}
                repeat with w in windows
                    set windowBounds to bounds of w
                    set end of windowList to windowBounds
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse multiple bounds
            bounds_list = []
            for line in result.stdout.strip().split('\n'):
                match = re.match(r'(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', line)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    bounds_list.append({
                        'x': x1,
                        'y': y1,
                        'width': x2 - x1,
                        'height': y2 - y1
                    })
            
            return bounds_list
            
        except Exception as e:
            print(f"⚠️  Error getting all windows: {e}")
            return []


