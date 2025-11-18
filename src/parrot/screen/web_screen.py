from .screen import Screen
from .chrome_controller import ChromeController


class WebScreen(Screen):
    def __init__(self, url: str, headless: bool, window_size: tuple[int, int]):
        super().__init__()
        self.url = url
        self.controller = ChromeController(
            url=url, headless=headless, window_size=window_size
        )

        # # Wait (poll) for Chrome window to appear with non-zero size
        # print("📐 Detecting Chrome window bounds...")
        # bounds = None
        # for _ in range(50):  # ~5s max
        #     b = window_detector.get_chrome_window_bounds()
        #     if b and b.get("width", 0) > 0 and b.get("height", 0) > 0:
        #         bounds = b
        #         break
        #     time.sleep(0.1)

        # if bounds:
        #     print(f"✅ Window bounds detected: {bounds}")
        #     print(f"   Position: ({bounds['x']}, {bounds['y']})")
        #     print(f"   Size: {bounds['width']} x {bounds['height']}")

    @property
    def pid(self):
        return self.controller.pid
