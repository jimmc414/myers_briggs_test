# MBTI Test Application - Sequence Diagrams

## 1. Complete Test Flow with Session Management
**Trigger:** User starts a new MBTI test
**Outcome:** Test completed, results calculated and displayed

```mermaid
sequenceDiagram
    participant U as User
    participant M as Main/MBTIApp
    participant UI as UIComponents
    participant TE as TestEngine
    participant SM as SessionManager
    participant SC as Scorer
    participant RA as ResultAnalyzer
    participant FS as FileSystem
    
    U->>M: python main.py
    M->>UI: display_welcome()
    UI-->>U: Show welcome screen
    
    U->>UI: Select test length
    UI-->>M: "short"|"medium"|"long"
    
    M->>TE: initialize_test(test_length)
    TE->>TE: _select_questions(config)
    Note over TE: Filter by priority
    
    TE->>SM: create_session(test_length, count)
    SM->>FS: Write session_{id}.json
    FS-->>SM: OK
    SM-->>TE: session_id
    TE-->>M: session_id
    
    loop For each question
        M->>TE: get_current_question()
        TE-->>M: question_data
        
        M->>UI: display_question(question, num, total)
        UI-->>U: Show question with options
        
        U->>UI: Select answer (1-5)
        UI-->>M: response_value
        
        M->>TE: submit_response(value)
        TE->>SC: add_response(id, data, value)
        SC->>SC: Store in memory
        
        TE->>SM: add_response(id, data, value)
        SM->>FS: Update session file
        FS-->>SM: Saved
        
        TE->>TE: current_index++
    end
    
    M->>TE: calculate_results()
    TE->>SC: determine_mbti_type()
    SC->>SC: Calculate all dimensions
    SC-->>TE: {type: "INTJ", confidence: 75}
    
    TE->>RA: get_type_analysis("INTJ", scores)
    RA->>FS: Read personality_types.json
    FS-->>RA: Type data
    RA-->>TE: Enriched analysis
    
    TE->>SM: mark_complete(results)
    SM->>FS: Update session with results
    
    TE-->>M: Complete results
    M->>UI: Display results
    UI-->>U: Show type, analysis, charts
```

### Performance Notes
- Question selection: <100ms (in-memory filtering)
- Per-question cycle: Limited by user response time
- Results calculation: <1 second
- Session saves: <50ms per write

### Failure Modes
- Session save failure: User warned but test continues
- Corrupt session: Cannot resume, must restart
- Missing data files: Application exits at startup

---

## 2. Resume Session Flow
**Trigger:** User chooses to resume a previous session
**Outcome:** Test continues from last answered question

```mermaid
sequenceDiagram
    participant U as User
    participant M as Main
    participant UI as UIComponents
    participant TE as TestEngine
    participant SM as SessionManager
    participant SC as Scorer
    participant FS as FileSystem
    
    M->>TE: get_available_sessions()
    TE->>SM: find_incomplete_sessions()
    SM->>FS: List session_*.json files
    FS-->>SM: File list
    
    loop For each session file
        SM->>FS: Read session data
        FS-->>SM: JSON data
        
        alt Session < 30 min old AND not complete
            SM->>SM: Add to resumable list
        else Session too old OR complete
            SM->>SM: Skip
        end
    end
    
    SM-->>TE: Resumable sessions list
    TE-->>M: Sessions with metadata
    
    M->>UI: display_resume_option(sessions)
    UI-->>U: Show resumable sessions
    
    U->>UI: Select session
    UI-->>M: session_id
    
    M->>TE: resume_test(session_id)
    TE->>SM: resume_session(session_id)
    SM->>FS: Read session_{id}.json
    FS-->>SM: Session data with responses
    
    SM->>SM: Update last_accessed
    SM-->>TE: Session data
    
    TE->>TE: Restore test state
    
    loop For each previous response
        TE->>SC: add_response(id, data, value)
        Note over SC: Rebuild scorer state
    end
    
    TE-->>M: Resume successful
    M->>M: Continue test from current_index
```

### Performance Notes
- Session discovery: <100ms for typical directory
- Session restoration: <200ms including response replay
- State rebuild: O(n) where n = answered questions

### Failure Modes
- Session file deleted: Shows as not found
- Corrupted JSON: Session skipped, logged
- Version mismatch: Handled gracefully

---

## 3. Response Validation and Pattern Detection
**Trigger:** User submits responses during test
**Outcome:** Invalid patterns detected and warned

```mermaid
sequenceDiagram
    participant U as User
    participant TE as TestEngine
    participant V as Validator
    participant SC as Scorer
    participant UI as UIComponents
    
    U->>TE: submit_response(raw_value)
    
    TE->>V: sanitize_response(raw_value)
    
    alt String input "3" or "3️⃣ Neutral"
        V->>V: Parse to integer
    else Float input 3.5
        V->>V: Round to integer
    else Out of range
        V->>V: Clamp to 1-5
    else Invalid
        V-->>TE: ValueError
        TE-->>UI: Show error
        UI-->>U: "Invalid input"
    end
    
    V-->>TE: Sanitized integer
    
    TE->>V: validate_response(int_value)
    alt Value in range 1-5
        V-->>TE: Valid
    else Out of range
        V-->>TE: ValueError
        TE-->>UI: Show error
    end
    
    TE->>SC: add_response(id, data, value)
    
    alt Test complete
        TE->>V: check_consistency(all_responses)
        
        V->>V: Check patterns
        
        alt All same value (straight-lining)
            V-->>TE: (False, "All identical")
            TE->>UI: Display warning
            UI-->>U: "Responses appear invalid"
            
            U->>UI: Continue anyway?
            alt User confirms
                UI-->>TE: Continue
            else User cancels
                UI-->>TE: Abort
            end
            
        else Alternating 1-5-1-5
            V-->>TE: (False, "Alternating pattern")
            TE->>UI: Display warning
            
        else >90% extreme (1 or 5)
            V-->>TE: (False, "Too extreme")
            TE->>UI: Display warning
            
        else Valid pattern
            V-->>TE: (True, "Valid")
        end
    end
```

### Performance Notes
- Validation: <1ms per response
- Pattern detection: <10ms for 88 responses
- No async operations needed

### Failure Modes
- Invalid input: Re-prompt user
- Pattern detected: Warning but can continue
- Validation bypass: Not possible due to sanitization

---

## 4. Results Calculation and Enrichment
**Trigger:** All questions answered
**Outcome:** MBTI type determined and enriched with analysis

```mermaid
sequenceDiagram
    participant TE as TestEngine
    participant SC as Scorer
    participant RA as ResultAnalyzer
    participant FS as FileSystem
    participant C as Charts
    participant R as Reports
    
    TE->>SC: get_detailed_results()
    
    loop For each dimension [E_I, S_N, T_F, J_P]
        SC->>SC: calculate_dimension_score(dim)
        
        Note over SC: Filter responses by dimension
        
        loop For each response
            alt reverse_coded == true
                SC->>SC: Invert value (6 - value)
            end
            SC->>SC: Add to total
        end
        
        SC->>SC: Normalize to percentage
        
        alt Score > 52%
            SC->>SC: Assign right preference (E/N/T/J)
        else Score < 48%
            SC->>SC: Assign left preference (I/S/F/P)
        else Borderline
            SC->>SC: Mark as borderline
        end
    end
    
    SC->>SC: Combine preferences → Type
    SC-->>TE: Raw results
    
    TE->>RA: get_type_analysis(type, scores)
    RA->>FS: Read personality_types.json
    FS-->>RA: Type descriptions
    
    RA->>FS: Read cognitive_functions.json
    FS-->>RA: Function mappings
    
    RA->>RA: Enrich with metadata
    RA-->>TE: Complete analysis
    
    TE->>R: display_full_results(results)
    R->>C: create_dimension_chart(scores)
    C->>C: Generate ASCII/plotext chart
    C-->>R: Visual representation
    
    R->>R: Format all sections
    R-->>TE: Formatted display
```

### Performance Notes
- Score calculation: O(n) where n = responses
- Type lookup: O(1) hash lookup
- Enrichment: <100ms for all data
- Chart generation: <500ms

### Failure Modes
- Missing type data: Show basic results only
- Chart library failure: Fall back to ASCII
- Calculation error: Log and show partial results

---

## 5. Export and Persistence Flow
**Trigger:** User chooses to export results
**Outcome:** Results saved to file system in chosen format

```mermaid
sequenceDiagram
    participant U as User
    participant M as Main
    participant UI as UIComponents
    participant E as Exporter
    participant R as Reports
    participant FS as FileSystem
    participant CB as Clipboard
    
    M->>UI: Offer export options
    UI-->>U: Menu [Text|JSON|Clipboard|None]
    
    U->>UI: Select export format
    UI-->>M: User choice
    
    alt Text export
        M->>E: export_results(results, 'txt')
        E->>R: generate_summary_report(results)
        R->>R: Format as text
        R-->>E: Text content
        
        E->>FS: Create ~/Documents/MBTI_Results/
        E->>FS: Write mbti_results_INTJ_timestamp.txt
        FS-->>E: File path
        E-->>M: Success path
        
    else JSON export
        M->>E: export_results(results, 'json')
        E->>E: Serialize with json.dump()
        E->>FS: Write mbti_results_INTJ_timestamp.json
        FS-->>E: File path
        E-->>M: Success path
        
    else Clipboard
        M->>E: copy_to_clipboard(results)
        E->>R: generate_summary_report(results)
        R-->>E: Text content
        
        E->>CB: pyperclip.copy(text)
        
        alt Clipboard available
            CB-->>E: Success
            E-->>M: True
        else No clipboard support
            CB-->>E: Error
            E-->>M: False
            M->>UI: Show error
        end
        
    else No export
        M->>M: Continue
    end
    
    alt Export successful
        M->>UI: display_success(path)
        UI-->>U: "Saved to: {path}"
    else Export failed
        M->>UI: display_error(reason)
        UI-->>U: Error message
    end
```

### Performance Notes
- Text generation: <100ms
- File write: <50ms for typical results
- Clipboard: Instant if supported

### Failure Modes
- Directory creation fails: Try alternate location
- File write fails: Show error, offer retry
- Clipboard unavailable: Hide option or show error

---

## Summary of Key Interactions

### Synchronous Operations
1. Question presentation → User response
2. Response validation → Score update
3. Results calculation → Type determination

### Asynchronous Patterns
- **Session auto-save**: Fire-and-forget after each response
- **No true async**: All operations are synchronous

### State Management
- **In-memory**: Current test state, responses, scores
- **Persisted**: Session files (JSON) after each response
- **Immutable**: Question data, personality types

### Critical Timing Constraints
1. Session timeout: 30 minutes for resume
2. Auto-save: Must complete before next question
3. No real-time requirements

### Transaction Boundaries
- Each response is atomic
- Results calculation is all-or-nothing
- Session updates are eventually consistent