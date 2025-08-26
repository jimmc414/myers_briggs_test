from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from config.settings import DIMENSIONS

class MBTIScorer:
    """Core scoring engine for MBTI assessment."""
    
    def __init__(self):
        self.dimensions = DIMENSIONS
        self.responses = {}
        self.dimension_scores = {}
        
    def add_response(self, question_id: str, question_data: dict, response_value: int):
        """Add a response to the scoring system."""
        self.responses[question_id] = {
            'dimension': question_data['dimension'],
            'value': response_value,
            'reverse_coded': question_data.get('reverse_coded', False)
        }
    
    def calculate_dimension_score(self, dimension: str) -> Dict:
        """
        Calculate percentage score for a dimension.
        
        Args:
            dimension: Dimension key (E_I, S_N, T_F, J_P)
        
        Returns:
            Dictionary with scores and preference
        """
        # Get all responses for this dimension
        dim_responses = [
            r for r in self.responses.values() 
            if r['dimension'] == dimension
        ]
        
        if not dim_responses:
            return {
                'preference': 'X',
                'strength': 50.0,
                'right_score': 50.0,
                'left_score': 50.0,
                'is_borderline': True,
                'response_count': 0
            }
        
        total_score = 0
        max_possible = len(dim_responses) * 5
        min_possible = len(dim_responses) * 1
        
        for response in dim_responses:
            # Handle reverse-coded questions
            if response['reverse_coded']:
                adjusted_value = 6 - response['value']
            else:
                adjusted_value = response['value']
            
            total_score += adjusted_value
        
        # Calculate percentage for right side (E, N, T, J)
        # Formula: normalize to 0-100 scale
        if max_possible > min_possible:
            normalized = (total_score - min_possible) / (max_possible - min_possible)
            right_percentage = normalized * 100
        else:
            right_percentage = 50.0
        
        left_percentage = 100 - right_percentage
        
        # Determine preference with clearer boundaries
        dim_config = self.dimensions[dimension]
        
        if right_percentage > 52:
            preference = dim_config['right']['code']
            strength = right_percentage
            preferred_label = dim_config['right']['label']
        elif right_percentage < 48:
            preference = dim_config['left']['code']
            strength = left_percentage
            preferred_label = dim_config['left']['label']
        else:
            # Borderline case - use slight preference
            if right_percentage >= 50:
                preference = dim_config['right']['code']
                preferred_label = dim_config['right']['label']
            else:
                preference = dim_config['left']['code']
                preferred_label = dim_config['left']['label']
            strength = 50.0
        
        return {
            'preference': preference,
            'preferred_label': preferred_label,
            'strength': strength,
            'right_score': right_percentage,
            'left_score': left_percentage,
            'right_label': dim_config['right']['label'],
            'left_label': dim_config['left']['label'],
            'is_borderline': 48 <= right_percentage <= 52,
            'response_count': len(dim_responses)
        }
    
    def calculate_all_dimensions(self) -> Dict[str, Dict]:
        """Calculate scores for all dimensions."""
        self.dimension_scores = {}
        for dimension in ['E_I', 'S_N', 'T_F', 'J_P']:
            self.dimension_scores[dimension] = self.calculate_dimension_score(dimension)
        return self.dimension_scores
    
    def determine_mbti_type(self) -> Dict:
        """
        Determine MBTI type from dimension scores.
        
        Returns:
            Dictionary with type code, confidence, and details
        """
        if not self.dimension_scores:
            self.calculate_all_dimensions()
        
        type_code = ""
        total_confidence = 0
        borderline_dimensions = []
        dimension_details = []
        
        for dimension in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = self.dimension_scores[dimension]
            
            if score['is_borderline']:
                borderline_dimensions.append({
                    'dimension': self.dimensions[dimension]['name'],
                    'scores': f"{score['left_label']} ({score['left_score']:.1f}%) vs {score['right_label']} ({score['right_score']:.1f}%)"
                })
            
            type_code += score['preference']
            total_confidence += score['strength']
            
            dimension_details.append({
                'dimension': self.dimensions[dimension]['name'],
                'preference': score['preferred_label'],
                'strength': score['strength'],
                'is_borderline': score['is_borderline']
            })
        
        # Average confidence across all dimensions
        confidence = total_confidence / 4
        
        # Determine confidence level
        if confidence > 70:
            confidence_level = "Strong"
        elif confidence > 60:
            confidence_level = "Moderate"
        else:
            confidence_level = "Low"
        
        # Get secondary type if there are borderline dimensions
        secondary_type = None
        if borderline_dimensions:
            secondary_type = self._get_secondary_type()
        
        return {
            'type': type_code,
            'confidence': confidence,
            'confidence_level': confidence_level,
            'borderline_dimensions': borderline_dimensions,
            'secondary_type': secondary_type,
            'dimension_details': dimension_details,
            'total_responses': len(self.responses)
        }
    
    def _get_secondary_type(self) -> Optional[str]:
        """Determine secondary type for borderline cases."""
        secondary = ""
        
        for dimension in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = self.dimension_scores[dimension]
            
            if score['is_borderline']:
                # Flip to the other preference
                dim_config = self.dimensions[dimension]
                if score['preference'] == dim_config['right']['code']:
                    secondary += dim_config['left']['code']
                else:
                    secondary += dim_config['right']['code']
            else:
                secondary += score['preference']
        
        # Only return if different from primary
        primary = self.determine_mbti_type()['type']
        return secondary if secondary != primary else None
    
    def get_detailed_results(self) -> Dict:
        """Get comprehensive results including all scoring details."""
        mbti_result = self.determine_mbti_type()
        
        return {
            'mbti_type': mbti_result['type'],
            'confidence': mbti_result['confidence'],
            'confidence_level': mbti_result['confidence_level'],
            'dimension_scores': self.dimension_scores,
            'borderline_dimensions': mbti_result['borderline_dimensions'],
            'secondary_type': mbti_result['secondary_type'],
            'dimension_details': mbti_result['dimension_details'],
            'total_responses': mbti_result['total_responses'],
            'response_breakdown': self._get_response_breakdown()
        }
    
    def _get_response_breakdown(self) -> Dict:
        """Get breakdown of responses by dimension."""
        breakdown = {}
        
        for dimension in ['E_I', 'S_N', 'T_F', 'J_P']:
            dim_responses = [
                r for r in self.responses.values() 
                if r['dimension'] == dimension
            ]
            
            breakdown[dimension] = {
                'count': len(dim_responses),
                'average_score': sum(r['value'] for r in dim_responses) / len(dim_responses) if dim_responses else 0
            }
        
        return breakdown
    
    def reset(self):
        """Reset the scorer for a new test."""
        self.responses = {}
        self.dimension_scores = {}


class ResultAnalyzer:
    """Analyze and provide insights on MBTI results."""
    
    def __init__(self, personality_types_path: Path):
        with open(personality_types_path) as f:
            self.personality_types = json.load(f)
    
    def get_type_analysis(self, mbti_type: str, dimension_scores: Dict) -> Dict:
        """Get detailed analysis for a personality type."""
        if mbti_type not in self.personality_types:
            return {
                'error': f'Unknown personality type: {mbti_type}'
            }
        
        type_data = self.personality_types[mbti_type]
        
        # Add strength indicators
        strengths_analysis = self._analyze_strengths(dimension_scores)
        
        return {
            'type': mbti_type,
            'title': type_data['title'],
            'overview': type_data['overview'],
            'strengths': type_data['strengths'],
            'weaknesses': type_data['weaknesses'],
            'career_matches': type_data['career_matches'],
            'cognitive_stack': type_data['cognitive_stack'],
            'famous_examples': type_data['famous_examples'],
            'relationship_style': type_data['relationship_style'],
            'dimension_analysis': strengths_analysis
        }
    
    def _analyze_strengths(self, dimension_scores: Dict) -> List[str]:
        """Analyze dimension strengths and provide insights."""
        insights = []
        
        for dim_key, scores in dimension_scores.items():
            if scores['strength'] > 70:
                insights.append(f"Strong {scores['preferred_label']} preference ({scores['strength']:.1f}%)")
            elif scores['strength'] > 60:
                insights.append(f"Moderate {scores['preferred_label']} preference ({scores['strength']:.1f}%)")
            elif scores['is_borderline']:
                insights.append(f"Balanced between {scores['left_label']} and {scores['right_label']}")
        
        return insights
    
    def get_compatibility_insights(self, mbti_type: str) -> Dict:
        """Get compatibility insights with other types."""
        # Simplified compatibility model
        compatibilities = {
            'highly_compatible': [],
            'compatible': [],
            'challenging': []
        }
        
        # This is a simplified model - real compatibility is more complex
        type_groups = {
            'analysts': ['INTJ', 'INTP', 'ENTJ', 'ENTP'],
            'diplomats': ['INFJ', 'INFP', 'ENFJ', 'ENFP'],
            'sentinels': ['ISTJ', 'ISFJ', 'ESTJ', 'ESFJ'],
            'explorers': ['ISTP', 'ISFP', 'ESTP', 'ESFP']
        }
        
        # Find which group this type belongs to
        my_group = None
        for group, types in type_groups.items():
            if mbti_type in types:
                my_group = group
                break
        
        if my_group:
            # Same group = generally compatible
            compatibilities['compatible'] = [t for t in type_groups[my_group] if t != mbti_type]
        
        return compatibilities