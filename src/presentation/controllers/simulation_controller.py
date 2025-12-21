"""
Presentation Layer - Simulation Controller
===========================================

Controller to manage simulation execution and state.
"""

import sys
import os
from typing import Optional, Callable, Dict, Any
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from application.services.simulation_service import SimulationService
from application.dtos import SimulationConfig, PopulationResult, AgentResult, HybridResult


class SimulationController:
    """
    Controller for simulation operations.
    
    Bridges the presentation layer with application services,
    managing simulation execution and results.
    
    Features:
    - Execute population, agent, and hybrid simulations
    - Progress tracking and cancellation
    - Result caching
    - Error handling
    """
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize simulation controller.
        
        Args:
            checkpoint_dir: Directory for checkpoint files
        """
        self.service = SimulationService(checkpoint_dir)
        self.current_result = None
        self.is_running = False
        self._cancel_requested = False
        
    def run_population_simulation(
        self,
        config: SimulationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> PopulationResult:
        """
        Execute population simulation.
        
        Args:
            config: Simulation configuration
            progress_callback: Optional callback(current_day, total_days)
            
        Returns:
            PopulationResult with trajectories
            
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
            
            # Run simulation
            result = self.service.run_population_simulation(config)
            
            # Cache result
            self.current_result = result
            
            return result
            
        finally:
            self.is_running = False
            
    def run_agent_simulation(
        self,
        config: SimulationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AgentResult:
        """
        Execute agent-based simulation.
        
        Args:
            config: Simulation configuration
            progress_callback: Optional callback(current_day, total_days)
            
        Returns:
            AgentResult with agent histories
            
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
            
            # Run simulation
            result = self.service.run_agent_simulation(config)
            
            # Cache result
            self.current_result = result
            
            return result
            
        finally:
            self.is_running = False
            
    def run_hybrid_simulation(
        self,
        config: SimulationConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> HybridResult:
        """
        Execute hybrid simulation (population + agent).
        
        Args:
            config: Simulation configuration
            progress_callback: Optional callback(current_day, total_days)
            
        Returns:
            HybridResult with both approaches
            
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
            
            # Run simulation
            result = self.service.run_hybrid_simulation(config)
            
            # Cache result
            self.current_result = result
            
            return result
            
        finally:
            self.is_running = False
            
    def cancel_simulation(self):
        """Request cancellation of running simulation."""
        if self.is_running:
            self._cancel_requested = True
            
    def get_last_result(self):
        """Get the most recent simulation result."""
        return self.current_result
    
    def clear_result(self):
        """Clear cached result."""
        self.current_result = None
        
    def get_default_config(self, species_id: str = 'aedes_aegypti') -> SimulationConfig:
        """
        Get default configuration for a species.
        
        Args:
            species_id: Species identifier
            
        Returns:
            Default SimulationConfig
        """
        if species_id == 'aedes_aegypti':
            return SimulationConfig(
                species_id='aedes_aegypti',
                duration_days=90,
                initial_eggs=1000,
                initial_larvae=500,
                initial_pupae=100,
                initial_adults=50,
                temperature=25.0,
                humidity=70.0,
                water_availability=1.0
            )
        elif species_id == 'toxorhynchites':
            return SimulationConfig(
                species_id='toxorhynchites',
                duration_days=90,
                initial_eggs=100,
                initial_larvae=50,
                initial_pupae=10,
                initial_adults=5,
                temperature=25.0,
                humidity=70.0,
                water_availability=1.0
            )
        else:
            raise ValueError(f"Unknown species: {species_id}")
            
    def save_checkpoint(self, name: str, config: SimulationConfig, simulation_type: str) -> Path:
        """
        Save current result as checkpoint.
        
        Args:
            name: Checkpoint name
            config: Simulation configuration used
            simulation_type: Type of simulation ('population', 'agent', 'hybrid')
            
        Returns:
            Path to checkpoint file
            
        Raises:
            ValueError: If no result to save
        """
        if self.current_result is None:
            raise ValueError("No result to save")
        
        return self.service.save_checkpoint(
            self.current_result,
            config,
            simulation_type,
            name
        )
    
    def list_checkpoints(self) -> list:
        """
        List available checkpoints.
        
        Returns:
            List of checkpoint info dictionaries
        """
        return self.service.list_checkpoints()
