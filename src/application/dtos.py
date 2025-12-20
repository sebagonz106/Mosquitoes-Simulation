"""
Application Layer - DTOs (Data Transfer Objects)
=================================================

Data structures for transferring information between layers.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union
import numpy as np


@dataclass
class SimulationConfig:
    """
    Configuration for a simulation run.
    
    This DTO encapsulates all parameters needed to execute
    a population or agent-based simulation.
    
    Attributes:
        species_id: Species identifier (e.g., 'aedes_aegypti', 'toxorhynchites')
        duration_days: Number of days to simulate
        initial_eggs: Initial egg count
        initial_larvae: Initial larvae count (can be [L1,L2,L3,L4] array or total int)
        initial_pupae: Initial pupae count
        initial_adults: Initial adult count
        temperature: Environmental temperature (°C) - default from config if None
        humidity: Environmental humidity (0-100 scale, percentage) - default from config if None
        water_availability: Water availability for oviposition (0-1 scale) - default 1.0
        random_seed: Random seed for reproducibility (optional)
    """
    
    species_id: str
    duration_days: int
    initial_eggs: int
    initial_larvae: Union[List[int], int]
    initial_pupae: int
    initial_adults: int
    temperature: Optional[float] = None  # Will use environment_config default if None
    humidity: Optional[float] = None     # 0-100 scale (percentage)
    water_availability: float = 1.0      # 1.0 = always available, 0.0 = never
    random_seed: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SimulationConfig':
        """Create from dictionary."""
        return cls(**data)
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate configuration parameters.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if self.duration_days < 1:
            errors.append("duration_days must be >= 1")
        
        if self.duration_days > 3650:
            errors.append("duration_days exceeds maximum (3650)")
        
        if self.initial_eggs < 0:
            errors.append("initial_eggs cannot be negative")
        
        if self.initial_pupae < 0:
            errors.append("initial_pupae cannot be negative")
        
        if self.initial_adults < 0:
            errors.append("initial_adults cannot be negative")
        
        # Validate temperature if provided
        if self.temperature is not None:
            if self.temperature < -10 or self.temperature > 50:
                errors.append("temperature must be between -10°C and 50°C")
        
        # Validate humidity if provided (0-100 scale)
        if self.humidity is not None:
            if self.humidity < 0 or self.humidity > 100:
                errors.append("humidity must be between 0 and 100 (%)")
        
        # Validate water availability
        if self.water_availability < 0 or self.water_availability > 1:
            errors.append("water_availability must be between 0 and 1")
        
        # Validate larvae
        if isinstance(self.initial_larvae, list):
            if len(self.initial_larvae) != 4:
                errors.append("initial_larvae list must have exactly 4 elements [L1,L2,L3,L4]")
            if any(l < 0 for l in self.initial_larvae):
                errors.append("initial_larvae values cannot be negative")
        elif isinstance(self.initial_larvae, int):
            if self.initial_larvae < 0:
                errors.append("initial_larvae cannot be negative")
        else:
            errors.append("initial_larvae must be List[int] or int")
        
        return (len(errors) == 0, errors)


@dataclass
class PopulationResult:
    """
    Result of a population simulation.
    
    Contains complete temporal trajectories and summary statistics
    for a population-based simulation.
    
    Attributes:
        species_id: Species identifier
        days: Array of simulation days [0, 1, 2, ..., N]
        eggs: Temporal evolution of egg count
        larvae: Temporal evolution of total larvae
        pupae: Temporal evolution of pupae count
        adults: Temporal evolution of adult count
        total_population: Temporal evolution of total population
        statistics: Summary statistics (peak, extinction, means, etc.)
    """
    
    species_id: str
    days: np.ndarray
    eggs: np.ndarray
    larvae: np.ndarray
    pupae: np.ndarray
    adults: np.ndarray
    total_population: np.ndarray
    statistics: Dict
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary for serialization.
        Converts numpy arrays to lists for JSON compatibility.
        """
        return {
            'species_id': self.species_id,
            'days': self.days.tolist(),
            'eggs': self.eggs.tolist(),
            'larvae': self.larvae.tolist(),
            'pupae': self.pupae.tolist(),
            'adults': self.adults.tolist(),
            'total_population': self.total_population.tolist(),
            'statistics': self.statistics
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PopulationResult':
        """Create from dictionary, converting lists back to numpy arrays."""
        return cls(
            species_id=data['species_id'],
            days=np.array(data['days']),
            eggs=np.array(data['eggs']),
            larvae=np.array(data['larvae']),
            pupae=np.array(data['pupae']),
            adults=np.array(data['adults']),
            total_population=np.array(data['total_population']),
            statistics=data['statistics']
        )
    
    def get_final_state(self) -> Dict:
        """Get final population state for checkpointing."""
        return {
            'day': int(self.days[-1]),
            'eggs': float(self.eggs[-1]),
            'larvae': float(self.larvae[-1]),
            'pupae': float(self.pupae[-1]),
            'adults': float(self.adults[-1])
        }


@dataclass
class AgentResult:
    """
    Result of an agent-based simulation.
    
    Contains agent statistics and daily evolution data.
    
    Attributes:
        num_vectors_initial: Initial number of vector agents
        num_predators_initial: Initial number of predator agents
        num_vectors_final: Final number of living vector agents
        num_predators_final: Final number of living predator agents
        total_eggs_laid: Total eggs laid by all vectors
        total_prey_consumed: Total prey consumed by all predators
        daily_stats: Daily statistics for each simulation day
    """
    
    num_vectors_initial: int
    num_predators_initial: int
    num_vectors_final: int
    num_predators_final: int
    total_eggs_laid: int
    total_prey_consumed: int
    daily_stats: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentResult':
        """Create from dictionary."""
        return cls(**data)
    
    def get_survival_rate_vectors(self) -> float:
        """Calculate survival rate for vector agents."""
        if self.num_vectors_initial == 0:
            return 0.0
        return self.num_vectors_final / self.num_vectors_initial
    
    def get_survival_rate_predators(self) -> float:
        """Calculate survival rate for predator agents."""
        if self.num_predators_initial == 0:
            return 0.0
        return self.num_predators_final / self.num_predators_initial
    
    def get_average_eggs_per_vector(self) -> float:
        """Calculate average eggs laid per vector agent."""
        if self.num_vectors_initial == 0:
            return 0.0
        return self.total_eggs_laid / self.num_vectors_initial
    
    def get_average_prey_per_predator(self) -> float:
        """Calculate average prey consumed per predator."""
        if self.num_predators_initial == 0:
            return 0.0
        return self.total_prey_consumed / self.num_predators_initial
    
    def get_statistics(self) -> Dict:
        """
        Get standardized statistics comparable with PopulationResult.
        
        Returns dictionary with metrics that match PopulationResult structure:
        - peak_population: Maximum number of vectors during simulation
        - peak_day: Day when peak occurred
        - final_population: Final number of vectors
        - mean_population: Average number of vectors across all days
        - extinction_day: Day when population reached zero (if applicable)
        
        For predators:
        - peak_predators: Maximum number of predators
        - final_predators: Final number of predators
        - mean_predators: Average number of predators
        
        Additional agent-specific metrics:
        - total_eggs: Total eggs laid
        - avg_eggs_per_vector: Average eggs per vector
        - vector_survival_rate: Fraction of vectors surviving
        - predator_survival_rate: Fraction of predators surviving
        """
        if not self.daily_stats:
            return {}
        
        # Extract vector population trajectory
        vector_counts = [stat['num_vectors_alive'] for stat in self.daily_stats]
        predator_counts = [stat['num_predators_alive'] for stat in self.daily_stats]
        
        # Calculate vector statistics
        peak_population = max(vector_counts)
        peak_day = vector_counts.index(peak_population)
        mean_population = sum(vector_counts) / len(vector_counts)
        
        # Check for extinction
        extinction_day = None
        for day, count in enumerate(vector_counts):
            if count == 0 and day > 0:
                extinction_day = day
                break
        
        # Calculate predator statistics
        peak_predators = max(predator_counts) if predator_counts else 0
        mean_predators = sum(predator_counts) / len(predator_counts) if predator_counts else 0.0
        
        return {
            # Vector population metrics (comparable with PopulationResult)
            'peak_population': peak_population,
            'peak_day': peak_day,
            'final_population': self.num_vectors_final,
            'mean_population': mean_population,
            'extinction_day': extinction_day,
            
            # Predator metrics
            'peak_predators': peak_predators,
            'final_predators': self.num_predators_final,
            'mean_predators': mean_predators,
            
            # Agent-specific metrics
            'total_eggs': self.total_eggs_laid,
            'avg_eggs_per_vector': self.get_average_eggs_per_vector(),
            'vector_survival_rate': self.get_survival_rate_vectors(),
            'predator_survival_rate': self.get_survival_rate_predators(),
            'total_prey_consumed': self.total_prey_consumed,
            'avg_prey_per_predator': self.get_average_prey_per_predator()
        }


@dataclass
class ComparisonResult:
    """
    Result of comparing multiple simulation scenarios.
    
    Contains results for each scenario and comparative analysis.
    
    Attributes:
        scenario_names: List of scenario names
        results: Dict mapping scenario name to PopulationResult
        comparison: Comparative statistics across scenarios
        checkpoint_paths: Optional dict of checkpoint file paths
    """
    
    scenario_names: List[str]
    results: Dict[str, PopulationResult]
    comparison: Dict
    checkpoint_paths: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary for serialization.
        Note: Does not include full results, only comparison summary.
        """
        return {
            'scenario_names': self.scenario_names,
            'comparison': self.comparison,
            'checkpoint_paths': self.checkpoint_paths
        }
    
    def get_best_scenario(self, metric: str = 'peak_population') -> str:
        """
        Get best scenario based on a metric.
        
        Args:
            metric: Metric to optimize ('peak_population', 'final_population', etc.)
                   Lower values are considered better (better control)
        
        Returns:
            Name of best scenario
        """
        if metric not in ['peak_population', 'final_population', 'mean_population']:
            raise ValueError(f"Unknown metric: {metric}")
        
        best_scenario = None
        best_value = float('inf')
        
        for scenario_name, stats in self.comparison.items():
            if isinstance(stats, dict) and metric in stats:
                value = stats[metric]
                if value < best_value:
                    best_value = value
                    best_scenario = scenario_name
        
        return best_scenario if best_scenario is not None else ""
    
    def get_worst_scenario(self, metric: str = 'peak_population') -> str:
        """
        Get worst scenario based on a metric.
        
        Args:
            metric: Metric to evaluate ('peak_population', 'final_population', etc.)
                   Higher values are considered worse (poor control)
        
        Returns:
            Name of worst scenario
        """
        if metric not in ['peak_population', 'final_population', 'mean_population']:
            raise ValueError(f"Unknown metric: {metric}")
        
        worst_scenario = None
        worst_value = float('-inf')
        
        for scenario_name, stats in self.comparison.items():
            if isinstance(stats, dict) and metric in stats:
                value = stats[metric]
                if value > worst_value:
                    worst_value = value
                    worst_scenario = scenario_name
        
        return worst_scenario if worst_scenario is not None else ""
    
    def get_scenario_ranking(self, metric: str = 'peak_population') -> List[tuple]:
        """
        Get scenarios ranked by metric (best to worst).
        
        Args:
            metric: Metric to rank by
        
        Returns:
            List of (scenario_name, metric_value) tuples, sorted best to worst
        """
        if metric not in ['peak_population', 'final_population', 'mean_population']:
            raise ValueError(f"Unknown metric: {metric}")
        
        ranking = []
        for scenario_name, stats in self.comparison.items():
            if isinstance(stats, dict) and metric in stats:
                ranking.append((scenario_name, stats[metric]))
        
        # Sort ascending (lower is better for control)
        ranking.sort(key=lambda x: x[1])
        
        return ranking
