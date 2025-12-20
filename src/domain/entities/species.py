"""
Species Entity Module
=====================

Represents a mosquito species with its biological characteristics
and behaviors. Wraps SpeciesConfig with domain logic.

Author: Mosquito Simulation System
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from infrastructure.config import SpeciesConfig, LifeStageConfig


class Species:
    """
    Represents a mosquito species with biological characteristics.
    
    This class wraps SpeciesConfig and provides domain-specific
    business logic for species behaviors and characteristics.
    
    Attributes:
        config: Underlying species configuration
        species_id: Unique species identifier
        display_name: Human-readable species name
        is_predatory: Whether this species is predatory
    """
    
    def __init__(self, config: SpeciesConfig):
        """
        Initialize species from configuration.
        
        Args:
            config: Species configuration object
        """
        self.config = config
        self.species_id = config.species_id
        self.display_name = config.display_name
        
        # Determine if species is predatory
        self.is_predatory = any(
            stage.is_predatory
            for stage in config.life_stages.values()
        )
    
    def get_life_stage(self, stage_name: str) -> Optional[LifeStageConfig]:
        """
        Get configuration for a specific life stage.
        
        Args:
            stage_name: Name of the life stage
        
        Returns:
            LifeStageConfig or None if not found
        """
        return self.config.life_stages.get(stage_name)
    
    def get_all_stages(self) -> List[str]:
        """
        Get list of all life stage names.
        
        Returns:
            List of stage names
        """
        return list(self.config.life_stages.keys())
    
    def get_survival_rate(self, stage_name: str) -> float:
        """
        Get survival rate for a life stage.
        
        Args:
            stage_name: Name of the life stage
        
        Returns:
            Survival rate [0-1]
        """
        stage = self.get_life_stage(stage_name)
        if stage:
            if stage.survival_to_next is not None:
                return stage.survival_to_next
            elif stage.survival_daily is not None:
                return stage.survival_daily
        return 1.0
    
    def get_development_duration(self, stage_name: str) -> tuple[int, int]:
        """
        Get development duration range for a stage.
        
        Args:
            stage_name: Name of the life stage
        
        Returns:
            Tuple of (min_days, max_days)
        """
        stage = self.get_life_stage(stage_name)
        if stage:
            return (stage.duration_min, stage.duration_max)
        return (0, 0)
    
    def is_stage_predatory(self, stage_name: str) -> bool:
        """
        Check if a specific life stage is predatory.
        
        Args:
            stage_name: Name of the life stage
        
        Returns:
            True if stage is predatory
        """
        stage = self.get_life_stage(stage_name)
        return stage.is_predatory if stage else False
    
    def get_predation_rate(self, stage_name: str) -> int:
        """
        Get predation rate for a predatory stage.
        
        Args:
            stage_name: Name of the life stage
        
        Returns:
            Number of prey consumed per day
        """
        stage = self.get_life_stage(stage_name)
        if stage and stage.is_predatory and stage.predation_rate:
            return stage.predation_rate
        return 0
    
    def get_reproduction_params(self) -> Dict[str, Any]:
        """
        Get reproduction parameters.
        
        Returns:
            Dictionary with reproduction parameters
        """
        repro = self.config.reproduction
        return {
            'eggs_per_batch_min': repro.eggs_per_batch_min,
            'eggs_per_batch_max': repro.eggs_per_batch_max,
            'oviposition_events': repro.oviposition_events,
            'min_age_reproduction_days': repro.min_age_reproduction_days
        }
    
    def can_reproduce_at_age(self, age_days: int) -> bool:
        """
        Check if individual can reproduce at given age.
        
        Args:
            age_days: Age in days
        
        Returns:
            True if old enough to reproduce
        """
        return age_days >= self.config.reproduction.min_age_reproduction_days
    
    def get_temperature_tolerance(self) -> Optional[tuple[float, float]]:
        """
        Get optimal temperature range.
        
        Returns:
            Tuple of (min_temp, max_temp) or None
        """
        if self.config.environmental_sensitivity:
            sens = self.config.environmental_sensitivity
            return (sens.optimal_temperature_min, sens.optimal_temperature_max)
        return None
    
    def get_lethal_temperature_range(self) -> Optional[tuple[float, float]]:
        """
        Get lethal temperature range.
        
        Returns:
            Tuple of (lethal_min, lethal_max) or None
        """
        if self.config.environmental_sensitivity:
            sens = self.config.environmental_sensitivity
            return (sens.lethal_temperature_min, sens.lethal_temperature_max)
        return None
    
    def is_temperature_lethal(self, temperature: float) -> bool:
        """
        Check if temperature is lethal for this species.
        
        Args:
            temperature: Temperature in °C
        
        Returns:
            True if temperature is lethal
        """
        lethal_range = self.get_lethal_temperature_range()
        if lethal_range:
            return temperature < lethal_range[0] or temperature > lethal_range[1]
        return False
    
    def is_temperature_optimal(self, temperature: float) -> bool:
        """
        Check if temperature is in optimal range.
        
        Args:
            temperature: Temperature in °C
        
        Returns:
            True if temperature is optimal
        """
        optimal_range = self.get_temperature_tolerance()
        if optimal_range:
            return optimal_range[0] <= temperature <= optimal_range[1]
        return True
    
    def __repr__(self) -> str:
        """String representation."""
        pred_status = "predatory" if self.is_predatory else "non-predatory"
        return f"Species(id='{self.species_id}', name='{self.display_name}', {pred_status})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        return self.display_name
