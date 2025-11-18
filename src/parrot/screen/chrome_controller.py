import psutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ChromeController:
    def __init__(self, url, headless=False, window_size=(1280, 720)):
        """Initialise, launch Chrome browser and navigate to URL."""
        self.browser = None

        chrome_options = Options()
        if not headless:
            # Keep browser visible for testing
            chrome_options.add_argument("--start-maximized")
        else:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument(
                f"--window-size={window_size[0]},{window_size[1]}"
            )

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Use webdriver-manager to handle ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=chrome_options)

        self.browser.get(url)
        WebDriverWait(self.browser, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Browser ready!!!

        # There are multiple processes/pids associated with Chrome (eg different helper processes)
        # For some reason, the `browser.service.process.pid` gives a different pid than the actual
        # So, we find all associated pids and process of index 0 seems to always give the actual main Google Chrome process
        self.pid = (
            psutil.Process(self.browser.service.process.pid)
            .children(recursive=True)[0]
            .pid
        )

    def cleanup(self):
        """Close browser and cleanup."""
        if self.browser:
            self.browser.quit()
            self.browser = None
