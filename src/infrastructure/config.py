"""
Configuration Management Module
================================

Manages loading and validation of JSON configuration files for the mosquito
population simulator. Provides typed access to simulation parameters, species
biology, and environmental conditions.

Author: Mosquito Simulation System
Date: January 2026
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Simulation parameters configuration."""
    default_days: int
    time_step: int
    random_seed: Optional[int]
    stochastic_mode: bool


@dataclass
class LifeStageConfig:
    """Life stage biological parameters."""
    duration_min: int
    duration_max: int
    survival_to_next: Optional[float] = None
    survival_daily: Optional[float] = None
    is_predatory: bool = False
    predation_rate: Optional[int] = None


@dataclass
class ReproductionConfig:
    """Reproduction parameters for a species."""
    eggs_per_batch_min: int
    eggs_per_batch_max: int
    oviposition_events: int
    min_age_reproduction_days: int


@dataclass
class EnvironmentalSensitivity:
    """Environmental sensitivity parameters."""
    optimal_temperature_min: float
    optimal_temperature_max: float
    lethal_temperature_min: float
    lethal_temperature_max: float
    optimal_humidity: float


@dataclass
class PredationConfig:
    """Predation-specific parameters."""
    attack_rate: float
    handling_time: float
    prey_stages: List[str]


@dataclass
class SpeciesConfig:
    """Complete species configuration."""
    species_id: str
    display_name: str
    life_stages: Dict[str, LifeStageConfig]
    reproduction: ReproductionConfig
    environmental_sensitivity: Optional[EnvironmentalSensitivity] = None
    predation: Optional[PredationConfig] = None


@dataclass
class EnvironmentConfig:
    """Environmental conditions configuration."""
    temperature: float
    humidity: float
    carrying_capacity: int
    water_availability: float


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigManager:
    """
    Central configuration manager for the simulation system.
    
    Loads and validates JSON configuration files, providing typed access
    to all simulation parameters. Handles default values and validates
    data integrity.
    
    Attributes:
        config_dir: Root directory for configuration files
        default_config: Main simulation configuration
        species_configs: Dictionary of loaded species configurations
        environment_config: Environmental parameters
    """
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Path to configuration directory. If None, uses
                       default '../config' relative to project root.
        
        Raises:
            ConfigurationError: If config directory doesn't exist
        """
        if config_dir is None:
            # Determine config directory relative to this file
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise ConfigurationError(
                f"Configuration directory not found: {self.config_dir}"
            )
        
        self.default_config: Optional[Dict[str, Any]] = None
        self.species_configs: Dict[str, SpeciesConfig] = {}
        self.environment_config: Optional[EnvironmentConfig] = None
        
        # Load all configurations
        self._load_all_configs()
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a JSON file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Parsed JSON data as dictionary
        
        Raises:
            ConfigurationError: If file doesn't exist or JSON is invalid
        """
        if not file_path.exists():
            raise ConfigurationError(f"Config file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in {file_path}: {str(e)}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Error reading {file_path}: {str(e)}"
            )
    
    def _load_all_configs(self):
        """Load all configuration files."""
        # Load main configuration
        self._load_default_config()
        
        # Load species configurations
        if self.default_config and 'species_configs' in self.default_config:
            for species_file in self.default_config['species_configs']:
                species_path = self.config_dir / species_file
                self._load_species_config(species_path)
        
        # Load environment configuration
        if self.default_config and 'environment_config' in self.default_config:
            env_path = self.config_dir / self.default_config['environment_config']
            self._load_environment_config(env_path)
    
    def _load_default_config(self):
        """Load default simulation configuration."""
        config_path = self.config_dir / "default_config.json"
        self.default_config = self._load_json_file(config_path)
        
        # Validate required fields
        required_fields = ['simulation', 'initial_populations']
        for field in required_fields:
            if field not in self.default_config:
                raise ConfigurationError(
                    f"Missing required field '{field}' in default_config.json"
                )
    
    def _load_species_config(self, file_path: Path):
        """
        Load and parse species configuration.
        
        Args:
            file_path: Path to species JSON file
        """
        data = self._load_json_file(file_path)
        
        # Validate required fields
        if 'species_id' not in data:
            raise ConfigurationError(
                f"Missing 'species_id' in {file_path}"
            )
        
        species_id = data['species_id']
        
        # Parse life stages
        life_stages = {}
        for stage_name, stage_data in data.get('life_stages', {}).items():
            duration = stage_data.get('duration_days', {})
            life_stages[stage_name] = LifeStageConfig(
                duration_min=duration.get('min', 1),
                duration_max=duration.get('max', 1),
                survival_to_next=stage_data.get('survival_to_next'),
                survival_daily=stage_data.get('survival_daily'),
                is_predatory=stage_data.get('is_predatory', False),
                predation_rate=stage_data.get('predation_rate')
            )
        
        # Parse reproduction
        repro_data = data.get('reproduction', {})
        eggs_range = repro_data.get('eggs_per_batch', {})
        reproduction = ReproductionConfig(
            eggs_per_batch_min=eggs_range.get('min', 50),
            eggs_per_batch_max=eggs_range.get('max', 100),
            oviposition_events=repro_data.get('oviposition_events', 1),
            min_age_reproduction_days=repro_data.get('min_age_reproduction_days', 3)
        )
        
        # Parse environmental sensitivity (optional)
        env_sens = None
        if 'environmental_sensitivity' in data:
            env_data = data['environmental_sensitivity']
            opt_temp = env_data.get('optimal_temperature', {})
            leth_temp = env_data.get('lethal_temperature', {})
            env_sens = EnvironmentalSensitivity(
                optimal_temperature_min=opt_temp.get('min', 20),
                optimal_temperature_max=opt_temp.get('max', 30),
                lethal_temperature_min=leth_temp.get('min', 0),
                lethal_temperature_max=leth_temp.get('max', 50),
                optimal_humidity=env_data.get('optimal_humidity', 70)
            )
        
        # Parse predation config (optional)
        pred_config = None
        if 'predation' in data:
            pred_data = data['predation']
            func_resp = pred_data.get('functional_response', {})
            pred_config = PredationConfig(
                attack_rate=func_resp.get('attack_rate', 0.5),
                handling_time=func_resp.get('handling_time', 0.1),
                prey_stages=pred_data.get('prey_stages', [])
            )
        
        # Create species config object
        species_config = SpeciesConfig(
            species_id=species_id,
            display_name=data.get('display_name', species_id),
            life_stages=life_stages,
            reproduction=reproduction,
            environmental_sensitivity=env_sens,
            predation=pred_config
        )
        
        self.species_configs[species_id] = species_config
    
    def _load_environment_config(self, file_path: Path):
        """
        Load environment configuration.
        
        Args:
            file_path: Path to environment JSON file
        """
        data = self._load_json_file(file_path)
        
        self.environment_config = EnvironmentConfig(
            temperature=data.get('temperature', 27.0),
            humidity=data.get('humidity', 75.0),
            carrying_capacity=data.get('carrying_capacity', 10000),
            water_availability=data.get('water_availability', 1.0)
        )
    
    # ========== PUBLIC GETTER METHODS ==========
    
    def get_simulation_config(self) -> SimulationConfig:
        """
        Get simulation parameters.
        
        Returns:
            SimulationConfig object with typed parameters
        
        Raises:
            ConfigurationError: If default config not loaded
        """
        if not self.default_config:
            raise ConfigurationError("Default configuration not loaded")
        
        sim_data = self.default_config['simulation']
        return SimulationConfig(
            default_days=sim_data.get('default_days', 365),
            time_step=sim_data.get('time_step', 1),
            random_seed=sim_data.get('random_seed'),
            stochastic_mode=sim_data.get('stochastic_mode', True)
        )
    
    def get_initial_populations(self) -> Dict[str, Dict[str, int]]:
        """
        Get initial population counts for all species and stages.
        
        Returns:
            Dictionary: {species_id: {stage: count}}
        
        Raises:
            ConfigurationError: If default config not loaded
        """
        if not self.default_config:
            raise ConfigurationError("Default configuration not loaded")
        
        return self.default_config.get('initial_populations', {})
    
    def get_species_config(self, species_id: str) -> SpeciesConfig:
        """
        Get configuration for a specific species.
        
        Args:
            species_id: Species identifier (e.g., 'aedes_aegypti')
        
        Returns:
            SpeciesConfig object
        
        Raises:
            ConfigurationError: If species not found
        """
        if species_id not in self.species_configs:
            raise ConfigurationError(
                f"Species '{species_id}' not found in loaded configurations"
            )
        
        return self.species_configs[species_id]
    
    def get_all_species_ids(self) -> List[str]:
        """
        Get list of all loaded species IDs.
        
        Returns:
            List of species identifiers
        """
        return list(self.species_configs.keys())
    
    def get_environment_config(self) -> EnvironmentConfig:
        """
        Get environment configuration.
        
        Returns:
            EnvironmentConfig object
        
        Raises:
            ConfigurationError: If environment config not loaded
        """
        if not self.environment_config:
            raise ConfigurationError("Environment configuration not loaded")
        
        return self.environment_config
    
    def get_life_stage_duration(
        self, 
        species_id: str, 
        stage: str
    ) -> tuple[int, int]:
        """
        Get duration range for a life stage.
        
        Args:
            species_id: Species identifier
            stage: Life stage name
        
        Returns:
            Tuple of (min_days, max_days)
        
        Raises:
            ConfigurationError: If species or stage not found
        """
        species = self.get_species_config(species_id)
        
        if stage not in species.life_stages:
            raise ConfigurationError(
                f"Stage '{stage}' not found for species '{species_id}'"
            )
        
        stage_config = species.life_stages[stage]
        return (stage_config.duration_min, stage_config.duration_max)
    
    def get_survival_rate(
        self, 
        species_id: str, 
        stage: str
    ) -> float:
        """
        Get survival rate for a life stage.
        
        Args:
            species_id: Species identifier
            stage: Life stage name
        
        Returns:
            Survival rate [0.0-1.0]
        
        Raises:
            ConfigurationError: If species or stage not found
        """
        species = self.get_species_config(species_id)
        
        if stage not in species.life_stages:
            raise ConfigurationError(
                f"Stage '{stage}' not found for species '{species_id}'"
            )
        
        stage_config = species.life_stages[stage]
        
        # Return survival_to_next for larval stages, survival_daily for adults
        if stage_config.survival_to_next is not None:
            return stage_config.survival_to_next
        elif stage_config.survival_daily is not None:
            return stage_config.survival_daily
        else:
            return 1.0  # Default: 100% survival if not specified
    
    def is_predatory_stage(self, species_id: str, stage: str) -> bool:
        """
        Check if a life stage is predatory.
        
        Args:
            species_id: Species identifier
            stage: Life stage name
        
        Returns:
            True if stage is predatory, False otherwise
        """
        try:
            species = self.get_species_config(species_id)
            if stage in species.life_stages:
                return species.life_stages[stage].is_predatory
        except ConfigurationError:
            pass
        
        return False
    
    def get_predation_rate(self, species_id: str, stage: str) -> Optional[int]:
        """
        Get predation rate for a predatory stage.
        
        Args:
            species_id: Species identifier
            stage: Life stage name
        
        Returns:
            Predation rate (prey consumed per day) or None if not predatory
        """
        try:
            species = self.get_species_config(species_id)
            if stage in species.life_stages:
                return species.life_stages[stage].predation_rate
        except ConfigurationError:
            pass
        
        return None
    
    def reload_configs(self):
        """
        Reload all configuration files from disk.
        
        Useful for dynamic config updates during runtime.
        """
        self.default_config = None
        self.species_configs.clear()
        self.environment_config = None
        self._load_all_configs()
    
    def validate_all(self) -> List[str]:
        """
        Validate all loaded configurations.
        
        Returns:
            List of validation warnings/errors (empty if all valid)
        """
        warnings = []
        
        # Check simulation config
        try:
            sim_config = self.get_simulation_config()
            if sim_config.default_days <= 0:
                warnings.append("Simulation days must be positive")
            if sim_config.time_step <= 0:
                warnings.append("Time step must be positive")
        except Exception as e:
            warnings.append(f"Simulation config error: {str(e)}")
        
        # Check species configs
        for species_id in self.get_all_species_ids():
            species = self.species_configs[species_id]
            
            # Validate life stages
            if not species.life_stages:
                warnings.append(f"{species_id}: No life stages defined")
            
            for stage_name, stage_config in species.life_stages.items():
                if stage_config.duration_min > stage_config.duration_max:
                    warnings.append(
                        f"{species_id}.{stage_name}: min duration > max duration"
                    )
                
                if stage_config.survival_to_next is not None:
                    if not (0.0 <= stage_config.survival_to_next <= 1.0):
                        warnings.append(
                            f"{species_id}.{stage_name}: survival rate out of range [0,1]"
                        )
            
            # Validate reproduction
            if species.reproduction.eggs_per_batch_min > species.reproduction.eggs_per_batch_max:
                warnings.append(
                    f"{species_id}: min eggs > max eggs"
                )
        
        # Check initial populations match species configs
        init_pops = self.get_initial_populations()
        for species_id in init_pops.keys():
            if species_id not in self.species_configs:
                warnings.append(
                    f"Initial population defined for unknown species: {species_id}"
                )
        
        return warnings


# ========== CONVENIENCE FUNCTIONS ==========

def load_default_config() -> ConfigManager:
    """
    Load configuration using default paths.
    
    Returns:
        Initialized ConfigManager instance
    
    Raises:
        ConfigurationError: If configuration loading fails
    """
    return ConfigManager()


def load_config_from_dir(config_dir: Union[str, Path]) -> ConfigManager:
    """
    Load configuration from specified directory.
    
    Args:
        config_dir: Path to configuration directory
    
    Returns:
        Initialized ConfigManager instance
    
    Raises:
        ConfigurationError: If configuration loading fails
    """
    return ConfigManager(config_dir)
