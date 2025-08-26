from rich.theme import Theme
from rich.console import Console
from questionary import Style

# Define color palette
COLORS = {
    'primary': '#00D9FF',      # Cyan - Headers, important text
    'secondary': '#FF6B6B',    # Coral - Highlights, selections
    'success': '#51CF66',      # Green - Correct, positive
    'warning': '#FFD93D',      # Yellow - Warnings, scores
    'info': '#6C5CE7',         # Purple - Information panels
    'text': '#FAFAFA',         # White - Regular text
    'muted': '#95A5A6',        # Gray - Secondary text
    'error': '#FF4757'         # Red - Errors
}

# Rich theme
custom_theme = Theme({
    "primary": "bold cyan",
    "secondary": "bold #FF6B6B",
    "success": "bold #51CF66",
    "warning": "bold #FFD93D",
    "info": "#6C5CE7",
    "error": "bold #FF4757",
    "muted": "dim white",
    "dimension_e_i": "cyan",
    "dimension_s_n": "magenta",
    "dimension_t_f": "yellow",
    "dimension_j_p": "green"
})

# Create console with theme
console = Console(theme=custom_theme)

# Questionary custom style
question_style = Style([
    ('qmark', 'fg:#00D9FF bold'),
    ('question', 'fg:#FAFAFA bold'),
    ('answer', 'fg:#51CF66 bold'),
    ('pointer', 'fg:#FF6B6B bold'),
    ('highlighted', 'fg:#FF6B6B bold'),
    ('selected', 'fg:#51CF66'),
    ('separator', 'fg:#95A5A6'),
    ('instruction', 'fg:#95A5A6'),
    ('text', 'fg:#FAFAFA'),
    ('disabled', 'fg:#858585 italic')
])

# Dimension colors mapping
DIMENSION_COLORS = {
    'E_I': 'dimension_e_i',
    'S_N': 'dimension_s_n',
    'T_F': 'dimension_t_f',
    'J_P': 'dimension_j_p'
}

# ASCII art styles
ASCII_FONTS = {
    'title': 'slant',
    'result': 'standard',
    'section': 'small'
}