# MBTI Test Application - API/Interface Documentation

## Command Line Interface

### Main Entry Point
**Location:** `main.py`

```bash
python main.py [OPTIONS]
```

**Options:**
- `--version`: Display application version
- `--disclaimer`: Show MBTI disclaimer
- No args: Start interactive test

**Exit Codes:**
- `0`: Successful completion
- `1`: Error or user interruption

---

## Core Class Interfaces

### MBTIApp Class
**Location:** `main.py`
**Purpose:** Main application orchestrator

#### run() -> None
**Purpose:** Main application entry point
**Side Effects:** 
- Creates session files in `~/.mbti_test/`
- May create export files in `~/Documents/MBTI_Results/`
**Terminal Requirements:** Minimum 80 columns width

---

### TestEngine Class
**Location:** `core/test_engine.py`
**Purpose:** Manages test flow and question presentation

#### initialize_test(test_length: str) -> str
**Purpose:** Start a new test session
**Parameters:**
- `test_length`: One of `"short"`, `"medium"`, `"long"`

**Returns:** Session ID (format: `YYYYMMDD_HHMMSS`)
**Side Effects:** Creates session file

#### submit_response(response_value: int) -> bool
**Purpose:** Submit answer for current question
**Parameters:**
- `response_value`: Integer 1-5 (Likert scale)

**Returns:** 
- `True`: Response accepted and saved
- `False`: Invalid response

**Validation Rules:**
- Value must be integer 1-5
- Cannot submit when test is complete

#### calculate_results() -> Dict
**Purpose:** Calculate final MBTI type and analysis
**Preconditions:** All questions must be answered

**Returns:**
```python
{
    'mbti_type': str,  # 4-letter type (e.g., "INTJ")
    'confidence': float,  # 0-100 percentage
    'confidence_level': str,  # "Strong"|"Moderate"|"Low"
    'dimension_scores': {
        'E_I': DimensionScore,
        'S_N': DimensionScore,
        'T_F': DimensionScore,
        'J_P': DimensionScore
    },
    'personality_analysis': PersonalityAnalysis,
    'test_metadata': {
        'test_length': str,
        'total_questions': int,
        'completion_time': str
    }
}
```

#### resume_test(session_id: str) -> bool
**Purpose:** Resume a previously saved session
**Parameters:**
- `session_id`: Previous session identifier

**Returns:** 
- `True`: Session successfully resumed
- `False`: Session not found or corrupted

---

### MBTIScorer Class
**Location:** `core/scoring.py`
**Purpose:** Calculate MBTI type from responses

#### add_response(question_id: str, question_data: Dict, response_value: int) -> None
**Purpose:** Add a response to scoring system
**Parameters:**
- `question_id`: Unique question identifier
- `question_data`: Dictionary with dimension and reverse_coded flag
- `response_value`: Integer 1-5

#### calculate_dimension_score(dimension: str) -> Dict
**Purpose:** Calculate score for one dimension
**Parameters:**
- `dimension`: One of `"E_I"`, `"S_N"`, `"T_F"`, `"J_P"`

**Returns:**
```python
{
    'preference': str,  # Letter code (E|I|S|N|T|F|J|P)
    'preferred_label': str,  # Full name
    'strength': float,  # 0-100 percentage
    'right_score': float,  # Score for E/N/T/J
    'left_score': float,  # Score for I/S/F/P
    'is_borderline': bool,  # True if 48-52%
    'response_count': int
}
```

#### determine_mbti_type() -> Dict
**Purpose:** Determine final MBTI type
**Returns:**
```python
{
    'type': str,  # 4-letter code
    'confidence': float,  # Average strength
    'confidence_level': str,
    'borderline_dimensions': List[Dict],
    'secondary_type': Optional[str],
    'dimension_details': List[Dict]
}
```

---

### SessionManager Class
**Location:** `core/session.py`
**Purpose:** Handle session persistence

#### create_session(test_length: str, total_questions: int) -> str
**Purpose:** Create new test session
**Returns:** Session ID
**Side Effects:** Creates JSON file in session directory

#### add_response(question_id: str, question_data: Dict, response_value: int) -> None
**Purpose:** Save response and auto-persist
**Side Effects:** Updates session file on disk

#### find_incomplete_sessions() -> List[Dict]
**Purpose:** Find resumable sessions
**Returns:** List of session metadata
**Constraints:** 
- Only returns sessions < 30 minutes old
- Sorted by most recent first

#### mark_complete(mbti_result: Dict) -> None
**Purpose:** Mark session as finished
**Side Effects:** Updates session file with results

---

### ResponseValidator Class
**Location:** `core/validator.py`
**Purpose:** Validate user input and response patterns

#### validate_response(response_value: int) -> bool
**Purpose:** Check if response value is valid
**Raises:** `ValueError` if invalid
**Valid Range:** 1-5 integer only

#### check_consistency(responses: List[Dict]) -> Tuple[bool, str]
**Purpose:** Detect invalid response patterns
**Returns:** `(is_valid, message)`
**Detects:**
- Straight-lining (all same answer)
- Alternating patterns
- >90% extreme responses

#### sanitize_response(response: Any) -> int
**Purpose:** Convert various inputs to valid integer
**Handles:**
- String numbers ("3")
- Float values (3.5 → 4)
- Out of range (clamped to 1-5)
**Raises:** `ValueError` if cannot parse

---

## Data File Interfaces

### Questions Data Structure
**File:** `data/questions.json`
**Format:**
```json
{
  "questions": [
    {
      "id": "E_I_001",
      "dimension": "E_I|S_N|T_F|J_P",
      "text": "Question text",
      "type": "question_type",
      "priority": 1|2|3,
      "reverse_coded": true|false,
      "options": [
        {
          "text": "Option text",
          "value": 1-5
        }
      ]
    }
  ]
}
```

### Personality Types Structure
**File:** `data/personality_types.json`
**Format:**
```json
{
  "XXXX": {
    "title": "Type title",
    "overview": "Description",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "career_matches": ["..."],
    "cognitive_stack": {
      "dominant": "Function description",
      "auxiliary": "...",
      "tertiary": "...",
      "inferior": "..."
    },
    "famous_examples": ["..."],
    "relationship_style": "Description"
  }
}
```

---

## UI Component Interfaces

### UIComponents Class
**Location:** `ui/components.py`
**Purpose:** Reusable UI elements

#### display_question(question_data: Dict, current: int, total: int) -> Optional[int]
**Purpose:** Display question and get response
**Returns:** 
- Integer 1-5: User's response
- `None`: User quit (Ctrl+C)
**Terminal Effects:** Clears screen, displays rich UI

#### select_test_length() -> str
**Purpose:** Interactive test length selection
**Returns:** One of `"short"`, `"medium"`, `"long"`
**Terminal Effects:** Displays selection menu with arrow navigation

---

## Export Interfaces

### Exporter Class
**Location:** `utils/exporter.py`
**Purpose:** Export results to files

#### export_results(results: Dict, format: str) -> Optional[str]
**Purpose:** Export test results
**Parameters:**
- `results`: Complete results dictionary
- `format`: `"txt"` or `"json"`

**Returns:** File path if successful, None if failed
**Side Effects:** Creates file in export directory
**File Naming:** `mbti_results_{TYPE}_{TIMESTAMP}.{ext}`

---

## File System Interfaces

### Session Storage
**Location:** 
- Unix/Mac: `~/.mbti_test/`
- Windows: `%APPDATA%/mbti_test/`

**File Format:** `session_{YYYYMMDD_HHMMSS}.json`
**Cleanup:** Files older than 7 days auto-deleted

### Export Storage
**Location:** `~/Documents/MBTI_Results/`
**Formats:** 
- `.txt`: Human-readable report
- `.json`: Machine-readable data

---

## Error Handling

### Common Errors

#### Invalid Response
**Trigger:** Response value outside 1-5 range
**Handling:** Display error message, prompt again

#### Session Not Found
**Trigger:** Attempting to resume non-existent session
**Handling:** Return to main menu

#### Terminal Too Small
**Trigger:** Terminal width < 80 columns
**Handling:** Display error and exit

#### Data Files Missing
**Trigger:** Required JSON files not found
**Handling:** Display error and exit

---

## State Mutations

### Session Lifecycle
1. **Created**: On test start
2. **Active**: During question answering (auto-saved)
3. **Complete**: When all questions answered
4. **Archived**: After export/manual save

### Response Updates
- Can update existing responses when going back
- Auto-saves after each response
- Maintains history with timestamps

### File System Changes
- Session files: Created/updated during test
- Export files: Created on user request
- No files deleted except old sessions (>7 days)

---

## Integration Notes

### Terminal Requirements
- **Minimum width**: 80 columns
- **Color support**: ANSI colors (auto-detected)
- **Unicode support**: UTF-8 for charts and symbols
- **Interactive input**: Arrow keys and number keys

### Dependencies
All functionality requires these pip packages:
- `rich>=13.7.0`
- `questionary>=2.0.1`
- `plotext>=5.2.8`
- `pyfiglet>=1.0.2`

### Performance Characteristics
- **Question loading**: < 100ms
- **Result calculation**: < 1 second
- **Session save**: < 50ms
- **Export generation**: < 2 seconds

### Concurrency
- **Not thread-safe**: Single user, single session
- **File locking**: None (assumes single process)
- **Auto-save**: After each response