"""
Tests for response validation and data integrity checks.
These tests ensure that user inputs are properly validated and sanitized.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validator import ResponseValidator


class TestResponseValidator(unittest.TestCase):
    """Test the response validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ResponseValidator()
    
    def test_valid_response_values(self):
        """Test validation of valid response values."""
        valid_values = [1, 2, 3, 4, 5]
        
        for value in valid_values:
            self.assertTrue(self.validator.validate_response(value))
    
    def test_invalid_response_values(self):
        """Test rejection of invalid response values."""
        invalid_values = [0, 6, -1, 10, 100]
        
        for value in invalid_values:
            with self.assertRaises(ValueError) as context:
                self.validator.validate_response(value)
            self.assertIn("between 1-5", str(context.exception))
    
    def test_non_integer_response(self):
        """Test rejection of non-integer responses."""
        invalid_types = ["5", 3.5, None, [], {}]
        
        for value in invalid_types:
            with self.assertRaises(ValueError) as context:
                self.validator.validate_response(value)
            self.assertIn("must be", str(context.exception).lower())
    
    def test_consistency_check_straight_lining(self):
        """Test detection of straight-lining (all same answers)."""
        # All 3s - clear straight-lining
        responses = [{'value': 3} for _ in range(20)]
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertFalse(is_valid)
        self.assertIn("identical", message.lower())
    
    def test_consistency_check_alternating_pattern(self):
        """Test detection of alternating response patterns."""
        # Clear alternating pattern 1,5,1,5...
        responses = []
        for i in range(20):
            responses.append({'value': 1 if i % 2 == 0 else 5})
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertFalse(is_valid)
        self.assertIn("alternating", message.lower())
    
    def test_consistency_check_extreme_responses(self):
        """Test detection of too many extreme responses."""
        # 95% extreme responses
        responses = []
        for i in range(100):
            if i < 95:
                responses.append({'value': 5 if i % 2 == 0 else 1})
            else:
                responses.append({'value': 3})
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertFalse(is_valid)
        self.assertIn("extreme", message.lower())
    
    def test_consistency_check_valid_pattern(self):
        """Test acceptance of valid response patterns."""
        # Realistic mixed responses
        responses = [
            {'value': 3}, {'value': 4}, {'value': 2}, {'value': 5},
            {'value': 3}, {'value': 3}, {'value': 4}, {'value': 1},
            {'value': 4}, {'value': 3}, {'value': 5}, {'value': 2},
            {'value': 3}, {'value': 4}, {'value': 3}, {'value': 4}
        ]
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertTrue(is_valid)
        self.assertIn("valid", message.lower())
    
    def test_consistency_check_too_few_responses(self):
        """Test handling of too few responses for consistency check."""
        responses = [{'value': 3}, {'value': 4}]
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertTrue(is_valid)  # Should pass with too few to check
        self.assertIn("too few", message.lower())
    
    def test_consistency_check_empty_responses(self):
        """Test handling of empty response list."""
        responses = []
        
        is_valid, message = self.validator.check_consistency(responses)
        
        self.assertFalse(is_valid)
        self.assertIn("no responses", message.lower())
    
    def test_validate_question_data_valid(self):
        """Test validation of properly structured question data."""
        valid_question = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'text': 'Test question?',
            'type': 'situational',
            'priority': 1,
            'options': [
                {'text': 'Option 1', 'value': 1},
                {'text': 'Option 2', 'value': 2},
                {'text': 'Option 3', 'value': 3},
                {'text': 'Option 4', 'value': 4},
                {'text': 'Option 5', 'value': 5}
            ]
        }
        
        is_valid, message = self.validator.validate_question_data(valid_question)
        
        self.assertTrue(is_valid)
        self.assertIn("valid", message.lower())
    
    def test_validate_question_missing_fields(self):
        """Test detection of missing required fields."""
        incomplete_question = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            # Missing: text, type, priority, options
        }
        
        is_valid, message = self.validator.validate_question_data(incomplete_question)
        
        self.assertFalse(is_valid)
        self.assertIn("missing", message.lower())
    
    def test_validate_question_invalid_dimension(self):
        """Test detection of invalid dimension."""
        question = {
            'id': 'X_Y_001',
            'dimension': 'X_Y',  # Invalid dimension
            'text': 'Test',
            'type': 'test',
            'priority': 1,
            'options': [{'text': 'A', 'value': i} for i in range(1, 6)]
        }
        
        is_valid, message = self.validator.validate_question_data(question)
        
        self.assertFalse(is_valid)
        self.assertIn("invalid dimension", message.lower())
    
    def test_validate_question_invalid_priority(self):
        """Test detection of invalid priority."""
        question = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'text': 'Test',
            'type': 'test',
            'priority': 5,  # Invalid (should be 1-3)
            'options': [{'text': 'A', 'value': i} for i in range(1, 6)]
        }
        
        is_valid, message = self.validator.validate_question_data(question)
        
        self.assertFalse(is_valid)
        self.assertIn("invalid priority", message.lower())
    
    def test_validate_question_invalid_options(self):
        """Test detection of invalid options structure."""
        # Wrong number of options
        question = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'text': 'Test',
            'type': 'test',
            'priority': 1,
            'options': [{'text': 'A', 'value': 1}]  # Only 1 option
        }
        
        is_valid, message = self.validator.validate_question_data(question)
        
        self.assertFalse(is_valid)
        self.assertIn("5 items", message.lower())
    
    def test_validate_test_completion_complete(self):
        """Test validation of a properly completed test."""
        responses = {
            f'{dim}_{i:03d}': {
                'dimension': dim,
                'value': 3
            }
            for dim in ['E_I', 'S_N', 'T_F', 'J_P']
            for i in range(4)
        }
        
        is_valid, message = self.validator.validate_test_completion(responses, 16)
        
        self.assertTrue(is_valid)
        self.assertIn("properly completed", message.lower())
    
    def test_validate_test_completion_incomplete(self):
        """Test detection of incomplete test."""
        responses = {
            f'E_I_{i:03d}': {'dimension': 'E_I', 'value': 3}
            for i in range(10)
        }
        
        is_valid, message = self.validator.validate_test_completion(responses, 20)
        
        self.assertFalse(is_valid)
        self.assertIn("incomplete", message.lower())
        self.assertIn("10", message)  # Should mention number remaining
    
    def test_validate_test_dimension_imbalance(self):
        """Test detection of dimension imbalance."""
        # Create very imbalanced responses
        responses = {}
        
        # 10 E_I questions
        for i in range(10):
            responses[f'E_I_{i:03d}'] = {'dimension': 'E_I', 'value': 3}
        
        # Only 2 S_N questions
        for i in range(2):
            responses[f'S_N_{i:03d}'] = {'dimension': 'S_N', 'value': 3}
        
        # 3 T_F questions
        for i in range(3):
            responses[f'T_F_{i:03d}'] = {'dimension': 'T_F', 'value': 3}
        
        # 1 J_P question
        responses['J_P_001'] = {'dimension': 'J_P', 'value': 3}
        
        is_valid, message = self.validator.validate_test_completion(responses, 16)
        
        self.assertFalse(is_valid)
        self.assertIn("imbalance", message.lower())
    
    def test_sanitize_response_string_numbers(self):
        """Test sanitization of string number inputs."""
        test_cases = [
            ("1", 1),
            ("5", 5),
            ("3", 3),
            ("1️⃣  Strongly Agree", 1),
            ("5️⃣  Strongly Disagree", 5)
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.sanitize_response(input_val)
            self.assertEqual(result, expected)
    
    def test_sanitize_response_float(self):
        """Test sanitization of float inputs."""
        test_cases = [
            (1.0, 1),
            (2.7, 3),  # Should round
            (4.4, 4),
            (5.0, 5)
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.sanitize_response(input_val)
            self.assertEqual(result, expected)
    
    def test_sanitize_response_out_of_range(self):
        """Test sanitization clamps values to valid range."""
        test_cases = [
            (0, 1),    # Below minimum
            (-5, 1),   # Way below
            (6, 5),    # Above maximum
            (100, 5)   # Way above
        ]
        
        for input_val, expected in test_cases:
            result = self.validator.sanitize_response(input_val)
            self.assertEqual(result, expected)
    
    def test_sanitize_response_invalid_string(self):
        """Test handling of unparseable strings."""
        invalid_inputs = ["abc", "test", "", "N/A"]
        
        for input_val in invalid_inputs:
            with self.assertRaises(ValueError) as context:
                self.validator.sanitize_response(input_val)
            self.assertIn("cannot parse", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()