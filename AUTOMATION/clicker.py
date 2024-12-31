#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import time
import subprocess
import logging
from datetime import datetime
from kill_switch import should_stop
from AppKit import NSScreen
import pyautogui

# Disable PyAutoGUI's failsafe and pause features
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"clicker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class Clicker:
    def __init__(self):
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        self.click_signal_file = os.path.join(self.working_dir, "click_positions")
        self.check_interval = 0.1
        self.last_check_time = time.time()
        
        logging.info(f"Clicker started")
        logging.info(f"Working directory: {self.working_dir}")
        logging.info(f"Click signal file: {self.click_signal_file}")
    
    def get_screen_dimensions(self):
        """Get the main screen dimensions using PyObjC"""
        try:
            main_screen = NSScreen.mainScreen()
            frame = main_screen.frame()
            return int(frame.size.width), int(frame.size.height)
        except Exception as e:
            logging.warning(f"Failed to get screen dimensions using PyObjC: {str(e)}")
            return pyautogui.size()  # Use PyAutoGUI's method as a fallback
    
    def click_and_press(self):
        """Click in the middle of the right third of the screen and press Command+Enter without any mouse movement"""
        try:
            # Get screen dimensions
            width, height = self.get_screen_dimensions()
            
            # Calculate position in right third
            right_third_x = int(width * 0.83)  # Positioned at 83% of screen width
            middle_y = int(height * 0.5)       # Middle of screen height
            
            logging.debug(f"Screen dimensions: {width}x{height}")
            logging.debug(f"Calculated click position: ({right_third_x}, {middle_y})")
            
            # Use AppleScript to focus Cursor app and perform actions
            script = f'''
            tell application "System Events"
                tell application process "Cursor"
                    set frontmost to true
                    delay 0.2
                    click at {{x:{right_third_x}, y:{middle_y}}}
                    delay 0.2
                    keystroke return using command down
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            logging.info(f"Clicked at right third ({right_third_x}, {middle_y}) and pressed Command+Enter")
                
        except Exception as e:
            logging.error(f"Error in click action: {str(e)}")
            logging.debug(f"Full error details: {repr(e)}")
    
    def process_click_positions(self):
        """Process click signals - triggers the right-third click and Command+Enter."""
        try:
            if os.path.exists(self.click_signal_file):
                self.click_and_press()
                
                try:
                    os.remove(self.click_signal_file)
                    logging.debug("Removed click signal file")
                except Exception as e:
                    logging.error(f"Error removing click signal file: {str(e)}")
                
        except Exception as e:
            logging.error(f"Error processing click positions: {str(e)}")
    
    def run(self):
        """Main loop to check for and process click signals."""
        try:
            logging.info("Starting clicker...")
            
            while not should_stop():  # Check kill conditions
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self.last_check_time = current_time
                    self.process_click_positions()
                
                time.sleep(0.1)
            
            logging.info("Clicker stopped by kill switch")
                
        except KeyboardInterrupt:
            logging.info("Clicker stopped by user")
        except Exception as e:
            logging.error(f"Fatal error in clicker: {str(e)}")

if __name__ == "__main__":
    clicker = Clicker()
    clicker.run()
