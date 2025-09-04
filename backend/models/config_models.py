"""
Configuration Models for Memo AI Coach
Pydantic models for type-safe configuration validation
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class Language(str, Enum):
    """Supported languages"""
    EN = "en"
    ES = "es"
    UNKNOWN = "unknown"

class RubricCriterion(BaseModel):
    """Individual rubric criterion with weight validation"""
    name: str = Field(..., description="Criterion name")
    description: str = Field(..., description="Criterion description")
    weight: int = Field(..., ge=1, le=100, description="Criterion weight (1-100)")
    
    @validator('weight')
    def validate_weight(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Weight must be between 1 and 100')
        return v

class RubricScores(BaseModel):
    """Scoring range configuration"""
    min: int = Field(1, ge=1, le=5, description="Minimum score")
    max: int = Field(5, ge=1, le=5, description="Maximum score")
    
    @validator('max')
    def validate_max_score(cls, v, values):
        if 'min' in values and v < values['min']:
            raise ValueError('Max score must be greater than or equal to min score')
        return v

class RubricConfig(BaseModel):
    """Rubric configuration with 4 core criteria"""
    scores: RubricScores = Field(..., description="Scoring range configuration")
    criteria: Dict[str, RubricCriterion] = Field(..., description="Rubric criteria")
    rubric_title: Optional[str] = Field(None, description="Localized title for the rubric section")
    scoring_scale_label: Optional[str] = Field(None, description="Localized label for scoring scale")
    evaluation_criteria_label: Optional[str] = Field(None, description="Localized label for evaluation criteria section")
    weight_label: Optional[str] = Field(None, description="Localized label for criterion weight")
    description_label: Optional[str] = Field(None, description="Localized label for criterion description")
    
    @validator('criteria')
    def validate_criteria_weights(cls, v):
        """Ensure total weights equal exactly 100%"""
        total_weight = sum(criterion.weight for criterion in v.values())
        if total_weight != 100:
            raise ValueError(f'Total criteria weights must equal 100%, got {total_weight}%')
        return v
    
    @validator('criteria')
    def validate_criteria_count(cls, v):
        """Ensure exactly 4 criteria"""
        if len(v) != 4:
            raise ValueError(f'Must have exactly 4 criteria, got {len(v)}')
        return v

class ContextConfig(BaseModel):
    """Context configuration for prompts"""
    context_text: str = Field(..., description="Context text for the LLM")

class RequestConfig(BaseModel):
    """Request configuration for prompts"""
    request_text: str = Field(..., description="Request text for the LLM")

class PromptLanguageConfig(BaseModel):
    """Language-specific prompt configuration"""
    context: ContextConfig = Field(..., description="Context configuration")
    request: RequestConfig = Field(..., description="Request configuration")
    rubric: RubricConfig = Field(..., description="Rubric configuration")

class PromptConfig(BaseModel):
    """Complete prompt configuration with language support"""
    languages: Dict[Language, PromptLanguageConfig] = Field(..., description="Language-specific configurations")
    default_language: Language = Field(Language.EN, description="Default language")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Language detection confidence threshold")
    
    @validator('languages')
    def validate_languages(cls, v):
        """Ensure at least English and Spanish are configured"""
        required_languages = {Language.EN, Language.ES}
        configured_languages = set(v.keys())
        if not required_languages.issubset(configured_languages):
            missing = required_languages - configured_languages
            raise ValueError(f'Missing required languages: {missing}')
        return v

class LLMConfig(BaseModel):
    """LLM service configuration"""
    provider: Dict[str, Any] = Field(..., description="LLM provider configuration")
    api_configuration: Dict[str, Any] = Field(..., description="API configuration")
    request_settings: Dict[str, Any] = Field(..., description="Request settings")
    response_handling: Dict[str, Any] = Field(..., description="Response handling configuration")
    performance_optimization: Dict[str, Any] = Field(..., description="Performance optimization settings")
    monitoring: Dict[str, Any] = Field(..., description="Monitoring configuration")
    fallback_configuration: Dict[str, Any] = Field(..., description="Fallback configuration")
    cost_management: Dict[str, Any] = Field(..., description="Cost management settings")
    security: Dict[str, Any] = Field(..., description="Security settings")
    model_specific_settings: Dict[str, Any] = Field(..., description="Model-specific settings")
    validation_rules: Dict[str, Any] = Field(..., description="Validation rules")
    environment_specific: Dict[str, Any] = Field(..., description="Environment-specific settings")

class AuthConfig(BaseModel):
    """Authentication configuration"""
    session_timeout_minutes: int = Field(..., ge=1, description="Session timeout in minutes")
    max_login_attempts: int = Field(..., ge=1, description="Maximum login attempts")
    lockout_duration_minutes: int = Field(..., ge=1, description="Lockout duration in minutes")
    password_min_length: int = Field(..., ge=6, description="Minimum password length")
    security_settings: Dict[str, Any] = Field(..., description="Additional security settings")

# Configuration validation functions
def validate_prompt_config(config_data: dict) -> PromptConfig:
    """Validate prompt configuration data"""
    return PromptConfig(**config_data)

def validate_llm_config(config_data: dict) -> LLMConfig:
    """Validate LLM configuration data"""
    return LLMConfig(**config_data)

def validate_auth_config(config_data: dict) -> AuthConfig:
    """Validate authentication configuration data"""
    return AuthConfig(**config_data)

def validate_all_configs(prompt_data: dict, llm_data: dict, auth_data: dict) -> Dict[str, Any]:
    """Validate all configuration files"""
    try:
        prompt_config = validate_prompt_config(prompt_data)
        llm_config = validate_llm_config(llm_data)
        auth_config = validate_auth_config(auth_data)
        
        return {
            "prompt": prompt_config,
            "llm": llm_config,
            "auth": auth_config,
            "valid": True
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
