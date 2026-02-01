# Parrot - AI Coding Agent Instructions

## Project Overview

Parrot is a **macOS-only** UI testing tool that uses vision AI (OWL-ViT) to detect UI elements via zero-shot object detection. It captures real screen regions and interacts with applications through native OS APIs, not DOM inspection.

## Architecture

```
src/parrot/
├── cli.py              # Entry point, argparse CLI
├── detector.py         # UIDetector: OWL-ViT zero-shot detection (transformers)
├── interaction.py      # InteractionHandler: pyautogui mouse/keyboard
├── screen_capture.py   # mss-based screen region capture
└── screen/
    ├── screen.py           # Abstract Screen base class
    ├── web_screen.py       # WebScreen: Selenium-controlled Chrome
    ├── xcode_screen.py     # XcodeScreen: attach to existing Xcode
    ├── chrome_controller.py # Selenium + webdriver-manager Chrome automation
    └── window_detector.py  # macOS Accessibility API (pyobjc) for window bounds
```

### Key Design Patterns

- **Screen abstraction**: All screen types inherit from `Screen` (abstract base). Each must implement a `pid` property. The base class provides `get_bounds()` via `WindowDetector`.
- **Controller pattern**: `WebScreen` delegates browser lifecycle to `ChromeController`. For native apps like Xcode, provide the PID directly.
- **Coordinate system**: All interactions use **absolute screen coordinates**. Convert from window-relative using bounds: `abs_x = bounds['x'] + rel_x`.

## macOS-Specific Dependencies

This project **only runs on macOS** due to:
- `pyobjc` / `pyobjc-framework-Quartz` for Accessibility API window detection
- `AppKit`, `ApplicationServices` imports in `window_detector.py`

When extending, ensure macOS platform checks (`sys_platform == 'darwin'`) for any new native integrations.

## Developer Workflow

```bash
# Install in editable mode (creates CLI command)
pip install -e .

# Run the tool
parrot https://example.com              # Launch Chrome, detect window bounds
parrot https://example.com --detect-ui  # Also run OWL-ViT UI detection
parrot https://example.com --headless   # Headless Chrome mode
```

## Key Conventions

1. **Screen implementations**: Create new screens by subclassing `Screen` and implementing the `pid` property. See `xcode_screen.py` as minimal example.
2. **Detection labels**: Pass custom labels via `--labels` flag (comma-separated). Default: `button,input,checkbox,radio,link,dropdown,modal,tooltip`.
3. **Window bounds**: Always a dict with `x`, `y`, `width`, `height` keys (floats). Use `WindowBounds` TypedDict from `window_detector.py`.
4. **Image format**: `UIDetector` expects PIL `Image.Image` (RGB). `screen_capture.capture_region()` returns this format.
5. **GPU support**: Detector auto-uses CUDA if available, falls back to CPU.

## Adding New Screen Types

```python
# src/parrot/screen/my_app_screen.py
from .screen import Screen

class MyAppScreen(Screen):
    def __init__(self, pid: int):
        super().__init__()
        self._pid = pid

    @property
    def pid(self):
        return self._pid
```

## Common Pitfalls

- **Chrome PID discovery**: Selenium's `browser.service.process.pid` returns the driver PID, not Chrome's. Use `psutil.Process().children(recursive=True)[0].pid` (see `chrome_controller.py`).
- **Accessibility permissions**: macOS requires Screen Recording + Accessibility permissions for window detection and screen capture.
- **Commented code in cli.py**: Much of the interaction test code is commented out—this is intentional scaffolding for future development.
