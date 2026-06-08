"""
Configuration module for MiMi.
Supports both legacy and enhanced configuration systems.
"""

import os
import sys
from pathlib import Path

# Add both config managers to the module
from .config import ConfigManager, config_manager, get_config

active_config_manager = config_manager
get_active_config = get_config

def get_active_resolved_path(path_key: str):
    """Get resolved path (not available in legacy system)"""
    print(f"Warning: get_resolved_path not available in legacy config system")
    return None

def get_active_status():
    """Get status (minimal implementation for legacy system)"""
    return {
        "config_file": config_manager.config_path,
    }


# Convenience imports
__all__ = [
    # Core classes
    "ConfigManager",
    "EnhancedConfigManager",
    
    # Legacy system
    "config_manager",
    "get_config",
    "validate_config",
    
    # Enhanced system
    "enhanced_config_manager",
    "get_enhanced_config",
    "get_resolved_path",
    "validate_enhanced_config",
    "get_config_status",
    
    # Active system (based on environment)
    "active_config_manager",
    "get_active_config",
    "get_active_resolved_path",
    "validate_active_config",
    "get_active_status",
    "USE_ENHANCED_CONFIG",
]