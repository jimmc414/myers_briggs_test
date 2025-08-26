"""
Tests for the main test engine.
These tests verify the core test flow, question selection, and result calculation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.test_engine import TestEngine
from config.settings import SETTINGS, TEST_CONFIGS


class TestTestEngine(unittest.TestCase):
    """Test the main test engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for sessions
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_session_dir = SETTINGS['session_directory']
        SETTINGS['session_directory'] = self.temp_dir
        
        self.engine = TestEngine()
        
    def tearDown(self):
        """Clean up temporary directory."""
        SETTINGS['session_directory'] = self.original_session_dir
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test that engine initializes with required components."""
        self.assertIsNotNone(self.engine.all_questions)
        self.assertGreater(len(self.engine.all_questions), 0)
        self.assertIsNotNone(self.engine.session_manager)
        self.assertIsNotNone(self.engine.scorer)
        self.assertIsNotNone(self.engine.validator)
        self.assertIsNotNone(self.engine.result_analyzer)
    
    def test_initialize_short_test(self):
        """Test initialization of short test."""
        session_id = self.engine.initialize_test('short')
        
        self.assertIsNotNone(session_id)
        self.assertEqual(self.engine.test_length, 'short')
        self.assertEqual(len(self.engine.questions), TEST_CONFIGS['short']['total_questions'])
        self.assertEqual(self.engine.current_index, 0)
        
        # Verify questions are balanced across dimensions
        dimensions = {}
        for q in self.engine.questions:
            dim = q['dimension']
            dimensions[dim] = dimensions.get(dim, 0) + 1
        
        # Should have 4 questions per dimension for short test
        for count in dimensions.values():
            self.assertEqual(count, 4)
    
    def test_initialize_medium_test(self):
        """Test initialization of medium test."""
        session_id = self.engine.initialize_test('medium')
        
        self.assertEqual(len(self.engine.questions), TEST_CONFIGS['medium']['total_questions'])
        
        # Verify priority distribution
        priorities = [q['priority'] for q in self.engine.questions]
        
        # Medium test should have priority 1 and 2 questions
        self.assertIn(1, priorities)
        self.assertIn(2, priorities)
        self.assertNotIn(3, priorities)  # Should not have priority 3
    
    def test_initialize_long_test(self):
        """Test initialization of long test."""
        session_id = self.engine.initialize_test('long')
        
        self.assertEqual(len(self.engine.questions), TEST_CONFIGS['long']['total_questions'])
        
        # Should have all priority levels
        priorities = set(q['priority'] for q in self.engine.questions)
        self.assertEqual(priorities, {1, 2, 3})
    
    def test_question_selection_priorities(self):
        """Test that questions are selected according to priority."""
        self.engine.initialize_test('short')
        
        # Short test should only have priority 1 questions
        for q in self.engine.questions:
            self.assertEqual(q['priority'], 1)
    
    def test_get_current_question(self):
        """Test getting the current question."""
        self.engine.initialize_test('short')
        
        question = self.engine.get_current_question()
        
        self.assertIsNotNone(question)
        self.assertIn('id', question)
        self.assertIn('text', question)
        self.assertIn('dimension', question)
        self.assertIn('options', question)
    
    def test_get_current_question_at_end(self):
        """Test getting question when test is complete."""
        self.engine.initialize_test('short')
        self.engine.current_index = len(self.engine.questions)
        
        question = self.engine.get_current_question()
        
        self.assertIsNone(question)
    
    def test_submit_response(self):
        """Test submitting a response."""
        self.engine.initialize_test('short')
        initial_index = self.engine.current_index
        
        result = self.engine.submit_response(4)
        
        self.assertTrue(result)
        self.assertEqual(self.engine.current_index, initial_index + 1)
        self.assertEqual(len(self.engine.scorer.responses), 1)
    
    def test_submit_invalid_response(self):
        """Test submitting invalid responses."""
        self.engine.initialize_test('short')
        
        # Test invalid values
        invalid_values = [0, 6, -1, 'abc', None]
        
        for value in invalid_values:
            result = self.engine.submit_response(value)
            self.assertFalse(result)
            # Should not advance
            self.assertEqual(self.engine.current_index, 0)
    
    def test_go_back(self):
        """Test going back to previous question."""
        self.engine.initialize_test('short')
        
        # Submit a few responses
        self.engine.submit_response(3)
        self.engine.submit_response(4)
        
        self.assertEqual(self.engine.current_index, 2)
        
        # Go back
        result = self.engine.go_back()
        
        self.assertTrue(result)
        self.assertEqual(self.engine.current_index, 1)
    
    def test_go_back_at_start(self):
        """Test that go_back fails at the beginning."""
        self.engine.initialize_test('short')
        
        result = self.engine.go_back()
        
        self.assertFalse(result)
        self.assertEqual(self.engine.current_index, 0)
    
    def test_skip_question(self):
        """Test skipping a question (neutral response)."""
        self.engine.initialize_test('short')
        
        result = self.engine.skip_question()
        
        self.assertTrue(result)
        self.assertEqual(self.engine.current_index, 1)
        
        # Should have recorded a neutral (3) response
        responses = list(self.engine.scorer.responses.values())
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]['value'], 3)
    
    def test_is_complete(self):
        """Test checking if test is complete."""
        self.engine.initialize_test('short')
        
        # Initially not complete
        self.assertFalse(self.engine.is_complete())
        
        # Submit all responses
        for _ in range(16):
            self.engine.submit_response(3)
        
        # Now should be complete
        self.assertTrue(self.engine.is_complete())
    
    def test_get_progress(self):
        """Test getting progress information."""
        self.engine.initialize_test('short')
        
        # Submit some responses
        for _ in range(8):
            self.engine.submit_response(3)
        
        progress = self.engine.get_progress()
        
        self.assertEqual(progress['current'], 8)
        self.assertEqual(progress['total'], 16)
        self.assertEqual(progress['questions_remaining'], 8)
        self.assertIn('dimension_progress', progress)
        
        # Check dimension progress
        for dim_key, dim_data in progress['dimension_progress'].items():
            self.assertIn('answered', dim_data)
            self.assertIn('total', dim_data)
            self.assertIn('name', dim_data)
    
    def test_calculate_results(self):
        """Test calculating final results."""
        self.engine.initialize_test('short')
        
        # Submit a pattern that should yield INTJ
        responses = [
            2, 1, 2, 1,  # E_I - Introversion
            4, 5, 4, 5,  # S_N - Intuition
            5, 4, 5, 4,  # T_F - Thinking
            5, 5, 4, 5   # J_P - Judging
        ]
        
        for response in responses:
            self.engine.submit_response(response)
        
        results = self.engine.calculate_results()
        
        self.assertIn('mbti_type', results)
        self.assertIn('confidence', results)
        self.assertIn('dimension_scores', results)
        self.assertIn('personality_analysis', results)
        self.assertIn('test_metadata', results)
        
        # Should be INTJ based on responses
        self.assertEqual(results['mbti_type'], 'INTJ')
    
    def test_validate_responses(self):
        """Test response validation."""
        self.engine.initialize_test('short')
        
        # Submit valid mixed responses
        for i in range(16):
            value = (i % 5) + 1  # Cycles through 1-5
            self.engine.submit_response(value)
        
        is_valid, message = self.engine.validate_responses()
        
        self.assertTrue(is_valid)
        self.assertIn('valid', message.lower())
    
    def test_validate_responses_straight_lining(self):
        """Test detection of straight-lining in responses."""
        self.engine.initialize_test('short')
        
        # Submit all same responses
        for _ in range(16):
            self.engine.submit_response(3)
        
        is_valid, message = self.engine.validate_responses()
        
        self.assertFalse(is_valid)
        self.assertIn('identical', message.lower())
    
    def test_resume_test(self):
        """Test resuming a previous test."""
        # Initialize and partially complete a test
        original_session_id = self.engine.initialize_test('short')
        
        # Submit some responses
        for i in range(8):
            self.engine.submit_response(3)
        
        # Create new engine instance
        new_engine = TestEngine()
        
        # Resume the test
        success = new_engine.resume_test(original_session_id)
        
        self.assertTrue(success)
        self.assertEqual(new_engine.test_length, 'short')
        self.assertEqual(new_engine.current_index, 8)
        self.assertTrue(new_engine.is_resuming)
        
        # Should have reloaded responses
        self.assertEqual(len(new_engine.scorer.responses), 8)
    
    def test_resume_nonexistent_session(self):
        """Test attempting to resume non-existent session."""
        result = self.engine.resume_test('nonexistent_id')
        
        self.assertFalse(result)
    
    def test_get_available_sessions(self):
        """Test getting list of resumable sessions."""
        # Create multiple sessions
        engine1 = TestEngine()
        session1 = engine1.initialize_test('short')
        engine1.submit_response(3)
        
        engine2 = TestEngine()
        session2 = engine2.initialize_test('medium')
        engine2.submit_response(4)
        
        # Get available sessions
        sessions = self.engine.get_available_sessions()
        
        self.assertEqual(len(sessions), 2)
        
        # Verify session details
        session_ids = [s['id'] for s in sessions]
        self.assertIn(session1, session_ids)
        self.assertIn(session2, session_ids)
    
    def test_cleanup_old_sessions(self):
        """Test cleanup functionality."""
        # This should run without errors
        self.engine.cleanup_old_sessions()
        
        # Verify it doesn't affect current session
        self.engine.initialize_test('short')
        self.engine.submit_response(3)
        
        self.engine.cleanup_old_sessions()
        
        # Current session should still be intact
        self.assertEqual(len(self.engine.scorer.responses), 1)
    
    def test_export_results(self):
        """Test exporting results."""
        # Set up export directory
        export_dir = self.temp_dir / 'exports'
        SETTINGS['export_directory'] = export_dir
        
        self.engine.initialize_test('short')
        
        # Complete test
        for _ in range(16):
            self.engine.submit_response(3)
        
        # Calculate results
        self.engine.calculate_results()
        
        # Export
        export_path = self.engine.export_results('json')
        
        self.assertIsNotNone(export_path)
        self.assertTrue(Path(export_path).exists())
    
    def test_question_distribution(self):
        """Test that questions are properly distributed across dimensions."""
        for test_type in ['short', 'medium', 'long']:
            self.engine.initialize_test(test_type)
            
            # Count questions per dimension
            dimension_counts = {}
            for q in self.engine.questions:
                dim = q['dimension']
                dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
            
            # All dimensions should have equal questions
            expected_per_dim = TEST_CONFIGS[test_type]['questions_per_dimension']
            for dim, count in dimension_counts.items():
                self.assertEqual(
                    count, 
                    expected_per_dim,
                    f"Dimension {dim} has {count} questions, expected {expected_per_dim} in {test_type} test"
                )
    
    def test_complete_test_flow(self):
        """Test complete flow from start to results."""
        # Initialize
        session_id = self.engine.initialize_test('short')
        self.assertIsNotNone(session_id)
        
        # Answer all questions
        responses = [3, 4, 2, 5, 1, 3, 4, 2, 5, 1, 3, 4, 2, 5, 1, 3]
        
        for i, response in enumerate(responses):
            # Get current question
            question = self.engine.get_current_question()
            self.assertIsNotNone(question, f"Question {i} should exist")
            
            # Submit response
            success = self.engine.submit_response(response)
            self.assertTrue(success, f"Response {i} should be accepted")
        
        # Should be complete
        self.assertTrue(self.engine.is_complete())
        
        # Calculate results
        results = self.engine.calculate_results()
        
        # Verify results structure
        self.assertIn('mbti_type', results)
        self.assertEqual(len(results['mbti_type']), 4)
        self.assertIn('confidence', results)
        self.assertGreater(results['confidence'], 0)
        self.assertLessEqual(results['confidence'], 100)


if __name__ == '__main__':
    unittest.main()