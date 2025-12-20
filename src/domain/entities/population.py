"""
Population Entity Module
========================

Represents aggregated mosquito populations.

Author: Mosquito Simulation System
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from domain.models.population_model import PopulationState, PopulationTrajectory, PopulationModel
from domain.entities.species import Species


@dataclass
class PopulationSnapshot:
    """
    Snapshot of population state at a specific time.
    
    Provides business-level view of population state with
    convenient access to common metrics.
    
    Attributes:
        day: Simulation day
        eggs: Number of eggs
        larvae: Total number of larvae (all stages)
        pupae: Number of pupae
        adults: Number of adults
        total: Total population size
        species_id: Species identifier
    """
    
    day: int
    eggs: int
    larvae: int
    pupae: int
    adults: int
    total: int
    species_id: str
    
    @classmethod
    def from_population_state(cls, state: PopulationState, species_id: str) -> 'PopulationSnapshot':
        """
        Create snapshot from PopulationState.
        
        Args:
            state: Population state from model
            species_id: Species identifier
        
        Returns:
            PopulationSnapshot instance
        """
        eggs = int(state.eggs)
        larvae = int(np.sum(state.larvae))
        pupae = int(state.pupae)
        adults = int(state.adults)
        
        return cls(
            day=state.day,
            eggs=eggs,
            larvae=larvae,
            pupae=pupae,
            adults=adults,
            total=eggs + larvae + pupae + adults,
            species_id=species_id
        )
    
    def is_extinct(self) -> bool:
        """Check if population is extinct."""
        return self.total == 0
    
    def aquatic_count(self) -> int:
        """Get count of aquatic stages."""
        return self.eggs + self.larvae + self.pupae
    
    def reproductive_count(self) -> int:
        """Get count of reproductive adults."""
        return self.adults
    
    def stage_proportions(self) -> Dict[str, float]:
        """
        Get proportion of each life stage.
        
        Returns:
            Dictionary with stage proportions [0-1]
        """
        if self.total == 0:
            return {
                'eggs': 0.0,
                'larvae': 0.0,
                'pupae': 0.0,
                'adults': 0.0
            }
        
        return {
            'eggs': self.eggs / self.total,
            'larvae': self.larvae / self.total,
            'pupae': self.pupae / self.total,
            'adults': self.adults / self.total
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PopulationSnapshot(day={self.day}, species='{self.species_id}', "
            f"E={self.eggs}, L={self.larvae}, P={self.pupae}, A={self.adults}, "
            f"total={self.total})"
        )


class Population:
    """
    Represents an aggregated mosquito population.
    
    This class provides a business-level interface to population
    dynamics, wrapping the mathematical PopulationModel with
    domain-specific operations.
    
    Attributes:
        species: Species this population belongs to
        model: Underlying population dynamics model
        trajectory: Complete simulation trajectory (after simulation)
        current_state: Current population state
    """
    
    def __init__(self, species: Species, model: PopulationModel):
        """
        Initialize population.
        
        Args:
            species: Species entity
            model: Population dynamics model
        """
        self.species = species
        self.model = model
        self.trajectory: Optional[PopulationTrajectory] = None
        self.current_state: Optional[PopulationState] = None
    
    def initialize(
        self,
        initial_eggs: int = 0,
        initial_larvae: Optional[Union[np.ndarray, int]] = None,
        initial_pupae: int = 0,
        initial_adults: int = 0
    ) -> None:
        """
        Initialize population with starting values.
        
        Args:
            initial_eggs: Starting number of eggs
            initial_larvae: Starting larvae by stage (array [L1, L2, L3, L4]) or total (int)
                           If array provided, will sum to get total
            initial_pupae: Starting number of pupae
            initial_adults: Starting number of adults
        """
        # Handle larvae input: convert array to total if necessary
        if initial_larvae is None:
            larvae_total = 0
        elif isinstance(initial_larvae, np.ndarray):
            larvae_total = int(np.sum(initial_larvae))
        else:
            larvae_total = int(initial_larvae)
        
        self.current_state = self.model.initialize(
            initial_eggs=initial_eggs,
            initial_larvae=larvae_total,
            initial_pupae=initial_pupae,
            initial_adults=initial_adults
        )
    
    def simulate(self, days: int) -> PopulationTrajectory:
        """
        Run population simulation.
        
        Args:
            days: Number of days to simulate
        
        Returns:
            Complete population trajectory
        """
        self.trajectory = self.model.simulate(days=days)
        
        # Update current state to final state
        if self.trajectory.states:
            self.current_state = self.trajectory.states[-1]
        
        return self.trajectory
    
    def get_current_snapshot(self) -> Optional[PopulationSnapshot]:
        """
        Get current population snapshot.
        
        Returns:
            PopulationSnapshot or None if not initialized
        """
        if self.current_state:
            return PopulationSnapshot.from_population_state(
                self.current_state,
                self.species.species_id
            )
        return None
    
    def get_trajectory_snapshots(self) -> List[PopulationSnapshot]:
        """
        Get all trajectory snapshots.
        
        Returns:
            List of PopulationSnapshot for each day
        """
        if not self.trajectory:
            return []
        
        return [
            PopulationSnapshot.from_population_state(state, self.species.species_id)
            for state in self.trajectory.states
        ]
    
    def get_extinction_day(self) -> Optional[int]:
        """
        Get day when population went extinct.
        
        Returns:
            Day of extinction or None if not extinct
        """
        if self.trajectory:
            # Check if population went to zero
            for state in self.trajectory.states:
                if state.total == 0:
                    return state.day
        return None
    
    def is_extinct(self) -> bool:
        """Check if population is currently extinct."""
        snapshot = self.get_current_snapshot()
        return snapshot.is_extinct() if snapshot else True
    
    def get_peak_population(self) -> tuple[int, int]:
        """
        Get peak population and day it occurred.
        
        Returns:
            Tuple of (day, population_size)
        """
        snapshots = self.get_trajectory_snapshots()
        if not snapshots:
            return (0, 0)
        
        peak_snapshot = max(snapshots, key=lambda s: s.total)
        return (peak_snapshot.day, peak_snapshot.total)
    
    def get_mean_population(self) -> float:
        """
        Get mean population size across trajectory.
        
        Returns:
            Mean population size
        """
        if self.trajectory:
            total_pops = [state.total for state in self.trajectory.states]
            return float(np.mean(total_pops))
        return 0.0
    
    def get_population_statistics(self) -> Dict[str, float]:
        """
        Get comprehensive population statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.trajectory:
            return {}
        
        peak_day, peak_size = self.get_peak_population()
        total_pops = [state.total for state in self.trajectory.states]
        
        extinction_day = self.get_extinction_day()
        
        return {
            'mean_population': float(np.mean(total_pops)),
            'max_population': float(np.max(total_pops)),
            'final_population': float(self.trajectory.states[-1].total) if self.trajectory.states else 0.0,
            'peak_day': peak_day,
            'peak_size': peak_size,
            'extinction_day': extinction_day if extinction_day is not None else -1,
            'is_extinct': self.is_extinct()
        }
    
    def get_stage_dynamics(self) -> Dict[str, List[int]]:
        """
        Get time series of each life stage.
        
        Returns:
            Dictionary with time series for each stage
        """
        snapshots = self.get_trajectory_snapshots()
        
        return {
            'eggs': [s.eggs for s in snapshots],
            'larvae': [s.larvae for s in snapshots],
            'pupae': [s.pupae for s in snapshots],
            'adults': [s.adults for s in snapshots],
            'total': [s.total for s in snapshots]
        }
    
    def __repr__(self) -> str:
        """String representation."""
        snapshot = self.get_current_snapshot()
        if snapshot:
            return (
                f"Population(species='{self.species.species_id}', "
                f"current_size={snapshot.total}, extinct={self.is_extinct()})"
            )
        return f"Population(species='{self.species.species_id}', uninitialized)"
    
    def __str__(self) -> str:
        """Human-readable string."""
        snapshot = self.get_current_snapshot()
        if snapshot:
            return f"{self.species.display_name} population: {snapshot.total} individuals"
        return f"{self.species.display_name} population (uninitialized)"
