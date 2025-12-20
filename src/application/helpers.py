"""
Application Layer - Helpers
============================

Helper utilities for application services.
"""

from pathlib import Path
from infrastructure.config import ConfigManager


# Global config manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """
    Get or create global ConfigManager instance.
    
    Returns:
        ConfigManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        # Determine config directory
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        _config_manager = ConfigManager(config_dir)
    
    return _config_manager
