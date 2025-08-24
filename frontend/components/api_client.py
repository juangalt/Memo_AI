"""
API Client for Memo AI Coach Frontend
Handles all communication with the backend API
"""

import requests
import os
import time
from typing import Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Memo AI Coach backend API"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client
        
        Args:
            base_url: Backend API base URL (defaults to environment variable)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Memo-AI-Coach-Frontend/1.0.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Make HTTP request with error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Tuple of (success, data, error_message)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Add timeout to kwargs
            kwargs.setdefault('timeout', self.timeout)
            
            logger.info(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            
            # Log response status
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, None
                except ValueError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return False, None, "Invalid JSON response from server"
            
            elif response.status_code == 404:
                return False, None, "API endpoint not found"
            
            elif response.status_code == 500:
                return False, None, "Internal server error"
            
            elif response.status_code == 503:
                return False, None, "Service temporarily unavailable"
            
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', f"HTTP {response.status_code} error")
                except ValueError:
                    error_msg = f"HTTP {response.status_code} error"
                
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            return False, None, "Request timeout - server is not responding"
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
            return False, None, "Cannot connect to server - please check if backend is running"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return False, None, f"Network error: {str(e)}"
        
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return False, None, f"Unexpected error: {str(e)}"
    
    def health_check(self) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Check backend health status
        
        Returns:
            Tuple of (healthy, health_data, error_message)
        """
        return self._make_request('GET', '/health')
    
    def create_session(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new session
        
        Returns:
            Tuple of (success, session_id, error_message)
        """
        success, data, error = self._make_request('POST', '/api/v1/sessions/create')
        
        if success and data:
            session_id = data.get('data', {}).get('session_id')
            if session_id:
                return True, session_id, None
            else:
                return False, None, "No session ID in response"
        
        return False, None, error
    
    def get_session(self, session_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (success, session_data, error_message)
        """
        return self._make_request('GET', f'/api/v1/sessions/{session_id}')
    
    def submit_evaluation(self, text_content: str, session_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Submit text for evaluation
        
        Args:
            text_content: Text to evaluate
            session_id: Session identifier
            
        Returns:
            Tuple of (success, evaluation_data, error_message)
        """
        payload = {
            "text_content": text_content,
            "session_id": session_id
        }
        
        headers = {"X-Session-ID": session_id}
        
        return self._make_request(
            'POST', 
            '/api/v1/evaluations/submit',
            json=payload,
            headers=headers
        )
    
    def get_evaluation(self, evaluation_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get evaluation results
        
        Args:
            evaluation_id: Evaluation identifier
            
        Returns:
            Tuple of (success, evaluation_data, error_message)
        """
        return self._make_request('GET', f'/api/v1/evaluations/{evaluation_id}')
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test basic connectivity to backend
        
        Returns:
            Tuple of (connected, error_message)
        """
        success, data, error = self.health_check()
        return success, error

# Global API client instance
api_client = APIClient()

def get_api_client() -> APIClient:
    """Get the global API client instance"""
    return api_client

def test_backend_connection() -> Tuple[bool, Optional[str]]:
    """Test backend connection and return status"""
    return api_client.test_connection()

def create_session_with_retry(max_retries: int = 3, delay: float = 1.0) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Create session with retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Tuple of (success, session_id, error_message)
    """
    for attempt in range(max_retries):
        success, session_id, error = api_client.create_session()
        
        if success:
            return True, session_id, None
        
        if attempt < max_retries - 1:
            logger.warning(f"Session creation failed (attempt {attempt + 1}/{max_retries}): {error}")
            time.sleep(delay)
        else:
            logger.error(f"Session creation failed after {max_retries} attempts: {error}")
    
    return False, None, error

def submit_evaluation_with_retry(text_content: str, session_id: str, max_retries: int = 3, delay: float = 1.0) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Submit evaluation with retry logic
    
    Args:
        text_content: Text to evaluate
        session_id: Session identifier
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Tuple of (success, evaluation_data, error_message)
    """
    for attempt in range(max_retries):
        success, data, error = api_client.submit_evaluation(text_content, session_id)
        
        if success:
            return True, data, None
        
        if attempt < max_retries - 1:
            logger.warning(f"Evaluation submission failed (attempt {attempt + 1}/{max_retries}): {error}")
            time.sleep(delay)
        else:
            logger.error(f"Evaluation submission failed after {max_retries} attempts: {error}")
    
    return False, None, error
