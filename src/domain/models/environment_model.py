"""
Environment Model Module
========================

Models environmental conditions and their temporal dynamics.

Provides:
- Temperature time series with seasonal variation
- Humidity time series with autocorrelation
- Integrated environmental model combining all factors
- Query interface for current conditions

Author: Mosquito Simulation System
"""

import numpy as np
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from infrastructure.config import EnvironmentConfig
from .stochastic_processes import EnvironmentalStochasticity


@dataclass
class EnvironmentalConditions:
    """
    Environmental conditions at a specific time point.
    
    Attributes:
        day: Day number (0-indexed)
        temperature: Temperature in °C
        humidity: Relative humidity in %
        carrying_capacity: Current carrying capacity
        rainfall: Daily rainfall in mm (optional)
    """
    day: int
    temperature: float
    humidity: float
    carrying_capacity: int
    rainfall: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'day': self.day,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'carrying_capacity': self.carrying_capacity,
            'rainfall': self.rainfall
        }


class TemperatureSeries:
    """
    Temperature time series generator with seasonal variation.
    
    Features:
    - Sinusoidal seasonal cycle
    - AR(1) autocorrelation for day-to-day persistence
    - Configurable mean and variability
    - Optional climate change trend
    """
    
    def __init__(
        self,
        mean: float = 27.0,
        seasonal_amplitude: float = 5.0,
        std: float = 3.0,
        autocorr: float = 0.7,
        seed: Optional[int] = None
    ):
        """
        Initialize temperature series generator.
        
        Args:
            mean: Annual mean temperature (°C)
            seasonal_amplitude: Amplitude of seasonal variation (°C)
            std: Standard deviation of daily noise (°C)
            autocorr: Autocorrelation coefficient [0-1]
            seed: Random seed for reproducibility
        
        Example:
            >>> temp_series = TemperatureSeries(mean=27, seasonal_amplitude=5)
            >>> temps = temp_series.generate(365)
            >>> len(temps)
            365
        """
        self.mean = mean
        self.seasonal_amplitude = seasonal_amplitude
        self.std = std
        self.autocorr = autocorr
        
        self.stoch = EnvironmentalStochasticity(seed=seed)
        self._series: Optional[np.ndarray] = None
    
    def generate(self, days: int) -> np.ndarray:
        """
        Generate temperature time series.
        
        Args:
            days: Number of days to simulate
        
        Returns:
            Array of daily temperatures
        
        Example:
            >>> temp_series = TemperatureSeries(mean=27, seed=42)
            >>> temps = temp_series.generate(365)
            >>> 20 <= temps.mean() <= 34
            True
        """
        self._series = self.stoch.generate_temperature_series(
            days=days,
            mean=self.mean,
            std=self.std,
            seasonal=True,
            seasonal_amplitude=self.seasonal_amplitude,
            autocorr=self.autocorr
        )
        return self._series
    
    def get_at_day(self, day: int) -> float:
        """
        Get temperature at specific day.
        
        Args:
            day: Day index (0-based)
        
        Returns:
            Temperature at that day
        
        Raises:
            ValueError: If series has not been generated
        """
        if self._series is None:
            raise ValueError("Temperature series not generated. Call generate() first.")
        
        if day < 0 or day >= len(self._series):
            raise IndexError(f"Day {day} out of range [0, {len(self._series)-1}]")
        
        return self._series[day]
    
    def get_range(self, start_day: int, end_day: int) -> np.ndarray:
        """
        Get temperature range between two days.
        
        Args:
            start_day: Start day (inclusive)
            end_day: End day (exclusive)
        
        Returns:
            Temperature array for the range
        """
        if self._series is None:
            raise ValueError("Temperature series not generated. Call generate() first.")
        
        return self._series[start_day:end_day]
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get statistical summary of temperature series.
        
        Returns:
            Dictionary with mean, std, min, max, etc.
        """
        if self._series is None:
            raise ValueError("Temperature series not generated. Call generate() first.")
        
        return {
            'mean': float(np.mean(self._series)),
            'std': float(np.std(self._series)),
            'min': float(np.min(self._series)),
            'max': float(np.max(self._series)),
            'median': float(np.median(self._series)),
            'q25': float(np.percentile(self._series, 25)),
            'q75': float(np.percentile(self._series, 75))
        }


class HumiditySeries:
    """
    Humidity time series generator with persistence.
    
    Features:
    - High autocorrelation (humidity persists over days)
    - Bounded in [0, 100]%
    - Optional seasonal variation
    """
    
    def __init__(
        self,
        mean: float = 75.0,
        std: float = 10.0,
        autocorr: float = 0.8,
        min_humidity: float = 30.0,
        max_humidity: float = 100.0,
        seed: Optional[int] = None
    ):
        """
        Initialize humidity series generator.
        
        Args:
            mean: Mean relative humidity (%)
            std: Standard deviation (%)
            autocorr: Autocorrelation coefficient [0-1]
            min_humidity: Minimum humidity (%)
            max_humidity: Maximum humidity (%)
            seed: Random seed
        
        Example:
            >>> hum_series = HumiditySeries(mean=75, std=10)
            >>> humidity = hum_series.generate(365)
            >>> len(humidity)
            365
        """
        self.mean = mean
        self.std = std
        self.autocorr = autocorr
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        
        self.stoch = EnvironmentalStochasticity(seed=seed)
        self._series: Optional[np.ndarray] = None
    
    def generate(self, days: int) -> np.ndarray:
        """
        Generate humidity time series.
        
        Args:
            days: Number of days to simulate
        
        Returns:
            Array of daily humidity values
        
        Example:
            >>> hum_series = HumiditySeries(mean=75, seed=42)
            >>> humidity = hum_series.generate(365)
            >>> (humidity >= 30).all() and (humidity <= 100).all()
            True
        """
        self._series = self.stoch.generate_humidity_series(
            days=days,
            mean=self.mean,
            std=self.std,
            autocorr=self.autocorr,
            min_humidity=self.min_humidity,
            max_humidity=self.max_humidity
        )
        return self._series
    
    def get_at_day(self, day: int) -> float:
        """Get humidity at specific day."""
        if self._series is None:
            raise ValueError("Humidity series not generated. Call generate() first.")
        
        if day < 0 or day >= len(self._series):
            raise IndexError(f"Day {day} out of range [0, {len(self._series)-1}]")
        
        return self._series[day]
    
    def get_range(self, start_day: int, end_day: int) -> np.ndarray:
        """Get humidity range between two days."""
        if self._series is None:
            raise ValueError("Humidity series not generated. Call generate() first.")
        
        return self._series[start_day:end_day]
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistical summary of humidity series."""
        if self._series is None:
            raise ValueError("Humidity series not generated. Call generate() first.")
        
        return {
            'mean': float(np.mean(self._series)),
            'std': float(np.std(self._series)),
            'min': float(np.min(self._series)),
            'max': float(np.max(self._series)),
            'median': float(np.median(self._series)),
            'q25': float(np.percentile(self._series, 25)),
            'q75': float(np.percentile(self._series, 75))
        }


class EnvironmentModel:
    """
    Integrated environmental model combining temperature, humidity, and capacity.
    
    This class manages all environmental conditions over the simulation period
    and provides a unified interface for querying conditions at any time point.
    
    Attributes:
        temperature_series: Temperature time series generator
        humidity_series: Humidity time series generator
        base_carrying_capacity: Base carrying capacity
        days: Total simulation days
    """
    
    def __init__(
        self,
        config: EnvironmentConfig,
        days: int,
        seed: Optional[int] = None
    ):
        """
        Initialize environment model from configuration.
        
        Args:
            config: Environment configuration
            days: Total simulation days
            seed: Random seed for reproducibility
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> env_config = config.environment
            >>> env = EnvironmentModel(env_config, days=365, seed=42)
            >>> env.days
            365
        """
        self.config = config
        self.days = days
        self.seed = seed
        
        # Extract temperature parameters
        temp_value = config.temperature
        temp_variation = config.temperature_variation
        
        # Extract humidity parameters
        hum_value = config.humidity
        hum_variation = config.humidity_variation
        
        # Initialize temperature series
        self.temperature_series = TemperatureSeries(
            mean=temp_value,
            seasonal_amplitude=temp_variation,
            std=2.0,
            autocorr=0.7,
            seed=seed
        )
        
        # Initialize humidity series
        self.humidity_series = HumiditySeries(
            mean=hum_value,
            std=hum_variation,
            autocorr=0.8,
            min_humidity=30.0,
            max_humidity=100.0,
            seed=seed
        )
        
        # Carrying capacity
        self.base_carrying_capacity = config.carrying_capacity
        
        # Generate time series
        self._temperature_data = self.temperature_series.generate(days)
        self._humidity_data = self.humidity_series.generate(days)
        self._carrying_capacity_data = self._compute_carrying_capacity_series()
    
    def _compute_carrying_capacity_series(self) -> np.ndarray:
        """
        Compute dynamic carrying capacity based on environmental conditions.
        
        Carrying capacity varies with:
        - Temperature (optimal range increases capacity)
        - Humidity (higher humidity increases capacity)
        - Base capacity from configuration
        
        Returns:
            Array of daily carrying capacities
        """
        capacity = np.zeros(self.days)
        
        for day in range(self.days):
            temp = self._temperature_data[day]
            hum = self._humidity_data[day]
            
            # Temperature effect (optimal range: 25-30°C)
            if 25 <= temp <= 30:
                temp_factor = 1.0
            elif temp < 25:
                temp_factor = max(0.5, 1.0 - (25 - temp) * 0.05)
            else:  # temp > 30
                temp_factor = max(0.5, 1.0 - (temp - 30) * 0.05)
            
            # Humidity effect (optimal: > 70%)
            if hum >= 70:
                hum_factor = 1.0
            else:
                hum_factor = max(0.5, hum / 70)
            
            # Combined capacity
            capacity[day] = self.base_carrying_capacity * temp_factor * hum_factor
        
        return capacity
    
    def get_conditions(self, day: int) -> EnvironmentalConditions:
        """
        Get environmental conditions at specific day.
        
        Args:
            day: Day index (0-based)
        
        Returns:
            EnvironmentalConditions object
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> env = EnvironmentModel(config.environment, days=365, seed=42)
            >>> conditions = env.get_conditions(0)
            >>> conditions.day
            0
            >>> 20 <= conditions.temperature <= 35
            True
        """
        if day < 0 or day >= self.days:
            raise IndexError(f"Day {day} out of range [0, {self.days-1}]")
        
        return EnvironmentalConditions(
            day=day,
            temperature=self._temperature_data[day],
            humidity=self._humidity_data[day],
            carrying_capacity=int(self._carrying_capacity_data[day])
        )
    
    def get_temperature_at(self, day: int) -> float:
        """Get temperature at specific day."""
        return self._temperature_data[day]
    
    def get_humidity_at(self, day: int) -> float:
        """Get humidity at specific day."""
        return self._humidity_data[day]
    
    def get_carrying_capacity_at(self, day: int) -> int:
        """Get carrying capacity at specific day."""
        return int(self._carrying_capacity_data[day])
    
    def get_temperature_range(self, start_day: int, end_day: int) -> np.ndarray:
        """Get temperature time series for a range of days."""
        return self._temperature_data[start_day:end_day]
    
    def get_humidity_range(self, start_day: int, end_day: int) -> np.ndarray:
        """Get humidity time series for a range of days."""
        return self._humidity_data[start_day:end_day]
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistical summary of all environmental variables.
        
        Returns:
            Dictionary with statistics for temperature, humidity, and capacity
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> env = EnvironmentModel(config.environment, days=365, seed=42)
            >>> stats = env.get_statistics()
            >>> 'temperature' in stats and 'humidity' in stats
            True
        """
        return {
            'temperature': self.temperature_series.get_statistics(),
            'humidity': self.humidity_series.get_statistics(),
            'carrying_capacity': {
                'mean': float(np.mean(self._carrying_capacity_data)),
                'std': float(np.std(self._carrying_capacity_data)),
                'min': float(np.min(self._carrying_capacity_data)),
                'max': float(np.max(self._carrying_capacity_data))
            }
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export full environmental data to dictionary.
        
        Returns:
            Dictionary with all time series and metadata
        """
        return {
            'days': self.days,
            'temperature': self._temperature_data.tolist(),
            'humidity': self._humidity_data.tolist(),
            'carrying_capacity': self._carrying_capacity_data.tolist(),
            'statistics': self.get_statistics()
        }
    
    def is_favorable_for_species(
        self,
        day: int,
        temp_range: Tuple[float, float] = (20.0, 32.0),
        hum_threshold: float = 60.0
    ) -> bool:
        """
        Check if conditions are favorable for mosquito development.
        
        Args:
            day: Day to check
            temp_range: Acceptable temperature range (min, max)
            hum_threshold: Minimum acceptable humidity
        
        Returns:
            True if conditions are favorable
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> env = EnvironmentModel(config.environment, days=365, seed=42)
            >>> favorable = env.is_favorable_for_species(0)
            >>> isinstance(favorable, bool)
            True
        """
        conditions = self.get_conditions(day)
        
        temp_ok = temp_range[0] <= conditions.temperature <= temp_range[1]
        hum_ok = conditions.humidity >= hum_threshold
        
        return temp_ok and hum_ok
    
    def count_favorable_days(
        self,
        temp_range: Tuple[float, float] = (20.0, 32.0),
        hum_threshold: float = 60.0
    ) -> int:
        """
        Count number of days with favorable conditions.
        
        Args:
            temp_range: Acceptable temperature range
            hum_threshold: Minimum humidity
        
        Returns:
            Number of favorable days
        """
        count = 0
        for day in range(self.days):
            if self.is_favorable_for_species(day, temp_range, hum_threshold):
                count += 1
        return count
    
    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"EnvironmentModel(days={self.days}, "
            f"temp_mean={stats['temperature']['mean']:.1f}°C, "
            f"humidity_mean={stats['humidity']['mean']:.1f}%, "
            f"capacity_mean={stats['carrying_capacity']['mean']:.0f})"
        )


def create_environment_from_config(
    config: EnvironmentConfig,
    days: int,
    seed: Optional[int] = None
) -> EnvironmentModel:
    """
    Convenience function to create EnvironmentModel from configuration.
    
    Args:
        config: Environment configuration
        days: Simulation duration in days
        seed: Random seed
    
    Returns:
        Configured EnvironmentModel
    
    Example:
        >>> from infrastructure.config import load_default_config
        >>> config = load_default_config()
        >>> env = create_environment_from_config(config.environment, 365, seed=42)
        >>> env.days
        365
    """
    return EnvironmentModel(config, days, seed)
