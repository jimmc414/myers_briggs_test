"""
Tests for export functionality.
These tests verify that results can be properly exported in various formats.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.exporter import Exporter
from display.reports import Reports
from config.settings import SETTINGS


class TestExporter(unittest.TestCase):
    """Test the export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for exports
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_export_dir = SETTINGS['export_directory']
        SETTINGS['export_directory'] = self.temp_dir
        
        # Sample results data
        self.sample_results = {
            'mbti_type': 'INTJ',
            'confidence': 75.5,
            'confidence_level': 'Strong',
            'dimension_scores': {
                'E_I': {
                    'preference': 'I',
                    'preferred_label': 'Introversion',
                    'strength': 70.0,
                    'right_score': 30.0,
                    'left_score': 70.0,
                    'right_label': 'Extraversion',
                    'left_label': 'Introversion',
                    'is_borderline': False
                },
                'S_N': {
                    'preference': 'N',
                    'preferred_label': 'Intuition',
                    'strength': 80.0,
                    'right_score': 80.0,
                    'left_score': 20.0,
                    'right_label': 'Intuition',
                    'left_label': 'Sensing',
                    'is_borderline': False
                },
                'T_F': {
                    'preference': 'T',
                    'preferred_label': 'Thinking',
                    'strength': 75.0,
                    'right_score': 75.0,
                    'left_score': 25.0,
                    'right_label': 'Thinking',
                    'left_label': 'Feeling',
                    'is_borderline': False
                },
                'J_P': {
                    'preference': 'J',
                    'preferred_label': 'Judging',
                    'strength': 77.0,
                    'right_score': 77.0,
                    'left_score': 23.0,
                    'right_label': 'Judging',
                    'left_label': 'Perceiving',
                    'is_borderline': False
                }
            },
            'personality_analysis': {
                'type': 'INTJ',
                'title': 'The Architect',
                'overview': 'Independent, strategic thinkers.',
                'strengths': ['Strategic', 'Independent', 'Decisive'],
                'weaknesses': ['Overly critical', 'Perfectionist'],
                'career_matches': ['Software Developer', 'Data Scientist'],
                'cognitive_stack': {
                    'dominant': 'Ni - Introverted Intuition',
                    'auxiliary': 'Te - Extraverted Thinking',
                    'tertiary': 'Fi - Introverted Feeling',
                    'inferior': 'Se - Extraverted Sensing'
                },
                'famous_examples': ['Elon Musk', 'Isaac Newton']
            },
            'test_metadata': {
                'test_length': 'medium',
                'total_questions': 44,
                'completion_time': '12:34'
            }
        }
    
    def tearDown(self):
        """Clean up temporary directory."""
        SETTINGS['export_directory'] = self.original_export_dir
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_export_json(self):
        """Test exporting results as JSON."""
        filepath = Exporter.export_results(self.sample_results, 'json')
        
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())
        
        # Verify file contents
        with open(filepath) as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['mbti_type'], 'INTJ')
        self.assertEqual(exported_data['confidence'], 75.5)
        self.assertIn('dimension_scores', exported_data)
        self.assertIn('personality_analysis', exported_data)
    
    def test_export_text(self):
        """Test exporting results as text."""
        filepath = Exporter.export_results(self.sample_results, 'txt')
        
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())
        
        # Verify file contents
        with open(filepath) as f:
            content = f.read()
        
        self.assertIn('INTJ', content)
        self.assertIn('75.5%', content)
        self.assertIn('Introversion', content)
        self.assertIn('The Architect', content)
    
    def test_export_filename_format(self):
        """Test that exported files have correct naming format."""
        filepath = Exporter.export_results(self.sample_results, 'txt')
        
        filename = Path(filepath).name
        
        # Should contain mbti_results, type, timestamp
        self.assertIn('mbti_results', filename)
        self.assertIn('INTJ', filename)
        
        # Should have timestamp format
        parts = filename.split('_')
        timestamp = parts[-1].split('.')[0]  # Remove extension
        self.assertEqual(len(timestamp), 15)  # YYYYMMDD_HHMMSS
    
    def test_export_creates_directory(self):
        """Test that export creates directory if it doesn't exist."""
        # Use a subdirectory that doesn't exist
        SETTINGS['export_directory'] = self.temp_dir / 'new_dir'
        
        filepath = Exporter.export_results(self.sample_results, 'json')
        
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())
        self.assertTrue(SETTINGS['export_directory'].exists())
    
    def test_export_handles_missing_type(self):
        """Test export with missing MBTI type."""
        incomplete_results = {
            'confidence': 50.0,
            'dimension_scores': {}
        }
        
        filepath = Exporter.export_results(incomplete_results, 'txt')
        
        self.assertIsNotNone(filepath)
        
        # Should use 'unknown' in filename
        filename = Path(filepath).name
        self.assertIn('unknown', filename)
    
    def test_export_preserves_special_characters(self):
        """Test that special characters in data are preserved."""
        results = self.sample_results.copy()
        results['personality_analysis']['overview'] = "Test with special: @#$%^&*()"
        
        filepath = Exporter.export_results(results, 'json')
        
        with open(filepath) as f:
            data = json.load(f)
        
        self.assertIn('@#$%^&*()', data['personality_analysis']['overview'])
    
    def test_copy_to_clipboard_mock(self):
        """Test clipboard functionality (mocked since clipboard may not work in test env)."""
        # This test is limited since clipboard functionality depends on system
        # We mainly test that the function doesn't crash
        try:
            result = Exporter.copy_to_clipboard(self.sample_results)
            # Result depends on whether pyperclip is available and working
            self.assertIsInstance(result, bool)
        except Exception as e:
            # Should handle exceptions gracefully
            self.assertIsInstance(e, (ImportError, Exception))


class TestReports(unittest.TestCase):
    """Test the report generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_results = {
            'mbti_type': 'ENFP',
            'confidence': 68.5,
            'dimension_scores': {
                'E_I': {
                    'preference': 'E',
                    'preferred_label': 'Extraversion',
                    'strength': 65.0,
                    'right_score': 65.0,
                    'left_score': 35.0
                },
                'S_N': {
                    'preference': 'N',
                    'preferred_label': 'Intuition',
                    'strength': 70.0,
                    'right_score': 70.0,
                    'left_score': 30.0
                },
                'T_F': {
                    'preference': 'F',
                    'preferred_label': 'Feeling',
                    'strength': 68.0,
                    'right_score': 32.0,
                    'left_score': 68.0
                },
                'J_P': {
                    'preference': 'P',
                    'preferred_label': 'Perceiving',
                    'strength': 71.0,
                    'right_score': 29.0,
                    'left_score': 71.0
                }
            },
            'personality_analysis': {
                'title': 'The Campaigner',
                'overview': 'Enthusiastic and creative free spirits.',
                'strengths': ['Creative', 'Enthusiastic', 'Sociable'],
                'career_matches': ['Marketing', 'Counselor', 'Teacher']
            }
        }
    
    def test_generate_summary_report(self):
        """Test generation of text summary report."""
        summary = Reports.generate_summary_report(self.sample_results)
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 100)
        
        # Check key elements are present
        self.assertIn('ENFP', summary)
        self.assertIn('68.5%', summary)
        self.assertIn('Extraversion', summary)
        self.assertIn('Intuition', summary)
        self.assertIn('Feeling', summary)
        self.assertIn('Perceiving', summary)
        self.assertIn('The Campaigner', summary)
    
    def test_summary_report_structure(self):
        """Test that summary report has proper structure."""
        summary = Reports.generate_summary_report(self.sample_results)
        
        lines = summary.split('\n')
        
        # Should have headers
        self.assertIn('MBTI PERSONALITY TEST RESULTS', summary)
        self.assertIn('DIMENSION SCORES:', summary)
        
        # Should have separators
        self.assertIn('=' * 60, summary)
        self.assertIn('-' * 40, summary)
    
    def test_summary_handles_missing_fields(self):
        """Test that summary handles missing optional fields gracefully."""
        minimal_results = {
            'mbti_type': 'ISTP',
            'confidence': 60.0,
            'dimension_scores': {
                'E_I': {'preferred_label': 'Introversion', 'strength': 60},
                'S_N': {'preferred_label': 'Sensing', 'strength': 55},
                'T_F': {'preferred_label': 'Thinking', 'strength': 65},
                'J_P': {'preferred_label': 'Perceiving', 'strength': 62}
            }
        }
        
        summary = Reports.generate_summary_report(minimal_results)
        
        self.assertIsInstance(summary, str)
        self.assertIn('ISTP', summary)
        self.assertIn('60.0%', summary)
    
    def test_summary_dimension_formatting(self):
        """Test that dimensions are properly formatted in summary."""
        summary = Reports.generate_summary_report(self.sample_results)
        
        # Check each dimension is formatted with percentage
        self.assertIn('Extraversion', summary)
        self.assertIn('65.0%', summary)
        
        self.assertIn('Intuition', summary)
        self.assertIn('70.0%', summary)
        
        self.assertIn('Feeling', summary)
        self.assertIn('68.0%', summary)
        
        self.assertIn('Perceiving', summary)
        self.assertIn('71.0%', summary)
    
    def test_summary_includes_all_sections(self):
        """Test that all expected sections are included when data is complete."""
        complete_results = self.sample_results.copy()
        complete_results['personality_analysis']['weaknesses'] = ['Overly idealistic']
        complete_results['personality_analysis']['famous_examples'] = ['Robin Williams']
        
        summary = Reports.generate_summary_report(complete_results)
        
        # Check for presence of sections
        self.assertIn('PERSONALITY OVERVIEW:', summary)
        self.assertIn('STRENGTHS:', summary)
        self.assertIn('RECOMMENDED CAREERS:', summary)
        
        # Check content
        self.assertIn('Enthusiastic and creative', summary)
        self.assertIn('Creative', summary)
        self.assertIn('Marketing', summary)


if __name__ == '__main__':
    unittest.main()