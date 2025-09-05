"""
Configuration Management Service for Memo AI Coach
Handles YAML configuration editing and validation
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import shutil
import tempfile
from .path_utils import resolve_config_dir_with_fallback

# Get logger for this module
logger = logging.getLogger(__name__)

class ConfigManager:
    """Service for managing YAML configuration files"""
    
    def __init__(self, config_path: str = None):
        """Initialize config manager with automatic path detection"""
        if config_path is None:
            config_path = resolve_config_dir_with_fallback()
        
        self.config_path = config_path
        self.config_files = {
            'prompt': 'prompt.yaml',
            'llm': 'llm.yaml',
            'auth': 'auth.yaml'
        }
        self.backup_dir = f"{config_path}/backups"
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_config_files(self) -> List[str]:
        """
        Get list of available configuration files
        
        Returns:
            List of configuration file names
        """
        return list(self.config_files.keys())
    
    def read_config_file(self, config_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Read configuration file content
        
        Args:
            config_name: Name of configuration file
            
        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            if config_name not in self.config_files:
                return False, None, f"Unknown configuration file: {config_name}"
            
            file_path = f"{self.config_path}/{self.config_files[config_name]}"
            
            if not os.path.exists(file_path):
                return False, None, f"Configuration file not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, content, None
            
        except Exception as e:
            logger.error(f"Failed to read configuration file {config_name}: {e}")
            return False, None, f"Failed to read configuration: {str(e)}"
    
    def validate_yaml(self, yaml_content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate YAML content
        
        Args:
            yaml_content: YAML content to validate
            
        Returns:
            Tuple of (valid, parsed_data, error_message)
        """
        try:
            parsed_data = yaml.safe_load(yaml_content)
            return True, parsed_data, None
        except yaml.YAMLError as e:
            logger.error(f"YAML validation failed: {e}")
            return False, None, f"Invalid YAML syntax: {str(e)}"
        except Exception as e:
            logger.error(f"YAML parsing failed: {e}")
            return False, None, f"YAML parsing error: {str(e)}"
    
    def validate_config_content(self, config_name: str, parsed_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration content based on file type
        
        Args:
            config_name: Name of configuration file
            parsed_data: Parsed configuration data
            
        Returns:
            Tuple of (valid, error_message)
        """
        try:
            if config_name == 'prompt':
                return self._validate_prompt_config(parsed_data)
            elif config_name == 'llm':
                return self._validate_llm_config(parsed_data)
            elif config_name == 'auth':
                return self._validate_auth_config(parsed_data)
            else:
                return True, None  # Unknown config type, assume valid
                
        except Exception as e:
            logger.error(f"Configuration validation failed for {config_name}: {e}")
            return False, f"Validation error: {str(e)}"
    
    # Removed rubric.yaml support; rubric is defined within prompt.yaml
    
    def _validate_prompt_config(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate prompt configuration"""
        try:
            if 'templates' not in data:
                return False, "Missing 'templates' section"
            
            templates = data['templates']
            if 'evaluation_prompt' not in templates:
                return False, "Missing 'evaluation_prompt' section"
            
            return True, None
            
        except Exception as e:
            return False, f"Prompt validation error: {str(e)}"
    
    def _validate_llm_config(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate LLM configuration"""
        try:
            if 'provider' not in data:
                return False, "Missing 'provider' section"
            
            provider = data['provider']
            if 'name' not in provider or 'model' not in provider:
                return False, "Provider must have 'name' and 'model' fields"
            
            return True, None
            
        except Exception as e:
            return False, f"LLM validation error: {str(e)}"
    
    def _validate_auth_config(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate authentication configuration"""
        try:
            if 'session_management' not in data:
                return False, "Missing 'session_management' section"
            
            if 'authentication_methods' not in data:
                return False, "Missing 'authentication_methods' section"
            
            return True, None
            
        except Exception as e:
            return False, f"Auth validation error: {str(e)}"
    
    def create_backup(self, config_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create backup of configuration file
        
        Args:
            config_name: Name of configuration file
            
        Returns:
            Tuple of (success, backup_path, error_message)
        """
        try:
            if config_name not in self.config_files:
                return False, None, f"Unknown configuration file: {config_name}"
            
            source_path = f"{self.config_path}/{self.config_files[config_name]}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{config_name}_{timestamp}.yaml"
            backup_path = f"{self.backup_dir}/{backup_filename}"
            
            shutil.copy2(source_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            
            return True, backup_path, None
            
        except Exception as e:
            logger.error(f"Failed to create backup for {config_name}: {e}")
            return False, None, f"Backup failed: {str(e)}"
    
    def write_config_file(self, config_name: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Write configuration file with validation
        
        Args:
            config_name: Name of configuration file
            content: New configuration content
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if config_name not in self.config_files:
                return False, f"Unknown configuration file: {config_name}"
            
            # Validate YAML syntax
            valid_yaml, parsed_data, yaml_error = self.validate_yaml(content)
            if not valid_yaml:
                return False, yaml_error
            
            # Validate configuration content
            valid_content, content_error = self.validate_config_content(config_name, parsed_data)
            if not valid_content:
                return False, content_error
            
            # Create backup before writing
            backup_success, backup_path, backup_error = self.create_backup(config_name)
            if not backup_success:
                logger.warning(f"Backup failed: {backup_error}")
            
            # Write new configuration
            file_path = f"{self.config_path}/{self.config_files[config_name]}"
            
            # Use temporary file for atomic write
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Atomic move
            shutil.move(temp_path, file_path)
            
            logger.info(f"Configuration file updated: {file_path}")
            return True, None
            
        except Exception as e:
            logger.error(f"Failed to write configuration file {config_name}: {e}")
            return False, f"Write failed: {str(e)}"
    
    def get_backups(self, config_name: str) -> List[Dict[str, Any]]:
        """
        Get list of backups for configuration file
        
        Args:
            config_name: Name of configuration file
            
        Returns:
            List of backup information
        """
        try:
            backups = []
            backup_pattern = f"{config_name}_*.yaml"
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(f"{config_name}_") and filename.endswith('.yaml'):
                    file_path = f"{self.backup_dir}/{filename}"
                    stat = os.stat(file_path)
                    
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to get backups for {config_name}: {e}")
            return []
    
    def restore_backup(self, config_name: str, backup_filename: str) -> Tuple[bool, Optional[str]]:
        """
        Restore configuration from backup
        
        Args:
            config_name: Name of configuration file
            backup_filename: Name of backup file to restore
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            backup_path = f"{self.backup_dir}/{backup_filename}"
            
            if not os.path.exists(backup_path):
                return False, f"Backup file not found: {backup_filename}"
            
            # Validate backup content
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            valid_yaml, parsed_data, yaml_error = self.validate_yaml(content)
            if not valid_yaml:
                return False, f"Invalid backup content: {yaml_error}"
            
            # Write backup content to configuration file
            return self.write_config_file(config_name, content)
            
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_filename}: {e}")
            return False, f"Restore failed: {str(e)}"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check configuration manager health
        
        Returns:
            Health status information
        """
        try:
            config_status = {}
            for config_name in self.config_files:
                success, content, error = self.read_config_file(config_name)
                config_status[config_name] = {
                    'exists': success,
                    'error': error if not success else None
                }
            
            return {
                "status": "healthy",
                "service": "configuration_manager",
                "config_files": config_status,
                "backup_dir": self.backup_dir,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Configuration manager health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "configuration_manager",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }

# Global config manager instance
config_manager = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager

def read_config_file(config_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Read configuration file content
    
    Args:
        config_name: Name of configuration file
        
    Returns:
        Tuple of (success, content, error_message)
    """
    manager = get_config_manager()
    return manager.read_config_file(config_name)

def write_config_file(config_name: str, content: str) -> Tuple[bool, Optional[str]]:
    """
    Write configuration file with validation
    
    Args:
        config_name: Name of configuration file
        content: New configuration content
        
    Returns:
        Tuple of (success, error_message)
    """
    manager = get_config_manager()
    return manager.write_config_file(config_name, content)
