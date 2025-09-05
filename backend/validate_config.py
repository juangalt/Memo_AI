"""
Configuration validation script for Memo AI Coach
Validates all essential YAML configuration files with new structure
"""

import yaml
import os
import sys
import logging
from pathlib import Path
from services.path_utils import resolve_config_dir_with_fallback

# Get logger for this module
logger = logging.getLogger(__name__)

def validate_yaml_file(file_path, required_fields=None):
    """Validate a YAML configuration file"""
    try:
        logger.info(f"Validating {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            raise ValueError(f"Empty or invalid YAML file: {file_path}")
        
        if required_fields:
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        logger.info(f"✓ {file_path} - Valid")
        return True
        
    except Exception as e:
        logger.error(f"✗ {file_path} - Error: {e}")
        return False

# rubric.yaml has been removed from the system; no validation needed.

def validate_prompt_config(config):
    """Validate prompt.yaml with new context/request/rubric structure"""
    try:
        # Check languages section
        if 'languages' not in config:
            return False, "Missing languages section"
        
        # Check required languages
        required_languages = ['en', 'es']
        for lang in required_languages:
            if lang not in config['languages']:
                return False, f"Missing required language: {lang}"
            
            lang_config = config['languages'][lang]
            
            # Check context, request, and rubric sections
            for section in ['context', 'request', 'rubric']:
                if section not in lang_config:
                    return False, f"Missing {section} section in {lang} language"
            
            # Check rubric structure
            rubric = lang_config['rubric']
            if 'scores' not in rubric or 'criteria' not in rubric:
                return False, f"Missing scores or criteria in {lang} rubric"
            
            # Check scoring range
            scores = rubric['scores']
            if scores.get('min') != 1 or scores.get('max') != 5:
                return False, f"Invalid scoring range in {lang} rubric (should be 1-5)"
            
            # Check criteria count and weights
            criteria = rubric['criteria']
            if len(criteria) != 4:
                return False, f"Invalid criteria count in {lang} rubric (should be 4)"
            
            # Check weights sum to 100%
            total_weight = sum(criterion['weight'] for criterion in criteria.values())
            if total_weight != 100:
                return False, f"Invalid total weight in {lang} rubric (should be 100%, got {total_weight}%)"
        
        # Check default language and confidence threshold
        if 'default_language' not in config:
            return False, "Missing default_language"
        
        if 'confidence_threshold' not in config:
            return False, "Missing confidence_threshold"
        
        return True, "Valid"
        
    except Exception as e:
        return False, str(e)

def validate_llm_config(config):
    """Validate llm.yaml specific configuration"""
    try:
        # Check provider
        if 'provider' not in config:
            return False, "Missing provider section"
        
        # Check API configuration
        if 'api_configuration' not in config:
            return False, "Missing api_configuration section"
        
        # Check performance optimization
        if 'performance_optimization' not in config:
            return False, "Missing performance_optimization section"
        
        return True, "Valid"
        
    except Exception as e:
        return False, str(e)

def validate_auth_config(config):
    """Validate auth.yaml specific configuration"""
    try:
        # Check session management
        if 'session_management' not in config:
            return False, "Missing session_management section"
        
        # Check authentication methods
        if 'authentication_methods' not in config:
            return False, "Missing authentication_methods section"
        
        # Check security settings
        if 'security_settings' not in config:
            return False, "Missing security_settings section"
        
        # Validate session timeout
        session_mgmt = config['session_management']
        if 'session_timeout' not in session_mgmt:
            return False, "Missing session_timeout in session_management"
        
        return True, "Valid"
        
    except Exception as e:
        return False, str(e)

def validate_all_configs():
    """Validate all essential configuration files"""
    config_dir = resolve_config_dir_with_fallback()
    
    logger.info(f"Validating configuration files in: {config_dir}")
    
    # Define required configuration files and their validation functions
    config_files = {
        'prompt.yaml': {
            'required_fields': ['languages', 'default_language', 'confidence_threshold'],
            'validator': validate_prompt_config
        },
        'llm.yaml': {
            'required_fields': ['provider', 'api_configuration'],
            'validator': validate_llm_config
        },
        'auth.yaml': {
            'required_fields': ['session_management', 'authentication_methods'],
            'validator': validate_auth_config
        }
    }
    
    all_valid = True
    validation_results = {}
    
    for filename, validation_config in config_files.items():
        file_path = Path(config_dir) / filename
        
        if not file_path.exists():
            logger.error(f"✗ {file_path} - File not found")
            all_valid = False
            validation_results[filename] = "File not found"
            continue
        
        # Basic YAML validation
        if not validate_yaml_file(file_path, validation_config['required_fields']):
            all_valid = False
            validation_results[filename] = "Basic validation failed"
            continue
        
        # Load config for specific validation
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Specific validation
            validator = validation_config['validator']
            is_valid, message = validator(config)
            
            if is_valid:
                logger.info(f"✓ {filename} - {message}")
                validation_results[filename] = "Valid"
            else:
                logger.error(f"✗ {filename} - {message}")
                all_valid = False
                validation_results[filename] = message
                
        except Exception as e:
            logger.error(f"✗ {filename} - Validation error: {e}")
            all_valid = False
            validation_results[filename] = f"Validation error: {e}"
    
    # Print summary
    logger.info("\nConfiguration Validation Summary:")
    logger.info("=" * 50)
    for filename, result in validation_results.items():
        status = "✓" if result == "Valid" else "✗"
        logger.info(f"{status} {filename}: {result}")
    
    if all_valid:
        logger.info("\n✓ All configuration files are valid")
        return True
    else:
        logger.error("\n✗ Configuration validation failed")
        return False

def check_configuration_files():
    """Check if all required configuration files exist"""
    config_dir = resolve_config_dir_with_fallback()
    
    required_files = ['prompt.yaml', 'llm.yaml', 'auth.yaml']
    missing_files = []
    
    for filename in required_files:
        file_path = Path(config_dir) / filename
        if not file_path.exists():
            missing_files.append(filename)
    
    if missing_files:
        logger.error(f"Missing configuration files: {', '.join(missing_files)}")
        return False
    
    logger.info("All required configuration files found")
    return True

if __name__ == "__main__":
    print("Validating Memo AI Coach configuration files...")
    
    # Check if files exist
    if not check_configuration_files():
        print("✗ Configuration file check failed")
        sys.exit(1)
    
    # Validate all configurations
    if validate_all_configs():
        print("✓ Configuration validation completed successfully")
        sys.exit(0)
    else:
        print("✗ Configuration validation failed")
        sys.exit(1)
