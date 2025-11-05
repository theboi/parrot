import pyautogui
import time

class InteractionHandler:
    """Handle mouse clicks and keyboard input."""
    
    def __init__(self):
        # Safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions
        
    def click(self, x, y, button='left', clicks=1):
        """Click at absolute screen coordinates."""
        pyautogui.click(x, y, button=button, clicks=clicks)
        time.sleep(0.2)  # Small delay after click
    
    def double_click(self, x, y):
        """Double click at coordinates."""
        self.click(x, y, clicks=2)
    
    def right_click(self, x, y):
        """Right click at coordinates."""
        self.click(x, y, button='right')
    
    def type_text(self, text, interval=0.05):
        """Type text at current cursor position."""
        pyautogui.write(text, interval=interval)
        time.sleep(0.2)
    
    def type_text_slow(self, text, interval=0.1):
        """Type text slowly (for testing)."""
        pyautogui.write(text, interval=interval)
    
    def press_key(self, key):
        """Press a single key."""
        pyautogui.press(key)
        time.sleep(0.1)
    
    def get_screen_size(self):
        """Get screen dimensions."""
        return pyautogui.size()


