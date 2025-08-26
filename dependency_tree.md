# MBTI Test Application - Dependency Tree

## Core Dependencies

### Terminal UI Framework
- **rich** (13.7.0)
  - Purpose: Terminal formatting, colors, panels, and progress bars
  - Used in: `ui/themes.py`, `ui/components.py`, `display/charts.py`, `display/reports.py`
  - Critical: **Yes** - entire UI built on this
  - Features enabled: Color themes, panels, tables, progress bars, status indicators

- **questionary** (2.0.1)
  - Purpose: Interactive terminal prompts with keyboard navigation
  - Used in: `ui/components.py`, `main.py`
  - Critical: **Yes** - all user input collection
  - Features enabled: Arrow key navigation, styled selections, confirmations
  - Depends on: prompt_toolkit (3.0.36)

### Data Visualization
- **plotext** (5.2.8)
  - Purpose: Terminal-native charts and graphs
  - Used in: `display/charts.py`
  - Critical: **No** - fallback to ASCII charts available
  - Features enabled: Bar charts for dimension scores

- **pyfiglet** (1.0.2)
  - Purpose: ASCII art text generation for titles
  - Used in: `ui/components.py`, `display/reports.py`
  - Critical: **No** - decorative feature only
  - Features enabled: Welcome screen, result reveal

### Data Processing
- **pandas** (2.1.0)
  - Purpose: Data manipulation for potential analytics
  - Used in: Currently unused (future feature)
  - Critical: **No** - included for future enhancements
  - Note: Could be removed to reduce dependencies

### Utilities
- **python-dotenv** (1.0.0)
  - Purpose: Environment variable management
  - Used in: Currently unused (prepared for config)
  - Critical: **No** - app uses direct config
  - Note: Could be removed if not implementing .env support

- **colorama** (0.4.6)
  - Purpose: Windows terminal ANSI color support
  - Used in: Automatic initialization for Windows
  - Critical: **Windows only** - enables colors in older terminals
  - Auto-initialized when on Windows platform

- **pyperclip** (1.8.2)
  - Purpose: Cross-platform clipboard operations
  - Used in: `utils/exporter.py`
  - Critical: **No** - optional export feature
  - Features enabled: Copy results to clipboard

## Dependency Relationships

```
MBTI Test App
├── rich (13.7.0) [CRITICAL]
│   ├── markdown-it-py (>=2.2.0)
│   └── pygments (2.13.0+)
├── questionary (2.0.1) [CRITICAL]
│   └── prompt_toolkit (3.0.36)
│       └── wcwidth
├── plotext (5.2.8) [OPTIONAL - Visualization]
├── pyfiglet (1.0.2) [OPTIONAL - Decoration]
├── pandas (2.1.0) [OPTIONAL - Future use]
│   ├── numpy (>=1.23.2)
│   ├── python-dateutil (>=2.8.2)
│   └── pytz (>=2020.1)
├── python-dotenv (1.0.0) [OPTIONAL - Config]
├── colorama (0.4.6) [CRITICAL on Windows]
└── pyperclip (1.8.2) [OPTIONAL - Export]
```

## Version Constraints

### Version Notes
- **rich**: Pinned to 13.7.0 for stable API (newer versions may break theme compatibility)
- **questionary**: 2.0.1 required for specific style API
- **prompt_toolkit**: Must be <=3.0.36 for questionary compatibility
- **pandas**: 2.1.0 specified but not strictly required (could use 2.0+)
- **plotext**: 5.2.8 for terminal compatibility (newer versions untested)

### Known Conflicts
- **prompt_toolkit**: Version >3.0.36 breaks questionary 2.0.1
- **pandas**: Version 2.1.0 may conflict with statsmodels if installed
- **rich**: Versions >13.9 change some API calls we depend on

## Installation Profiles

### Minimal Installation (Core functionality only)
```bash
pip install rich==13.7.0 questionary==2.0.1 colorama==0.4.6
```
Size: ~5MB
Features: Full test functionality, no charts or clipboard

### Standard Installation (Recommended)
```bash
pip install -r requirements.txt
```
Size: ~50MB
Features: All features including charts, ASCII art, clipboard

### Development Installation
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```
Size: ~60MB
Features: All features plus testing and linting tools

## Optional Features Matrix

| Dependency | Feature | Impact if Missing |
|-----------|---------|-------------------|
| plotext | Bar charts | Falls back to ASCII bars |
| pyfiglet | ASCII art titles | Plain text titles |
| pyperclip | Clipboard export | Option hidden from menu |
| pandas | Future analytics | No impact currently |
| python-dotenv | .env config | Uses hardcoded config |

## Security Considerations

### Regular Updates Needed
- **None critical** - No dependencies handle authentication or sensitive data

### Low Risk Dependencies  
- All dependencies are well-maintained, popular packages
- No known security vulnerabilities in pinned versions
- No network communication in any dependency

## Platform-Specific Notes

### Windows
- **colorama**: Required for color support in Command Prompt
- **pyperclip**: Works with Windows clipboard
- All paths automatically handled with `pathlib`

### macOS/Linux
- **colorama**: Not needed but harmless if installed
- **pyperclip**: Requires `pbcopy`/`xclip` for clipboard
- Terminal must support ANSI colors

### Docker/Container
- Minimal installation recommended
- No clipboard support needed
- Can disable animations for better performance

## Upgrade Strategy

### Safe to Upgrade
- colorama (any version)
- pyperclip (any version)
- python-dotenv (any version)

### Test Before Upgrading
- plotext (may change chart API)
- pyfiglet (may change font names)

### Locked Versions (Do not upgrade without testing)
- rich (API changes between major versions)
- questionary (tightly coupled to UI code)
- prompt_toolkit (must match questionary requirement)

## Dependency Purpose Summary

| Category | Critical | Optional |
|----------|----------|----------|
| **UI** | rich, questionary | pyfiglet |
| **Visualization** | - | plotext |
| **Export** | - | pyperclip |
| **Windows Support** | colorama | - |
| **Future** | - | pandas, python-dotenv |

Total critical dependencies: **3** (4 on Windows)  
Total optional dependencies: **5**  
Total install size: ~50MB with all dependencies