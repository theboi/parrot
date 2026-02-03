"""
Test video capture functionality of Screen class.
"""

import os
import time
import tempfile
from parrot.screen.web_screen import WebScreen


def test_single_frame_capture():
    """Test capturing a single frame."""
    screen = WebScreen('https://example.com', headless=False, window_size=(800, 600))
    time.sleep(2)
    
    try:
        frame = screen.capture()
        
        assert frame is not None, "Frame should not be None"
        assert frame.mode == "RGB", f"Expected RGB mode, got {frame.mode}"
        assert frame.size[0] > 0 and frame.size[1] > 0, "Frame should have positive dimensions"
        
        print(f"✓ Single frame capture: {frame.size} pixels, mode: {frame.mode}")
    finally:
        screen.close()


def test_frame_generator():
    """Test the frame generator yields frames at target FPS."""
    screen = WebScreen('https://example.com', headless=False, window_size=(800, 600))
    time.sleep(2)
    
    try:
        frames_captured = []
        start_time = time.time()
        
        for frame in screen.frames(fps=10):
            frames_captured.append(frame)
            if len(frames_captured) >= 5:
                break
        
        elapsed = time.time() - start_time
        
        assert len(frames_captured) == 5, f"Expected 5 frames, got {len(frames_captured)}"
        
        for i, frame in enumerate(frames_captured):
            assert frame is not None, f"Frame {i} should not be None"
            assert frame.mode == "RGB", f"Frame {i} expected RGB mode"
        
        # At 10 FPS, 5 frames should take ~0.5 seconds (allowing some tolerance)
        assert elapsed >= 0.4, f"Frames captured too fast: {elapsed:.2f}s"
        assert elapsed < 1.0, f"Frames captured too slow: {elapsed:.2f}s"
        
        print(f"✓ Frame generator: captured {len(frames_captured)} frames in {elapsed:.2f}s")
    finally:
        screen.close()


def test_video_recording():
    """Test recording to a video file."""
    screen = WebScreen('https://example.com', headless=False, window_size=(800, 600))
    time.sleep(2)
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        output_path = f.name
    
    try:
        assert not screen.is_recording, "Should not be recording initially"
        
        screen.start_recording(output_path, fps=15)
        
        assert screen.is_recording, "Should be recording after start"
        
        time.sleep(2)  # Record for 2 seconds
        
        screen.stop_recording()
        
        assert not screen.is_recording, "Should not be recording after stop"
        
        # Check file was created and has content
        assert os.path.exists(output_path), "Output file should exist"
        file_size = os.path.getsize(output_path)
        assert file_size > 0, f"Output file should not be empty, got {file_size} bytes"
        
        print(f"✓ Video recording: saved {file_size} bytes to {output_path}")
    finally:
        screen.close()
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_recording_prevents_double_start():
    """Test that starting recording twice raises an error."""
    screen = WebScreen('https://example.com', headless=False, window_size=(800, 600))
    time.sleep(2)
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        output_path = f.name
    
    try:
        screen.start_recording(output_path, fps=15)
        
        try:
            screen.start_recording(output_path, fps=15)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Already recording" in str(e)
            print(f"✓ Double start prevention: correctly raised RuntimeError")
    finally:
        screen.stop_recording()
        screen.close()
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_stop_recording_when_not_recording():
    """Test that stopping when not recording is safe (no-op)."""
    screen = WebScreen('https://example.com', headless=False, window_size=(800, 600))
    time.sleep(2)
    
    try:
        # Should not raise
        screen.stop_recording()
        print("✓ Stop when not recording: no error raised")
    finally:
        screen.close()


def run_all_tests():
    """Run all video capture tests."""
    print("=" * 50)
    print("Running Video Capture Tests")
    print("=" * 50)
    print()
    
    tests = [
        ("Single frame capture", test_single_frame_capture),
        ("Frame generator", test_frame_generator),
        ("Video recording", test_video_recording),
        ("Double start prevention", test_recording_prevents_double_start),
        ("Stop when not recording", test_stop_recording_when_not_recording),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        print(f"Running: {name}")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
