"""
Infrastructure Layer
====================

Core infrastructure components for the mosquito population simulator.

Modules:
    - config: Configuration management (JSON loading and validation)
    - prolog_bridge: Python-Prolog interface via PySwip
"""

from .config import (
    ConfigManager,
    ConfigurationError,
    SimulationConfig,
    SpeciesConfig,
    EnvironmentConfig,
    load_default_config,
    load_config_from_dir
)

from .prolog_bridge import (
    PrologBridge,
    PrologBridgeError,
    create_prolog_bridge
)

__all__ = [
    'ConfigManager',
    'ConfigurationError',
    'SimulationConfig',
    'SpeciesConfig',
    'EnvironmentConfig',
    'load_default_config',
    'load_config_from_dir',
    'PrologBridge',
    'PrologBridgeError',
    'create_prolog_bridge'
]
