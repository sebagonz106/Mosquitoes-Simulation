"""
Habitat Entity Module
=====================

Represents environmental habitats for mosquito populations.

Author: Mosquito Simulation System
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from domain.models.environment_model import EnvironmentModel, EnvironmentalConditions
from infrastructure.config import EnvironmentConfig


@dataclass
class HabitatConditions:
    """
    Business-level view of habitat conditions.
    
    Attributes:
        day: Current day
        temperature: Temperature in °C
        humidity: Relative humidity %
        carrying_capacity: Maximum population capacity
        is_favorable: Whether conditions are favorable
        quality_index: Habitat quality [0-1]
    """
    
    day: int
    temperature: float
    humidity: float
    carrying_capacity: int
    is_favorable: bool
    quality_index: float
    
    @classmethod
    def from_environmental_conditions(
        cls,
        conditions: EnvironmentalConditions,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None
    ) -> 'HabitatConditions':
        """
        Create habitat conditions from environmental model output.
        
        Args:
            conditions: Environmental conditions from model
            optimal_temp_range: Optimal temperature range (min, max)
            lethal_temp_range: Lethal temperature range (min, max)
        
        Returns:
            HabitatConditions instance
        """
        temp = conditions.temperature
        
        # Determine if conditions are favorable
        is_favorable = True
        quality = 1.0
        
        if lethal_temp_range:
            if temp < lethal_temp_range[0] or temp > lethal_temp_range[1]:
                is_favorable = False
                quality = 0.0
        
        if is_favorable and optimal_temp_range:
            # Calculate quality based on distance from optimal range
            if optimal_temp_range[0] <= temp <= optimal_temp_range[1]:
                quality = 1.0
            elif temp < optimal_temp_range[0]:
                # Below optimal
                if lethal_temp_range:
                    distance = optimal_temp_range[0] - temp
                    max_distance = optimal_temp_range[0] - lethal_temp_range[0]
                    quality = 1.0 - (distance / max_distance) if max_distance > 0 else 0.5
                else:
                    quality = 0.5
            else:
                # Above optimal
                if lethal_temp_range:
                    distance = temp - optimal_temp_range[1]
                    max_distance = lethal_temp_range[1] - optimal_temp_range[1]
                    quality = 1.0 - (distance / max_distance) if max_distance > 0 else 0.5
                else:
                    quality = 0.5
        
        return cls(
            day=conditions.day,
            temperature=temp,
            humidity=conditions.humidity,
            carrying_capacity=int(conditions.carrying_capacity),
            is_favorable=is_favorable,
            quality_index=max(0.0, min(1.0, quality))
        )
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"HabitatConditions(day={self.day}, T={self.temperature:.1f}°C, "
            f"H={self.humidity:.1f}%, K={self.carrying_capacity}, "
            f"quality={self.quality_index:.2f})"
        )


class Habitat:
    """
    Represents an environmental habitat for mosquito populations.
    
    This class provides business-level interface to environmental
    conditions, wrapping the EnvironmentModel with domain logic.
    
    Attributes:
        habitat_id: Unique habitat identifier
        name: Human-readable habitat name
        environment_model: Underlying environment model
        config: Environment configuration
        location: Optional geographic location
    """
    
    def __init__(
        self,
        habitat_id: str,
        name: str,
        environment_model: EnvironmentModel,
        config: EnvironmentConfig,
        location: Optional[str] = None
    ):
        """
        Initialize habitat.
        
        Args:
            habitat_id: Unique identifier
            name: Habitat name
            environment_model: Environment dynamics model
            config: Environment configuration
            location: Optional location description
        """
        self.habitat_id = habitat_id
        self.name = name
        self.environment_model = environment_model
        self.config = config
        self.location = location
    
    def get_conditions_at_day(
        self,
        day: int,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None
    ) -> HabitatConditions:
        """
        Get habitat conditions for a specific day.
        
        Args:
            day: Simulation day
            optimal_temp_range: Species optimal temperature range
            lethal_temp_range: Species lethal temperature range
        
        Returns:
            HabitatConditions for that day
        """
        env_conditions = self.environment_model.get_conditions(day)
        
        return HabitatConditions.from_environmental_conditions(
            env_conditions,
            optimal_temp_range,
            lethal_temp_range
        )
    
    def get_time_series(
        self,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None
    ) -> List[HabitatConditions]:
        """
        Get complete time series of habitat conditions.
        
        Args:
            optimal_temp_range: Species optimal temperature range
            lethal_temp_range: Species lethal temperature range
        
        Returns:
            List of HabitatConditions for each day
        """
        return [
            self.get_conditions_at_day(day, optimal_temp_range, lethal_temp_range)
            for day in range(self.environment_model.days)
        ]
    
    def count_favorable_days(
        self,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None
    ) -> int:
        """
        Count number of days with favorable conditions.
        
        Args:
            optimal_temp_range: Species optimal temperature range
            lethal_temp_range: Species lethal temperature range
        
        Returns:
            Number of favorable days
        """
        time_series = self.get_time_series(optimal_temp_range, lethal_temp_range)
        return sum(1 for cond in time_series if cond.is_favorable)
    
    def get_mean_temperature(self) -> float:
        """
        Get mean temperature across time series.
        
        Returns:
            Mean temperature in °C
        """
        stats = self.environment_model.get_statistics()
        return float(stats['temperature']['mean'])
    
    def get_mean_humidity(self) -> float:
        """
        Get mean humidity across time series.
        
        Returns:
            Mean relative humidity %
        """
        stats = self.environment_model.get_statistics()
        return float(stats['humidity']['mean'])
    
    def get_mean_carrying_capacity(self) -> float:
        """
        Get mean carrying capacity.
        
        Returns:
            Mean carrying capacity
        """
        stats = self.environment_model.get_statistics()
        return float(stats['carrying_capacity']['mean'])
    
    def get_temperature_range(self) -> tuple[float, float]:
        """
        Get temperature range.
        
        Returns:
            Tuple of (min_temp, max_temp)
        """
        stats = self.environment_model.get_statistics()
        return (float(stats['temperature']['min']), float(stats['temperature']['max']))
    
    def get_habitat_statistics(
        self,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive habitat statistics.
        
        Args:
            optimal_temp_range: Species optimal temperature range
            lethal_temp_range: Species lethal temperature range
        
        Returns:
            Dictionary with habitat statistics
        """
        time_series = self.get_time_series(optimal_temp_range, lethal_temp_range)
        temp_range = self.get_temperature_range()
        
        favorable_days = sum(1 for cond in time_series if cond.is_favorable)
        total_days = len(time_series)
        
        mean_quality = np.mean([cond.quality_index for cond in time_series])
        
        return {
            'habitat_id': self.habitat_id,
            'name': self.name,
            'location': self.location,
            'total_days': total_days,
            'favorable_days': favorable_days,
            'favorable_fraction': favorable_days / total_days if total_days > 0 else 0,
            'mean_temperature': self.get_mean_temperature(),
            'temperature_range': temp_range,
            'mean_humidity': self.get_mean_humidity(),
            'mean_carrying_capacity': self.get_mean_carrying_capacity(),
            'mean_quality_index': float(mean_quality)
        }
    
    def is_suitable_for_species(
        self,
        optimal_temp_range: Optional[tuple[float, float]] = None,
        lethal_temp_range: Optional[tuple[float, float]] = None,
        min_favorable_fraction: float = 0.5
    ) -> bool:
        """
        Check if habitat is suitable for a species.
        
        Args:
            optimal_temp_range: Species optimal temperature range
            lethal_temp_range: Species lethal temperature range
            min_favorable_fraction: Minimum fraction of favorable days
        
        Returns:
            True if habitat is suitable
        """
        stats = self.get_habitat_statistics(optimal_temp_range, lethal_temp_range)
        return stats['favorable_fraction'] >= min_favorable_fraction
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Habitat(id='{self.habitat_id}', name='{self.name}', "
            f"days={self.environment_model.days}, "
            f"mean_temp={self.get_mean_temperature():.1f}°C)"
        )
    
    def __str__(self) -> str:
        """Human-readable string."""
        location_str = f" at {self.location}" if self.location else ""
        return f"{self.name}{location_str}"
