from .screen import Screen
from .chrome_controller import ChromeController


class WebScreen(Screen):
    def __init__(self, url: str, headless: bool, window_size: tuple[int, int]):
        super().__init__()
        self.url = url
        self.controller = ChromeController(
            url=url, headless=headless, window_size=window_size
        )

    @property
    def pid(self):
        return self.controller.pid
