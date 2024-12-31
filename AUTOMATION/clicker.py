#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import time
import subprocess
import logging
from kill_switch import should_stop

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
    
    def hidden_click(self, x, y):
        """Use AppleScript to perform a hidden click"""
        try:
            script = f'''
            tell application "System Events"
                click at {{x:{x}, y:{y}}}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            logging.info(f"Hidden click at {x}, {y}")
        except Exception as e:
            logging.error(f"Error in hidden click: {str(e)}")
    
    def process_click_positions(self):
        """Read and process click positions from the signal file."""
        try:
            if os.path.exists(self.click_signal_file):
                with open(self.click_signal_file, "r") as f:
                    positions = []
                    for line in f:
                        x, y = map(int, line.strip().split(","))
                        positions.append((x, y))
                
                if positions:
                    logging.info(f"Clicking {len(positions)} positions")
                    for x, y in positions:
                        self.hidden_click(x, y)
                        time.sleep(0.2)  # Small delay between clicks
                
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