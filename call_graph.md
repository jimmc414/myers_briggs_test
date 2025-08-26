# MBTI Test Application - Call Graph Documentation

## Entry Points and Call Chains

### Main Entry Point

```mermaid
graph TD
    subgraph "CLI Entry"
        MAIN[main.py::main]
        ARGS[Parse Arguments]
    end
    
    subgraph "Application Layer"
        APP[MBTIApp.__init__]
        RUN[MBTIApp.run]
        START[MBTIApp.start_new_test]
        TEST[MBTIApp.run_test]
        RESULTS[MBTIApp.show_results]
        EXPORT[MBTIApp.offer_export]
    end
    
    subgraph "Core Engine"
        ENGINE_INIT[TestEngine.__init__]
        INIT_TEST[TestEngine.initialize_test]
        GET_Q[TestEngine.get_current_question]
        SUBMIT[TestEngine.submit_response]
        CALC[TestEngine.calculate_results]
        VALIDATE[TestEngine.validate_responses]
    end
    
    subgraph "UI Layer"
        WELCOME[UIComponents.display_welcome]
        SELECT[UIComponents.select_test_length]
        DISPLAY_Q[UIComponents.display_question]
        CONFIRM[UIComponents.confirm_action]
    end
    
    MAIN --> ARGS
    ARGS -->|--version| VERSION[Display Version]
    ARGS -->|--disclaimer| DISC[Display Disclaimer]
    ARGS -->|normal| APP
    APP --> ENGINE_INIT
    APP --> RUN
    RUN --> WELCOME
    RUN --> START
    START --> SELECT
    SELECT --> INIT_TEST
    INIT_TEST --> TEST
    TEST --> GET_Q
    GET_Q --> DISPLAY_Q
    DISPLAY_Q --> SUBMIT
    SUBMIT --> GET_Q
    TEST --> RESULTS
    RESULTS --> VALIDATE
    VALIDATE --> CALC
    CALC --> EXPORT
```

### Test Initialization Flow

```mermaid
graph TD
    subgraph "Test Setup"
        INIT[TestEngine.initialize_test]
        SELECT_Q[TestEngine._select_questions]
        CREATE_S[SessionManager.create_session]
    end
    
    subgraph "Question Selection"
        LOAD[Load all_questions]
        FILTER[Filter by dimension]
        PRIORITY[Sort by priority]
        SHUFFLE[Random shuffle]
    end
    
    subgraph "Session Creation"
        GEN_ID[Generate session ID]
        CREATE_FILE[Create session file]
        SAVE[SessionManager.save]
    end
    
    subgraph "Scorer Setup"
        RESET[MBTIScorer.reset]
        CLEAR[Clear responses]
    end
    
    INIT --> SELECT_Q
    INIT --> CREATE_S
    INIT --> RESET
    
    SELECT_Q --> LOAD
    LOAD --> FILTER
    FILTER --> PRIORITY
    PRIORITY --> SHUFFLE
    
    CREATE_S --> GEN_ID
    GEN_ID --> CREATE_FILE
    CREATE_FILE --> SAVE
    
    RESET --> CLEAR
```

### Response Processing Chain

```mermaid
graph TD
    subgraph "Response Input"
        USER[User Input 1-5]
        DISPLAY[UIComponents.display_question]
    end
    
    subgraph "Validation"
        SANITIZE[ResponseValidator.sanitize_response]
        VALIDATE[ResponseValidator.validate_response]
    end
    
    subgraph "Processing"
        SUBMIT[TestEngine.submit_response]
        ADD_SCORE[MBTIScorer.add_response]
        ADD_SESSION[SessionManager.add_response]
    end
    
    subgraph "Persistence"
        UPDATE[Update session data]
        SAVE[Auto-save to disk]
    end
    
    USER --> DISPLAY
    DISPLAY --> SUBMIT
    SUBMIT --> SANITIZE
    SANITIZE --> VALIDATE
    VALIDATE -->|Valid| ADD_SCORE
    VALIDATE -->|Valid| ADD_SESSION
    VALIDATE -->|Invalid| DISPLAY
    
    ADD_SESSION --> UPDATE
    UPDATE --> SAVE
```

### Results Calculation Flow

```mermaid
graph TD
    subgraph "Calculation Trigger"
        COMPLETE[All questions answered]
        SHOW_RES[MBTIApp.show_results]
    end
    
    subgraph "Validation"
        VAL_RESP[TestEngine.validate_responses]
        CHECK_PAT[ResponseValidator.check_consistency]
    end
    
    subgraph "Scoring"
        CALC[TestEngine.calculate_results]
        DET_TYPE[MBTIScorer.determine_mbti_type]
        CALC_DIM[MBTIScorer.calculate_dimension_score x4]
    end
    
    subgraph "Enrichment"
        GET_ANAL[ResultAnalyzer.get_type_analysis]
        LOAD_TYPE[Load personality_types.json]
        GET_FUNC[Load cognitive_functions.json]
    end
    
    subgraph "Display"
        REVEAL[Animations.reveal_result]
        REPORT[Reports.display_full_results]
        CHARTS[Charts.create_dimension_chart]
    end
    
    COMPLETE --> SHOW_RES
    SHOW_RES --> VAL_RESP
    VAL_RESP --> CHECK_PAT
    CHECK_PAT -->|Valid| CALC
    CALC --> DET_TYPE
    DET_TYPE --> CALC_DIM
    CALC --> GET_ANAL
    GET_ANAL --> LOAD_TYPE
    GET_ANAL --> GET_FUNC
    CALC --> REVEAL
    REVEAL --> REPORT
    REPORT --> CHARTS
```

## Call Frequency Analysis

### High-Traffic Functions
These functions are called most frequently during a test session:

| Function | Called By | Frequency | Purpose |
|----------|-----------|-----------|---------|
| `SessionManager.save` | All state changes | Every response | Auto-save progress |
| `TestEngine.get_current_question` | Main test loop | Once per question | Question retrieval |
| `ResponseValidator.validate_response` | Submit response | Every input attempt | Input validation |
| `UIComponents.display_question` | Test loop | Once per question | UI rendering |
| `MBTIScorer.add_response` | Submit response | Once per valid response | Score tracking |

### Most Called Utility Functions

| Function | Call Count | Called From |
|----------|------------|-------------|
| `console.print` | ~200+ | All UI components |
| `console.clear` | ~90 | Screen transitions |
| `Path operations` | ~50 | File operations |
| `datetime.now` | ~30 | Timestamps |
| `json.load/dump` | ~20 | Data persistence |

## Cross-Module Dependencies

### Module Interaction Matrix

| Caller → | test_engine | scoring | session | validator | ui | display | utils |
|----------|-------------|---------|---------|-----------|----|---------| ------|
| **main** | ✓ | - | - | - | ✓ | ✓ | ✓ |
| **test_engine** | - | ✓ | ✓ | ✓ | - | - | - |
| **scoring** | - | - | - | - | - | - | - |
| **session** | - | - | - | - | - | - | - |
| **validator** | - | - | - | - | - | - | - |
| **ui** | - | - | - | - | - | - | - |
| **display** | - | - | - | - | - | ✓ | - |

✓ = Direct function calls between modules

### Dependency Layers

```mermaid
graph BT
    subgraph "Data Layer"
        JSON[JSON Files]
        SESSION[Session Files]
    end
    
    subgraph "Core Logic"
        VALID[validator]
        SCORE[scoring]
        SESS[session]
    end
    
    subgraph "Business Logic"
        ENGINE[test_engine]
    end
    
    subgraph "Presentation"
        UI[ui/components]
        DISPLAY[display/reports]
        CHARTS[display/charts]
    end
    
    subgraph "Application"
        MAIN[main]
    end
    
    JSON --> ENGINE
    SESSION --> SESS
    VALID --> ENGINE
    SCORE --> ENGINE
    SESS --> ENGINE
    ENGINE --> MAIN
    UI --> MAIN
    DISPLAY --> MAIN
    CHARTS --> DISPLAY
```

## Critical Call Paths

### Test Session Lifecycle
```
python main.py
  └── MBTIApp.run (entry)
      ├── validate_data_files (5ms)
      ├── cleanup_old_sessions (10ms)
      ├── display_welcome (500ms with animation)
      ├── select_test_length (user wait)
      └── initialize_test (20ms)
          ├── _select_questions (5ms)
          ├── create_session (10ms)
          └── run_test (5-25 minutes)
              └── [Question Loop]
                  ├── get_current_question (1ms)
                  ├── display_question (user wait)
                  ├── submit_response (5ms)
                  │   ├── validate_response (1ms)
                  │   ├── add_response (scorer) (1ms)
                  │   └── add_response (session) (10ms save)
                  └── [Repeat 16-88 times]
              └── calculate_results (100ms)
                  ├── validate_responses (10ms)
                  ├── determine_mbti_type (50ms)
                  └── get_type_analysis (20ms)
Total: 5-25 minutes (user-dependent)
```

### Session Resume Path
```
resume_test(session_id)
  └── SessionManager.resume_session (50ms)
      ├── Read session file (10ms)
      ├── Validate timestamp (1ms)
      ├── Restore responses (20ms)
      │   └── [For each response]
      │       └── MBTIScorer.add_response (1ms)
      └── Update current_index (1ms)
Total: ~50ms for typical session
```

### Export Path
```
offer_export(results)
  └── User selects format
      ├── [Text Export]
      │   ├── generate_summary_report (20ms)
      │   ├── Create directory (5ms if needed)
      │   └── Write file (10ms)
      ├── [JSON Export]
      │   ├── json.dumps (5ms)
      │   └── Write file (10ms)
      └── [Clipboard]
          ├── generate_summary_report (20ms)
          └── pyperclip.copy (5ms)
Total: 15-35ms
```

## Dependency Hotspots

### Most Depended Upon Functions
Functions that would have highest impact if changed:

1. **ResponseValidator.validate_response**
   - Called by: TestEngine.submit_response
   - Critical: All user input flows through here
   - Change impact: **High** - Could break input handling

2. **SessionManager.save**
   - Called by: Every state change
   - Critical: Data persistence
   - Change impact: **High** - Could cause data loss

3. **MBTIScorer.calculate_dimension_score**
   - Called by: determine_mbti_type (4 times)
   - Critical: Core algorithm
   - Change impact: **High** - Would affect all results

4. **UIComponents.display_question**
   - Called by: Main test loop
   - Critical: User interaction
   - Change impact: **Medium** - UI changes only

5. **TestEngine.get_current_question**
   - Called by: Main test loop
   - Critical: Question flow
   - Change impact: **Medium** - Could break navigation

### Isolated Components
These have minimal dependencies and are safe to modify:

- **Animations** - Pure presentation, no business logic
- **Charts** - Display only, receives processed data
- **Helpers** - Utility functions, well-isolated
- **Themes** - Visual configuration only

## Performance Characteristics

### Bottlenecks
1. **Session auto-save** (~10ms per response) - File I/O
2. **Terminal clearing** (~5ms) - Screen refresh
3. **Animation delays** (configured delays) - Intentional UX
4. **Question shuffling** (minimal) - O(n) operation

### Optimization Opportunities
- Session saves could be batched (currently immediate)
- Terminal operations could be buffered
- Question selection could be pre-computed
- Results calculation is already optimal (~100ms total)

## Call Graph Summary

The application follows a clear hierarchical structure:

1. **Entry Layer**: `main.py` orchestrates the flow
2. **Business Layer**: `TestEngine` manages test logic
3. **Service Layer**: `Scorer`, `SessionManager`, `Validator` provide services
4. **UI Layer**: `UIComponents`, `Reports`, `Charts` handle presentation
5. **Data Layer**: JSON files provide static data

Key characteristics:
- **No circular dependencies** between modules
- **Clear separation of concerns**
- **Minimal coupling** between layers
- **High cohesion** within modules
- **Predictable call patterns** (no complex recursion)