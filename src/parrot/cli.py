import argparse
import sys
import time

from .screen.web_screen import WebScreen
from .window_detector import WindowDetector
from .interaction import InteractionHandler
from .screen_capture import capture_region
from .detector import UIDetector

def run():
    parser = argparse.ArgumentParser(description='UI Testing Agent for Chrome')
    parser.add_argument('url', help='Webpage URL to test (e.g., https://example.com)')
    parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
    parser.add_argument('--window-size', nargs=2, type=int, default=[1280, 720], 
                       metavar=('WIDTH', 'HEIGHT'), help='Window size (default: 1280 720)')
    parser.add_argument('--detect-ui', action='store_true', help='Capture window via OS and run pretrained UI detector')
    parser.add_argument('--labels', type=str, default='button,input,checkbox,radio,link,dropdown,modal,tooltip',
                       help='Comma-separated labels for zero-shot detector')
    
    args = parser.parse_args()
    
    print(f"🚀 Launching Chrome with URL: {args.url}")

    try:
        screen = WebScreen(args.url, args.headless, args.window_size)
        print(screen.get_bounds())
         
        # Wait (poll) for Chrome window to appear with non-zero size
        # print("📐 Detecting Chrome window bounds...")
        # bounds = None
        # for _ in range(50):  # ~5s max
        #     b = window_detector.get_chrome_window_bounds()
        #     if b and b.get('width', 0) > 0 and b.get('height', 0) > 0:
        #         bounds = b
        #         break
        #     time.sleep(0.1)
        
        # if bounds:
        #     print(f"✅ Window bounds detected: {bounds}")
        #     print(f"   Position: ({bounds['x']}, {bounds['y']})")
        #     print(f"   Size: {bounds['width']} x {bounds['height']}")

        #     if args.detect_ui:
        #         print("\n🔎 Capturing window and running UI detector...")
        #         image = capture_region(bounds)
        #         labels = [s.strip() for s in args.labels.split(',') if s.strip()]
        #         detections = detector.detect(image, labels=labels, score_thresh=0.3)
        #         annotated = UIDetector.draw_detections(image, detections)
        #         import os
        #         annot_dir = os.path.join(os.getcwd(), 'temp')
        #         os.makedirs(annot_dir, exist_ok=True)
        #         out_path = os.path.join(annot_dir, f"annotated_{int(time.time())}.png")
        #         import cv2
        #         cv2.imwrite(out_path, annotated)
        #         print(f"✅ Saved annotated detection to: {out_path}")
            
            # print("\n🧪 Testing interactions...")
            # test_clicks = [
            #     (400, 300),
            #     (500, 350),
            # ]
            
            # test_text_fields = [
            #     (300, 250, "test@example.com"),
            # ]
            
            # for i, (x, y) in enumerate(test_clicks):
            #     abs_x = bounds['x'] + x
            #     abs_y = bounds['y'] + y
            #     print(f"   Clicking at relative ({x}, {y}) -> absolute ({abs_x}, {abs_y})")
            #     interaction.click(abs_x, abs_y)
            #     time.sleep(1)
            
            # for x, y, text in test_text_fields:
            #     abs_x = bounds['x'] + x
            #     abs_y = bounds['y'] + y
            #     print(f"   Clicking text field at ({x}, {y}) and typing: {text}")
            #     interaction.click(abs_x, abs_y)
            #     time.sleep(0.5)
            #     interaction.type_text(text)
            #     time.sleep(1)
            
            # print("\n✅ Interaction tests completed")
        # else:
        #     print("❌ Failed to detect Chrome window bounds")
        #     sys.exit(1)
        
        # if not args.detect_ui:
        #     print("\n⏸️  Keeping browser open for 10 seconds...")
        #     print("   Press Ctrl+C to exit early")
        #     time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    # finally:
    #     chrome_controller.cleanup()

if __name__ == "__main__":
    run()


