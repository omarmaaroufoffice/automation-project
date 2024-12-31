#!/usr/bin/env python3
import os
import sys
import psutil
import subprocess
import signal
import logging
from datetime import datetime

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"global_python_kill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def kill_python_processes(force=False, exclude_current=True):
    """
    Kill Python processes with optional force and exclusion of current process.
    
    Args:
        force (bool): Use SIGKILL instead of SIGTERM if True
        exclude_current (bool): Exclude the current process from being killed
    
    Returns:
        list: List of killed process PIDs
    """
    killed_pids = []
    current_pid = os.getpid()
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip if it's not a Python process
                if 'python' not in proc.info['name'].lower():
                    continue
                
                # Skip current process if exclude_current is True
                if exclude_current and proc.info['pid'] == current_pid:
                    continue
                
                # Additional filtering to avoid killing system or critical Python processes
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(critical in cmdline for critical in [
                    'pyenv', 
                    '/usr/libexec', 
                    'VSCode', 
                    'Visual Studio Code', 
                    'iTerm', 
                    'Terminal'
                ]):
                    continue
                
                # Get the process
                process = psutil.Process(proc.info['pid'])
                
                # Log the process details
                logging.info(f"Killing Python process: PID {process.pid}, CMD: {cmdline}")
                
                # Choose termination method
                if force:
                    process.kill()  # SIGKILL
                else:
                    process.terminate()  # SIGTERM
                
                killed_pids.append(process.pid)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Additional tmux session killing
        try:
            subprocess.run(['tmux', 'kill-server'], capture_output=True, text=True)
            logging.info("Killed all tmux sessions")
        except Exception as e:
            logging.warning(f"Error killing tmux sessions: {e}")
        
        return killed_pids
    
    except Exception as e:
        logging.error(f"Error in kill_python_processes: {e}")
        return killed_pids

def main():
    """Main function to handle different kill switch modes."""
    force_kill = False
    
    # Check for force kill argument
    if len(sys.argv) > 1 and sys.argv[1] in ['-f', '--force']:
        force_kill = True
        logging.info("Force kill mode activated")
    
    # Kill Python processes
    killed_pids = kill_python_processes(force=force_kill)
    
    # Report results
    if killed_pids:
        print(f"Killed {len(killed_pids)} Python processes:")
        for pid in killed_pids:
            print(f"- PID {pid}")
    else:
        print("No Python processes found to kill.")
    
    logging.info(f"Killed {len(killed_pids)} Python processes")

if __name__ == "__main__":
    main() 