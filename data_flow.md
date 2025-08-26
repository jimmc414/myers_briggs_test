# MBTI Test Application - Data Flow Diagram

```mermaid
graph TD
    subgraph "Input Sources"
        USER_START[/User Starts Test/]
        USER_INPUT[/User Response<br/>1-5 Likert Scale/]
        RESUME_REQUEST[/Resume Session ID/]
        CLI_ARGS[/CLI Arguments/]
    end
    
    subgraph "Data Loading"
        LOAD_QUESTIONS[Load Questions<br/>from JSON]
        LOAD_TYPES[Load Personality<br/>Types JSON]
        LOAD_FUNCTIONS[Load Cognitive<br/>Functions JSON]
        LOAD_SESSION[Load Saved<br/>Session JSON]
    end
    
    subgraph "Processing Pipeline"
        INIT_TEST{Initialize<br/>Test Type}
        SELECT_Q[Select Questions<br/>by Priority]
        VALIDATE_RESP{Validate<br/>Response}
        SANITIZE[Sanitize<br/>Input]
        SCORE_CALC[Calculate<br/>Dimension Score]
        TYPE_DETERMINE[Determine<br/>MBTI Type]
        ANALYZE[Enrich with<br/>Type Analysis]
        CHECK_PATTERN{Check Response<br/>Pattern}
    end
    
    subgraph "Session Management"
        SESSION_CREATE[Create New<br/>Session]
        SESSION_UPDATE[Update Session<br/>with Response]
        SESSION_SAVE[(Session File<br/>JSON)]
        SESSION_COMPLETE[Mark Session<br/>Complete]
    end
    
    subgraph "Data Stores"
        QUESTIONS_DB[(questions.json<br/>88 questions)]
        TYPES_DB[(personality_types.json<br/>16 types)]
        FUNCTIONS_DB[(cognitive_functions.json<br/>8 functions)]
        SESSIONS_DIR[(~/.mbti_test/<br/>Session Files)]
    end
    
    subgraph "Results Processing"
        BUILD_REPORT[Build Results<br/>Report]
        FORMAT_TEXT[Format as<br/>Text Report]
        FORMAT_JSON[Format as<br/>JSON]
        CREATE_CHART[Generate<br/>Visual Charts]
    end
    
    subgraph "Outputs"
        DISPLAY[/Terminal Display<br/>Rich UI/]
        EXPORT_TXT[/Text File<br/>Export/]
        EXPORT_JSON[/JSON File<br/>Export/]
        CLIPBOARD[/Clipboard<br/>Copy/]
    end
    
    %% Initial Flow
    CLI_ARGS -->|--version/--disclaimer| DISPLAY
    USER_START -->|test length selection| INIT_TEST
    
    %% Test Initialization
    INIT_TEST -->|short/medium/long| SELECT_Q
    QUESTIONS_DB -->|all questions| SELECT_Q
    SELECT_Q -->|filtered by priority| SESSION_CREATE
    SESSION_CREATE -->|session ID| SESSION_SAVE
    
    %% Resume Flow
    RESUME_REQUEST -->|session ID| LOAD_SESSION
    SESSIONS_DIR -->|session data| LOAD_SESSION
    LOAD_SESSION -->|restored state| SELECT_Q
    
    %% Question-Answer Loop
    SELECT_Q -->|next question| DISPLAY
    USER_INPUT -->|raw input| VALIDATE_RESP
    VALIDATE_RESP -->|invalid| DISPLAY
    VALIDATE_RESP -->|valid 1-5| SANITIZE
    SANITIZE -->|clean integer| SESSION_UPDATE
    SESSION_UPDATE -->|auto-save| SESSION_SAVE
    SESSION_SAVE -->|persisted| SESSIONS_DIR
    SESSION_UPDATE -->|add to scorer| SCORE_CALC
    
    %% Completion Check
    SESSION_UPDATE -->|check if complete| INIT_TEST
    
    %% Results Calculation
    SCORE_CALC -->|all responses collected| TYPE_DETERMINE
    TYPE_DETERMINE -->|4-letter type| ANALYZE
    TYPES_DB -->|type data| ANALYZE
    FUNCTIONS_DB -->|function mappings| ANALYZE
    
    %% Pattern Validation
    SCORE_CALC -->|response list| CHECK_PATTERN
    CHECK_PATTERN -->|straight-lining warning| DISPLAY
    CHECK_PATTERN -->|valid pattern| TYPE_DETERMINE
    
    %% Results Processing
    ANALYZE -->|enriched results| SESSION_COMPLETE
    SESSION_COMPLETE -->|with results| SESSION_SAVE
    ANALYZE -->|complete results| BUILD_REPORT
    BUILD_REPORT -->|formatted report| CREATE_CHART
    CREATE_CHART -->|with visuals| DISPLAY
    
    %% Export Options
    BUILD_REPORT -->|user choice| FORMAT_TEXT
    BUILD_REPORT -->|user choice| FORMAT_JSON
    FORMAT_TEXT -->|.txt file| EXPORT_TXT
    FORMAT_JSON -->|.json file| EXPORT_JSON
    FORMAT_TEXT -->|text content| CLIPBOARD
    
    %% Data Loading at Startup
    QUESTIONS_DB -->|startup| LOAD_QUESTIONS
    TYPES_DB -->|startup| LOAD_TYPES
    FUNCTIONS_DB -->|startup| LOAD_FUNCTIONS
    
    style USER_START fill:#90EE90
    style USER_INPUT fill:#90EE90
    style DISPLAY fill:#FFB6C1
    style EXPORT_TXT fill:#FFB6C1
    style EXPORT_JSON fill:#FFB6C1
    style SESSION_SAVE fill:#87CEEB
    style SESSIONS_DIR fill:#87CEEB
    style QUESTIONS_DB fill:#F0E68C
    style TYPES_DB fill:#F0E68C
    style FUNCTIONS_DB fill:#F0E68C
```

## Data Flow Context

### Primary User Flow
1. **Test Initialization** (2-3 seconds)
   - User selects test length → System loads 16/44/88 questions
   - Questions filtered by priority level
   - New session created with timestamp ID

2. **Question-Answer Loop** (5-25 minutes)
   - Each question displayed → User provides 1-5 response
   - Response validated and sanitized
   - Session auto-saved after each answer
   - Progress tracked in memory and on disk

3. **Results Calculation** (<1 second)
   - All responses aggregated by dimension
   - Scoring algorithm calculates percentages
   - MBTI type determined from 4 dimension preferences
   - Results enriched with personality data

4. **Results Display & Export** (2-5 seconds)
   - Terminal display with charts and formatting
   - Optional export to text/JSON
   - Session marked complete

### Data Transformations

#### Input Sanitization
- **Raw Input**: String from terminal (e.g., "3", "3.5", "abc")
- **Sanitized**: Integer 1-5 (clamped if out of range)
- **Location**: `ResponseValidator.sanitize_response()`

#### Score Calculation
- **Input**: List of 1-5 responses per dimension
- **Transformation**: 
  - Reverse-coded questions inverted (5→1, 4→2, etc.)
  - Sum normalized to 0-100 percentage
- **Output**: Preference letter + strength percentage

#### Type Enrichment
- **Input**: 4-letter code (e.g., "INTJ")
- **Enrichment**: Adds title, overview, strengths, careers, etc.
- **Source**: `personality_types.json` lookup

### Data Volume & Performance

| Stage | Data Size | Processing Time |
|-------|-----------|-----------------|
| Question Load | 88 questions (~50KB) | <100ms |
| Session Save | ~2-5KB per save | <50ms |
| Response Validation | Single integer | <1ms |
| Score Calculation | 16-88 responses | <100ms |
| Type Determination | 4 dimension scores | <10ms |
| Results Display | ~10KB formatted | <500ms |
| Export Generation | ~5-15KB file | <2s |

### Data Consistency

#### Transaction Boundaries
- **Session Updates**: Each response is atomic
- **Auto-save**: After every response (no batching)
- **Results**: Calculated only after all questions answered

#### Data Persistence Points
1. Session creation (empty session)
2. After each response (incremental save)
3. On test completion (with results)
4. On manual export (separate file)

#### Recovery Mechanisms
- **Session Resume**: Can recover from any point
- **Incomplete Detection**: Sessions <30min old can resume
- **Data Validation**: Each save includes timestamp

### Error Handling

#### Failed Response Validation
- **Path**: `VALIDATE_RESP` → `DISPLAY` (error message)
- **Recovery**: User prompted to try again
- **No data saved**: Invalid responses never persisted

#### Corrupt Session Files
- **Detection**: JSON parse failure on load
- **Handling**: Session ignored, user starts fresh
- **No cascade**: Other sessions unaffected

#### Missing Data Files
- **Detection**: On application startup
- **Handling**: Application exits with error
- **Required Files**: All 3 JSON data files must exist

### Performance Bottlenecks

1. **File I/O**: Session saves (mitigated by <50ms writes)
2. **Terminal Rendering**: Rich UI updates (optimized by clearing screen)
3. **Chart Generation**: Plotext rendering (cached where possible)

### Data Routing Logic

#### Question Selection by Test Length
- **Short (16)**: Priority 1 only, 4 per dimension
- **Medium (44)**: Priority 1-2, 11 per dimension  
- **Long (88)**: Priority 1-3, all 22 per dimension

#### Response Pattern Detection
- **Straight-lining**: All responses identical → Warning
- **Alternating**: 1-5-1-5 pattern → Warning
- **Extreme**: >90% responses are 1 or 5 → Warning
- **Valid**: Mixed responses → Continue

### Caching Strategy
- **Static Data**: Questions/types loaded once at startup
- **Session Data**: Kept in memory during test
- **No External Cache**: All caching is in-process

## Data Privacy Notes

- **No Network Calls**: All processing is local
- **No Analytics**: No usage data collected
- **Local Storage Only**: Data never leaves user's machine
- **Manual Export**: User controls when/if results are shared