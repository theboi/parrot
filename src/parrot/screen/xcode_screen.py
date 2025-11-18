from .screen import Screen


class XcodeScreen(Screen):
    def __init__(self, pid: str):
        super().__init__()
        self._pid = pid

    @property
    def pid(self):
        return self._pid
