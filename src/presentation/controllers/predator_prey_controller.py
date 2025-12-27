"""
Presentation Layer - Predator-Prey Controller
===============================================

Controller to manage predator-prey simulation execution and state.
"""

import sys
import os
from typing import Optional, Callable, Dict, Any
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from application.services.population_service import PopulationService
from application.dtos import PredatorPreyConfig, PredatorPreyResult


class PredatorPreyController:
    """
    Controller for predator-prey simulation operations.
    
    Bridges the presentation layer with application services,
    managing predator-prey simulation execution and results.
    
    Features:
    - Execute predator-prey simulations
    - Execute comparison simulations (with/without predators)
    - Get equilibrium analysis
    - Progress tracking and cancellation
    - Result caching
    - Error handling
    """
    
    def __init__(self):
        """Initialize predator-prey controller."""
        self.service = PopulationService()
        self.current_result = None
        self.is_running = False
        self._cancel_requested = False
        
    def run_predator_prey_simulation(
        self,
        config: PredatorPreyConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> PredatorPreyResult:
        """
        Execute predator-prey simulation.
        
        Args:
            config: PredatorPreyConfig simulation configuration
            progress_callback: Optional callback(current_day, total_days)
            
        Returns:
            PredatorPreyResult with trajectories and statistics
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If simulation is already running
        """
        if self.is_running:
            raise RuntimeError("Simulation already running")
        
        # Validate config
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        try:
            self.is_running = True
            self._cancel_requested = False
            
            # Run simulation with Prolog enabled
            result = self.service.simulate_predator_prey(config, use_prolog=True)
            
            # Cache result
            self.current_result = result
            
            return result
            
        finally:
            self.is_running = False
    
    def run_predator_prey_comparison(
        self,
        config: PredatorPreyConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, PredatorPreyResult]:
        """
        Execute comparison simulation: with and without predators.
        
        Args:
            config: PredatorPreyConfig simulation configuration
            progress_callback: Optional callback(current_day, total_days)
            
        Returns:
            Dictionary with keys 'with_predators' and 'without_predators'
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If simulation is already running
        """
        if self.is_running:
            raise RuntimeError("Simulation already running")
        
        # Validate config
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        try:
            self.is_running = True
            self._cancel_requested = False
            
            # Run comparison with Prolog enabled
            comparison = self.service.compare_predation_effect(config, use_prolog=True)
            
            return comparison
            
        finally:
            self.is_running = False
    
    def get_equilibrium_analysis(self, result: PredatorPreyResult) -> Dict[str, Any]:
        """
        Analyze equilibrium status of simulation result.
        
        Args:
            result: PredatorPreyResult from simulation
            
        Returns:
            Dictionary with equilibrium classification and metrics
        """
        return self.service.get_system_equilibrium(result)
    
    def cancel_simulation(self):
        """Request cancellation of running simulation."""
        self._cancel_requested = True
        self.is_running = False
    
    def is_simulation_running(self) -> bool:
        """Check if simulation is currently running."""
        return self.is_running
    
    def get_cached_result(self) -> Optional[PredatorPreyResult]:
        """Get last cached simulation result."""
        return self.current_result
    
    def clear_cache(self):
        """Clear cached result."""
        self.current_result = None
