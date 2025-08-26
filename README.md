# MBTI Personality Test - Terminal Application

A beautiful, feature-rich Myers-Briggs Type Indicator (MBTI) personality assessment tool for the terminal.

## Features

- **Three Test Lengths**:
  - Quick (16 questions) - 5 minutes
  - Balanced (44 questions) - 12 minutes - Recommended
  - Comprehensive (88 questions) - 25 minutes - Most accurate

- **Beautiful Terminal UI**:
  - Rich color themes and formatting
  - ASCII art and animations
  - Interactive question prompts
  - Progress tracking with visual indicators

- **Advanced Features**:
  - Session save/resume capability
  - Detailed personality analysis
  - Cognitive function stack display
  - Career recommendations
  - Export results (text/JSON)
  - Result validation

## Installation

### Requirements
- Python 3.8 or higher
- Terminal with at least 80 columns width

### Setup

1. Clone or download the project
2. Navigate to the project directory:
```bash
cd mbti_test
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Test

```bash
python main.py
```

### Command Line Options

```bash
# Show version
python main.py --version

# Show disclaimer
python main.py --disclaimer
```

## Test Structure

The test measures four personality dimensions:

1. **Extraversion (E) vs Introversion (I)**
   - How you direct and receive energy

2. **Sensing (S) vs Intuition (N)**
   - How you take in information

3. **Thinking (T) vs Feeling (F)**
   - How you make decisions

4. **Judging (J) vs Perceiving (P)**
   - How you approach the outside world

## Results

Your results will include:

- Your 4-letter personality type (e.g., INTJ, ENFP)
- Detailed personality overview
- Strengths and growth areas
- Cognitive function stack
- Career recommendations
- Famous people with your type
- Confidence scores for each dimension

## Saving Results

After completing the test, you can:
- Save as a text file
- Save as JSON for data analysis
- Copy to clipboard
- Results are saved to `~/Documents/MBTI_Results/`

## Session Management

- Tests are automatically saved as you progress
- Resume incomplete tests within 30 minutes
- Session files stored in `~/.mbti_test/` (Unix) or `%APPDATA%/mbti_test/` (Windows)

## Keyboard Shortcuts

- `1-5`: Quick answer selection
- `↑↓`: Navigate options
- `Enter`: Confirm selection
- `q`: Save and quit (during test)
- `Ctrl+C`: Exit (progress is saved)

## Data Files

The application uses three main data files:
- `questions.json`: 88 scientifically designed questions
- `personality_types.json`: Detailed descriptions for all 16 types
- `cognitive_functions.json`: Cognitive function mappings

## Disclaimer

This MBTI assessment is for entertainment and self-reflection purposes only. The Myers-Briggs Type Indicator is not scientifically validated for psychological diagnosis or personnel selection. Results should not be used as the sole basis for important life decisions.

For professional psychological assessment, please consult a qualified mental health professional.

## Troubleshooting

### Terminal Too Small
Ensure your terminal is at least 80 columns wide.

### Missing Data Files
Ensure all files in the `data/` directory are present.

### Can't See Colors
- On Windows, colors should work automatically
- On Unix systems, ensure your terminal supports ANSI colors

## Version

Version 1.0.0

## License

This project is for educational purposes.

## Acknowledgments

- Based on Carl Jung's psychological types theory
- Inspired by the work of Katharine Cook Briggs and Isabel Briggs Myers