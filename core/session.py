import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from config.settings import SETTINGS

class SessionManager:
    """Handle saving and resuming test sessions."""
    
    def __init__(self):
        self.session_dir = SETTINGS['session_directory']
        self.session_dir.mkdir(exist_ok=True, parents=True)
        self.current_session = None
        self.session_file = None
    
    def create_session(self, test_length: str, total_questions: int) -> str:
        """
        Create new test session.
        
        Args:
            test_length: Type of test (short/medium/long)
            total_questions: Total number of questions
            
        Returns:
            Session ID
        """
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_session = {
            'id': session_id,
            'test_length': test_length,
            'total_questions': total_questions,
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'responses': [],
            'current_question': 0,
            'completed': False,
            'mbti_result': None
        }
        
        self.session_file = self.session_dir / f"session_{session_id}.json"
        self.save()
        return session_id
    
    def save(self):
        """Auto-save current session."""
        if self.current_session and self.session_file:
            self.current_session['last_updated'] = datetime.now().isoformat()
            
            try:
                with open(self.session_file, 'w') as f:
                    json.dump(self.current_session, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not save session: {e}")
    
    def find_incomplete_sessions(self) -> List[Dict]:
        """
        Find sessions that can be resumed.
        
        Returns:
            List of incomplete session data
        """
        sessions = []
        
        try:
            for filepath in self.session_dir.glob("session_*.json"):
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                        
                    # Check if session is incomplete and not too old
                    if not data.get('completed', False):
                        last_updated = datetime.fromisoformat(data['last_updated'])
                        timeout = timedelta(minutes=SETTINGS['session_timeout_minutes'])
                        
                        if datetime.now() - last_updated < timeout:
                            sessions.append({
                                'id': data['id'],
                                'test_length': data['test_length'],
                                'progress': f"{data['current_question']}/{data['total_questions']}",
                                'last_updated': last_updated.strftime('%Y-%m-%d %H:%M'),
                                'filepath': str(filepath)
                            })
                except (json.JSONDecodeError, KeyError):
                    continue
                    
        except Exception:
            pass
        
        return sorted(sessions, key=lambda x: x['last_updated'], reverse=True)
    
    def resume_session(self, session_id: str) -> Optional[Dict]:
        """
        Load and resume a session.
        
        Args:
            session_id: Session ID to resume
            
        Returns:
            Session data or None if not found
        """
        session_file = self.session_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            # Try to find by partial match
            for filepath in self.session_dir.glob(f"session_*{session_id}*.json"):
                session_file = filepath
                break
            else:
                return None
        
        try:
            with open(session_file) as f:
                self.current_session = json.load(f)
            
            self.session_file = session_file
            
            # Update last access time
            self.current_session['last_updated'] = datetime.now().isoformat()
            self.save()
            
            return self.current_session
            
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def add_response(self, question_id: str, question_data: Dict, response_value: int):
        """
        Add response and auto-save.
        
        Args:
            question_id: Question identifier
            question_data: Full question data
            response_value: User's response (1-5)
        """
        if not self.current_session:
            raise ValueError("No active session")
        
        response_data = {
            'question_id': question_id,
            'dimension': question_data['dimension'],
            'value': response_value,
            'reverse_coded': question_data.get('reverse_coded', False),
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if this question was already answered (for back navigation)
        existing = next(
            (i for i, r in enumerate(self.current_session['responses']) 
             if r['question_id'] == question_id), 
            None
        )
        
        if existing is not None:
            # Update existing response
            self.current_session['responses'][existing] = response_data
        else:
            # Add new response
            self.current_session['responses'].append(response_data)
            self.current_session['current_question'] += 1
        
        self.save()
    
    def go_back(self) -> bool:
        """
        Go back to previous question.
        
        Returns:
            True if successful, False if at beginning
        """
        if not self.current_session:
            return False
        
        if self.current_session['current_question'] > 0:
            self.current_session['current_question'] -= 1
            # Remove last response
            if self.current_session['responses']:
                self.current_session['responses'].pop()
            self.save()
            return True
        
        return False
    
    def mark_complete(self, mbti_result: Dict):
        """
        Mark session as complete.
        
        Args:
            mbti_result: Final MBTI results
        """
        if not self.current_session:
            return
        
        self.current_session['completed'] = True
        self.current_session['completed_at'] = datetime.now().isoformat()
        self.current_session['mbti_result'] = mbti_result
        self.save()
    
    def get_progress(self) -> Dict:
        """
        Get current progress information.
        
        Returns:
            Progress data
        """
        if not self.current_session:
            return {
                'current': 0,
                'total': 0,
                'percentage': 0,
                'time_elapsed': '0:00'
            }
        
        current = self.current_session['current_question']
        total = self.current_session['total_questions']
        percentage = (current / total * 100) if total > 0 else 0
        
        # Calculate time elapsed
        started = datetime.fromisoformat(self.current_session['started_at'])
        elapsed = datetime.now() - started
        hours, remainder = divmod(elapsed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes}:{seconds:02d}"
        
        return {
            'current': current,
            'total': total,
            'percentage': percentage,
            'time_elapsed': time_str,
            'responses_count': len(self.current_session['responses'])
        }
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        Remove sessions older than specified days.
        
        Args:
            days: Number of days to keep sessions
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            for filepath in self.session_dir.glob("session_*.json"):
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                    
                    last_updated = datetime.fromisoformat(data.get('last_updated', data['started_at']))
                    
                    if last_updated < cutoff:
                        filepath.unlink()
                        
                except (json.JSONDecodeError, KeyError, OSError):
                    # Remove corrupted files
                    try:
                        filepath.unlink()
                    except:
                        pass
        except Exception:
            pass
    
    def export_session(self, format: str = 'json') -> Optional[str]:
        """
        Export current session data.
        
        Args:
            format: Export format (json/txt)
            
        Returns:
            Export file path or None
        """
        if not self.current_session:
            return None
        
        export_dir = SETTINGS['export_directory']
        export_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filepath = export_dir / f"mbti_session_{timestamp}.json"
            with open(filepath, 'w') as f:
                json.dump(self.current_session, f, indent=2)
        else:
            filepath = export_dir / f"mbti_session_{timestamp}.txt"
            with open(filepath, 'w') as f:
                f.write(f"MBTI Test Session\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Session ID: {self.current_session['id']}\n")
                f.write(f"Started: {self.current_session['started_at']}\n")
                f.write(f"Test Length: {self.current_session['test_length']}\n")
                f.write(f"Questions: {self.current_session['current_question']}/{self.current_session['total_questions']}\n")
                
                if self.current_session.get('mbti_result'):
                    f.write(f"\nResult: {self.current_session['mbti_result']['type']}\n")
        
        return str(filepath)