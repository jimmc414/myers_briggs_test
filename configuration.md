# MBTI Test Application - Configuration Documentation

## Configuration Hierarchy
1. Environment variables (only `APPDATA` on Windows)
2. Hardcoded defaults in `config/settings.py`
3. Static theme configuration in `ui/themes.py`

*Note: This application uses minimal environment configuration by design, favoring sensible defaults for a terminal application.*

## Core Configuration

### File System Paths
| Setting | Env Var | Default | Required | Description |
|---------|---------|---------|----------|-------------|
| Session Directory (Windows) | `APPDATA` | `%USERPROFILE%\AppData\Roaming\mbti_test` | No | Session storage location on Windows |
| Session Directory (Unix) | - | `~/.mbti_test` | No | Session storage location on Mac/Linux |
| Export Directory | - | `~/Documents/MBTI_Results` | No | Where test results are exported |

**Platform Detection:**
```python
if platform.system() == 'Windows':
    SESSION_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'mbti_test'
else:
    SESSION_DIR = Path.home() / '.mbti_test'
```

### Application Settings
| Setting | Config Key | Default | Description | Impact |
|---------|-----------|---------|-------------|--------|
| Animations Enabled | `animations_enabled` | `true` | Enable terminal animations | Disabling speeds up UI on slow terminals |
| Animation Speed | `animation_speed` | `0.03` | Seconds per animation frame | Lower = faster animations |
| Auto Save | `auto_save` | `true` | Save after each response | Ensures no data loss on crash |
| Theme | `theme` | `dark` | Color theme (dark/light) | Currently only dark theme implemented |
| Unicode Support | `unicode_support` | `true` | Use Unicode characters | Set false for ASCII-only terminals |
| Min Terminal Width | `min_terminal_width` | `80` | Minimum columns required | App exits if terminal smaller |
| Session Timeout | `session_timeout_minutes` | `30` | Minutes before session expires | Old sessions cannot be resumed |

### Test Configurations
| Test Type | Questions/Dimension | Total Questions | Priority Levels | Est. Time |
|-----------|---------------------|-----------------|-----------------|-----------|
| Short | 4 | 16 | [1] only | 5 minutes |
| Medium | 11 | 44 | [1, 2] | 12 minutes |
| Long | 22 | 88 | [1, 2, 3] | 25 minutes |

**Configuration Structure:**
```python
TEST_CONFIGS = {
    'short': {
        'questions_per_dimension': 4,
        'total_questions': 16,
        'priorities': [1],  # Only high-priority questions
        'estimated_time': 5,
        'name': 'Quick Assessment'
    }
    # ... medium and long configs
}
```

## UI Theme Configuration

### Color Palette
| Color Role | Hex Value | Usage | Rich Style |
|------------|-----------|-------|------------|
| Primary | `#00D9FF` | Headers, important text | `bold cyan` |
| Secondary | `#FF6B6B` | Highlights, selections | `bold #FF6B6B` |
| Success | `#51CF66` | Correct answers, positive | `bold #51CF66` |
| Warning | `#FFD93D` | Warnings, scores | `bold #FFD93D` |
| Info | `#6C5CE7` | Information panels | `#6C5CE7` |
| Error | `#FF4757` | Error messages | `bold #FF4757` |
| Text | `#FAFAFA` | Regular text | `white` |
| Muted | `#95A5A6` | Secondary text | `dim white` |

### Dimension-Specific Colors
| Dimension | Color Style | Display Color |
|-----------|-------------|---------------|
| E_I | `dimension_e_i` | Cyan |
| S_N | `dimension_s_n` | Magenta |
| T_F | `dimension_t_f` | Yellow |
| J_P | `dimension_j_p` | Green |

### ASCII Art Fonts
| Usage | Font Name | Pyfiglet Style |
|-------|-----------|----------------|
| Title | `slant` | Slanted large text |
| Result | `standard` | Standard ASCII art |
| Section | `small` | Compact headers |

## Error Messages
| Error Type | Message | When Shown |
|------------|---------|------------|
| `file_not_found` | ❌ Required data files not found | Missing JSON data files |
| `invalid_response` | ⚠️ Please select a valid option (1-5) | Input outside 1-5 range |
| `session_corrupted` | ❌ Session data corrupted | Cannot parse session JSON |
| `export_failed` | ❌ Failed to export results | File write permission denied |
| `terminal_too_small` | ⚠️ Terminal width must be at least 80 columns | Terminal < 80 columns |

## Keyboard Shortcuts
| Key | Action | Context |
|-----|--------|---------|
| `1-5` | Quick answer selection | During questions |
| `↑↓` | Navigate options | Menu selection |
| `Enter` | Confirm selection | All prompts |
| `q` | Quit with confirmation | Any time |
| `h` | Show help | Main menu |
| `s` | Save progress | During test |

## Data File Requirements

### Required JSON Files
All must be present in `data/` directory for app to start:

| File | Purpose | Size | Format |
|------|---------|------|--------|
| `questions.json` | 88 test questions | ~50KB | JSON array |
| `personality_types.json` | 16 type descriptions | ~30KB | JSON object |
| `cognitive_functions.json` | 8 function descriptions | ~10KB | JSON object |

## Session Storage

### Session File Format
```json
{
    "id": "20240101_143022",
    "test_length": "medium",
    "total_questions": 44,
    "started_at": "2024-01-01T14:30:22",
    "last_updated": "2024-01-01T14:35:10",
    "responses": [...],
    "current_question": 15,
    "completed": false,
    "mbti_result": null
}
```

### Session Lifecycle
- **Creation**: New file per session with timestamp ID
- **Updates**: Auto-saved after each response
- **Expiration**: Cannot resume after 30 minutes
- **Cleanup**: Files > 7 days automatically deleted

## Performance Tuning

### Resource Limits
| Resource | Limit | Configurable | Impact |
|----------|-------|--------------|--------|
| Max Session Age | 30 min | Yes (`session_timeout_minutes`) | Older sessions cannot resume |
| Session Cleanup | 7 days | No (hardcoded) | Old files auto-deleted |
| Animation FPS | ~33 FPS | Yes (`animation_speed`) | Lower FPS on slow terminals |
| Min Terminal Width | 80 cols | Yes (`min_terminal_width`) | UI layout requirements |

### Memory Usage
- Questions loaded once at startup: ~100KB
- Session data in memory: ~5-10KB
- No caching or connection pools

## Startup Validation

### Application Startup Checks
1. **Terminal width**: Must be ≥ 80 columns
2. **Data files**: All 3 JSON files must exist
3. **Session directory**: Created if missing
4. **Export directory**: Created on first export
5. **Python version**: Requires 3.8+

### Validation Errors
```python
# Terminal too small
if terminal_width < SETTINGS['min_terminal_width']:
    print(ERROR_MESSAGES['terminal_too_small'])
    sys.exit(1)

# Missing data files
if not (data_dir / 'questions.json').exists():
    print(ERROR_MESSAGES['file_not_found'])
    sys.exit(1)
```

## Optional Dependencies

### Feature Availability
| Feature | Dependency | Fallback | Configuration |
|---------|------------|----------|---------------|
| Charts | `plotext` | ASCII bars | Automatic detection |
| ASCII Art | `pyfiglet` | Plain text | Automatic detection |
| Clipboard | `pyperclip` | Hide option | Automatic detection |
| Colors (Windows) | `colorama` | No colors | Auto-initialized |

## Configuration Best Practices

### For Different Environments

#### Slow/Remote Terminals
```python
SETTINGS = {
    'animations_enabled': False,  # Disable animations
    'animation_speed': 0.1,       # Slower updates
    'unicode_support': False      # ASCII only
}
```

#### Minimal Installation
```bash
# Install only core dependencies
pip install rich questionary colorama
# Charts and clipboard features will be disabled
```

#### Accessibility Mode
```python
SETTINGS = {
    'animations_enabled': False,  # No motion
    'theme': 'high_contrast',     # If implemented
    'min_terminal_width': 120     # Larger text
}
```

## Future Configuration Options
Currently unused but infrastructure exists:

- **python-dotenv**: Installed but not used, ready for `.env` file support
- **Theme selection**: Only 'dark' theme currently implemented
- **Language support**: Structure allows for i18n configuration
- **Custom question sets**: Could load alternative question files

## Security Notes

- **No sensitive data**: Application stores no passwords or keys
- **Local only**: No network configuration needed
- **User data isolation**: Sessions stored in user home directory
- **No external services**: No API keys or authentication required

## Troubleshooting Configuration

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Colors not working | Windows terminal | Colorama should auto-fix, or use Windows Terminal |
| Can't resume session | >30 minutes old | Start new test |
| Export fails | No write permission | Check `~/Documents` permissions |
| Charts not showing | plotext not installed | `pip install plotext` |
| Session not saving | Disk full | Check available space |