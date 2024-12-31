#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import time
import numpy as np
import cv2
import subprocess
from datetime import datetime
import logging
from kill_switch import should_stop

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"motion_detector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class MotionDetector:
    def __init__(self, position, threshold=30):
        self.position = position  # (x, y) tuple
        self.threshold = threshold
        self.last_frame = None
        self.last_motion_time = time.time()
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        self.motion_signal_file = os.path.join(self.working_dir, "motion_status")
        self.check_interval = 0.1
        self.last_check_time = time.time()
        self.motion_sensitivity = 5  # Reduced sensitivity
        
        logging.info(f"Motion Detector started at position: {self.position}")
        logging.info(f"Working directory: {self.working_dir}")
        logging.info(f"Motion signal file: {self.motion_signal_file}")
    
    def hidden_screen_capture(self, area):
        """Capture screen area using a hidden method with minimal processing."""
        try:
            x1, y1, x2, y2 = area
            width = x2 - x1
            height = y2 - y1
            
            # Use a shell command to capture the screen
            temp_file = f"/tmp/screen_capture_{time.time()}.png"
            capture_cmd = f"screencapture -R {x1},{y1},{width},{height} -x {temp_file}"
            
            # Use os.system to execute the command
            os.system(capture_cmd)
            
            # Check if the file was created
            if not os.path.exists(temp_file):
                logging.error(f"Screen capture failed: {temp_file} not created")
                return None
            
            # Read the image in grayscale to reduce processing
            frame = cv2.imread(temp_file, cv2.IMREAD_GRAYSCALE)
            
            # Remove the temporary file
            os.remove(temp_file)
            
            return frame
        except Exception as e:
            logging.error(f"Error in hidden screen capture: {str(e)}")
            return None
    
    def detect_motion(self):
        """Detect if there's any motion in the area."""
        try:
            x, y = self.position
            area = (x - self.threshold, y - self.threshold, x + self.threshold, y + self.threshold)
            current_frame = self.hidden_screen_capture(area)
            
            if current_frame is None or self.last_frame is None:
                self.last_frame = current_frame
                logging.info("Initial frame captured")
                return False
            
            # Calculate absolute difference between frames
            diff = cv2.absdiff(current_frame, self.last_frame)
            
            # Apply threshold to identify significant changes
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            # Count changed pixels
            total_changed_pixels = np.sum(thresh > 0)
            
            # Store current frame for next comparison
            self.last_frame = current_frame.copy()
            
            # Consider motion only if significant changes detected
            motion_detected = total_changed_pixels > self.motion_sensitivity
            
            if motion_detected:
                self.last_motion_time = time.time()
                logging.info(f"Motion Detected | Pixels Changed: {total_changed_pixels} | Position: {x},{y}")
            else:
                # Log a periodic heartbeat to show the script is still running
                if time.time() - self.last_motion_time > 30:  # Every 30 seconds
                    logging.info(f"No Motion | Last Motion: {time.time() - self.last_motion_time:.2f} seconds ago")
            
            return motion_detected
            
        except Exception as e:
            logging.error(f"Error in motion detection: {str(e)}")
            return False
    
    def update_motion_status(self):
        """Update the motion status file."""
        try:
            with open(self.motion_signal_file, "w") as f:
                f.write(f"{time.time()}")
            os.chmod(self.motion_signal_file, 0o666)  # Make file readable/writable by all
        except Exception as e:
            logging.error(f"Error updating motion status: {str(e)}")
    
    def run(self):
        """Main loop to detect motion and update status."""
        try:
            logging.info("Starting motion detection...")
            
            while not should_stop():  # Check kill conditions
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self.last_check_time = current_time
                    
                    if self.detect_motion():
                        self.update_motion_status()
                    
                time.sleep(0.1)
            
            logging.info("Motion detector stopped by kill switch")
                
        except KeyboardInterrupt:
            logging.info("Motion detector stopped by user")
        except Exception as e:
            logging.error(f"Fatal error in motion detector: {str(e)}")

if __name__ == "__main__":
    # Default position if not specified
    position = (1693, 1073)
    
    # Create motion detector instance
    detector = MotionDetector(position)
    
    logging.info("Starting motion detection...")
    
    try:
        while not should_stop():
            # Detect motion
            motion_detected = detector.detect_motion()
            
            # Optional: Add a small delay to prevent excessive CPU usage
            time.sleep(detector.check_interval)
    
    except KeyboardInterrupt:
        logging.info("Motion detection stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error in motion detection: {str(e)}")
    finally:
        logging.info("Motion detection script terminated.") 