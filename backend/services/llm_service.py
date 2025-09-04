"""
Enhanced LLM Service for Memo AI Coach
Handles Claude API integration with Jinja2 templating, language detection, and Pydantic validation
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
from jinja2 import Environment, FileSystemLoader, Template
from .path_utils import resolve_config_dir_with_fallback

# Import new components
try:
    from models.config_models import PromptConfig, LLMConfig, Language
except ImportError:
    from backend.models.config_models import PromptConfig, LLMConfig, Language
from .language_detection import RobustLanguageDetector, DetectionResult

# Get logger for this module
logger = logging.getLogger(__name__)

class EnhancedLLMService:
    """Enhanced LLM service with Jinja2 templating, language detection, and Pydantic validation"""
    
    def __init__(self, config_path: str = None):
        """Initialize enhanced LLM service with automatic path detection"""
        if config_path is None:
            config_path = resolve_config_dir_with_fallback()
        
        self.config_path = config_path
        self.client = None
        self.prompt_config = None
        self.llm_config = None
        self.language_detector = None
        self.jinja_env = None
        self.response_templates = {}
        
        # Load configurations with Pydantic validation
        self._load_configurations()
        
        # Initialize components
        self._initialize_components()
    
    def _load_configurations(self):
        """Load and validate all required configuration files"""
        try:
            # Load prompt configuration with Pydantic validation
            with open(f"{self.config_path}/prompt.yaml", 'r') as f:
                prompt_data = yaml.safe_load(f)
                self.prompt_config = PromptConfig(**prompt_data)
                logger.info("Prompt configuration loaded and validated successfully")
            
            # Load LLM configuration with Pydantic validation
            with open(f"{self.config_path}/llm.yaml", 'r') as f:
                llm_data = yaml.safe_load(f)
                self.llm_config = LLMConfig(**llm_data)
                logger.info("LLM configuration loaded and validated successfully")

            # Load response template configuration (simple YAML)
            try:
                with open(f"{self.config_path}/response_template.yaml", 'r') as f:
                    rt_data = yaml.safe_load(f) or {}
                    langs = (rt_data.get('languages') or {})
                    # Normalize to a flat dict { 'en': template_str, 'es': template_str }
                    self.response_templates = {
                        k: (v.get('response_format') if isinstance(v, dict) else str(v))
                        for k, v in langs.items()
                        if v is not None
                    }
                    logger.info("Response templates loaded successfully")
            except FileNotFoundError:
                logger.warning("response_template.yaml not found; using empty response templates")
                
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            raise
    
    def _initialize_components(self):
        """Initialize all service components"""
        try:
            # Initialize language detector
            confidence_threshold = self.prompt_config.confidence_threshold
            self.language_detector = RobustLanguageDetector(confidence_threshold)
            logger.info("Language detector initialized successfully")
            
            # Initialize Jinja2 environment with a stable path
            base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/
            templates_dir = os.path.join(base_dir, 'templates')
            self.jinja_env = Environment(loader=FileSystemLoader(templates_dir))
            logger.info("Jinja2 environment initialized successfully")
            
            # Initialize Claude client
            self._initialize_client()
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _initialize_client(self):
        """Initialize Claude API client"""
        try:
            # Prefer new variable name; support legacy LLM_API_KEY for compatibility
            api_key = os.getenv('CLAUDE_API_KEY') or os.getenv('LLM_API_KEY')
            if not api_key:
                logger.warning("CLAUDE_API_KEY not set (LLM_API_KEY legacy not found) - using mock mode")
                self.client = None
                return
            
            self.client = Anthropic(api_key=api_key)
            logger.info("Claude API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Claude API client: {e}")
            raise
    
    def _get_rubric_content(self, language: Language) -> str:
        """Generate rubric content for prompts using new structure.

        Prepends a configurable title from `prompt.yaml` (rubric_title) to allow
        language-specific section headers without hardcoding them in templates.
        """
        try:
            lang_config = self.prompt_config.languages[language]
            rubric = lang_config.rubric
            
            # Title and labels from config (with sensible defaults)
            rubric_title = getattr(rubric, 'rubric_title', None) or "EVALUATION RUBRIC"
            scoring_label = getattr(rubric, 'scoring_scale_label', None) or "Scoring Scale"
            criteria_label = getattr(rubric, 'evaluation_criteria_label', None) or "Evaluation Criteria"

            rubric_content = f"{rubric_title}\n"
            rubric_content += f"{scoring_label}: {rubric.scores.min}-{rubric.scores.max}\n\n"
            rubric_content += f"{criteria_label}:\n"
            
            for criterion_key, criterion in rubric.criteria.items():
                weight_label = getattr(rubric, 'weight_label', None) or "Weight"
                description_label = getattr(rubric, 'description_label', None) or "Description"
                rubric_content += f"\n{criterion.name} ({weight_label}: {criterion.weight}%)\n"
                rubric_content += f"{description_label}: {criterion.description}\n"
            
            return rubric_content
            
        except Exception as e:
            logger.error(f"Error generating rubric content: {e}")
            raise
    
    def _generate_prompt(self, text_content: str, language: Language) -> str:
        """Generate prompt using Jinja2 template with new structure"""
        try:
            # Get language-specific configuration
            lang_config = self.prompt_config.languages[language]
            
            # Prepare template variables
            template_vars = {
                'context': lang_config.context.context_text,
                'request': lang_config.request.request_text,
                'text_content': text_content,
                'rubric_content': self._get_rubric_content(language),
                'response_template': self._get_response_template(language)
            }
            
            # Render template
            template = self.jinja_env.get_template('evaluation_prompt.j2')
            prompt = template.render(**template_vars)
            
            logger.info(f"Prompt generated successfully for language: {language}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            raise

    def _get_response_template(self, language: Language) -> str:
        """Return the response JSON example/template for the given language.

        Falls back to English if the specific language is not present, and
        to an empty JSON object if nothing is configured.
        """
        try:
            lang_key = getattr(language, 'value', None) or str(language)
            if lang_key in self.response_templates:
                return self.response_templates[lang_key]
            if 'en' in self.response_templates:
                return self.response_templates['en']
            return "{}"
        except Exception as e:
            logger.error(f"Failed to obtain response template: {e}")
            return "{}"
    
    def evaluate_text_with_llm(self, text_content: str) -> Dict[str, Any]:
        """
        Evaluate text using LLM with language detection and enhanced prompt generation
        
        Args:
            text_content: Text to evaluate
            
        Returns:
            Dictionary containing evaluation results and metadata
        """
        start_time = time.time()
        
        try:
            # Detect language
            detection_result = self.language_detector.detect_language(text_content)
            detected_language = detection_result.language
            
            # Use detected language or fallback to default
            if detected_language == Language.UNKNOWN:
                detected_language = Language(self.prompt_config.default_language)
                logger.warning(f"Language detection failed, using default: {detected_language}")
            
            # Generate language-appropriate prompt
            prompt = self._generate_prompt(text_content, detected_language)
            
            # Get LLM response
            if self.client:
                # Real API call
                response = self._call_claude_api(prompt)
            else:
                # Mock response for development
                response = self._generate_mock_response(detected_language)
            
            # Parse and validate response
            parsed_response = self._parse_llm_response(response, detected_language)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Add metadata
            result = {
                **parsed_response,
                "metadata": {
                    "language_detection": {
                        "detected_language": detected_language.value,
                        "confidence": detection_result.confidence,
                        "method": detection_result.method.value
                    },
                    "processing_time": processing_time,
                    "prompt_length": len(prompt),
                    "response_length": len(response) if response else 0,
                    "llm_model": self.llm_config.provider.get('model', 'claude-3-haiku-20240307') if self.llm_config else 'unknown',
                    "raw_prompt": prompt,
                    "raw_response": response if response else ""
                }
            }
            
            logger.info(f"Evaluation completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Evaluation failed after {processing_time:.2f}s: {e}")
            raise
    
    def _call_claude_api(self, prompt: str) -> str:
        """Call Claude API with the generated prompt"""
        try:
            # Get model from configuration
            model = self.llm_config.provider.get('model', 'claude-3-haiku-20240307')
            max_tokens = self.llm_config.api_configuration.get('max_tokens', 4000)
            temperature = self.llm_config.api_configuration.get('temperature', 0.1)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _generate_mock_response(self, language: Language) -> str:
        """Generate mock response for development/testing"""
        if language == Language.ES:
            return json.dumps({
                "overall_score": 4.2,
                "strengths": [
                    "Resumen ejecutivo claro con estructura lógica",
                    "Argumentos sólidos basados en evidencia",
                    "Uso efectivo de métricas financieras"
                ],
                "opportunities": [
                    "Fortalecer estrategias de mitigación de riesgos",
                    "Agregar cronograma de implementación más específico"
                ],
                "rubric_scores": {
                    "structure": {"score": 4, "justification": "Organización clara con flujo lógico"},
                    "arguments_and_evidence": {"score": 5, "justification": "Evidencia sólida de fuentes creíbles"},
                    "strategic_alignment": {"score": 4, "justification": "Buena alineación estratégica"},
                    "implementation_and_risks": {"score": 3, "justification": "Plan de implementación básico"}
                },
                "segment_feedback": [
                    {
                        "segment": "El resumen ejecutivo...",
                        "comment": "Apertura sólida que establece la oportunidad",
                        "questions": ["¿Cómo podría ser más convincente?"],
                        "suggestions": ["Agregar contexto de mercado"]
                    }
                ]
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "overall_score": 4.2,
                "strengths": [
                    "Clear executive summary with logical structure",
                    "Strong evidence-based arguments with credible sources",
                    "Effective use of financial metrics"
                ],
                "opportunities": [
                    "Strengthen risk mitigation strategies",
                    "Add more specific implementation timeline"
                ],
                "rubric_scores": {
                    "structure": {"score": 4, "justification": "Clear organization with logical flow"},
                    "arguments_and_evidence": {"score": 5, "justification": "Strong evidence from credible sources"},
                    "strategic_alignment": {"score": 4, "justification": "Good strategic alignment"},
                    "implementation_and_risks": {"score": 3, "justification": "Basic implementation plan"}
                },
                "segment_feedback": [
                    {
                        "segment": "The executive summary...",
                        "comment": "Strong opening that states the opportunity",
                        "questions": ["How could this be more compelling?"],
                        "suggestions": ["Add market context"]
                    }
                ]
            })
    
    def _parse_llm_response(self, response: str, language: Language) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            # Validate required fields
            required_fields = ['overall_score', 'strengths', 'opportunities', 'rubric_scores', 'segment_feedback']
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate rubric scores structure
            expected_criteria = ['structure', 'arguments_and_evidence', 'strategic_alignment', 'implementation_and_risks']
            for criterion in expected_criteria:
                if criterion not in parsed['rubric_scores']:
                    raise ValueError(f"Missing rubric criterion: {criterion}")
                
                score_data = parsed['rubric_scores'][criterion]
                if 'score' not in score_data or 'justification' not in score_data:
                    raise ValueError(f"Invalid score data for criterion: {criterion}")
                
                score = score_data['score']
                if not isinstance(score, int) or score < 1 or score > 5:
                    raise ValueError(f"Invalid score for {criterion}: {score}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Response validation error: {e}")
            raise
    
    def get_language_detection_summary(self, text: str) -> Dict[str, Any]:
        """Get comprehensive language detection summary"""
        if self.language_detector:
            return self.language_detector.get_detection_summary(text)
        else:
            return {"error": "Language detector not initialized"}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        try:
            # Validate prompt configuration
            prompt_valid = self.prompt_config is not None
            
            # Validate LLM configuration
            llm_valid = self.llm_config is not None
            
            # Validate language detector
            detector_valid = self.language_detector is not None
            
            # Validate Jinja2 environment
            jinja_valid = self.jinja_env is not None
            
            # Validate Claude client
            client_valid = self.client is not None
            
            return {
                "valid": all([prompt_valid, llm_valid, detector_valid, jinja_valid]),
                "components": {
                    "prompt_config": prompt_valid,
                    "llm_config": llm_valid,
                    "language_detector": detector_valid,
                    "jinja2_env": jinja_valid,
                    "claude_client": client_valid
                },
                "supported_languages": [lang.value for lang in self.prompt_config.languages.keys()] if self.prompt_config else [],
                "default_language": self.prompt_config.default_language.value if self.prompt_config else None,
                "model": self.llm_config.provider.get('model', 'claude-3-haiku-20240307') if self.llm_config else 'unknown'
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
