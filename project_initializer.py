#!/usr/bin/env python3
import os
import sys
import pyautogui
import pyperclip
import time
import subprocess

# Ensure the script can find its associated files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

# Hardcoded paths with absolute references
PASTE_POSITION = (1306, 1029)  # Updated with recorded position
AUTOMATION_SCRIPT = os.path.join(SCRIPT_DIR, 'AUTOMATION', 'run_automation.py')

def check_roadmap():
    """Check if ROAD_MAP.md exists in the current directory."""
    return os.path.exists("ROAD_MAP.md")

def create_roadmap():
    """Create ROAD_MAP.md file if it doesn't exist."""
    if not check_roadmap():
        with open("ROAD_MAP.md", "w") as f:
            f.write("0% complete\n\n# Project Roadmap\n")
        print("Created ROAD_MAP.md file.")
        
        # Append the do not delete line
        with open("ROAD_MAP.md", "a") as f:
            f.write("\n\n###### DO NOT CHANGE OR DELETE ANYTHING ABOVE THIS LINE EXCEPT THE FIRST LINE TO UPDATE PERCENTAGE #####")
        
        return True
    return False

def paste_text(text):
    """Paste text at the recorded position using clipboard."""
    try:
        # Copy text to clipboard
        pyperclip.copy(text)
        
        # Move and click
        pyautogui.moveTo(PASTE_POSITION[0], PASTE_POSITION[1])
        pyautogui.click()
        time.sleep(0.5)
        
        # Paste from clipboard
        pyautogui.hotkey('command', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return True
    except Exception as e:
        print(f"Error pasting text: {str(e)}")
        return False

def get_project_info():
    """Get project information from user."""
    print("\n=== New Project Setup ===")
    project_description = input("What project do you want to do? ")
    
    # Standard instruction to be added
    standard_instruction = (
        "Please create a ROAD_MAP.md file and fill it with all the necessary steps "
        "and extreme detail about what the project needs, its file structure, and "
        "its description, make sure to add a step by step enumerated full guide "
        "on how to build it, all in the ROAD_MAP.md file. "
        "The first line of the ROAD_MAP.md file should be the percentage of completion "
        "of the project in this form: xx% complete. "
        "STRICTLY FOLLOW these project structure and naming conventions: "
        "1. Implement a PRECISE and CONSISTENT naming convention for ALL files, variables, and functions. "
        "2. Create a DETAILED and RIGID project tree structure that outlines EXACTLY how the project "
        "will be organized, including all directories, subdirectories, and file types. "
        "3. The naming convention MUST be descriptive, use snake_case for files and functions, "
        "PascalCase for classes, and follow a clear, logical pattern that reflects the file's purpose. "
        "4. The project tree MUST be comprehensive, showing EVERY expected file and directory, "
        "with clear explanations of each component's role and expected contents. "
        "5. Include specific guidelines for file naming, variable naming, and directory organization "
        "that will be STRICTLY adhered to throughout the entire project development."
    )
    
    # Combine user input with standard instruction in a single line
    full_instruction = f"Project Description: {project_description} | Instructions: {standard_instruction}"
    
    # Save to initial_instruction.txt (with proper formatting)
    with open("initial_instruction.txt", "w") as f:
        f.write(full_instruction)
    
    print("\nCreated initial_instruction.txt with project information.")
    
    # Paste the instruction
    if paste_text(full_instruction):
        print("Instruction pasted successfully!")
    else:
        print("\nFailed to paste automatically. The text has been saved to initial_instruction.txt")
        print("You can manually copy and paste it from there.")
    
    return full_instruction

def copy_associated_files():
    """
    No file copying needed. 
    Scripts will run from their original locations.
    """
    return True

def start_automation():
    """Start the automation script and attach to tmux session."""
    try:
        # Ensure the script is executable
        os.chmod(AUTOMATION_SCRIPT, 0o755)
        
        # Open a new Terminal window with the project initializer
        open_terminal_command = (
            'tell application "Terminal" to do script '
            '"cd ' + os.path.dirname(AUTOMATION_SCRIPT) + ' && ' + 
            'python ' + AUTOMATION_SCRIPT + '"'
        )
        
        # Use subprocess to run the AppleScript with error capture
        result = subprocess.run(['osascript', '-e', open_terminal_command], 
                       capture_output=True, 
                       text=True)
        
        # Check for any errors in AppleScript execution
        if result.returncode != 0:
            print("Error opening Terminal window:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        print("Automation script started in a new Terminal window!")
        return True
    except Exception as e:
        print(f"Unexpected error starting automation script: {str(e)}")
        return False

def main():
    # Get current directory
    current_dir = os.getcwd()
    print(f"\nChecking project setup in: {current_dir}")
    
    # Copy associated files
    copy_associated_files()
    
    # Check if ROAD_MAP.md exists
    if not check_roadmap():
        # Get project information and paste instructions
        get_project_info()
        
        # Create ROAD_MAP.md after getting project info
        create_roadmap()
    
    # Prompt user to continue to automation
    continue_prompt = input("\nDo you want to start the automation? (yes/no): ").lower()
    
    if continue_prompt in ['yes', 'y']:
        # Start automation script
        start_automation()
    else:
        print("Automation not started. You can start it later using the 'comp' command.")

if __name__ == "__main__":
    # Enable fail-safe
    pyautogui.FAILSAFE = True
    # Set up pyautogui to be more reliable
    pyautogui.PAUSE = 0.1  # Small delay between commands
    main() 