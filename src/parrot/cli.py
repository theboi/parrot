import argparse
import sys
import time
from .chrome_controller import ChromeController
from .window_detector import WindowDetector
from .interaction import InteractionHandler

def run():
    parser = argparse.ArgumentParser(description='UI Testing Agent for Chrome')
    parser.add_argument('url', help='Webpage URL to test (e.g., https://example.com)')
    parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
    parser.add_argument('--window-size', nargs=2, type=int, default=[1280, 720], 
                       metavar=('WIDTH', 'HEIGHT'), help='Window size (default: 1280 720)')
    
    args = parser.parse_args()
    
    print(f"🚀 Launching Chrome with URL: {args.url}")
    
    chrome_controller = ChromeController()
    window_detector = WindowDetector()
    interaction = InteractionHandler()
    
    try:
        driver = chrome_controller.launch_chrome(
            url=args.url,
            headless=args.headless,
            window_size=args.window_size
        )
        
        print("✅ Chrome launched successfully")
        time.sleep(2)
        
        print("📐 Detecting Chrome window bounds...")
        bounds = window_detector.get_chrome_window_bounds()
        
        if bounds:
            print(f"✅ Window bounds detected: {bounds}")
            print(f"   Position: ({bounds['x']}, {bounds['y']})")
            print(f"   Size: {bounds['width']} x {bounds['height']}")
            
            print("\n🧪 Testing interactions...")
            test_clicks = [
                (400, 300),
                (500, 350),
            ]
            
            test_text_fields = [
                (300, 250, "test@example.com"),
            ]
            
            for i, (x, y) in enumerate(test_clicks):
                abs_x = bounds['x'] + x
                abs_y = bounds['y'] + y
                print(f"   Clicking at relative ({x}, {y}) -> absolute ({abs_x}, {abs_y})")
                interaction.click(abs_x, abs_y)
                time.sleep(1)
            
            for x, y, text in test_text_fields:
                abs_x = bounds['x'] + x
                abs_y = bounds['y'] + y
                print(f"   Clicking text field at ({x}, {y}) and typing: {text}")
                interaction.click(abs_x, abs_y)
                time.sleep(0.5)
                interaction.type_text(text)
                time.sleep(1)
            
            print("\n✅ Interaction tests completed")
        else:
            print("❌ Failed to detect Chrome window bounds")
            sys.exit(1)
        
        print("\n⏸️  Keeping browser open for 10 seconds...")
        print("   Press Ctrl+C to exit early")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        chrome_controller.cleanup()

if __name__ == "__main__":
    run()


