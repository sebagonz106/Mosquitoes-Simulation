"""
Application Layer - Population Service
======================================

Service for executing population-based simulations.
"""

from typing import Dict, List, Optional
import numpy as np

from domain.entities.population import Population
from domain.entities.species import Species
from domain.models.population_model import PopulationModel
from domain.models.environment_model import EnvironmentModel
from application.dtos import SimulationConfig, PopulationResult
from application.helpers import get_config_manager


class PopulationService:
    """
    Service for population dynamics simulations.
    
    This service manages the creation and execution of population-based
    simulations using the domain layer entities and converting results
    to application-layer DTOs.
    
    Methods:
        create_population: Create a population from config
        simulate: Execute simulation and return results
    """
    
    @staticmethod
    def create_population(config: SimulationConfig) -> Population:
        """
        Create a Population from a configuration DTO.
        
        Args:
            config: Simulation configuration
            
        Returns:
            Initialized Population instance
            
        Raises:
            ValueError: If species_id is unknown or config is invalid
        """
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        # Get config manager
        config_manager = get_config_manager()
        
        # Check species exists
        available_species = config_manager.get_all_species_ids()
        if config.species_id not in available_species:
            raise ValueError(
                f"Unknown species '{config.species_id}'. "
                f"Available species: {available_species}"
            )
        
        # Load species configuration
        species_config = config_manager.get_species_config(config.species_id)
        
        # Create Species entity
        species = Species(config=species_config)
        
        # Create environment model (need +1 for inclusive range [0, duration_days])
        env_config = config_manager.get_environment_config()
        environment_model = EnvironmentModel(
            config=env_config,
            days=config.duration_days + 1
        )
        
        # Create PopulationModel
        model = PopulationModel(
            species_config=species_config,
            environment_model=environment_model,
            stochastic_mode=True,
            seed=config.random_seed
        )
        
        # Create Population entity
        population = Population(species=species, model=model)
        
        # Convert larvae format if needed
        if isinstance(config.initial_larvae, list):
            larvae_total = sum(config.initial_larvae)
        else:
            larvae_total = config.initial_larvae
        
        # Initialize with starting values
        population.initialize(
            initial_eggs=config.initial_eggs,
            initial_larvae=larvae_total,
            initial_pupae=config.initial_pupae,
            initial_adults=config.initial_adults
        )
        
        return population
    
    @staticmethod
    def simulate(
        config: SimulationConfig,
        save_trajectory: bool = True
    ) -> PopulationResult:
        """
        Execute a population simulation.
        
        Args:
            config: Simulation configuration
            save_trajectory: Whether to save daily trajectories
            
        Returns:
            PopulationResult with complete simulation data
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Create population
        population = PopulationService.create_population(config)
        
        # Convert larvae format if needed
        if isinstance(config.initial_larvae, list):
            larvae_total = sum(config.initial_larvae)
        else:
            larvae_total = config.initial_larvae
        
        # Run simulation directly on model with initial values
        trajectory = population.model.simulate(
            days=config.duration_days,
            initial_eggs=config.initial_eggs,
            initial_larvae=larvae_total,
            initial_pupae=config.initial_pupae,
            initial_adults=config.initial_adults
        )
        
        # Extract trajectories from simulation
        days = config.duration_days
        time_array = np.arange(days + 1, dtype=np.int32)
        
        eggs_trajectory = np.zeros(days + 1, dtype=np.float64)
        larvae_trajectory = np.zeros(days + 1, dtype=np.float64)
        pupae_trajectory = np.zeros(days + 1, dtype=np.float64)
        adults_trajectory = np.zeros(days + 1, dtype=np.float64)
        total_trajectory = np.zeros(days + 1, dtype=np.float64)
        
        # Extract data from trajectory states
        for i, state in enumerate(trajectory.states):
            eggs_trajectory[i] = state.eggs
            larvae_trajectory[i] = state.larvae
            pupae_trajectory[i] = state.pupae
            adults_trajectory[i] = state.adults
            total_trajectory[i] = state.total
        
        # Calculate statistics
        peak_day = int(np.argmax(total_trajectory))
        peak_population = float(total_trajectory[peak_day])
        
        # Find extinction day if any
        extinction_day = None
        for i, total in enumerate(total_trajectory):
            if total == 0 and i > 0:
                extinction_day = int(i)
                break
        
        statistics = {
            'peak_day': peak_day,
            'peak_population': peak_population,
            'extinction_day': extinction_day,
            'final_population': float(total_trajectory[-1]),
            'mean_eggs': float(np.mean(eggs_trajectory)),
            'mean_larvae': float(np.mean(larvae_trajectory)),
            'mean_pupae': float(np.mean(pupae_trajectory)),
            'mean_adults': float(np.mean(adults_trajectory)),
            'mean_total': float(np.mean(total_trajectory))
        }
        
        # Build result DTO
        result = PopulationResult(
            species_id=config.species_id,
            days=time_array,
            eggs=eggs_trajectory,
            larvae=larvae_trajectory,
            pupae=pupae_trajectory,
            adults=adults_trajectory,
            total_population=total_trajectory,
            statistics=statistics
        )
        
        return result
    
    @staticmethod
    def get_available_species() -> List[str]:
        """
        Get list of available species for simulation.
        
        Returns:
            List of species identifiers
        """
        config_manager = get_config_manager()
        return config_manager.get_all_species_ids()
    
    @staticmethod
    def get_species_info(species_id: str) -> Optional[Dict]:
        """
        Get parameter information for a species.
        
        Args:
            species_id: Species identifier
            
        Returns:
            Dictionary with species parameters, or None if not found
        """
        try:
            config_manager = get_config_manager()
            species_config = config_manager.get_species_config(species_id)
            
            # Extract development rates
            development_rates = {}
            for stage_name, stage_config in species_config.life_stages.items():
                duration = (stage_config.duration_min + stage_config.duration_max) / 2
                rate = 1.0 / duration if duration > 0 else 0.0
                development_rates[stage_name] = rate
            
            # Extract survival rates
            survival_rates = {}
            for stage_name, stage_config in species_config.life_stages.items():
                if stage_config.survival_to_next is not None:
                    survival_rates[stage_name] = stage_config.survival_to_next
                elif stage_config.survival_daily is not None:
                    survival_rates[stage_name] = stage_config.survival_daily
                else:
                    survival_rates[stage_name] = 0.9
            
            # Extract fecundity
            reproduction = species_config.reproduction
            fecundity = (reproduction.eggs_per_batch_min + reproduction.eggs_per_batch_max) / 2
            
            return {
                'species_id': species_config.species_id,
                'display_name': species_config.display_name,
                'development_rates': development_rates,
                'survival_rates': survival_rates,
                'fecundity': fecundity,
                'is_predatory': any(
                    stage.is_predatory 
                    for stage in species_config.life_stages.values()
                )
            }
        except Exception:
            return None
