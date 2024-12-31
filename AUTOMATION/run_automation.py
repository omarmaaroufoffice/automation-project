#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import subprocess
import time
import logging
from datetime import datetime

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"automation_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def create_tmux_session(session_name, script_dir):
    """Create and configure tmux session with four panes."""
    try:
        logging.info(f"Attempting to create tmux session: {session_name}")
        logging.info(f"Script directory: {script_dir}")
        
        # Ensure tmux is installed
        tmux_check = subprocess.run(["which", "tmux"], capture_output=True, text=True)
        if tmux_check.returncode != 0:
            logging.error("tmux is not installed. Please install tmux.")
            return False
        
        # Kill existing session if it exists
        kill_result = subprocess.run(["tmux", "kill-session", "-t", session_name], 
                                     capture_output=True, text=True)
        logging.info(f"Killed existing session result: {kill_result.returncode}")
        
        # Create new session
        create_result = subprocess.run(["tmux", "new-session", "-d", "-s", session_name], 
                                       capture_output=True, text=True)
        if create_result.returncode != 0:
            logging.error(f"Failed to create tmux session: {create_result.stderr}")
            return False
        logging.info("Created new tmux session")
        
        # Split into four panes with error checking
        split_commands = [
            (["tmux", "split-window", "-v", "-t", f"{session_name}:0.0"], "Vertical split"),
            (["tmux", "split-window", "-h", "-t", f"{session_name}:0.0"], "Top horizontal split"),
            (["tmux", "split-window", "-h", "-t", f"{session_name}:0.2"], "Bottom horizontal split")
        ]
        
        for cmd, description in split_commands:
            split_result = subprocess.run(cmd, capture_output=True, text=True)
            if split_result.returncode != 0:
                logging.error(f"Failed to perform {description}: {split_result.stderr}")
                return False
            logging.info(description)
        
        # Set up pyenv initialization
        pyenv_init = (
            "eval \"$(pyenv init -)\" && "
            "eval \"$(pyenv init --path)\" && "
            "pyenv shell 3.10.0 && "
        )
        
        # Start components in each pane
        components = [
            ("motion_detector.py", "0.0", "Motion Detector"),
            ("blue_detector.py", "0.1", "Blue Detector"),
            ("clicker.py", "0.2", "Clicker"),
            ("instruction_typer.py", "0.3", "Instruction Typer")
        ]
        
        for script, pane, name in components:
            cmd = f"cd {script_dir} && {pyenv_init} python {script}"
            start_result = subprocess.run(
                ["tmux", "send-keys", "-t", f"{session_name}:{pane}", cmd, "Enter"], 
                capture_output=True, text=True
            )
            if start_result.returncode != 0:
                logging.error(f"Failed to start {name}: {start_result.stderr}")
                return False
            logging.info(f"Started {name} in pane {pane}")
        
        # Verify panes are created
        list_panes_result = subprocess.run(
            ["tmux", "list-panes", "-t", session_name], 
            capture_output=True, text=True
        )
        logging.info(f"Panes created: {list_panes_result.stdout}")
        
        return True
    except Exception as e:
        logging.error(f"Comprehensive error in create_tmux_session: {str(e)}")
        return False

def main():
    try:
        logging.info("Starting automation system...")
        
        # Get script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logging.info(f"Script directory: {script_dir}")
        
        # Create signal files with proper permissions
        signal_files = ["motion_status", "click_positions", "Instructions_medium"]
        for file in signal_files:
            file_path = os.path.join(script_dir, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    if file == "Instructions_medium":
                        f.write("continue")
                os.chmod(file_path, 0o666)
                logging.info(f"Created signal file: {file}")
        
        # Set session name
        session_name = "automation"
        
        # Create and configure tmux session
        if not create_tmux_session(session_name, script_dir):
            logging.error("Failed to create and configure tmux session")
            return
        
        # Attach to session
        logging.info("Attaching to tmux session...")
        subprocess.run(["tmux", "attach-session", "-t", session_name])
        
    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}")

if __name__ == "__main__":
    main() 