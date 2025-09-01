"""
LLM Service for Memo AI Coach
Handles Claude API integration with prompt management and response parsing
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import anthropic
from anthropic import Anthropic
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM integration with Claude API"""
    
    def __init__(self, config_path: str = None):
        """Initialize LLM service with automatic path detection"""
        if config_path is None:
            # In container, config is mounted at /app/config
            # For development, fallback to ../config
            if os.path.exists('/app/config'):
                config_path = '/app/config'
            else:
                config_path = '../config'
        
        self.config_path = config_path
        self.client = None
        self.llm_config = None
        self.prompt_config = None
        self.rubric_config = None
        
        # Load configurations
        self._load_configurations()
        
        # Initialize Claude client
        self._initialize_client()
    
    def _load_configurations(self):
        """Load all required configuration files"""
        try:
            # Load LLM configuration
            with open(f"{self.config_path}/llm.yaml", 'r') as f:
                self.llm_config = yaml.safe_load(f)
            
            # Load prompt configuration
            with open(f"{self.config_path}/prompt.yaml", 'r') as f:
                self.prompt_config = yaml.safe_load(f)
            
            # Load rubric configuration
            with open(f"{self.config_path}/rubric.yaml", 'r') as f:
                self.rubric_config = yaml.safe_load(f)
                
            logger.info("All LLM configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load LLM configurations: {e}")
            raise
    
    def _initialize_client(self):
        """Initialize Claude API client"""
        try:
            api_key = os.getenv('LLM_API_KEY')
            if not api_key:
                logger.warning("LLM_API_KEY environment variable not set - using mock mode for testing")
                self.client = None
                return
            
            self.client = Anthropic(api_key=api_key)
            logger.info("Claude API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Claude API client: {e}")
            raise
    
    def _get_rubric_content(self) -> str:
        """Generate rubric content for prompts"""
        try:
            rubric = self.rubric_config.get('rubric', {})
            criteria = rubric.get('criteria', [])
            
            rubric_content = f"Rubric: {rubric.get('name', 'Business Memo Evaluation')}\n\n"
            rubric_content += f"Description: {rubric.get('description', '')}\n\n"
            rubric_content += "Evaluation Criteria:\n"
            
            for criterion in criteria:
                rubric_content += f"\n{criterion['name']} (Weight: {criterion['weight']}%)\n"
                rubric_content += f"Description: {criterion['description']}\n"
                rubric_content += "Scoring Guidance:\n"
                
                for score, guidance in criterion.get('scoring_guidance', {}).items():
                    rubric_content += f"  {score}: {guidance}\n"
            
            return rubric_content
            
        except Exception as e:
            logger.error(f"Failed to generate rubric content: {e}")
            return "Standard evaluation rubric"
    
    def _generate_prompt(self, text_content: str) -> Tuple[str, str]:
        """
        Generate evaluation prompt from templates
        
        Args:
            text_content: Text to evaluate
            
        Returns:
            Tuple of (system_message, user_message)
        """
        try:
            templates = self.prompt_config.get('templates', {})
            evaluation_prompt = templates.get('evaluation_prompt', {})
            
            # Get system message
            system_message = evaluation_prompt.get('system_message', '')
            
            # Get user template and fill variables
            user_template = evaluation_prompt.get('user_template', '')
            
            # Generate rubric content
            rubric_content = self._get_rubric_content()
            
            # Fill template variables
            user_message = user_template.format(
                text_content=text_content,
                rubric_content=rubric_content,
                frameworks_section="EVALUATION FRAMEWORKS:\nUse these frameworks to guide your evaluation:\n\n- Business Communication Framework\n- Healthcare Investment Analysis\n- Strategic Planning Framework",
                framework_application_guidance="Apply the provided frameworks to ensure comprehensive evaluation."
            )
            
            return system_message, user_message
            
        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            raise
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response and extract structured data
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed evaluation data
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            evaluation_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['overall_score', 'strengths', 'opportunities', 'rubric_scores']
            for field in required_fields:
                if field not in evaluation_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate overall score
            overall_score = evaluation_data.get('overall_score')
            if not isinstance(overall_score, (int, float)) or overall_score < 0 or overall_score > 5:
                raise ValueError(f"Invalid overall score: {overall_score}")
            
            # Validate rubric scores
            rubric_scores = evaluation_data.get('rubric_scores', {})
            if not isinstance(rubric_scores, dict):
                raise ValueError("Invalid rubric_scores format")
            
            for criterion, score_data in rubric_scores.items():
                if isinstance(score_data, dict):
                    score = score_data.get('score', score_data)
                else:
                    score = score_data
                
                if not isinstance(score, (int, float)) or score < 1 or score > 5:
                    raise ValueError(f"Invalid score for {criterion}: {score}")
            
            return evaluation_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise
    
    def _mock_evaluation(self, text_content: str, start_time: float) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Generate mock evaluation for testing purposes
        
        Args:
            text_content: Text to evaluate
            start_time: Start time for processing calculation
            
        Returns:
            Tuple of (success, evaluation_data, error_message)
        """
        try:
            # Simulate processing time
            time.sleep(2)
            processing_time = time.time() - start_time
            
            # Generate mock evaluation based on text content
            text_length = len(text_content)
            word_count = len(text_content.split())
            
            # Simple scoring logic based on text characteristics
            if text_length < 100:
                overall_score = 2.0
            elif text_length < 500:
                overall_score = 3.0
            elif text_length < 1000:
                overall_score = 3.5
            else:
                overall_score = 4.0
            
            # Adjust score based on content quality indicators
            if "executive summary" in text_content.lower():
                overall_score += 0.5
            if "roi" in text_content.lower() or "return on investment" in text_content.lower():
                overall_score += 0.3
            if "implementation" in text_content.lower():
                overall_score += 0.2
            
            # Cap at 5.0
            overall_score = min(5.0, overall_score)
            
            # Generate mock rubric scores
            rubric_scores = {
                "structure_and_logic": {"score": int(overall_score), "justification": "Mock evaluation based on text structure"},
                "arguments_and_evidence": {"score": int(overall_score), "justification": "Mock evaluation based on content quality"},
                "clarity_style_financial_metrics": {"score": int(overall_score), "justification": "Mock evaluation based on writing style"},
                "relevance_strategic_alignment": {"score": int(overall_score), "justification": "Mock evaluation based on strategic focus"},
                "clear_opportunity_ask": {"score": int(overall_score), "justification": "Mock evaluation based on opportunity clarity"},
                "risk_mitigation": {"score": int(overall_score), "justification": "Mock evaluation based on risk awareness"},
                "feasibility_implementation": {"score": int(overall_score), "justification": "Mock evaluation based on implementation planning"}
            }
            
            # Generate mock strengths and opportunities
            strengths = [
                "The text demonstrates clear organization and logical flow",
                "Content is relevant and well-structured",
                "Good use of business terminology and concepts"
            ]
            
            opportunities = [
                "Consider adding more specific examples and data",
                "Strengthen the conclusion with actionable next steps",
                "Enhance risk mitigation strategies"
            ]
            
            # Generate mock segment feedback
            segments = text_content.split('\n\n')
            segment_feedback = []
            
            for i, segment in enumerate(segments[:3]):  # Limit to first 3 segments
                if segment.strip():
                    segment_feedback.append({
                        "segment": segment.strip()[:100] + "..." if len(segment) > 100 else segment.strip(),
                        "comment": f"This segment is well-written and contributes to the overall message.",
                        "questions": [
                            "How could this segment be expanded with more detail?",
                            "What additional evidence would strengthen this point?"
                        ],
                        "suggestions": [
                            "Consider adding specific examples",
                            "Include more quantitative data if available"
                        ]
                    })
            
            # Generate mock raw prompt and response
            system_message, user_message = self._generate_prompt(text_content)
            raw_prompt = f"System: {system_message}\n\nUser: {user_message}"
            raw_response = f"""Mock LLM Response for text evaluation:

Overall Score: {overall_score}

Strengths:
{chr(10).join(strengths)}

Opportunities:
{chr(10).join(opportunities)}

Rubric Scores:
{chr(10).join([f"{k}: {v['score']} - {v['justification']}" for k, v in rubric_scores.items()])}

Segment Feedback:
{chr(10).join([f"Segment {i+1}: {s['comment']}" for i, s in enumerate(segment_feedback)])}"""

            evaluation_data = {
                "overall_score": round(overall_score, 1),
                "strengths": strengths,
                "opportunities": opportunities,
                "rubric_scores": rubric_scores,
                "segment_feedback": segment_feedback,
                "processing_time": round(processing_time, 2),
                "created_at": datetime.utcnow().isoformat(),
                "model_used": "mock-claude-3-haiku-20240307",
                "raw_prompt": raw_prompt,
                "raw_response": raw_response
            }
            
            logger.info(f"Mock text evaluation completed successfully in {processing_time:.2f} seconds")
            
            return True, evaluation_data, None
            
        except Exception as e:
            logger.error(f"Mock evaluation failed: {e}")
            return False, None, f"Mock evaluation error: {str(e)}"
    
    def evaluate_text(self, text_content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Evaluate text using Claude API
        
        Args:
            text_content: Text to evaluate
            
        Returns:
            Tuple of (success, evaluation_data, error_message)
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not text_content or len(text_content.strip()) == 0:
                return False, None, "Text content is required"
            
            max_length = self.llm_config.get('request_settings', {}).get('max_text_length', 10000)
            if len(text_content) > max_length:
                return False, None, f"Text exceeds maximum length of {max_length} characters"
            
            # Check if we're in mock mode (either no client or debug settings enabled)
            debug_mode = self.llm_config.get('debug_settings', {}).get('debug_mode', False)
            mock_responses = self.llm_config.get('debug_settings', {}).get('mock_responses', False)
            
            if self.client is None or (debug_mode and mock_responses):
                logger.info("Using mock evaluation mode")
                return self._mock_evaluation(text_content, start_time)
            
            # Generate prompt
            system_message, user_message = self._generate_prompt(text_content)
            raw_prompt = f"System: {system_message}\n\nUser: {user_message}"
            
            # Get model configuration
            model = self.llm_config.get('provider', {}).get('model', 'claude-3-haiku-20240307')
            max_tokens = self.llm_config.get('api_configuration', {}).get('max_tokens', 4000)
            temperature = self.llm_config.get('api_configuration', {}).get('temperature', 0.7)
            
            # Make API call
            logger.info(f"Making Claude API call for text evaluation (length: {len(text_content)})")
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract response content
            response_text = response.content[0].text if response.content else ""
            raw_response = response_text
            
            if not response_text:
                return False, None, "Empty response from Claude API"
            
            # Parse response
            evaluation_data = self._parse_response(response_text)
            
            # Add raw data to evaluation_data
            evaluation_data['raw_prompt'] = raw_prompt
            evaluation_data['raw_response'] = raw_response
            
            # Add metadata
            processing_time = time.time() - start_time
            evaluation_data['processing_time'] = round(processing_time, 2)
            evaluation_data['created_at'] = datetime.utcnow().isoformat()
            evaluation_data['model_used'] = model
            
            logger.info(f"Text evaluation completed successfully in {processing_time:.2f} seconds")
            
            return True, evaluation_data, None
            
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            return False, None, "Rate limit exceeded. Please try again later."
        
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return False, None, f"API error: {str(e)}"
        
        except anthropic.APITimeoutError as e:
            logger.error(f"Claude API timeout: {e}")
            return False, None, "Request timed out. Please try again."
        
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return False, None, "Authentication failed. Please check API key."
        
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return False, None, f"Validation error: {str(e)}"
        
        except Exception as e:
            logger.error(f"Unexpected error during text evaluation: {e}")
            return False, None, f"Unexpected error: {str(e)}"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check LLM service health
        
        Returns:
            Health status information
        """
        try:
            # Check if we're in mock mode (either no client or debug settings enabled)
            debug_mode = self.llm_config.get('debug_settings', {}).get('debug_mode', False)
            mock_responses = self.llm_config.get('debug_settings', {}).get('mock_responses', False)
            
            if self.client is None or (debug_mode and mock_responses):
                return {
                    "status": "healthy",
                    "provider": self.llm_config.get('provider', {}).get('name', 'claude'),
                    "model": self.llm_config.get('provider', {}).get('model', 'claude-3-haiku-20240307'),
                    "api_accessible": False,
                    "config_loaded": True,
                    "mock_mode": True,
                    "debug_mode": debug_mode,
                    "mock_responses": mock_responses,
                    "last_check": datetime.utcnow().isoformat()
                }
            
            # Test API connection with a simple request
            test_response = self.client.messages.create(
                model=self.llm_config.get('provider', {}).get('model', 'claude-3-haiku-20240307'),
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )
            
            return {
                "status": "healthy",
                "provider": self.llm_config.get('provider', {}).get('name', 'claude'),
                "model": self.llm_config.get('provider', {}).get('model', 'claude-3-haiku-20240307'),
                "api_accessible": True,
                "config_loaded": True,
                "mock_mode": False,
                "debug_mode": debug_mode,
                "mock_responses": mock_responses,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {
                "status": "unhealthy",
                "provider": self.llm_config.get('provider', {}).get('name', 'claude'),
                "model": self.llm_config.get('provider', {}).get('model', 'claude-3-haiku-20240307'),
                "api_accessible": False,
                "config_loaded": True,
                "mock_mode": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

# Global LLM service instance
llm_service = None

def get_llm_service() -> LLMService:
    """Get the global LLM service instance"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service

def evaluate_text_with_llm(text_content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Evaluate text using LLM service
    
    Args:
        text_content: Text to evaluate
        
    Returns:
        Tuple of (success, evaluation_data, error_message)
    """
    service = get_llm_service()
    return service.evaluate_text(text_content)
