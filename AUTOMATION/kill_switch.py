#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import sys
import subprocess
import signal
import psutil
import time
import pyautogui

# Automation-related process names to kill
AUTOMATION_PROCESSES = [
    'python',  # Generic Python processes
    'motion_detector.py',
    'blue_detector.py',
    'clicker.py',
    'instruction_typer.py',
    'run_automation.py',
    'tmux',  # Kill tmux sessions
]

def kill_processes():
    """Terminate all processes related to automation."""
    killed_pids = []
    
    # List all active tmux sessions before killing
    try:
        active_sessions = subprocess.run(['tmux', 'list-sessions'], 
                                         capture_output=True, 
                                         text=True, 
                                         stderr=subprocess.PIPE)
        print("Active tmux sessions before kill:")
        print(active_sessions.stdout or "No active sessions")
    except Exception as e:
        print(f"Error listing tmux sessions: {e}")
    
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            # Check if any of the process names match our target processes
            if any(proc_name in ' '.join(proc.info['cmdline'] or []) for proc_name in AUTOMATION_PROCESSES):
                pid = proc.pid
                process_name = proc.info['name']
                
                try:
                    # First try graceful termination
                    parent = psutil.Process(pid)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    parent.terminate()
                    killed_pids.append(pid)
                except psutil.NoSuchProcess:
                    pass
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Kill tmux sessions with more detailed error handling
    try:
        kill_result = subprocess.run(['tmux', 'kill-session', '-t', 'automation'], 
                                     capture_output=True, 
                                     text=True, 
                                     stderr=subprocess.PIPE)
        
        if kill_result.returncode == 0:
            print("Successfully killed 'automation' tmux session")
        else:
            print("Failed to kill 'automation' tmux session")
            print("Error output:", kill_result.stderr)
    except Exception as e:
        print(f"Exception when killing tmux session: {e}")
    
    return killed_pids

def should_stop():
    """Check if any kill condition is met:
    1. Kill switch file exists
    2. Mouse in top-left corner for 2 seconds
    """
    kill_switch_file = "/Users/omarmaarouf/automation_files/KILL_SWITCH"
    
    # Check for kill switch file
    if os.path.exists(kill_switch_file):
        return True
    
    # Check mouse position
    try:
        x, y = pyautogui.position()
        if x < 5 and y < 5:  # Mouse in top-left corner
            time.sleep(2)  # Wait 2 seconds
            new_x, new_y = pyautogui.position()
            if new_x < 5 and new_y < 5:  # Still in corner
                return True
    except:
        pass
    
    return False

def main():
    """Main kill switch function."""
    print("Kill switch activated!")
    
    # Kill all related processes
    killed_pids = kill_processes()
    
    if killed_pids:
        print(f"Killed {len(killed_pids)} processes:")
        for pid in killed_pids:
            print(f"- PID {pid}")
    else:
        print("No processes found to kill.")

if __name__ == "__main__":
    main() 