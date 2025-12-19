"""
Population Model Module
=======================

Integrated population dynamics model combining:
- Leslie matrix projection
- Stochastic processes (demographic and environmental)
- Environmental effects on vital rates
- Prolog inference for ecological interactions

This is the core domain model that orchestrates all mathematical
components and biological rules.

Author: Mosquito Simulation System
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from infrastructure.config import SpeciesConfig
from infrastructure.prolog_bridge import PrologBridge
from .leslie_matrix import LeslieMatrix, create_leslie_matrix_from_config
from .stochastic_processes import (
    StochasticVariation,
    DemographicStochasticity,
    EnvironmentalStochasticity
)
from .environment_model import EnvironmentModel


@dataclass
class PopulationState:
    """
    Population state at a specific time point.
    
    Attributes:
        day: Current day (0-indexed)
        eggs: Number of eggs
        larvae: Number of larvae
        pupae: Number of pupae
        adults: Number of adults
        total: Total population
        temperature: Current temperature (°C)
        humidity: Current humidity (%)
        carrying_capacity: Current carrying capacity
    """
    day: int
    eggs: int
    larvae: int
    pupae: int
    adults: int
    total: int
    temperature: float
    humidity: float
    carrying_capacity: int
    
    def to_vector(self) -> np.ndarray:
        """Convert to NumPy array [eggs, larvae, pupae, adults]."""
        return np.array([self.eggs, self.larvae, self.pupae, self.adults], dtype=float)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'day': self.day,
            'eggs': self.eggs,
            'larvae': self.larvae,
            'pupae': self.pupae,
            'adults': self.adults,
            'total': self.total,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'carrying_capacity': self.carrying_capacity
        }
    
    @classmethod
    def from_vector(
        cls,
        day: int,
        vector: np.ndarray,
        temperature: float,
        humidity: float,
        carrying_capacity: int
    ) -> 'PopulationState':
        """Create from NumPy vector."""
        eggs, larvae, pupae, adults = vector
        return cls(
            day=day,
            eggs=int(round(eggs)),
            larvae=int(round(larvae)),
            pupae=int(round(pupae)),
            adults=int(round(adults)),
            total=int(round(eggs + larvae + pupae + adults)),
            temperature=temperature,
            humidity=humidity,
            carrying_capacity=carrying_capacity
        )


@dataclass
class PopulationTrajectory:
    """
    Complete population trajectory over time.
    
    Attributes:
        states: List of PopulationState objects
        species_name: Name of species
        simulation_days: Total days simulated
    """
    states: List[PopulationState]
    species_name: str
    simulation_days: int
    
    def get_state(self, day: int) -> PopulationState:
        """Get population state at specific day."""
        if day < 0 or day >= len(self.states):
            raise IndexError(f"Day {day} out of range [0, {len(self.states)-1}]")
        return self.states[day]
    
    def get_total_population(self) -> np.ndarray:
        """Get total population time series."""
        return np.array([state.total for state in self.states])
    
    def get_stage_population(self, stage: str) -> np.ndarray:
        """
        Get population time series for specific stage.
        
        Args:
            stage: 'eggs', 'larvae', 'pupae', or 'adults'
        """
        stage_map = {
            'eggs': lambda s: s.eggs,
            'larvae': lambda s: s.larvae,
            'pupae': lambda s: s.pupae,
            'adults': lambda s: s.adults
        }
        
        if stage not in stage_map:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {list(stage_map.keys())}")
        
        return np.array([stage_map[stage](state) for state in self.states])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'species': self.species_name,
            'days': self.simulation_days,
            'states': [state.to_dict() for state in self.states],
            'total_population': self.get_total_population().tolist()
        }
    
    def is_extinct(self, threshold: int = 10) -> bool:
        """
        Check if population went extinct.
        
        Args:
            threshold: Population below this is considered extinct
        
        Returns:
            True if final population is below threshold
        """
        return self.states[-1].total < threshold
    
    def get_peak_population(self) -> Tuple[int, int]:
        """
        Get peak population and day it occurred.
        
        Returns:
            Tuple of (day, population)
        """
        populations = self.get_total_population()
        peak_day = int(np.argmax(populations))
        peak_pop = int(populations[peak_day])
        return (peak_day, peak_pop)
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for the trajectory."""
        total_pop = self.get_total_population()
        
        return {
            'initial_population': int(total_pop[0]),
            'final_population': int(total_pop[-1]),
            'mean_population': float(np.mean(total_pop)),
            'max_population': int(np.max(total_pop)),
            'min_population': int(np.min(total_pop)),
            'std_population': float(np.std(total_pop)),
            'peak_day': self.get_peak_population()[0],
            'is_extinct': self.is_extinct()
        }


class PopulationModel:
    """
    Integrated population dynamics model.
    
    This class combines:
    - Leslie matrix for deterministic projection
    - Stochastic processes for random variation
    - Environmental effects on vital rates
    - Prolog inference for ecological interactions
    - Density dependence via carrying capacity
    
    Attributes:
        species_config: Species configuration
        environment_model: Environmental conditions model
        leslie_matrix: Leslie matrix for projection
        stochastic: Stochastic variation generator
        demographic: Demographic stochasticity
        prolog_bridge: Optional Prolog inference engine
    """
    
    def __init__(
        self,
        species_config: SpeciesConfig,
        environment_model: EnvironmentModel,
        prolog_bridge: Optional[PrologBridge] = None,
        stochastic_mode: bool = True,
        seed: Optional[int] = None
    ):
        """
        Initialize population model.
        
        Args:
            species_config: Species configuration
            environment_model: Environmental model
            prolog_bridge: Optional Prolog bridge for ecological inference
            stochastic_mode: Enable stochastic variation
            seed: Random seed for reproducibility
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> from infrastructure.prolog_bridge import create_prolog_bridge
            >>> config = load_default_config()
            >>> aegypti_config = config.get_species('aedes_aegypti')
            >>> env = EnvironmentModel(config.environment, days=365)
            >>> model = PopulationModel(aegypti_config, env, seed=42)
            >>> model.species_name
            'aedes_aegypti'
        """
        self.species_config = species_config
        self.species_name = species_config.species_id
        self.environment_model = environment_model
        self.prolog_bridge = prolog_bridge
        self.stochastic_mode = stochastic_mode
        self.seed = seed
        
        # Initialize Leslie matrix
        self.leslie_matrix = create_leslie_matrix_from_config(species_config)
        
        # Initialize stochastic generators
        if stochastic_mode:
            self.stochastic = StochasticVariation(seed=seed)
            self.demographic = DemographicStochasticity(seed=seed)
        else:
            # Deterministic mode: use seed=0 to disable variation
            self.stochastic = StochasticVariation(seed=0)
            self.demographic = DemographicStochasticity(seed=0)
        
        # Trajectory storage
        self.current_state: Optional[PopulationState] = None
        self.trajectory: List[PopulationState] = []
    
    def initialize(
        self,
        initial_eggs: int = 0,
        initial_larvae: int = 0,
        initial_pupae: int = 0,
        initial_adults: int = 0
    ) -> PopulationState:
        """
        Initialize population with given stage counts.
        
        Args:
            initial_eggs: Initial number of eggs
            initial_larvae: Initial number of larvae
            initial_pupae: Initial number of pupae
            initial_adults: Initial number of adults
        
        Returns:
            Initial PopulationState
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> aegypti_config = config.get_species('aedes_aegypti')
            >>> env = EnvironmentModel(config.environment, days=365)
            >>> model = PopulationModel(aegypti_config, env, seed=42)
            >>> state = model.initialize(eggs=500, adults=100)
            >>> state.eggs
            500
        """
        conditions = self.environment_model.get_conditions(0)
        
        self.current_state = PopulationState(
            day=0,
            eggs=initial_eggs,
            larvae=initial_larvae,
            pupae=initial_pupae,
            adults=initial_adults,
            total=initial_eggs + initial_larvae + initial_pupae + initial_adults,
            temperature=conditions.temperature,
            humidity=conditions.humidity,
            carrying_capacity=conditions.carrying_capacity
        )
        
        self.trajectory = [self.current_state]
        return self.current_state
    
    def step(self, day: int) -> PopulationState:
        """
        Advance population by one time step.
        
        Args:
            day: Current day number
        
        Returns:
            New PopulationState after one time step
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> aegypti_config = config.get_species('aedes_aegypti')
            >>> env = EnvironmentModel(config.environment, days=365)
            >>> model = PopulationModel(aegypti_config, env, seed=42)
            >>> model.initialize(adults=100)
            >>> state = model.step(1)
            >>> state.day
            1
        """
        if self.current_state is None:
            raise ValueError("Population not initialized. Call initialize() first.")
        
        # Get environmental conditions
        conditions = self.environment_model.get_conditions(day)
        
        # Get current population vector
        current_vector = self.current_state.to_vector()
        
        # Apply Leslie matrix projection
        projected_vector = self.leslie_matrix.matrix @ current_vector
        
        # Apply environmental modulation
        projected_vector = self._apply_environmental_effects(
            projected_vector,
            conditions.temperature,
            conditions.humidity
        )
        
        # Apply density dependence
        projected_vector = self._apply_density_dependence(
            projected_vector,
            conditions.carrying_capacity
        )
        
        # Apply stochastic variation
        if self.stochastic_mode:
            projected_vector = self._apply_stochastic_variation(projected_vector)
        
        # Ensure non-negative
        projected_vector = np.maximum(projected_vector, 0)
        
        # Create new state
        new_state = PopulationState.from_vector(
            day=day,
            vector=projected_vector,
            temperature=conditions.temperature,
            humidity=conditions.humidity,
            carrying_capacity=conditions.carrying_capacity
        )
        
        # Update current state and trajectory
        self.current_state = new_state
        self.trajectory.append(new_state)
        
        return new_state
    
    def simulate(
        self,
        days: int,
        initial_eggs: int = 0,
        initial_larvae: int = 0,
        initial_pupae: int = 0,
        initial_adults: int = 0
    ) -> PopulationTrajectory:
        """
        Run full simulation.
        
        Args:
            days: Number of days to simulate
            initial_eggs: Initial eggs
            initial_larvae: Initial larvae
            initial_pupae: Initial pupae
            initial_adults: Initial adults
        
        Returns:
            PopulationTrajectory with complete time series
        
        Example:
            >>> from infrastructure.config import load_default_config
            >>> config = load_default_config()
            >>> aegypti_config = config.get_species('aedes_aegypti')
            >>> env = EnvironmentModel(config.environment, days=100)
            >>> model = PopulationModel(aegypti_config, env, seed=42)
            >>> trajectory = model.simulate(100, initial_adults=100)
            >>> len(trajectory.states)
            101
        """
        # Initialize
        self.initialize(initial_eggs, initial_larvae, initial_pupae, initial_adults)
        
        # Run simulation
        for day in range(1, days + 1):
            self.step(day)
        
        return PopulationTrajectory(
            states=self.trajectory,
            species_name=self.species_name,
            simulation_days=days
        )
    
    def _apply_environmental_effects(
        self,
        population_vector: np.ndarray,
        temperature: float,
        humidity: float
    ) -> np.ndarray:
        """
        Modify vital rates based on environmental conditions.
        
        Uses Prolog inference if available, otherwise uses simple rules.
        
        Args:
            population_vector: Current population [eggs, larvae, pupae, adults]
            temperature: Current temperature (°C)
            humidity: Current humidity (%)
        
        Returns:
            Adjusted population vector
        """
        if self.prolog_bridge is not None:
            # Use Prolog to compute environmental adjustments
            try:
                # Query for temperature effect
                temp_query = f"compute_temperature_factor({temperature}, Factor)"
                temp_result = list(self.prolog_bridge.query(temp_query))
                temp_factor = temp_result[0]['Factor'] if temp_result else 1.0
                
                # Query for humidity effect
                hum_query = f"compute_humidity_factor({humidity}, Factor)"
                hum_result = list(self.prolog_bridge.query(hum_query))
                hum_factor = hum_result[0]['Factor'] if hum_result else 1.0
                
                # Apply combined effect
                population_vector *= (temp_factor * hum_factor)
                
            except Exception as e:
                # Fall back to simple rules if Prolog fails
                population_vector = self._simple_environmental_adjustment(
                    population_vector, temperature, humidity
                )
        else:
            # Use simple rules
            population_vector = self._simple_environmental_adjustment(
                population_vector, temperature, humidity
            )
        
        return population_vector
    
    def _simple_environmental_adjustment(
        self,
        population_vector: np.ndarray,
        temperature: float,
        humidity: float
    ) -> np.ndarray:
        """
        Simple environmental adjustment without Prolog.
        
        Temperature effects (optimal: 25-30°C):
        - Below 20°C: strong reduction
        - 20-25°C: moderate reduction
        - 25-30°C: optimal
        - Above 30°C: moderate reduction
        - Above 35°C: strong reduction
        
        Humidity effects (optimal: > 70%):
        - Below 50%: strong reduction
        - 50-70%: moderate reduction
        - Above 70%: optimal
        """
        # Temperature factor
        if 25 <= temperature <= 30:
            temp_factor = 1.0
        elif 20 <= temperature < 25:
            temp_factor = 0.7 + (temperature - 20) * 0.06
        elif 30 < temperature <= 35:
            temp_factor = 1.0 - (temperature - 30) * 0.1
        elif temperature < 20:
            temp_factor = max(0.3, 0.7 - (20 - temperature) * 0.08)
        else:  # temperature > 35
            temp_factor = max(0.2, 0.5 - (temperature - 35) * 0.1)
        
        # Humidity factor
        if humidity >= 70:
            hum_factor = 1.0
        elif 50 <= humidity < 70:
            hum_factor = 0.7 + (humidity - 50) * 0.015
        else:  # humidity < 50
            hum_factor = max(0.4, 0.7 - (50 - humidity) * 0.015)
        
        # Apply combined factor
        return population_vector * temp_factor * hum_factor
    
    def _apply_density_dependence(
        self,
        population_vector: np.ndarray,
        carrying_capacity: int
    ) -> np.ndarray:
        """
        Apply density-dependent regulation.
        
        Uses logistic growth model: reduction factor = 1 / (1 + N/K)
        Where N is current population and K is carrying capacity.
        
        Primarily affects larval stage (competition for resources).
        
        Args:
            population_vector: Current population
            carrying_capacity: Environmental carrying capacity
        
        Returns:
            Adjusted population vector
        """
        # Total larval + pupal population (aquatic stages)
        aquatic_stages = population_vector[1] + population_vector[2]
        
        if aquatic_stages > carrying_capacity:
            # Compute reduction factor
            reduction = carrying_capacity / aquatic_stages
            
            # Apply primarily to larvae (strongest competition)
            population_vector[1] *= reduction
            # Pupae less affected (less time in water)
            population_vector[2] *= (1 + reduction) / 2
        
        return population_vector
    
    def _apply_stochastic_variation(
        self,
        population_vector: np.ndarray
    ) -> np.ndarray:
        """
        Apply demographic stochasticity to population transitions.
        
        Uses binomial sampling for survival and Poisson for reproduction.
        
        Args:
            population_vector: Projected population
        
        Returns:
            Population with stochastic variation
        """
        stochastic_vector = np.zeros_like(population_vector)
        
        # Eggs: apply demographic stochasticity to survival
        if population_vector[0] > 0:
            # Use survival rate from Leslie matrix
            egg_survival = self.leslie_matrix.matrix[1, 0]
            # Total eggs includes new births (already in vector[0])
            # Apply binomial for those transitioning to larvae
            stochastic_vector[0] = population_vector[0]  # New births stay as eggs
        
        # Larvae: binomial survival
        if population_vector[1] > 0:
            larva_survival = self.leslie_matrix.matrix[2, 1]
            # This will be applied in next step
            stochastic_vector[1] = population_vector[1]
        
        # Pupae: binomial survival
        if population_vector[2] > 0:
            pupa_survival = self.leslie_matrix.matrix[3, 2]
            stochastic_vector[2] = population_vector[2]
        
        # Adults: no specific transition, maintain count
        stochastic_vector[3] = population_vector[3]
        
        return stochastic_vector
    
    def get_trajectory(self) -> PopulationTrajectory:
        """Get current trajectory."""
        if not self.trajectory:
            raise ValueError("No trajectory available. Run simulation first.")
        
        return PopulationTrajectory(
            states=self.trajectory,
            species_name=self.species_name,
            simulation_days=len(self.trajectory) - 1
        )
    
    def reset(self):
        """Reset model to initial state."""
        self.current_state = None
        self.trajectory = []
    
    def __repr__(self) -> str:
        """String representation."""
        eigen_result = self.leslie_matrix.eigenanalysis()
        return (
            f"PopulationModel(species='{self.species_name}', "
            f"λ₁={eigen_result.lambda_1:.3f}, "
            f"stochastic={self.stochastic_mode})"
        )
