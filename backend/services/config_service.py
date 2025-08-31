"""
Configuration management service for Memo AI Coach
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigService:
    """Configuration management service with validation and environment overrides"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration service"""
        if config_dir is None:
            # In container, config is mounted at /app/config
            # For development, fallback to ../config
            if os.path.exists('/app/config'):
                config_dir = '/app/config'
            else:
                config_dir = os.getenv('CONFIG_DIR', '../config')
        
        self.config_dir = Path(config_dir)
        self.configs = {}
        self.last_loaded = None
        
        logger.info(f"Configuration service initialized with directory: {self.config_dir}")
    
    def load_all_configs(self) -> Dict[str, Any]:
        """Load all configuration files with validation"""
        try:
            configs = {}
            
            # Load each configuration file
            config_files = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml', 'deployment.yaml']
            
            for filename in config_files:
                file_path = self.config_dir / filename
                if file_path.exists():
                    config = self._load_yaml_file(file_path)
                    configs[filename] = config
                    logger.info(f"Loaded configuration: {filename}")
                else:
                    logger.error(f"Configuration file not found: {file_path}")
                    raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            # Validate configurations
            self._validate_configs(configs)
            
            # Apply environment overrides
            configs = self._apply_environment_overrides(configs)
            
            self.configs = configs
            self.last_loaded = datetime.utcnow()
            
            logger.info("All configurations loaded and validated successfully")
            return configs
            
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            raise
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a single YAML configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                raise ValueError(f"Empty or invalid YAML file: {file_path}")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise
    
    def _validate_configs(self, configs: Dict[str, Any]) -> None:
        """Validate all configuration files"""
        try:
            # Validate rubric.yaml
            if 'rubric.yaml' in configs:
                self._validate_rubric_config(configs['rubric.yaml'])
            
            # Validate prompt.yaml
            if 'prompt.yaml' in configs:
                self._validate_prompt_config(configs['prompt.yaml'])
            
            # Validate llm.yaml
            if 'llm.yaml' in configs:
                self._validate_llm_config(configs['llm.yaml'])
            
            # Validate auth.yaml
            if 'auth.yaml' in configs:
                self._validate_auth_config(configs['auth.yaml'])
            
            # Validate deployment.yaml
            if 'deployment.yaml' in configs:
                self._validate_deployment_config(configs['deployment.yaml'])
            
            logger.info("All configurations validated successfully")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _validate_rubric_config(self, config: Dict[str, Any]) -> None:
        """Validate rubric configuration"""
        required_fields = ['rubric', 'scoring_categories']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in rubric.yaml")
        
        # Validate rubric section
        rubric = config['rubric']
        required_rubric_fields = ['name', 'description', 'total_weight', 'scoring_scale', 'criteria']
        for field in required_rubric_fields:
            if field not in rubric:
                raise ValueError(f"Missing required field '{field}' in rubric section")
    
    def _validate_prompt_config(self, config: Dict[str, Any]) -> None:
        """Validate prompt configuration"""
        required_fields = ['templates', 'instructions']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in prompt.yaml")
    
    def _validate_llm_config(self, config: Dict[str, Any]) -> None:
        """Validate LLM configuration"""
        required_fields = ['provider', 'api_configuration']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in llm.yaml")
    
    def _validate_auth_config(self, config: Dict[str, Any]) -> None:
        """Validate authentication configuration"""
        required_fields = ['session_management', 'authentication_methods']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in auth.yaml")
    
    def _validate_deployment_config(self, config: Dict[str, Any]) -> None:
        """Validate deployment configuration"""
        required_fields = ['traefik', 'database', 'frontend']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in deployment.yaml")
    
    def _apply_environment_overrides(self, configs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configurations"""
        try:
            # Get the target environment
            app_env = os.environ.get('APP_ENV', 'production').lower()
            logger.info(f"Applying environment-specific configuration for: {app_env}")
            
            # Apply environment-specific configurations
            configs = self._apply_environment_specific_configs(configs, app_env)
            
            # Apply LLM API key override
            if 'LLM_API_KEY' in os.environ:
                if 'llm.yaml' in configs and 'api_configuration' in configs['llm.yaml']:
                    configs['llm.yaml']['api_configuration']['api_key'] = os.environ['LLM_API_KEY']
                    logger.info("Applied LLM API key from environment")
            
            # Apply session timeout override only if explicitly set (allows YAML defaults to work)
            if 'SESSION_TIMEOUT' in os.environ and os.environ['SESSION_TIMEOUT'].strip():
                if 'auth.yaml' in configs and 'session_management' in configs['auth.yaml']:
                    configs['auth.yaml']['session_management']['session_timeout'] = int(os.environ['SESSION_TIMEOUT'])
                    logger.info("Applied session timeout override from environment")
            
            # Apply debug mode override only if explicitly set (allows YAML defaults to work)
            if 'DEBUG_MODE' in os.environ and os.environ['DEBUG_MODE'].strip():
                debug_mode = os.environ['DEBUG_MODE'].lower() == 'true'
                if 'auth.yaml' in configs and 'security_settings' in configs['auth.yaml']:
                    configs['auth.yaml']['security_settings']['debug_mode'] = debug_mode
                    logger.info("Applied debug mode override from environment")
            
            return configs
            
        except Exception as e:
            logger.error(f"Environment override application failed: {e}")
            raise
    
    def _apply_environment_specific_configs(self, configs: Dict[str, Any], app_env: str) -> Dict[str, Any]:
        """Apply environment-specific configuration settings"""
        try:
            # Apply auth.yaml environment-specific settings
            if 'auth.yaml' in configs and 'environment_specific' in configs['auth.yaml']:
                env_config = configs['auth.yaml']['environment_specific'].get(app_env, {})
                if env_config:
                    # Apply debug mode
                    if 'debug_mode' in env_config:
                        if 'security_settings' not in configs['auth.yaml']:
                            configs['auth.yaml']['security_settings'] = {}
                        configs['auth.yaml']['security_settings']['debug_mode'] = env_config['debug_mode']
                    
                    # Apply session timeout
                    if 'session_timeout' in env_config:
                        if 'session_management' not in configs['auth.yaml']:
                            configs['auth.yaml']['session_management'] = {}
                        configs['auth.yaml']['session_management']['session_timeout'] = env_config['session_timeout']
                        logger.info(f"Applied session timeout: {env_config['session_timeout']} seconds for {app_env} environment")
                    
                    # Apply rate limiting
                    if 'rate_limiting' in env_config:
                        if 'rate_limiting' not in configs['auth.yaml']:
                            configs['auth.yaml']['rate_limiting'] = {}
                        configs['auth.yaml']['rate_limiting']['enabled'] = env_config['rate_limiting']
                    
                    # Apply secure cookies
                    if 'secure_cookies' in env_config:
                        if 'security_settings' not in configs['auth.yaml']:
                            configs['auth.yaml']['security_settings'] = {}
                        configs['auth.yaml']['security_settings']['secure_cookies'] = env_config['secure_cookies']
                    
                    logger.info(f"Applied {app_env} environment settings to auth.yaml")
            
            # Apply llm.yaml environment-specific settings
            if 'llm.yaml' in configs and 'environment_specific' in configs['llm.yaml']:
                env_config = configs['llm.yaml']['environment_specific'].get(app_env, {})
                if env_config:
                    # Apply debug mode
                    if 'debug_mode' in env_config:
                        if 'debug_settings' not in configs['llm.yaml']:
                            configs['llm.yaml']['debug_settings'] = {}
                        configs['llm.yaml']['debug_settings']['debug_mode'] = env_config['debug_mode']
                    
                    # Apply log level
                    if 'log_level' in env_config:
                        if 'logging' not in configs['llm.yaml']:
                            configs['llm.yaml']['logging'] = {}
                        configs['llm.yaml']['logging']['level'] = env_config['log_level']
                    
                    # Apply mock responses
                    if 'mock_responses' in env_config:
                        if 'debug_settings' not in configs['llm.yaml']:
                            configs['llm.yaml']['debug_settings'] = {}
                        configs['llm.yaml']['debug_settings']['mock_responses'] = env_config['mock_responses']
                    
                    # Apply cost tracking
                    if 'cost_tracking' in env_config:
                        if 'cost_management' not in configs['llm.yaml']:
                            configs['llm.yaml']['cost_management'] = {}
                        configs['llm.yaml']['cost_management']['track_costs'] = env_config['cost_tracking']
                    
                    # Apply target response time
                    if 'target_response_time' in env_config:
                        if 'performance' not in configs['llm.yaml']:
                            configs['llm.yaml']['performance'] = {}
                        configs['llm.yaml']['performance']['target_response_time'] = env_config['target_response_time']
                    
                    logger.info(f"Applied {app_env} environment settings to llm.yaml")
            
            return configs
            
        except Exception as e:
            logger.error(f"Environment-specific configuration application failed: {e}")
            raise
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration"""
        if not self.configs:
            self.load_all_configs()
        
        return self.configs.get(config_name)
    
    def get_rubric_config(self) -> Optional[Dict[str, Any]]:
        """Get rubric configuration"""
        return self.get_config('rubric.yaml')
    
    def get_prompt_config(self) -> Optional[Dict[str, Any]]:
        """Get prompt configuration"""
        return self.get_config('prompt.yaml')
    
    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        """Get LLM configuration"""
        return self.get_config('llm.yaml')
    
    def get_auth_config(self) -> Optional[Dict[str, Any]]:
        """Get authentication configuration"""
        return self.get_config('auth.yaml')
    
    def get_deployment_config(self) -> Optional[Dict[str, Any]]:
        """Get deployment configuration"""
        return self.get_config('deployment.yaml')
    
    def health_check(self) -> Dict[str, Any]:
        """Check configuration health and accessibility"""
        try:
            if not self.configs:
                self.load_all_configs()
            
            config_files = ['rubric.yaml', 'prompt.yaml', 'llm.yaml', 'auth.yaml', 'deployment.yaml']
            missing_configs = []
            
            for filename in config_files:
                if filename not in self.configs:
                    missing_configs.append(filename)
            
            if missing_configs:
                return {
                    "status": "unhealthy",
                    "error": f"Missing configurations: {missing_configs}",
                    "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
                }
            
            return {
                "status": "healthy",
                "configs_loaded": list(self.configs.keys()),
                "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None,
                "config_dir": str(self.config_dir)
            }
            
        except Exception as e:
            logger.error(f"Configuration health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
            }
    
    def reload_configs(self) -> Dict[str, Any]:
        """Reload all configurations"""
        try:
            self.configs = {}
            self.load_all_configs()
            return {
                "status": "success",
                "message": "Configurations reloaded successfully",
                "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
            }
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
            }

# Global configuration service instance
config_service = ConfigService()
