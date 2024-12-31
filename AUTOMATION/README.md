# Automation System

An automated system for monitoring screen activity and typing instructions based on motion detection.

## Components

1. **Motion Detector** (`motion_detector.py`)
   - Monitors specific screen areas for pixel changes
   - Detects even single pixel changes
   - Updates motion status in real-time

2. **Blue Detector** (`blue_detector.py`)
   - Monitors multiple screen positions for blue elements
   - Triggers clicks when blue elements are detected
   - Includes cooldown mechanism

3. **Clicker** (`clicker.py`)
   - Processes click signals from blue detector
   - Executes clicks at specified coordinates
   - Includes safety delays between clicks

4. **Instruction Typer** (`instruction_typer.py`)
   - Monitors right third of screen for motion
   - Types instructions when no motion detected for 12 seconds
   - Cycles through instructions from file

5. **Kill Switch** (`kill_switch.py`)
   - Provides emergency stop functionality
   - Monitors for kill conditions
   - Ensures safe shutdown of all components

## Setup

1. Install Python 3.10.0 using pyenv:
   ```bash
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```

2. Install required packages:
   ```bash
   python -m pip install pyautogui pillow opencv-python numpy pyperclip
   ```

3. Make scripts executable:
   ```bash
   chmod +x *.py
   ```

## Usage

1. Start the automation:
   ```bash
   ./run_both.py
   ```

2. Emergency Stop Options:
   - Press Ctrl+C in terminal
   - Move cursor to top-left corner (0,0) for 2 seconds
   - Run `./kill_automation.sh kill`

## Configuration

- Edit `instructions.txt` to modify the instruction list
- Adjust coordinates in scripts for different screen setups
- Modify timing parameters in scripts as needed

## Logging

Logs are stored in `~/automation_logs/` with timestamps for each component. 