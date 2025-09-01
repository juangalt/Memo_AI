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
    
    def _get_frameworks_content(self) -> str:
        """Generate frameworks content for prompts from rubric.yaml"""
        try:
            frameworks = self.rubric_config.get('frameworks', {})
            framework_definitions = frameworks.get('framework_definitions', {})
            application_guidance = frameworks.get('application_guidance', {})
            
            if not framework_definitions:
                return "EVALUATION FRAMEWORKS:\nUse standard business communication frameworks for evaluation."
            
            frameworks_content = "EVALUATION FRAMEWORKS:\nUse these frameworks to guide your evaluation:\n\n"
            
            for framework_key, framework_data in framework_definitions.items():
                name = framework_data.get('name', framework_key.upper())
                description = framework_data.get('description', '')
                application = framework_data.get('application', '')
                
                frameworks_content += f"{name}\n"
                frameworks_content += f"Description: {description}\n"
                if application:
                    frameworks_content += f"Application: {application}\n"
                frameworks_content += "\n"
            
            return frameworks_content
            
        except Exception as e:
            logger.error(f"Failed to generate frameworks content: {e}")
            return "EVALUATION FRAMEWORKS:\nUse standard business communication frameworks for evaluation."
    
    def _get_framework_application_guidance(self) -> str:
        """Generate framework application guidance from rubric.yaml"""
        try:
            frameworks = self.rubric_config.get('frameworks', {})
            application_guidance = frameworks.get('application_guidance', {})
            
            guidance_parts = []
            
            if application_guidance.get('overall_evaluation'):
                guidance_parts.append(application_guidance['overall_evaluation'])
            
            if application_guidance.get('scoring_evaluation'):
                guidance_parts.append(application_guidance['scoring_evaluation'])
            
            if application_guidance.get('segment_evaluation'):
                guidance_parts.append(application_guidance['segment_evaluation'])
            
            if application_guidance.get('domain_focus'):
                guidance_parts.append(f"Focus on: {application_guidance['domain_focus']}")
            
            if guidance_parts:
                return " ".join(guidance_parts)
            else:
                return "Apply the provided frameworks to ensure comprehensive evaluation."
                
        except Exception as e:
            logger.error(f"Failed to generate framework application guidance: {e}")
            return "Apply the provided frameworks to ensure comprehensive evaluation."
    
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
            
            # Generate frameworks content dynamically
            frameworks_section = self._get_frameworks_content()
            framework_application_guidance = self._get_framework_application_guidance()
            
            # Fill template variables
            user_message = user_template.format(
                text_content=text_content,
                rubric_content=rubric_content,
                frameworks_section=frameworks_section,
                framework_application_guidance=framework_application_guidance
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
                strengths = ["Brief and concise"]
                opportunities = ["Needs more detail and development"]
            elif text_length < 500:
                overall_score = 3.0
                strengths = ["Adequate length and structure"]
                opportunities = ["Could benefit from more specific examples"]
            else:
                overall_score = 4.0
                strengths = ["Comprehensive coverage", "Good length for detailed analysis"]
                opportunities = ["Consider adding more quantitative data"]
            
            # Generate mock rubric scores
            rubric_scores = {
                "structure_and_logic": {"score": 3, "justification": "Basic structure present"},
                "arguments_and_evidence": {"score": 3, "justification": "Some evidence provided"},
                "clarity_style_financial_metrics": {"score": 3, "justification": "Clear communication"},
                "relevance_strategic_alignment": {"score": 3, "justification": "Relevant content"},
                "clear_opportunity_ask": {"score": 3, "justification": "Opportunity identified"},
                "risk_mitigation": {"score": 3, "justification": "Basic risk consideration"},
                "feasibility_implementation": {"score": 3, "justification": "Feasible approach"}
            }
            
            # Generate mock segment feedback
            segment_feedback = [
                {
                    "segment": text_content[:100] + "..." if len(text_content) > 100 else text_content,
                    "comment": "This segment provides a good introduction to the topic",
                    "questions": ["How could this be made more compelling?", "What additional context would help?"],
                    "suggestions": ["Add specific examples", "Include quantitative data"]
                }
            ]
            
            evaluation_data = {
                "overall_score": overall_score,
                "strengths": strengths,
                "opportunities": opportunities,
                "rubric_scores": rubric_scores,
                "segment_feedback": segment_feedback,
                "processing_time": processing_time,
                "llm_provider": "mock",
                "llm_model": "mock-claude-3.5-sonnet",
                "debug_enabled": True,
                "raw_prompt": "Mock prompt for testing",
                "raw_response": "Mock response for testing"
            }
            
            return True, evaluation_data, None
            
        except Exception as e:
            logger.error(f"Mock evaluation failed: {e}")
            return False, None, str(e)
    
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
            # Check if we have a client (API key available)
            if not self.client:
                logger.info("Using mock evaluation mode")
                return self._mock_evaluation(text_content, start_time)
            
            # Generate prompt
            system_message, user_message = self._generate_prompt(text_content)
            
            # Store raw prompt for debugging
            raw_prompt = f"System: {system_message}\n\nUser: {user_message}"
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.llm_config.get('model', 'claude-3-5-sonnet-20241022'),
                max_tokens=self.llm_config.get('max_tokens', 4000),
                temperature=self.llm_config.get('temperature', 0.1),
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract response content
            response_content = response.content[0].text if response.content else ""
            
            # Store raw response for debugging
            raw_response = response_content
            
            # Parse response
            evaluation_data = self._parse_response(response_content)
            
            # Add metadata
            evaluation_data.update({
                "processing_time": time.time() - start_time,
                "llm_provider": "anthropic",
                "llm_model": self.llm_config.get('model', 'claude-3-5-sonnet-20241022'),
                "debug_enabled": True,
                "raw_prompt": raw_prompt,
                "raw_response": raw_response
            })
            
            return True, evaluation_data, None
            
        except Exception as e:
            logger.error(f"Text evaluation failed: {e}")
            return False, None, str(e)
