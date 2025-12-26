"""
Application Layer - Population Service
======================================

Service for executing population-based simulations.
"""

from typing import Dict, List, Optional
import numpy as np
import logging

from domain.entities.population import Population
from domain.entities.species import Species
from domain.models.population_model import PopulationModel
from domain.models.environment_model import EnvironmentModel
from application.dtos import SimulationConfig, PopulationResult, PredatorPreyConfig
from application.helpers import get_config_manager
from application.services.predator_prey_service import PredatorPreyService

# Configure logging
logger = logging.getLogger(__name__)


class PopulationService:
    """
    Service for population dynamics simulations.
    
    This service manages the creation and execution of population-based
    simulations using the domain layer entities and converting results
    to application-layer DTOs.
    
    Also provides access to predator-prey simulations via PredatorPreyService.
    
    Methods:
        create_population: Create a population from config
        simulate: Execute single-species simulation
        simulate_predator_prey: Execute predator-prey simulation (Etapa 2)
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
        
        # OVERRIDE environmental values with user input from SimulationConfig
        env_config.temperature = config.temperature
        env_config.humidity = config.humidity
        env_config.water_availability = config.water_availability
        
        environment_model = EnvironmentModel(
            config=env_config,
            days=config.duration_days + 1
        )
        
        # Initialize PrologBridge for dynamic survival rate adjustment
        # Falls back to None if unavailable (uses static rates)
        prolog_bridge = None
        try:
            from infrastructure.prolog_bridge import PrologBridge
            prolog_bridge = PrologBridge(config_manager)
            prolog_bridge.inject_parameters()
            logger.debug("PrologBridge initialized for dynamic simulation")
        except Exception as e:
            logger.debug(f"PrologBridge not available, using static rates: {e}")
        
        # Create PopulationModel with optional Prolog integration
        model = PopulationModel(
            species_config=species_config,
            environment_model=environment_model,
            prolog_bridge=prolog_bridge,
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
        
        # PROLOG ANALYSIS: Analyze results with Prolog inference engine
        try:
            prolog_analysis = PopulationService._analyze_with_prolog(
                result, config, time_array, 
                eggs_trajectory, larvae_trajectory, 
                pupae_trajectory, adults_trajectory
            )
            result.prolog_analysis = prolog_analysis
            logger.info(f"Prolog analysis completed: {prolog_analysis.get('trend')}")
        except Exception as e:
            logger.warning(f"Prolog analysis failed (simulation continues): {e}")
            result.prolog_analysis = None
        
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
    
    @staticmethod
    def _analyze_with_prolog(
        result: PopulationResult,
        config: SimulationConfig,
        time_array: np.ndarray,
        eggs_trajectory: np.ndarray,
        larvae_trajectory: np.ndarray,
        pupae_trajectory: np.ndarray,
        adults_trajectory: np.ndarray
    ) -> Dict:
        """
        Analyze simulation results using Prolog inference engine.
        
        This method:
        1. Initializes PrologBridge with configuration
        2. Injects simulation results as Prolog facts
        3. Executes declarative queries for qualitative analysis
        4. Returns interpretation of results
        
        Args:
            result: PopulationResult with simulation data
            config: SimulationConfig used for simulation
            time_array: Array of day numbers
            eggs_trajectory: Eggs population over time
            larvae_trajectory: Larvae population over time
            pupae_trajectory: Pupae population over time
            adults_trajectory: Adults population over time
        
        Returns:
            Dictionary with Prolog analysis results:
            - trend: Population trend ('growing', 'stable', 'declining')
            - extinction_risk: Risk level ('low', 'moderate', 'high', 'critical')
            - equilibrium_days: List of days where equilibrium was reached
            - peak_analysis: Interpretation of peak day
        
        Raises:
            Exception: If Prolog analysis fails
        """
        from infrastructure.prolog_bridge import PrologBridge
        
        logger.info("Starting Prolog analysis...")
        
        # 1. Initialize Prolog Bridge
        config_manager = get_config_manager()
        prolog = PrologBridge(config_manager)
        prolog.inject_parameters()
        
        # 2. Inject simulation results into Prolog
        logger.debug("Injecting simulation data into Prolog...")
        
        for day in range(len(time_array)):
            # Initialize population states for this day
            prolog.initialize_population(
                config.species_id, 'egg', 
                int(eggs_trajectory[day]), day
            )
            prolog.initialize_population(
                config.species_id, 'larva_l1', 
                int(larvae_trajectory[day] * 0.25), day  # Approximate L1-L4 distribution
            )
            prolog.initialize_population(
                config.species_id, 'larva_l2', 
                int(larvae_trajectory[day] * 0.25), day
            )
            prolog.initialize_population(
                config.species_id, 'larva_l3', 
                int(larvae_trajectory[day] * 0.25), day
            )
            prolog.initialize_population(
                config.species_id, 'larva_l4', 
                int(larvae_trajectory[day] * 0.25), day
            )
            prolog.initialize_population(
                config.species_id, 'pupa', 
                int(pupae_trajectory[day]), day
            )
            prolog.initialize_population(
                config.species_id, 'adult_female', 
                int(adults_trajectory[day] * 0.5), day  # Assume 50/50 sex ratio
            )
            prolog.initialize_population(
                config.species_id, 'adult_male', 
                int(adults_trajectory[day] * 0.5), day
            )
            
            # Set environmental state
            prolog.set_environment_state(
                day, 
                config.temperature if config.temperature else 27.0,
                config.humidity if config.humidity else 75.0
            )
        
        # 3. Execute Prolog queries
        logger.debug("Executing Prolog queries...")
        
        final_day = len(time_array) - 1
        
        # Query: Population trend
        trend = prolog.get_population_trend(config.species_id, final_day)
        
        # Query: Extinction risk
        extinction_risk = prolog.get_extinction_risk(config.species_id, final_day)
        
        # Query: Equilibrium days (check each day)
        equilibrium_days = []
        for day in range(10, final_day):  # Start from day 10 to allow stabilization
            if prolog.check_ecological_equilibrium(day):
                equilibrium_days.append(day)
        
        # Peak analysis
        peak_day = result.statistics['peak_day']
        peak_value = result.statistics['peak_population']
        
        if peak_day > 0:
            trend_before_peak = prolog.get_population_trend(
                config.species_id, max(0, peak_day - 1)
            )
        else:
            trend_before_peak = 'initial'
        
        if peak_day < final_day:
            trend_after_peak = prolog.get_population_trend(
                config.species_id, min(final_day, peak_day + 1)
            )
        else:
            trend_after_peak = 'stable'
        
        # Interpret peak
        peak_interpretation = PopulationService._interpret_peak(
            peak_day, peak_value, trend_before_peak, trend_after_peak
        )
        
        # 4. Build analysis result
        analysis = {
            'trend': trend,
            'extinction_risk': extinction_risk,
            'equilibrium_days': equilibrium_days,
            'equilibrium_reached': len(equilibrium_days) > 0,
            'equilibrium_day_first': equilibrium_days[0] if equilibrium_days else None,
            'peak_analysis': {
                'day': peak_day,
                'value': peak_value,
                'trend_before': trend_before_peak,
                'trend_after': trend_after_peak,
                'interpretation': peak_interpretation
            }
        }
        
        logger.info(f"Prolog analysis complete: trend={trend}, risk={extinction_risk}")
        
        return analysis
    
    @staticmethod
    def _interpret_peak(
        peak_day: int, 
        peak_value: float, 
        trend_before: str, 
        trend_after: str
    ) -> str:
        """
        Generate natural language interpretation of population peak.
        
        Args:
            peak_day: Day when peak occurred
            peak_value: Population value at peak
            trend_before: Trend before peak
            trend_after: Trend after peak
        
        Returns:
            Natural language interpretation string
        """
        if trend_before == 'growing' and trend_after == 'declining':
            return (f"Pico poblacional alcanzado en día {peak_day} con {int(peak_value)} individuos. "
                   f"La población creció hasta este punto y luego comenzó a declinar, "
                   f"posiblemente debido a limitaciones ambientales o capacidad de carga.")
        
        elif trend_before == 'growing' and trend_after == 'stable':
            return (f"Pico poblacional de {int(peak_value)} individuos en día {peak_day}, "
                   f"seguido de estabilización. Indica que la población alcanzó "
                   f"equilibrio cerca de la capacidad de carga del ambiente.")
        
        elif trend_before == 'stable' and trend_after == 'stable':
            return (f"Población fluctuó alrededor de {int(peak_value)} individuos cerca del día {peak_day}, "
                   f"manteniendo equilibrio estable durante la simulación.")
        
        elif trend_after == 'growing':
            return (f"Población alcanzó {int(peak_value)} individuos en día {peak_day} "
                   f"y continúa en crecimiento, indicando condiciones favorables persistentes.")
        
        else:
            return (f"Pico de {int(peak_value)} individuos observado en día {peak_day}.")    
    # =========================================================================
    # PREDATOR-PREY INTEGRATION (Etapa 2)
    # =========================================================================
    
    @staticmethod
    def simulate_predator_prey(config: PredatorPreyConfig, use_prolog: bool = True):
        """
        Execute predator-prey simulation.
        
        Delegates to PredatorPreyService for full predator-prey dynamics.
        
        Args:
            config: PredatorPreyConfig with prey and predator parameters
            use_prolog: Whether to use Prolog for dynamic rate inference
            
        Returns:
            PredatorPreyResult from PredatorPreyService.simulate()
            
        Example:
            >>> config = PredatorPreyConfig(
            ...     species_id='aedes_aegypti',
            ...     predator_species_id='toxorhynchites',
            ...     duration_days=90,
            ...     initial_adults=100,
            ...     predator_initial_larvae=20
            ... )
            >>> result = PopulationService.simulate_predator_prey(config)
            >>> print(result.get_predation_impact())
        """
        return PredatorPreyService.simulate(config, use_prolog)
    
    @staticmethod
    def compare_predation_effect(config: PredatorPreyConfig, use_prolog: bool = True):
        """
        Compare prey population with and without predators.
        
        Runs two simulations (one with predators, one without) and returns
        comparison metrics showing predation impact.
        
        Args:
            config: PredatorPreyConfig including predator species and populations
            use_prolog: Whether to use Prolog for rate inference
            
        Returns:
            Dictionary with comparison metrics showing predation impact
            
        Example:
            >>> comparison = PopulationService.compare_predation_effect(config)
            >>> print(f"Predation reduced prey by {comparison['predation_impact']['reduction_percent']}%")
        """
        return PredatorPreyService.compare_with_without_predators(config, use_prolog)
    
    @staticmethod
    def get_system_equilibrium(predator_prey_result):
        """
        Analyze predator-prey system equilibrium.
        
        Args:
            predator_prey_result: PredatorPreyResult from simulate_predator_prey
            
        Returns:
            Dictionary with equilibrium status and stability metrics
        """
        return PredatorPreyService.get_equilibrium_status(predator_prey_result)