import os
import sys
from datetime import datetime
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_terminal_size() -> tuple:
    """
    Check terminal size.
    
    Returns:
        Tuple of (columns, rows)
    """
    try:
        columns, rows = os.get_terminal_size()
        return columns, rows
    except:
        return 80, 24  # Default size

def ensure_terminal_size(min_width: int = 80) -> bool:
    """
    Ensure terminal is wide enough.
    
    Args:
        min_width: Minimum required width
        
    Returns:
        True if terminal is wide enough
    """
    columns, _ = check_terminal_size()
    return columns >= min_width

def format_time(seconds: int) -> str:
    """
    Format seconds into human readable time.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_data_path() -> Path:
    """
    Get the path to the data directory.
    
    Returns:
        Path to data directory
    """
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / 'data',
        Path.cwd() / 'data',
        Path.cwd() / 'mbti_test' / 'data'
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Default to first option
    return possible_paths[0]

def validate_data_files() -> bool:
    """
    Check if all required data files exist.
    
    Returns:
        True if all files exist
    """
    data_path = get_data_path()
    required_files = [
        'questions.json',
        'personality_types.json',
        'cognitive_functions.json'
    ]
    
    for file in required_files:
        if not (data_path / file).exists():
            return False
    
    return True

def get_version() -> str:
    """Get application version."""
    return "1.0.0"

def display_disclaimer():
    """Display disclaimer about MBTI."""
    disclaimer = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                         DISCLAIMER                            ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ This MBTI assessment is for entertainment and self-reflection ║
    ║ purposes only. The Myers-Briggs Type Indicator is not        ║
    ║ scientifically validated for psychological diagnosis or       ║
    ║ personnel selection. Results should not be used as the sole  ║
    ║ basis for important life decisions. For professional         ║
    ║ psychological assessment, please consult a qualified mental   ║
    ║ health professional.                                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(disclaimer)