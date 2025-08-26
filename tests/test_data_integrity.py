"""
Tests for data file integrity and completeness.
These tests verify that all data files are properly formatted and contain valid data.
"""

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validator import ResponseValidator
from config.settings import DIMENSIONS


class TestDataIntegrity(unittest.TestCase):
    """Test the integrity of data files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.validator = ResponseValidator()
    
    def test_data_directory_exists(self):
        """Test that data directory exists."""
        self.assertTrue(self.data_dir.exists())
        self.assertTrue(self.data_dir.is_dir())
    
    def test_required_files_exist(self):
        """Test that all required data files exist."""
        required_files = [
            'questions.json',
            'personality_types.json',
            'cognitive_functions.json'
        ]
        
        for filename in required_files:
            filepath = self.data_dir / filename
            self.assertTrue(
                filepath.exists(),
                f"Required file {filename} does not exist"
            )
    
    def test_questions_file_structure(self):
        """Test that questions.json has valid structure."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        self.assertIn('questions', data)
        self.assertIsInstance(data['questions'], list)
        self.assertGreater(len(data['questions']), 0)
    
    def test_questions_total_count(self):
        """Test that we have exactly 88 questions."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['questions']), 88)
    
    def test_questions_dimension_distribution(self):
        """Test that questions are evenly distributed across dimensions."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        dimension_counts = {}
        for question in data['questions']:
            dim = question['dimension']
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        # Should have 22 questions per dimension
        for dim in ['E_I', 'S_N', 'T_F', 'J_P']:
            self.assertEqual(
                dimension_counts.get(dim, 0),
                22,
                f"Dimension {dim} should have 22 questions"
            )
    
    def test_questions_priority_distribution(self):
        """Test that questions have proper priority distribution."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        # Count priorities per dimension
        for dim in ['E_I', 'S_N', 'T_F', 'J_P']:
            dim_questions = [q for q in data['questions'] if q['dimension'] == dim]
            
            priority_counts = {}
            for q in dim_questions:
                p = q['priority']
                priority_counts[p] = priority_counts.get(p, 0) + 1
            
            # Each dimension should have questions at all priority levels
            self.assertIn(1, priority_counts, f"Dimension {dim} missing priority 1 questions")
            self.assertIn(2, priority_counts, f"Dimension {dim} missing priority 2 questions")
            self.assertIn(3, priority_counts, f"Dimension {dim} missing priority 3 questions")
            
            # Should have at least 4 priority 1 questions (for short test)
            self.assertGreaterEqual(
                priority_counts[1],
                4,
                f"Dimension {dim} needs at least 4 priority 1 questions"
            )
    
    def test_each_question_validity(self):
        """Test that each question has valid structure and data."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        for i, question in enumerate(data['questions']):
            # Validate using validator
            is_valid, message = self.validator.validate_question_data(question)
            self.assertTrue(
                is_valid,
                f"Question {i} ({question.get('id', 'unknown')}): {message}"
            )
            
            # Additional checks
            self.assertIsInstance(question['text'], str)
            self.assertGreaterEqual(len(question['text']), 10, "Question text too short")
            self.assertIn('reverse_coded', question)
            self.assertIsInstance(question['reverse_coded'], bool)
    
    def test_question_ids_unique(self):
        """Test that all question IDs are unique."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        ids = [q['id'] for q in data['questions']]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate question IDs found")
    
    def test_question_options_valid(self):
        """Test that all question options are valid."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        for question in data['questions']:
            options = question['options']
            
            # Should have exactly 5 options
            self.assertEqual(len(options), 5)
            
            # Check values are 1-5
            values = [opt['value'] for opt in options]
            self.assertEqual(sorted(values), [1, 2, 3, 4, 5])
            
            # Each option should have text
            for opt in options:
                self.assertIn('text', opt)
                self.assertIsInstance(opt['text'], str)
                self.assertGreater(len(opt['text']), 0)
    
    def test_personality_types_structure(self):
        """Test that personality_types.json has valid structure."""
        with open(self.data_dir / 'personality_types.json') as f:
            data = json.load(f)
        
        # Should have exactly 16 types
        self.assertEqual(len(data), 16)
        
        # Check all 16 types are present
        expected_types = [
            'INTJ', 'INTP', 'ENTJ', 'ENTP',
            'INFJ', 'INFP', 'ENFJ', 'ENFP',
            'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
            'ISTP', 'ISFP', 'ESTP', 'ESFP'
        ]
        
        for type_code in expected_types:
            self.assertIn(type_code, data, f"Missing personality type: {type_code}")
    
    def test_each_personality_type_complete(self):
        """Test that each personality type has all required fields."""
        with open(self.data_dir / 'personality_types.json') as f:
            data = json.load(f)
        
        required_fields = [
            'title', 'overview', 'strengths', 'weaknesses',
            'career_matches', 'cognitive_stack', 'famous_examples',
            'relationship_style'
        ]
        
        for type_code, type_data in data.items():
            for field in required_fields:
                self.assertIn(
                    field,
                    type_data,
                    f"Type {type_code} missing field: {field}"
                )
            
            # Check list fields have content
            self.assertGreater(len(type_data['strengths']), 0)
            self.assertGreater(len(type_data['weaknesses']), 0)
            self.assertGreater(len(type_data['career_matches']), 0)
            self.assertGreater(len(type_data['famous_examples']), 0)
            
            # Check text fields have content
            self.assertGreater(len(type_data['title']), 0)
            self.assertGreater(len(type_data['overview']), 20)
            self.assertGreater(len(type_data['relationship_style']), 20)
    
    def test_cognitive_functions_structure(self):
        """Test that cognitive_functions.json has valid structure."""
        with open(self.data_dir / 'cognitive_functions.json') as f:
            data = json.load(f)
        
        self.assertIn('functions', data)
        self.assertIn('stacks', data)
        
        # Should have 8 cognitive functions
        self.assertEqual(len(data['functions']), 8)
        
        # Should have stacks for all 16 types
        self.assertEqual(len(data['stacks']), 16)
    
    def test_cognitive_functions_complete(self):
        """Test that cognitive functions have all required data."""
        with open(self.data_dir / 'cognitive_functions.json') as f:
            data = json.load(f)
        
        expected_functions = ['Ni', 'Ne', 'Si', 'Se', 'Ti', 'Te', 'Fi', 'Fe']
        
        for func in expected_functions:
            self.assertIn(func, data['functions'])
            func_data = data['functions'][func]
            
            self.assertIn('name', func_data)
            self.assertIn('description', func_data)
            self.assertIn('characteristics', func_data)
            
            self.assertIsInstance(func_data['characteristics'], list)
            self.assertGreater(len(func_data['characteristics']), 0)
    
    def test_cognitive_stacks_valid(self):
        """Test that cognitive stacks are valid for each type."""
        with open(self.data_dir / 'cognitive_functions.json') as f:
            data = json.load(f)
        
        for type_code, stack in data['stacks'].items():
            # Should have exactly 4 functions
            self.assertEqual(len(stack), 4, f"Type {type_code} should have 4 functions")
            
            # All functions should be valid
            for func in stack:
                self.assertIn(
                    func,
                    data['functions'],
                    f"Invalid function {func} in {type_code} stack"
                )
    
    def test_no_duplicate_questions_text(self):
        """Test that no questions have duplicate text."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        texts = [q['text'] for q in data['questions']]
        unique_texts = set(texts)
        
        if len(texts) != len(unique_texts):
            # Find duplicates for better error message
            seen = set()
            duplicates = set()
            for text in texts:
                if text in seen:
                    duplicates.add(text)
                seen.add(text)
            
            self.fail(f"Duplicate question texts found: {duplicates}")
    
    def test_personality_types_cognitive_stack_format(self):
        """Test that cognitive stacks in personality types are properly formatted."""
        with open(self.data_dir / 'personality_types.json') as f:
            data = json.load(f)
        
        for type_code, type_data in data.items():
            stack = type_data['cognitive_stack']
            
            # Should have all four positions
            self.assertIn('dominant', stack)
            self.assertIn('auxiliary', stack)
            self.assertIn('tertiary', stack)
            self.assertIn('inferior', stack)
            
            # Each should have function code and description
            for position in ['dominant', 'auxiliary', 'tertiary', 'inferior']:
                value = stack[position]
                self.assertIsInstance(value, str)
                # Should contain function code (e.g., "Ni", "Te")
                self.assertTrue(
                    any(func in value for func in ['Ni', 'Ne', 'Si', 'Se', 'Ti', 'Te', 'Fi', 'Fe']),
                    f"Type {type_code} {position} function missing code"
                )
    
    def test_json_files_valid(self):
        """Test that all JSON files are valid JSON."""
        json_files = list(self.data_dir.glob('*.json'))
        
        for filepath in json_files:
            try:
                with open(filepath) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in {filepath.name}: {e}")
    
    def test_question_types_valid(self):
        """Test that question types are consistent."""
        with open(self.data_dir / 'questions.json') as f:
            data = json.load(f)
        
        # Collect all question types
        types = set(q['type'] for q in data['questions'])
        
        # Should have various question types
        self.assertGreater(len(types), 3, "Should have at least 4 different question types")
        
        # All types should be meaningful strings
        for q_type in types:
            self.assertIsInstance(q_type, str)
            self.assertGreater(len(q_type), 0)


if __name__ == '__main__':
    unittest.main()