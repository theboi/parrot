from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class ChromeController:
    def __init__(self):
        self.driver = None
    
    def launch_chrome(self, url, headless=False, window_size=(1280, 720)):
        """Launch Chrome browser and navigate to URL."""
        chrome_options = Options()
        
        if not headless:
            # Keep browser visible for testing
            chrome_options.add_argument("--start-maximized")
        else:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        
        # Additional options for better control
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to handle ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to URL
        self.driver.get(url)
        time.sleep(1)  # Give it a moment to start
        
        return self.driver
    
    def cleanup(self):
        """Close browser and cleanup."""
        if self.driver:
            self.driver.quit()
            self.driver = None


