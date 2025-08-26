"""
Tests for session management functionality.
These tests verify save/resume capabilities and session persistence.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.session import SessionManager
from config.settings import SETTINGS


class TestSessionManager(unittest.TestCase):
    """Test the session management functionality."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        # Create temporary directory for test sessions
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Override session directory in settings
        self.original_session_dir = SETTINGS['session_directory']
        SETTINGS['session_directory'] = self.temp_dir
        
        self.session_manager = SessionManager()
        
    def tearDown(self):
        """Clean up temporary directory and restore settings."""
        # Restore original settings
        SETTINGS['session_directory'] = self.original_session_dir
        
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Test creating a new session."""
        session_id = self.session_manager.create_session('medium', 44)
        
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(self.session_manager.current_session)
        self.assertEqual(self.session_manager.current_session['test_length'], 'medium')
        self.assertEqual(self.session_manager.current_session['total_questions'], 44)
        self.assertEqual(self.session_manager.current_session['current_question'], 0)
        self.assertFalse(self.session_manager.current_session['completed'])
        
        # Check that session file was created
        session_file = self.temp_dir / f"session_{session_id}.json"
        self.assertTrue(session_file.exists())
    
    def test_save_session(self):
        """Test saving session data to file."""
        session_id = self.session_manager.create_session('short', 16)
        
        # Modify session data
        self.session_manager.current_session['current_question'] = 5
        
        # Save
        self.session_manager.save()
        
        # Load file directly and verify
        session_file = self.temp_dir / f"session_{session_id}.json"
        with open(session_file) as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['current_question'], 5)
        self.assertEqual(saved_data['test_length'], 'short')
    
    def test_add_response(self):
        """Test adding responses to session."""
        self.session_manager.create_session('short', 16)
        
        question_data = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'reverse_coded': False
        }
        
        self.session_manager.add_response('E_I_001', question_data, 4)
        
        self.assertEqual(len(self.session_manager.current_session['responses']), 1)
        self.assertEqual(self.session_manager.current_session['current_question'], 1)
        
        response = self.session_manager.current_session['responses'][0]
        self.assertEqual(response['question_id'], 'E_I_001')
        self.assertEqual(response['value'], 4)
        self.assertEqual(response['dimension'], 'E_I')
    
    def test_update_existing_response(self):
        """Test updating an existing response (for back navigation)."""
        self.session_manager.create_session('short', 16)
        
        question_data = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'reverse_coded': False
        }
        
        # Add initial response
        self.session_manager.add_response('E_I_001', question_data, 3)
        
        # Update same response
        self.session_manager.add_response('E_I_001', question_data, 5)
        
        # Should still have only 1 response, but updated
        self.assertEqual(len(self.session_manager.current_session['responses']), 1)
        self.assertEqual(self.session_manager.current_session['responses'][0]['value'], 5)
    
    def test_go_back(self):
        """Test going back to previous question."""
        self.session_manager.create_session('short', 16)
        
        # Add some responses
        for i in range(3):
            q_data = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.session_manager.add_response(f'E_I_{i:03d}', q_data, 3)
        
        self.assertEqual(self.session_manager.current_session['current_question'], 3)
        self.assertEqual(len(self.session_manager.current_session['responses']), 3)
        
        # Go back
        result = self.session_manager.go_back()
        
        self.assertTrue(result)
        self.assertEqual(self.session_manager.current_session['current_question'], 2)
        self.assertEqual(len(self.session_manager.current_session['responses']), 2)
    
    def test_go_back_at_beginning(self):
        """Test that go_back fails at the beginning."""
        self.session_manager.create_session('short', 16)
        
        result = self.session_manager.go_back()
        
        self.assertFalse(result)
        self.assertEqual(self.session_manager.current_session['current_question'], 0)
    
    def test_find_incomplete_sessions(self):
        """Test finding resumable sessions."""
        # Create multiple sessions
        session1_id = self.session_manager.create_session('short', 16)
        self.session_manager.current_session['current_question'] = 5
        self.session_manager.save()
        
        session2_id = self.session_manager.create_session('medium', 44)
        self.session_manager.current_session['current_question'] = 10
        self.session_manager.save()
        
        # Mark one as complete
        session3_id = self.session_manager.create_session('long', 88)
        self.session_manager.mark_complete({'type': 'INTJ'})
        
        # Find incomplete sessions
        incomplete = self.session_manager.find_incomplete_sessions()
        
        # Should find 2 incomplete sessions
        self.assertEqual(len(incomplete), 2)
        
        # Verify they're the right ones
        session_ids = [s['id'] for s in incomplete]
        self.assertIn(session1_id, session_ids)
        self.assertIn(session2_id, session_ids)
        self.assertNotIn(session3_id, session_ids)
    
    def test_find_incomplete_sessions_timeout(self):
        """Test that old sessions are not returned as resumable."""
        # Create a session with old timestamp
        session_id = self.session_manager.create_session('short', 16)
        
        # Manually set last_updated to be old
        old_time = datetime.now() - timedelta(hours=2)
        self.session_manager.current_session['last_updated'] = old_time.isoformat()
        self.session_manager.save()
        
        # Should not find this old session
        incomplete = self.session_manager.find_incomplete_sessions()
        
        self.assertEqual(len(incomplete), 0)
    
    def test_resume_session(self):
        """Test resuming an existing session."""
        # Create and save a session
        original_id = self.session_manager.create_session('medium', 44)
        
        # Add some responses
        for i in range(5):
            q_data = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.session_manager.add_response(f'E_I_{i:03d}', q_data, 3)
        
        # Create new manager instance to simulate restart
        new_manager = SessionManager()
        
        # Resume session
        resumed_data = new_manager.resume_session(original_id)
        
        self.assertIsNotNone(resumed_data)
        self.assertEqual(resumed_data['id'], original_id)
        self.assertEqual(resumed_data['current_question'], 5)
        self.assertEqual(len(resumed_data['responses']), 5)
    
    def test_resume_nonexistent_session(self):
        """Test attempting to resume a non-existent session."""
        result = self.session_manager.resume_session('nonexistent_id')
        
        self.assertIsNone(result)
    
    def test_mark_complete(self):
        """Test marking a session as complete."""
        self.session_manager.create_session('short', 16)
        
        mbti_result = {
            'type': 'INTJ',
            'confidence': 75.5
        }
        
        self.session_manager.mark_complete(mbti_result)
        
        self.assertTrue(self.session_manager.current_session['completed'])
        self.assertIsNotNone(self.session_manager.current_session['completed_at'])
        self.assertEqual(self.session_manager.current_session['mbti_result'], mbti_result)
    
    def test_get_progress(self):
        """Test getting progress information."""
        self.session_manager.create_session('short', 16)
        
        # Add some responses
        for i in range(8):
            q_data = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.session_manager.add_response(f'E_I_{i:03d}', q_data, 3)
        
        progress = self.session_manager.get_progress()
        
        self.assertEqual(progress['current'], 8)
        self.assertEqual(progress['total'], 16)
        self.assertEqual(progress['percentage'], 50.0)
        self.assertEqual(progress['responses_count'], 8)
        self.assertIn('time_elapsed', progress)
    
    def test_get_progress_no_session(self):
        """Test getting progress with no active session."""
        progress = self.session_manager.get_progress()
        
        self.assertEqual(progress['current'], 0)
        self.assertEqual(progress['total'], 0)
        self.assertEqual(progress['percentage'], 0)
        self.assertEqual(progress['time_elapsed'], '0:00')
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of old session files."""
        # Create an old session
        old_session_id = self.session_manager.create_session('short', 16)
        
        # Manually set to old date
        old_time = datetime.now() - timedelta(days=10)
        self.session_manager.current_session['last_updated'] = old_time.isoformat()
        self.session_manager.save()
        
        # Create a recent session
        recent_session_id = self.session_manager.create_session('medium', 44)
        
        # Run cleanup (7 days default)
        self.session_manager.cleanup_old_sessions(days=7)
        
        # Old session should be deleted
        old_file = self.temp_dir / f"session_{old_session_id}.json"
        recent_file = self.temp_dir / f"session_{recent_session_id}.json"
        
        self.assertFalse(old_file.exists())
        self.assertTrue(recent_file.exists())
    
    def test_export_session_json(self):
        """Test exporting session as JSON."""
        # Create temp export directory
        export_dir = self.temp_dir / 'exports'
        SETTINGS['export_directory'] = export_dir
        
        self.session_manager.create_session('short', 16)
        
        # Add some data
        for i in range(3):
            q_data = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.session_manager.add_response(f'E_I_{i:03d}', q_data, 3)
        
        # Export
        export_path = self.session_manager.export_session('json')
        
        self.assertIsNotNone(export_path)
        self.assertTrue(Path(export_path).exists())
        
        # Verify content
        with open(export_path) as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['test_length'], 'short')
        self.assertEqual(len(exported_data['responses']), 3)
    
    def test_export_session_text(self):
        """Test exporting session as text."""
        # Create temp export directory
        export_dir = self.temp_dir / 'exports'
        SETTINGS['export_directory'] = export_dir
        
        self.session_manager.create_session('medium', 44)
        
        # Export
        export_path = self.session_manager.export_session('txt')
        
        self.assertIsNotNone(export_path)
        self.assertTrue(Path(export_path).exists())
        
        # Verify content
        with open(export_path) as f:
            content = f.read()
        
        self.assertIn('MBTI Test Session', content)
        self.assertIn('Test Length: medium', content)
        self.assertIn('Questions: 0/44', content)
    
    def test_session_persistence_through_crash(self):
        """Test that sessions persist through application crashes."""
        # Create session and add responses
        session_id = self.session_manager.create_session('short', 16)
        
        for i in range(10):
            q_data = {'id': f'Q_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.session_manager.add_response(f'Q_{i:03d}', q_data, 3)
        
        # Simulate crash (no proper cleanup)
        del self.session_manager
        
        # Create new manager (simulate restart)
        new_manager = SessionManager()
        
        # Should be able to find and resume
        sessions = new_manager.find_incomplete_sessions()
        self.assertEqual(len(sessions), 1)
        
        # Resume and verify data integrity
        resumed = new_manager.resume_session(session_id)
        self.assertIsNotNone(resumed)
        self.assertEqual(len(resumed['responses']), 10)
        self.assertEqual(resumed['current_question'], 10)


if __name__ == '__main__':
    unittest.main()