import json
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from core.scoring import MBTIScorer, ResultAnalyzer
from core.session import SessionManager
from core.validator import ResponseValidator
from config.settings import TEST_CONFIGS, DIMENSIONS

class TestEngine:
    """Main engine for running the MBTI test."""
    
    def __init__(self, data_dir: Path = None):
        # Set data directory
        self.data_dir = data_dir or Path(__file__).parent.parent / 'data'
        
        # Load questions
        with open(self.data_dir / 'questions.json') as f:
            self.all_questions = json.load(f)['questions']
        
        # Initialize components
        self.session_manager = SessionManager()
        self.scorer = MBTIScorer()
        self.validator = ResponseValidator()
        self.result_analyzer = ResultAnalyzer(self.data_dir / 'personality_types.json')
        
        # Test state
        self.test_length = None
        self.questions = []
        self.current_index = 0
        self.is_resuming = False
    
    def initialize_test(self, test_length: str) -> str:
        """
        Initialize a new test.
        
        Args:
            test_length: Type of test (short/medium/long)
            
        Returns:
            Session ID
        """
        self.test_length = test_length
        config = TEST_CONFIGS[test_length]
        
        # Select questions based on test length
        self.questions = self._select_questions(config)
        
        # Create session
        session_id = self.session_manager.create_session(
            test_length, 
            len(self.questions)
        )
        
        self.current_index = 0
        self.scorer.reset()
        
        return session_id
    
    def _select_questions(self, config: Dict) -> List[Dict]:
        """
        Select questions based on test configuration.
        
        Args:
            config: Test configuration dictionary
            
        Returns:
            List of selected questions
        """
        selected = []
        questions_per_dim = config['questions_per_dimension']
        priorities = config['priorities']
        
        # Select questions for each dimension
        for dimension in ['E_I', 'S_N', 'T_F', 'J_P']:
            dim_questions = [
                q for q in self.all_questions 
                if q['dimension'] == dimension and q['priority'] in priorities
            ]
            
            # Sort by priority to ensure we get the most important questions
            dim_questions.sort(key=lambda x: x['priority'])
            
            # Take the required number of questions
            if len(dim_questions) >= questions_per_dim:
                selected.extend(dim_questions[:questions_per_dim])
            else:
                # If not enough questions, take what we have
                selected.extend(dim_questions)
                # Fill with lower priority questions if needed
                remaining = questions_per_dim - len(dim_questions)
                other_dim_questions = [
                    q for q in self.all_questions 
                    if q['dimension'] == dimension and q not in dim_questions
                ][:remaining]
                selected.extend(other_dim_questions)
        
        # Shuffle questions for better test experience
        # But keep some structure - group by dimension pairs
        random.shuffle(selected)
        
        return selected
    
    def resume_test(self, session_id: str) -> bool:
        """
        Resume an existing test session.
        
        Args:
            session_id: Session ID to resume
            
        Returns:
            True if successful, False otherwise
        """
        session_data = self.session_manager.resume_session(session_id)
        
        if not session_data:
            return False
        
        self.test_length = session_data['test_length']
        self.current_index = session_data['current_question']
        self.is_resuming = True
        
        # Reload questions
        config = TEST_CONFIGS[self.test_length]
        self.questions = self._select_questions(config)
        
        # Reload previous responses into scorer
        self.scorer.reset()
        for response in session_data['responses']:
            # Find the original question
            question = next(
                (q for q in self.questions if q['id'] == response['question_id']), 
                None
            )
            if question:
                self.scorer.add_response(
                    response['question_id'],
                    question,
                    response['value']
                )
        
        return True
    
    def get_current_question(self) -> Optional[Dict]:
        """
        Get the current question.
        
        Returns:
            Current question data or None if test complete
        """
        if self.current_index >= len(self.questions):
            return None
        
        return self.questions[self.current_index]
    
    def submit_response(self, response_value: int) -> bool:
        """
        Submit a response for the current question.
        
        Args:
            response_value: User's response (1-5)
            
        Returns:
            True if successful, False otherwise
        """
        # Validate response
        try:
            response_value = self.validator.sanitize_response(response_value)
            self.validator.validate_response(response_value)
        except ValueError as e:
            print(f"Invalid response: {e}")
            return False
        
        # Get current question
        question = self.get_current_question()
        if not question:
            return False
        
        # Add to scorer
        self.scorer.add_response(question['id'], question, response_value)
        
        # Save to session
        self.session_manager.add_response(question['id'], question, response_value)
        
        # Move to next question
        self.current_index += 1
        
        return True
    
    def go_back(self) -> bool:
        """
        Go back to the previous question.
        
        Returns:
            True if successful, False if at beginning
        """
        if self.current_index > 0:
            self.current_index -= 1
            self.session_manager.go_back()
            
            # Remove last response from scorer
            # This is simplified - in production would need better tracking
            return True
        
        return False
    
    def skip_question(self) -> bool:
        """
        Skip the current question.
        
        Returns:
            True if successful
        """
        # Record a neutral response (3)
        return self.submit_response(3)
    
    def is_complete(self) -> bool:
        """
        Check if the test is complete.
        
        Returns:
            True if all questions answered
        """
        return self.current_index >= len(self.questions)
    
    def get_progress(self) -> Dict:
        """
        Get current progress information.
        
        Returns:
            Progress data
        """
        progress = self.session_manager.get_progress()
        progress['questions_remaining'] = len(self.questions) - self.current_index
        
        # Add dimension progress
        dimension_progress = {}
        for dim in ['E_I', 'S_N', 'T_F', 'J_P']:
            answered = sum(
                1 for r in self.scorer.responses.values() 
                if r['dimension'] == dim
            )
            total = sum(1 for q in self.questions if q['dimension'] == dim)
            dimension_progress[dim] = {
                'answered': answered,
                'total': total,
                'name': DIMENSIONS[dim]['name']
            }
        
        progress['dimension_progress'] = dimension_progress
        
        return progress
    
    def calculate_results(self) -> Dict:
        """
        Calculate final results.
        
        Returns:
            Complete results dictionary
        """
        # Get basic results
        results = self.scorer.get_detailed_results()
        
        # Get personality analysis
        type_analysis = self.result_analyzer.get_type_analysis(
            results['mbti_type'],
            results['dimension_scores']
        )
        
        # Combine results
        final_results = {
            **results,
            'personality_analysis': type_analysis,
            'test_metadata': {
                'test_length': self.test_length,
                'total_questions': len(self.questions),
                'completion_time': self.session_manager.get_progress()['time_elapsed']
            }
        }
        
        # Save to session
        self.session_manager.mark_complete(final_results)
        
        return final_results
    
    def validate_responses(self) -> Tuple[bool, str]:
        """
        Validate all responses for consistency.
        
        Returns:
            Tuple of (is_valid, message)
        """
        responses = list(self.scorer.responses.values())
        return self.validator.check_consistency(responses)
    
    def get_question_by_index(self, index: int) -> Optional[Dict]:
        """
        Get a specific question by index.
        
        Args:
            index: Question index
            
        Returns:
            Question data or None
        """
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None
    
    def get_available_sessions(self) -> List[Dict]:
        """
        Get list of resumable sessions.
        
        Returns:
            List of session information
        """
        return self.session_manager.find_incomplete_sessions()
    
    def cleanup_old_sessions(self):
        """Clean up old session files."""
        self.session_manager.cleanup_old_sessions()
    
    def export_results(self, format: str = 'json') -> Optional[str]:
        """
        Export test results.
        
        Args:
            format: Export format (json/txt)
            
        Returns:
            Export file path or None
        """
        return self.session_manager.export_session(format)