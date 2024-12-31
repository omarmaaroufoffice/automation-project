#!/Users/omarmaarouf/.pyenv/versions/3.10.0/bin/python
import os
import time
import pyautogui
import pyperclip
import numpy as np
import cv2
from PIL import ImageGrab
from datetime import datetime
import logging
from kill_switch import should_stop
import subprocess

# Set up logging
log_dir = os.path.expanduser("~/automation_logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"instruction_typer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class InstructionTyper:
    def __init__(self):
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        self.instructions_file = os.path.join(self.working_dir, "instructions.txt")
        self.paste_position = (1306, 1029)  # Paste position coordinates
        self.current_instruction = 0
        self.check_interval = 0.1
        self.last_check_time = time.time()
        self.no_motion_delay = 6  # Seconds to wait after last motion
        self.last_type_time = 0
        self.type_cooldown = 1  # Seconds between typing attempts
        self.last_motion_time = time.time()
        self.last_frame = None
        self.completion_time = None  # Time when project reached 100%
        
        # Capture the initial directory where the script was first executed
        self.initial_execution_dir = os.environ.get('INITIAL_EXECUTION_DIR', os.getcwd())
        
        # Get screen size for right third detection
        screen_width, screen_height = pyautogui.size()
        self.right_third_x = int(screen_width * 2/3)
        
        logging.info(f"Instruction Typer started")
        logging.info(f"Working directory: {self.working_dir}")
        logging.info(f"Initial execution directory: {self.initial_execution_dir}")
        logging.info(f"Instructions file: {self.instructions_file}")
        logging.info(f"Paste position: {self.paste_position}")
        logging.info(f"Right third starts at x={self.right_third_x}")
    
    def detect_motion(self):
        """Detect any motion in the right third of the screen."""
        try:
            # Capture the right third of the screen
            screen_width, screen_height = pyautogui.size()
            area = (self.right_third_x, 0, screen_width, screen_height)
            current_frame = np.array(ImageGrab.grab(area))
            
            if self.last_frame is None:
                self.last_frame = current_frame
                return False
            
            # Calculate difference between frames
            diff = cv2.absdiff(current_frame, self.last_frame)
            
            # Calculate RGB differences separately
            r_diff = diff[:,:,0]
            g_diff = diff[:,:,1]
            b_diff = diff[:,:,2]
            
            # Count changed pixels (any channel changed by more than 0)
            total_changed_pixels = np.sum((r_diff > 0) | (g_diff > 0) | (b_diff > 0))
            
            # Store current frame for next comparison
            self.last_frame = current_frame.copy()
            
            # Consider ANY pixel change as motion
            if total_changed_pixels > 0:
                self.last_motion_time = time.time()
                if total_changed_pixels > 10:  # Only log significant motion
                    logging.info(f"Motion detected in right third: {total_changed_pixels} pixels changed")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error in motion detection: {str(e)}")
            return False
    
    def check_motion_status(self):
        """Check if there has been no motion for the required time."""
        try:
            # First check if enough time has passed since last typing
            if time.time() - self.last_type_time < self.type_cooldown:
                return False
            
            # Check for current motion
            if self.detect_motion():
                return False
            
            # Check if enough time has passed since last motion
            time_since_motion = time.time() - self.last_motion_time
            if time_since_motion >= self.no_motion_delay:
                logging.info(f"No motion confirmed for {time_since_motion:.1f} seconds")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking motion status: {str(e)}")
            return False
    
    def create_instructions_file(self):
        """Create hardcoded instructions."""
        # Check percentage from ROAD_MAP.md
        try:
            with open('ROAD_MAP.md', 'r') as f:
                first_line = f.readline().strip()
                # Extract percentage
                percentage = int(first_line.replace('% complete', '').strip())
        except (FileNotFoundError, ValueError):
            percentage = 0

        # Get project tree structure
        project_tree = get_project_tree()
        
        # Determine instructions based on percentage
        if percentage < 30:
            # Add continue instruction for low percentage projects
            continue_instruction = (
                "Continue project development. Focus on maintaining momentum. "
                "Review current progress and identify next immediate steps. "
                "Break down complex tasks into smaller, manageable components."
                "Continue project development. Focus on maintaining momentum. "
                "Review current progress and identify next immediate steps. "
                "Break down complex tasks into smaller, manageable components."
                "Continue project development. Focus on maintaining momentum. "
                "Review current progress and identify next immediate steps. "
                "Break down complex tasks into smaller, manageable components."
            )
            
            # Hardcoded comprehensive instructions
            self.instructions = [
                f"Project Tree Structure and Setup Guidelines:\n\n{project_tree}\n\n"
                f"{continue_instruction}",
                "1. Verify Project Structure: Ensure all directories and files are correctly organized.",
                "4. Duplicate Check: Thoroughly review all files for potential duplicates.",
                "6. Strict Adherence: Follow ROAD_MAP.md guidelines precisely.",
                "7. Continuous Improvement: Regularly update project documentation and structure.",
                "9. Code Quality: Maintain high code quality ",         
            ]
        elif percentage >= 80:
            # Deployment-focused instructions for projects nearing completion
            deployment_instruction = (
                "Prepare for Deployment: Comprehensive Pre-Launch Checklist\n"
                "3. Deployment Preparation:\n"
                "   - Configure production environment settings\n"
                "   - Set up continuous integration and deployment (CI/CD) pipeline\n"
                "   - Prepare deployment scripts and automation\n"
                "5. Performance Optimization:\n"
                "   - Profile and optimize critical code paths\n"
                "6. Documentation and Handover:\n"
                "   - Update all project documentation\n"
                "   - Create deployment and maintenance guides\n"
                "   - Prepare knowledge transfer materials\n"
                "   - Run it and fix it\n"
                "   - Make sure it is working multiple times\n"
                "   - Verify all functionalities\n"
                "   - Conduct final system checks"
            )
            
            self.instructions = [
                f"Project Tree Structure and Deployment Guidelines:\n\n{project_tree}\n\n"
                f"{deployment_instruction}",
                "1. Verify Project Structure: Ensure all directories and files are correctly organized.",
                "4. Duplicate Check: Thoroughly review all files for potential duplicates.",
                "6. Strict Adherence: Follow ROAD_MAP.md guidelines precisely.",
                "7. Continuous Improvement: Regularly update project documentation and structure.",
                "9. Code Quality: Maintain high code quality ",         
            ]
        else:
            # Original instructions for projects between 30% and 80% completion
            self.instructions = [
                f"Project Tree Structure and Setup Guidelines:\n\n{project_tree}\n\n"
                "1. Verify Project Structure: Ensure all directories and files are correctly organized.",
                "2. Naming Convention: Use snake_case for files and functions, PascalCase for classes.",
                "3. ROAD_MAP.md Management: Update first line with current project completion percentage.",
                "4. Duplicate Check: Thoroughly review all files for potential duplicates.",
                "5. Path Verification: Always check file paths before creating or modifying files.",
                "6. Strict Adherence: Follow ROAD_MAP.md guidelines precisely.",
                "7. Continuous Improvement: Regularly update project documentation and structure.",
                "8. Error Handling: Implement robust error handling in all scripts.",
                "9. Code Quality: Maintain high code quality with clear comments and documentation.",
                "10. Version Control: Commit changes frequently with descriptive commit messages."
            ]
        
        logging.info("Hardcoded instructions generated with project tree")
    
    def type_instruction(self):
        """Type the next instruction when conditions are met."""
        try:
            # Use hardcoded instructions list instead of file
            if not hasattr(self, 'instructions') or not self.instructions:
                self.create_instructions_file()
            
            if not hasattr(self, 'current_instruction'):
                self.current_instruction = 0
            
            if self.current_instruction >= len(self.instructions):
                self.current_instruction = 0
            
            instruction = self.instructions[self.current_instruction]
            
            if instruction:
                # Append additional guidance
                full_instruction = (
                    f"{instruction} "
                    '"Please follow the ROAD_MAP.md closely and update it as you go, DO NOT DELETE EXCEPT NECESSARY". '
                    "Check pathway before creating any file. "
                    "At the first line of the ROAD_MAP.md file, enter what percentage of the project is done.Path Verification: Always check file paths before creating or modifying files"
                )
                
                logging.info(f"Typing instruction {self.current_instruction + 1}: {instruction[:30]}...")
                
                # Click to focus the correct window
                pyautogui.click(self.paste_position[0], self.paste_position[1])
                time.sleep(0.5)  # Wait for focus
                
                # Type the instruction
                pyperclip.copy(full_instruction)
                time.sleep(0.2)
                pyautogui.hotkey('command', 'v')
                time.sleep(0.2)
                pyautogui.press('enter')
                
                # Click in the middle of the screen
                screen_width, screen_height = pyautogui.size()
                middle_x = screen_width // 2
                middle_y = screen_height // 2
                pyautogui.click(middle_x, middle_y)
                
                self.current_instruction += 1
                self.last_type_time = time.time()
            
        except Exception as e:
            logging.error(f"Error typing instruction: {str(e)}")
    
    def check_project_completion(self):
        """Check if project is 100% complete and track time."""
        try:
            roadmap_path = os.path.join(self.initial_execution_dir, 'ROAD_MAP.md')
            if os.path.exists(roadmap_path):
                with open(roadmap_path, 'r') as f:
                    first_line = f.readline().strip()
                    try:
                        percentage = int(first_line.replace('% complete', '').strip())
                        if percentage >= 100:
                            if self.completion_time is None:
                                self.completion_time = time.time()
                                logging.info("Project reached 100% completion. Timer started.")
                            elif time.time() - self.completion_time >= 3600:  # 1 hour = 3600 seconds
                                logging.info("1 hour passed since 100% completion. Stopping automation.")
                                return True
                    except ValueError:
                        pass
            return False
        except Exception as e:
            logging.error(f"Error checking project completion: {str(e)}")
            return False
    
    def run(self):
        """Main loop to check motion status and type instructions."""
        try:
            logging.info("Starting instruction typer...")
            self.create_instructions_file()
            
            while not should_stop():
                # Check if it's time to stop due to project completion
                if self.check_project_completion():
                    break
                    
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self.last_check_time = current_time
                    
                    if self.check_motion_status():
                        self.type_instruction()
                
                time.sleep(0.1)
            
            logging.info("Instruction typer stopped")
                
        except KeyboardInterrupt:
            logging.info("Instruction typer stopped by user")
        except Exception as e:
            logging.error(f"Fatal error in instruction typer: {str(e)}")

def get_project_tree():
    """
    Capture the directory tree structure of the current project.
    
    Returns:
        str: Formatted tree structure of the project directory
    """
    try:
        # Use the initial execution directory captured during script initialization
        current_dir = os.environ.get('INITIAL_EXECUTION_DIR', os.getcwd())
        
        # Ensure we have a valid directory
        if not os.path.isdir(current_dir):
            return f"Error: {current_dir} is not a valid directory"
        
        # Run tree command with specific formatting
        try:
            tree_result = subprocess.run(
                ['tree', '-I', 'node_modules|.git|__pycache__|*.pyc'], 
                cwd=current_dir, 
                capture_output=True, 
                text=True
            )
            
            # If tree command is successful, return its output
            if tree_result.returncode == 0:
                return tree_result.stdout
        except FileNotFoundError:
            pass
        
        # Fallback to find command if tree is not available
        find_result = subprocess.run(
            ['find', '.', 
             '-not', '-path', '*/node_modules/*',
             '-not', '-path', '*/.git*', 
             '-not', '-path', '*/__pycache__*'], 
            cwd=current_dir, 
            capture_output=True, 
            text=True
        )
        
        return find_result.stdout
    
    except Exception as e:
        return f"Error generating project tree: {str(e)}"

def write_project_instructions():
    """Write project instructions with project tree structure."""
    try:
        # Capture project tree
        project_tree = get_project_tree()
        
        # Write instructions to file
        with open('Instructions_medium', 'w') as f:
            f.write("Project Instruction Generation:\n\n")
            f.write("This is your project tree structure make sure it is correct and match it with the ROAD_MAP.md file.\n")
            f.write("=" * 50 + "\n")
            f.write(project_tree)
            f.write("\n")
            f.write("Verify that this tree structure accurately represents your project's organization.\n")
            f.write("Ensure each directory and file serves a clear and documented purpose.\n")
            f.write("Cross-reference with ROAD_MAP.md to confirm alignment.\n")
    
    except Exception as e:
        print(f"Error writing instructions: {str(e)}")

# Call the function to generate instructions
write_project_instructions()

if __name__ == "__main__":
    typer = InstructionTyper()
    typer.run() 