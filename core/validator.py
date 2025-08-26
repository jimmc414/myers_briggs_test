from typing import List, Tuple, Dict

class ResponseValidator:
    """Validate user responses and data integrity."""
    
    @staticmethod
    def validate_response(response_value: int) -> bool:
        """
        Ensure response is valid.
        
        Args:
            response_value: The response value to validate
            
        Returns:
            True if valid, raises ValueError if not
        """
        if not isinstance(response_value, int):
            raise ValueError("Response must be an integer")
        if response_value not in range(1, 6):
            raise ValueError("Response must be between 1-5")
        return True
    
    @staticmethod
    def check_consistency(responses: List[Dict]) -> Tuple[bool, str]:
        """
        Check for response patterns indicating low quality.
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not responses:
            return False, "No responses provided"
        
        values = [r.get('value', r) for r in responses]
        
        # Check minimum responses
        if len(values) < 10:
            return True, "Too few responses to check consistency"
        
        # Check for straight-lining (all same answer)
        unique_values = set(values)
        if len(unique_values) == 1:
            return False, "All responses are identical - possible straight-lining"
        
        # Check for alternating pattern
        is_alternating = True
        if len(values) >= 4:
            for i in range(2, len(values)):
                if values[i] != values[i-2]:
                    is_alternating = False
                    break
        
        if is_alternating and len(unique_values) == 2:
            return False, "Alternating pattern detected - possible random responses"
        
        # Check for too many extreme responses
        extreme_count = sum(1 for v in values if v in [1, 5])
        extreme_ratio = extreme_count / len(values)
        
        if extreme_ratio > 0.9:
            return False, "Too many extreme responses - consider more nuanced answers"
        
        # Check for response time patterns (if timestamps available)
        # This would require timestamp data
        
        return True, "Valid response pattern"
    
    @staticmethod
    def validate_question_data(question: Dict) -> Tuple[bool, str]:
        """
        Validate question data structure.
        
        Args:
            question: Question dictionary
            
        Returns:
            Tuple of (is_valid, message)
        """
        required_fields = ['id', 'dimension', 'text', 'type', 'priority', 'options']
        
        for field in required_fields:
            if field not in question:
                return False, f"Missing required field: {field}"
        
        # Validate dimension
        valid_dimensions = ['E_I', 'S_N', 'T_F', 'J_P']
        if question['dimension'] not in valid_dimensions:
            return False, f"Invalid dimension: {question['dimension']}"
        
        # Validate priority
        if question['priority'] not in [1, 2, 3]:
            return False, f"Invalid priority: {question['priority']}"
        
        # Validate options
        if not isinstance(question['options'], list) or len(question['options']) != 5:
            return False, "Options must be a list of 5 items"
        
        for option in question['options']:
            if 'text' not in option or 'value' not in option:
                return False, "Each option must have 'text' and 'value' fields"
            if option['value'] not in range(1, 6):
                return False, f"Invalid option value: {option['value']}"
        
        return True, "Valid question data"
    
    @staticmethod
    def validate_test_completion(responses: Dict, expected_count: int) -> Tuple[bool, str]:
        """
        Validate that a test has been properly completed.
        
        Args:
            responses: Dictionary of responses
            expected_count: Expected number of questions
            
        Returns:
            Tuple of (is_valid, message)
        """
        actual_count = len(responses)
        
        if actual_count < expected_count:
            missing = expected_count - actual_count
            return False, f"Test incomplete: {missing} questions remaining"
        
        if actual_count > expected_count:
            return False, f"Too many responses: expected {expected_count}, got {actual_count}"
        
        # Check dimension balance
        dimension_counts = {'E_I': 0, 'S_N': 0, 'T_F': 0, 'J_P': 0}
        
        for response in responses.values():
            if 'dimension' in response:
                dim = response['dimension']
                if dim in dimension_counts:
                    dimension_counts[dim] += 1
        
        # Check if dimensions are reasonably balanced
        counts = list(dimension_counts.values())
        if counts:
            min_count = min(counts)
            max_count = max(counts)
            
            if max_count > min_count * 2:
                return False, "Dimension imbalance detected"
        
        return True, "Test properly completed"
    
    @staticmethod
    def sanitize_response(response: any) -> int:
        """
        Sanitize and convert response to valid integer.
        
        Args:
            response: Raw response value
            
        Returns:
            Sanitized integer value
        """
        # Handle string numbers
        if isinstance(response, str):
            try:
                response = int(response)
            except ValueError:
                # Try to extract number from string like "1️⃣  Strongly Agree"
                if response and response[0].isdigit():
                    response = int(response[0])
                else:
                    raise ValueError(f"Cannot parse response: {response}")
        
        # Handle float
        if isinstance(response, float):
            response = round(response)
        
        # Validate range
        if response < 1:
            response = 1
        elif response > 5:
            response = 5
        
        return int(response)