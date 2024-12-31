#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import time
import numpy as np
import pyautogui
from PIL import ImageGrab
from datetime import datetime
import logging
from kill_switch import should_stop

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"blue_detector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class BlueDetector:
    def __init__(self, positions):
        self.positions = positions  # List of (x, y) tuples
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        self.click_signal_file = os.path.join(self.working_dir, "click_positions")
        self.check_interval = 0.1
        self.last_check_time = time.time()
        self.last_click_time = 0
        self.click_cooldown = 3  # Seconds between clicks
        
        logging.info(f"Blue Detector started")
        logging.info(f"Working directory: {self.working_dir}")
        logging.info(f"Click signal file: {self.click_signal_file}")
        logging.info("Monitoring positions:")
        for i, pos in enumerate(positions, 1):
            logging.info(f"  Position {i}: {pos}")
    
    def is_blue_present(self, x, y, threshold=30):
        """Check if blue is present at the given position."""
        try:
            area = (x - threshold, y - threshold, x + threshold, y + threshold)
            screenshot = ImageGrab.grab(area)
            img_array = np.array(screenshot)
            
            for row in img_array:
                for pixel in row:
                    r, g, b = pixel[:3]
                    if b > 150 and b > (r + 30) and b > (g + 30):
                        return True
            return False
        except Exception as e:
            logging.error(f"Error in blue detection: {str(e)}")
            return False
    
    def update_click_positions(self, positions_to_click):
        """Update the click positions file."""
        try:
            if positions_to_click:
                with open(self.click_signal_file, "w") as f:
                    for pos in positions_to_click:
                        f.write(f"{pos[0]},{pos[1]}\n")
                os.chmod(self.click_signal_file, 0o666)
                logging.debug(f"Updated click positions file")
        except Exception as e:
            logging.error(f"Error updating click positions: {str(e)}")
    
    def run(self):
        """Main loop to detect blue and signal clicks."""
        try:
            logging.info("Starting blue detection...")
            
            while not should_stop():  # Check kill conditions
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self.last_check_time = current_time
                    
                    if current_time - self.last_click_time >= self.click_cooldown:
                        positions_to_click = []
                        for x, y in self.positions:
                            if self.is_blue_present(x, y):
                                positions_to_click.append((x, y))
                        
                        if positions_to_click:
                            logging.info(f"Blue detected at {len(positions_to_click)} positions")
                            self.update_click_positions(positions_to_click)
                            self.last_click_time = current_time
                
                time.sleep(0.1)
            
            logging.info("Blue detector stopped by kill switch")
                
        except KeyboardInterrupt:
            logging.info("Blue detector stopped by user")
        except Exception as e:
            logging.error(f"Fatal error in blue detector: {str(e)}")

if __name__ == "__main__":
    # All positions to monitor
    POSITIONS = [
        (1693, 1073),  # Submit button
        (1673, 976),   # Position 1
        (1668, 727),   # Position 2
        (1678, 930),   # Position 3
        (1666, 910)    # Position 4
    ]
    
    detector = BlueDetector(POSITIONS)
    detector.run() 