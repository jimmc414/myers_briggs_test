from pathlib import Path
import platform
import os

# Platform-specific settings
if platform.system() == 'Windows':
    SESSION_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'mbti_test'
else:
    SESSION_DIR = Path.home() / '.mbti_test'

# User-configurable settings
SETTINGS = {
    'animations_enabled': True,
    'animation_speed': 0.03,  # Seconds
    'auto_save': True,
    'export_directory': Path.home() / 'Documents' / 'MBTI_Results',
    'theme': 'dark',  # 'dark' or 'light'
    'unicode_support': True,  # False for ASCII-only terminals
    'min_terminal_width': 80,
    'session_timeout_minutes': 30,
    'session_directory': SESSION_DIR
}

# Test configurations
TEST_CONFIGS = {
    'short': {
        'questions_per_dimension': 4,
        'total_questions': 16,
        'priorities': [1],  # Only high-priority questions
        'estimated_time': 5,
        'name': 'Quick Assessment'
    },
    'medium': {
        'questions_per_dimension': 11,
        'total_questions': 44,
        'priorities': [1, 2],  # High and medium priority
        'estimated_time': 12,
        'name': 'Balanced Test'
    },
    'long': {
        'questions_per_dimension': 22,
        'total_questions': 88,
        'priorities': [1, 2, 3],  # All questions
        'estimated_time': 25,
        'name': 'Comprehensive Analysis'
    }
}

# Dimension mappings
DIMENSIONS = {
    'E_I': {
        'name': 'Extraversion-Introversion',
        'left': {'code': 'I', 'label': 'Introversion'},
        'right': {'code': 'E', 'label': 'Extraversion'}
    },
    'S_N': {
        'name': 'Sensing-Intuition',
        'left': {'code': 'S', 'label': 'Sensing'},
        'right': {'code': 'N', 'label': 'Intuition'}
    },
    'T_F': {
        'name': 'Thinking-Feeling',
        'left': {'code': 'F', 'label': 'Feeling'},
        'right': {'code': 'T', 'label': 'Thinking'}
    },
    'J_P': {
        'name': 'Judging-Perceiving',
        'left': {'code': 'P', 'label': 'Perceiving'},
        'right': {'code': 'J', 'label': 'Judging'}
    }
}

# Error messages
ERROR_MESSAGES = {
    'file_not_found': "❌ Required data files not found",
    'invalid_response': "⚠️  Please select a valid option (1-5)",
    'session_corrupted': "❌ Session data corrupted",
    'export_failed': "❌ Failed to export results",
    'terminal_too_small': "⚠️  Terminal width must be at least 80 columns"
}

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    '1-5': 'Quick answer selection',
    '↑↓': 'Navigate options',
    'Enter': 'Confirm selection',
    'q': 'Quit (with confirmation)',
    'h': 'Show help',
    's': 'Save progress'
}