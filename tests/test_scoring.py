"""
Comprehensive tests for the MBTI scoring algorithm.
These tests verify the accuracy and reliability of personality type determination.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scoring import MBTIScorer, ResultAnalyzer


class TestMBTIScorer(unittest.TestCase):
    """Test the MBTI scoring engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = MBTIScorer()
        
    def tearDown(self):
        """Clean up after tests."""
        self.scorer.reset()
    
    def test_scorer_initialization(self):
        """Test that scorer initializes correctly."""
        self.assertEqual(len(self.scorer.responses), 0)
        self.assertEqual(len(self.scorer.dimension_scores), 0)
        self.assertIsNotNone(self.scorer.dimensions)
        self.assertEqual(len(self.scorer.dimensions), 4)
    
    def test_add_response(self):
        """Test adding responses to the scorer."""
        question_data = {
            'id': 'E_I_001',
            'dimension': 'E_I',
            'reverse_coded': False
        }
        
        self.scorer.add_response('E_I_001', question_data, 5)
        
        self.assertEqual(len(self.scorer.responses), 1)
        self.assertIn('E_I_001', self.scorer.responses)
        self.assertEqual(self.scorer.responses['E_I_001']['value'], 5)
        self.assertEqual(self.scorer.responses['E_I_001']['dimension'], 'E_I')
    
    def test_reverse_coded_questions(self):
        """Test that reverse-coded questions are handled correctly."""
        # Add normal question (high value = extraversion)
        normal_q = {'id': 'E_I_001', 'dimension': 'E_I', 'reverse_coded': False}
        self.scorer.add_response('E_I_001', normal_q, 5)
        
        # Add reverse-coded question (high value = introversion)
        reverse_q = {'id': 'E_I_002', 'dimension': 'E_I', 'reverse_coded': True}
        self.scorer.add_response('E_I_002', reverse_q, 5)
        
        # Calculate dimension score
        score = self.scorer.calculate_dimension_score('E_I')
        
        # With one max E and one max I, should be balanced (50%)
        self.assertAlmostEqual(score['right_score'], 50.0, places=1)
        self.assertAlmostEqual(score['left_score'], 50.0, places=1)
        self.assertTrue(score['is_borderline'])
    
    def test_strong_preference_calculation(self):
        """Test calculation of strong preferences."""
        # Add multiple responses favoring extraversion
        for i in range(5):
            q = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.scorer.add_response(f'E_I_{i:03d}', q, 5)  # Strong extraversion
        
        score = self.scorer.calculate_dimension_score('E_I')
        
        self.assertEqual(score['preference'], 'E')
        self.assertGreater(score['strength'], 90)  # Should be very high
        self.assertFalse(score['is_borderline'])
        self.assertEqual(score['response_count'], 5)
    
    def test_weak_preference_calculation(self):
        """Test calculation of weak/borderline preferences."""
        # Add responses that are mostly neutral
        questions = [
            {'id': 'E_I_001', 'dimension': 'E_I', 'reverse_coded': False, 'value': 3},
            {'id': 'E_I_002', 'dimension': 'E_I', 'reverse_coded': False, 'value': 3},
            {'id': 'E_I_003', 'dimension': 'E_I', 'reverse_coded': False, 'value': 4},
            {'id': 'E_I_004', 'dimension': 'E_I', 'reverse_coded': False, 'value': 2},
        ]
        
        for q in questions:
            self.scorer.add_response(q['id'], q, q['value'])
        
        score = self.scorer.calculate_dimension_score('E_I')
        
        # Should be close to 50%
        self.assertLess(abs(score['right_score'] - 50), 10)
        self.assertTrue(score['is_borderline'])
    
    def test_mbti_type_determination(self):
        """Test complete MBTI type determination."""
        # Create a clear INTJ profile
        dimensions_responses = {
            'E_I': [1, 2, 1, 2],  # Clear introversion
            'S_N': [4, 5, 5, 4],  # Clear intuition
            'T_F': [5, 4, 5, 4],  # Clear thinking
            'J_P': [5, 5, 4, 5],  # Clear judging
        }
        
        for dim, values in dimensions_responses.items():
            for i, value in enumerate(values):
                q = {'id': f'{dim}_{i:03d}', 'dimension': dim, 'reverse_coded': False}
                self.scorer.add_response(f'{dim}_{i:03d}', q, value)
        
        result = self.scorer.determine_mbti_type()
        
        self.assertEqual(result['type'], 'INTJ')
        self.assertGreater(result['confidence'], 60)
        self.assertEqual(len(result['dimension_details']), 4)
        self.assertEqual(result['total_responses'], 16)
    
    def test_borderline_type_with_secondary(self):
        """Test handling of borderline cases with secondary type."""
        # Create a profile with borderline E/I
        dimensions_responses = {
            'E_I': [3, 3, 3, 3],  # Borderline
            'S_N': [5, 5, 5, 5],  # Clear N
            'T_F': [5, 5, 5, 5],  # Clear T
            'J_P': [5, 5, 5, 5],  # Clear J
        }
        
        for dim, values in dimensions_responses.items():
            for i, value in enumerate(values):
                q = {'id': f'{dim}_{i:03d}', 'dimension': dim, 'reverse_coded': False}
                self.scorer.add_response(f'{dim}_{i:03d}', q, value)
        
        result = self.scorer.determine_mbti_type()
        
        # Should identify borderline dimension
        self.assertGreater(len(result['borderline_dimensions']), 0)
        self.assertIn('Extraversion/Introversion', 
                     result['borderline_dimensions'][0]['dimension'])
    
    def test_all_dimensions_calculation(self):
        """Test calculation of all dimensions at once."""
        # Add responses for all dimensions
        test_data = [
            ('E_I_001', 'E_I', 5),
            ('S_N_001', 'S_N', 2),
            ('T_F_001', 'T_F', 4),
            ('J_P_001', 'J_P', 3),
        ]
        
        for qid, dim, value in test_data:
            q = {'id': qid, 'dimension': dim, 'reverse_coded': False}
            self.scorer.add_response(qid, q, value)
        
        all_scores = self.scorer.calculate_all_dimensions()
        
        self.assertEqual(len(all_scores), 4)
        self.assertIn('E_I', all_scores)
        self.assertIn('S_N', all_scores)
        self.assertIn('T_F', all_scores)
        self.assertIn('J_P', all_scores)
    
    def test_empty_dimension_handling(self):
        """Test handling of dimensions with no responses."""
        # Add responses only for E_I
        q = {'id': 'E_I_001', 'dimension': 'E_I', 'reverse_coded': False}
        self.scorer.add_response('E_I_001', q, 5)
        
        # Try to calculate S_N with no data
        score = self.scorer.calculate_dimension_score('S_N')
        
        self.assertEqual(score['preference'], 'X')  # Unknown
        self.assertEqual(score['strength'], 50.0)
        self.assertTrue(score['is_borderline'])
        self.assertEqual(score['response_count'], 0)
    
    def test_scorer_reset(self):
        """Test that reset clears all data."""
        # Add some responses
        q = {'id': 'E_I_001', 'dimension': 'E_I', 'reverse_coded': False}
        self.scorer.add_response('E_I_001', q, 5)
        self.scorer.calculate_all_dimensions()
        
        # Reset
        self.scorer.reset()
        
        self.assertEqual(len(self.scorer.responses), 0)
        self.assertEqual(len(self.scorer.dimension_scores), 0)
    
    def test_extreme_scores(self):
        """Test handling of extreme scores (all 1s or all 5s)."""
        # Test all 1s (extreme introversion)
        for i in range(4):
            q = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.scorer.add_response(f'E_I_{i:03d}', q, 1)
        
        score = self.scorer.calculate_dimension_score('E_I')
        
        self.assertEqual(score['preference'], 'I')
        self.assertEqual(score['strength'], 100.0)
        self.assertEqual(score['right_score'], 0.0)
        
        # Reset and test all 5s (extreme extraversion)
        self.scorer.reset()
        for i in range(4):
            q = {'id': f'E_I_{i:03d}', 'dimension': 'E_I', 'reverse_coded': False}
            self.scorer.add_response(f'E_I_{i:03d}', q, 5)
        
        score = self.scorer.calculate_dimension_score('E_I')
        
        self.assertEqual(score['preference'], 'E')
        self.assertEqual(score['strength'], 100.0)
        self.assertEqual(score['right_score'], 100.0)


class TestResultAnalyzer(unittest.TestCase):
    """Test the result analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        data_path = Path(__file__).parent.parent / 'data' / 'personality_types.json'
        self.analyzer = ResultAnalyzer(data_path)
    
    def test_type_analysis_retrieval(self):
        """Test retrieving analysis for a valid type."""
        dimension_scores = {
            'E_I': {'preference': 'I', 'strength': 70, 'preferred_label': 'Introversion'},
            'S_N': {'preference': 'N', 'strength': 65, 'preferred_label': 'Intuition'},
            'T_F': {'preference': 'T', 'strength': 75, 'preferred_label': 'Thinking'},
            'J_P': {'preference': 'J', 'strength': 80, 'preferred_label': 'Judging'},
        }
        
        analysis = self.analyzer.get_type_analysis('INTJ', dimension_scores)
        
        self.assertEqual(analysis['type'], 'INTJ')
        self.assertEqual(analysis['title'], 'The Architect')
        self.assertIn('strengths', analysis)
        self.assertIn('weaknesses', analysis)
        self.assertIn('career_matches', analysis)
        self.assertIsInstance(analysis['strengths'], list)
        self.assertGreater(len(analysis['strengths']), 0)
    
    def test_invalid_type_handling(self):
        """Test handling of invalid personality type."""
        analysis = self.analyzer.get_type_analysis('XXXX', {})
        
        self.assertIn('error', analysis)
        self.assertIn('Unknown personality type', analysis['error'])
    
    def test_strength_analysis(self):
        """Test analysis of dimension strengths."""
        dimension_scores = {
            'E_I': {
                'preference': 'E', 
                'strength': 85, 
                'preferred_label': 'Extraversion',
                'left_label': 'Introversion',
                'right_label': 'Extraversion',
                'is_borderline': False
            },
            'S_N': {
                'preference': 'N', 
                'strength': 51, 
                'preferred_label': 'Intuition',
                'left_label': 'Sensing',
                'right_label': 'Intuition',
                'is_borderline': True
            },
            'T_F': {
                'preference': 'T', 
                'strength': 65, 
                'preferred_label': 'Thinking',
                'left_label': 'Feeling',
                'right_label': 'Thinking',
                'is_borderline': False
            },
            'J_P': {
                'preference': 'J', 
                'strength': 70, 
                'preferred_label': 'Judging',
                'left_label': 'Perceiving',
                'right_label': 'Judging',
                'is_borderline': False
            }
        }
        
        analysis = self.analyzer.get_type_analysis('ENTJ', dimension_scores)
        
        self.assertIn('dimension_analysis', analysis)
        insights = analysis['dimension_analysis']
        
        # Check that strong preferences are identified
        strong_insights = [i for i in insights if 'Strong' in i]
        self.assertGreater(len(strong_insights), 0)
        
        # Check that borderline is identified
        borderline_insights = [i for i in insights if 'Balanced' in i]
        self.assertGreater(len(borderline_insights), 0)


if __name__ == '__main__':
    unittest.main()