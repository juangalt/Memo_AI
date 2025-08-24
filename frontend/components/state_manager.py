"""
State Manager for Memo AI Coach Frontend
Handles session state and evaluation results management
"""

import streamlit as st
from typing import Dict, Any, Optional
import json
from datetime import datetime

class StateManager:
    """Manages application state and session data"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = None
        
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "Text Input"
        
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False
        
        if 'admin_session_token' not in st.session_state:
            st.session_state.admin_session_token = None
        
        if 'last_evaluation_time' not in st.session_state:
            st.session_state.last_evaluation_time = None
        
        if 'evaluation_count' not in st.session_state:
            st.session_state.evaluation_count = 0
    
    @staticmethod
    def set_session_id(session_id: str):
        """Set the current session ID"""
        st.session_state.session_id = session_id
    
    @staticmethod
    def get_session_id() -> Optional[str]:
        """Get the current session ID"""
        return st.session_state.session_id
    
    @staticmethod
    def clear_session_id():
        """Clear the current session ID"""
        st.session_state.session_id = None
    
    @staticmethod
    def set_evaluation_results(results: Dict[str, Any]):
        """Set evaluation results and update metadata"""
        st.session_state.evaluation_results = results
        st.session_state.last_evaluation_time = datetime.now().isoformat()
        st.session_state.evaluation_count += 1
    
    @staticmethod
    def get_evaluation_results() -> Optional[Dict[str, Any]]:
        """Get the current evaluation results"""
        return st.session_state.evaluation_results
    
    @staticmethod
    def clear_evaluation_results():
        """Clear the current evaluation results"""
        st.session_state.evaluation_results = None
    
    @staticmethod
    def set_current_tab(tab_name: str):
        """Set the current active tab"""
        st.session_state.current_tab = tab_name
    
    @staticmethod
    def get_current_tab() -> str:
        """Get the current active tab"""
        return st.session_state.current_tab
    
    @staticmethod
    def set_admin_authenticated(authenticated: bool):
        """Set admin authentication status"""
        st.session_state.admin_authenticated = authenticated
    
    @staticmethod
    def is_admin_authenticated() -> bool:
        """Check if admin is authenticated"""
        return st.session_state.admin_authenticated
    
    @staticmethod
    def set_admin_session_token(token: str):
        """Set admin session token"""
        st.session_state.admin_session_token = token
    
    @staticmethod
    def get_admin_session_token() -> Optional[str]:
        """Get admin session token"""
        return st.session_state.get('admin_session_token')
    
    @staticmethod
    def clear_admin_session_token():
        """Clear admin session token"""
        st.session_state.admin_session_token = None
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """Get comprehensive session information"""
        return {
            'session_id': st.session_state.session_id,
            'current_tab': st.session_state.current_tab,
            'admin_authenticated': st.session_state.admin_authenticated,
            'last_evaluation_time': st.session_state.last_evaluation_time,
            'evaluation_count': st.session_state.evaluation_count,
            'has_evaluation_results': st.session_state.evaluation_results is not None
        }
    
    @staticmethod
    def reset_session():
        """Reset all session state (except admin authentication)"""
        st.session_state.session_id = None
        st.session_state.evaluation_results = None
        st.session_state.current_tab = "Text Input"
        st.session_state.last_evaluation_time = None
        st.session_state.evaluation_count = 0
    
    @staticmethod
    def validate_evaluation_results(results: Dict[str, Any]) -> bool:
        """Validate evaluation results structure"""
        if not results:
            return False
        
        # Check for required top-level keys
        required_keys = ['evaluation']
        if not all(key in results for key in required_keys):
            return False
        
        evaluation = results.get('evaluation', {})
        
        # Check for required evaluation keys
        evaluation_keys = ['overall_score', 'strengths', 'opportunities', 'rubric_scores']
        if not all(key in evaluation for key in evaluation_keys):
            return False
        
        # Validate overall score
        overall_score = evaluation.get('overall_score')
        if not isinstance(overall_score, (int, float)) or overall_score < 0 or overall_score > 5:
            return False
        
        # Validate rubric scores
        rubric_scores = evaluation.get('rubric_scores', {})
        if not isinstance(rubric_scores, dict):
            return False
        
        for score in rubric_scores.values():
            if not isinstance(score, (int, float)) or score < 0 or score > 5:
                return False
        
        return True
    
    @staticmethod
    def format_evaluation_summary(results: Dict[str, Any]) -> Dict[str, Any]:
        """Format evaluation results for display"""
        if not StateManager.validate_evaluation_results(results):
            return {}
        
        evaluation = results.get('evaluation', {})
        
        return {
            'overall_score': evaluation.get('overall_score', 0),
            'strengths': evaluation.get('strengths', ''),
            'opportunities': evaluation.get('opportunities', ''),
            'rubric_scores': evaluation.get('rubric_scores', {}),
            'segment_feedback': evaluation.get('segment_feedback', []),
            'evaluation_id': results.get('evaluation_id', ''),
            'submission_id': results.get('submission_id', ''),
            'timestamp': results.get('timestamp', '')
        }
    
    @staticmethod
    def export_session_data() -> str:
        """Export session data as JSON string"""
        session_data = {
            'session_info': StateManager.get_session_info(),
            'evaluation_results': st.session_state.evaluation_results,
            'export_timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        return json.dumps(session_data, indent=2)
    
    @staticmethod
    def import_session_data(json_data: str) -> bool:
        """Import session data from JSON string"""
        try:
            data = json.loads(json_data)
            
            # Validate imported data
            if 'session_info' not in data or 'evaluation_results' not in data:
                return False
            
            # Import session info
            session_info = data['session_info']
            if session_info.get('session_id'):
                st.session_state.session_id = session_info['session_id']
            
            if session_info.get('current_tab'):
                st.session_state.current_tab = session_info['current_tab']
            
            # Import evaluation results if valid
            evaluation_results = data['evaluation_results']
            if evaluation_results and StateManager.validate_evaluation_results(evaluation_results):
                st.session_state.evaluation_results = evaluation_results
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
