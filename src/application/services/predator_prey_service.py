"""
Application Layer - Predator-Prey Service
==========================================

Service for executing predator-prey simulations (Etapa 2).

Manages predator-prey population dynamics simulations and provides
high-level interface for GUI and API layers.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import logging

from domain.models.population_model import PopulationModel
from domain.models.environment_model import EnvironmentModel
from application.dtos import PredatorPreyConfig, PredatorPreyResult
from application.helpers import get_config_manager
from infrastructure.prolog_bridge import create_prolog_bridge
# Configure logging
logger = logging.getLogger(__name__)


class PredatorPreyService:
    """
    Service for predator-prey population simulations.
    
    Manages creation and execution of simulations involving both prey
    (vector species like Aedes aegypti) and predators (like Toxorhynchites).
    
    Methods:
        simulate: Execute predator-prey simulation
        analyze_predation_impact: Analyze impact of predation on prey
        get_equilibrium_status: Check if system reached equilibrium
    """
    
    @staticmethod
    def simulate(config: PredatorPreyConfig, use_prolog: bool = True) -> PredatorPreyResult:
        """
        Execute predator-prey simulation.
        
        Args:
            config: Predator-prey simulation configuration
            use_prolog: Whether to use Prolog for dynamic rate inference
            
        Returns:
            PredatorPreyResult with complete simulation data
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        logger.info(f"Starting predator-prey simulation: "
                   f"{config.species_id} + {config.predator_species_id}")
        
        # Get config manager
        config_manager = get_config_manager()
        
        # Validate species
        available_species = config_manager.get_all_species_ids()
        if config.species_id not in available_species:
            raise ValueError(f"Unknown prey species '{config.species_id}'")
        if config.predator_species_id and config.predator_species_id not in available_species:
            raise ValueError(f"Unknown predator species '{config.predator_species_id}'")
        
        # Load species configurations
        prey_config = config_manager.get_species_config(config.species_id)
        predator_config = (
            config_manager.get_species_config(config.predator_species_id)
            if config.predator_species_id else None
        )
        
        # Create environment model
        env_config = config_manager.get_environment_config()
        env_config.temperature = config.temperature or env_config.temperature
        env_config.humidity = config.humidity or env_config.humidity
        env_config.water_availability = config.water_availability
        
        environment_model = EnvironmentModel(
            config=env_config,
            days=config.duration_days + 1  # +1 because we simulate 0 to duration_days
        )
        
        # Create Prolog bridge if requested
        prolog_bridge = None
        if use_prolog:
            try:
                prolog_bridge = create_prolog_bridge(config_manager)
                logger.info("Prolog bridge initialized for dynamic rate inference")
            except Exception as e:
                logger.warning(f"Could not initialize Prolog: {e}. Using static rates.")
        
        # Create population model with predators
        population_model = PopulationModel(
            species_config=prey_config,
            environment_model=environment_model,
            prolog_bridge=prolog_bridge,
            stochastic_mode=True,
            seed=config.random_seed,
            predator_config=predator_config,
            predator_populations={
                'egg': config.predator_initial_eggs,
                'larva_l1': config.predator_initial_larvae,
                'larva_l2': config.predator_initial_larvae,
                'larva_l3': config.predator_initial_larvae,
                'larva_l4': config.predator_initial_larvae,
                'pupa': config.predator_initial_pupae,
                'adult': config.predator_initial_adults
            } if predator_config else None
        )
        
        # Initialize populations
        initial_state = population_model.initialize(
            initial_eggs=config.initial_eggs,
            initial_larvae=config.initial_larvae if isinstance(config.initial_larvae, int) 
                           else sum(config.initial_larvae),
            initial_pupae=config.initial_pupae,
            initial_adults=config.initial_adults
        )
        
        # Run simulation
        prey_trajectory = []
        predator_trajectory = []
        peak_day = 0
        peak_population = 0
        extinction_day = None
        
        try:
            # Record initial state
            initial_data = {
                'day': initial_state.day,
                'eggs': int(initial_state.eggs),
                'larvae': int(initial_state.larvae),
                'pupae': int(initial_state.pupae),
                'adults': int(initial_state.adults),
                'total': int(initial_state.total),
                'temperature': float(initial_state.temperature),
                'humidity': float(initial_state.humidity),
                'carrying_capacity': int(initial_state.carrying_capacity)
            }
            prey_trajectory.append(initial_data)
            
            # Record initial predator state if present
            if population_model.has_predators:
                predator_trajectory.append(population_model.predator_state.copy())
            
            # Track peak from initial state
            if initial_state.total > peak_population:
                peak_population = int(initial_state.total)
                peak_day = 0
            
            # Run simulation steps
            for day in range(1, config.duration_days + 1):
                # Step simulation
                state = population_model.step(day)
                
                # Record prey data
                prey_data = {
                    'day': state.day,
                    'eggs': int(state.eggs),
                    'larvae': int(state.larvae),
                    'pupae': int(state.pupae),
                    'adults': int(state.adults),
                    'total': int(state.total),
                    'temperature': float(state.temperature),
                    'humidity': float(state.humidity),
                    'carrying_capacity': int(state.carrying_capacity)
                }
                prey_trajectory.append(prey_data)
                
                # Track peak
                if state.total > peak_population:
                    peak_population = int(state.total)
                    peak_day = day
                
                # Record predator data if present
                if population_model.has_predators:
                    predator_vec = population_model.predator_state.copy()
                    predator_trajectory.append(predator_vec)
                    
                    # Check extinction
                    prey_extinct = state.total == 0
                    predator_extinct = np.sum(predator_vec) == 0
                    
                    if (prey_extinct or predator_extinct) and extinction_day is None:
                        extinction_day = day
                        logger.info(f"Extinction detected on day {day}: "
                                   f"prey={prey_extinct}, predators={predator_extinct}")
            
            # Calculate statistics
            statistics = PredatorPreyService._calculate_statistics(
                prey_trajectory, predator_trajectory, population_model.has_predators
            )
            
            logger.info(f"Simulation completed: peak={peak_population} on day {peak_day}")
            
            # Create result
            result = PredatorPreyResult(
                prey_species_id=config.species_id,
                predator_species_id=config.predator_species_id,
                duration_days=config.duration_days,
                prey_trajectory=prey_trajectory,
                predator_trajectory=predator_trajectory,
                statistics=statistics,
                peak_day=peak_day,
                extinction_day=extinction_day,
                success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise
    
    @staticmethod
    def _calculate_statistics(prey_trajectory: List[Dict], 
                             predator_trajectory: List[np.ndarray],
                             has_predators: bool) -> Dict[str, float]:
        """
        Calculate summary statistics from simulation.
        
        Args:
            prey_trajectory: List of prey population states
            predator_trajectory: List of predator population vectors
            has_predators: Whether predators are present
            
        Returns:
            Dictionary of statistical summaries
        """
        if not prey_trajectory:
            return {}
        
        # Prey statistics
        prey_totals = [p['total'] for p in prey_trajectory]
        prey_stats = {
            'prey_initial': float(prey_totals[0]),
            'prey_final': float(prey_totals[-1]),
            'prey_peak': float(max(prey_totals)),
            'prey_mean': float(np.mean(prey_totals)),
            'prey_std': float(np.std(prey_totals))
        }
        
        # Predator statistics if present
        if has_predators and predator_trajectory:
            predator_totals = [float(np.sum(p)) for p in predator_trajectory]
            predator_stats = {
                'predator_initial': predator_totals[0] if predator_totals else 0.0,
                'predator_final': predator_totals[-1] if predator_totals else 0.0,
                'predator_peak': float(max(predator_totals)) if predator_totals else 0.0,
                'predator_mean': float(np.mean(predator_totals)) if predator_totals else 0.0,
                'predator_std': float(np.std(predator_totals)) if predator_totals else 0.0
            }
            prey_stats.update(predator_stats)
            
            # Predation impact
            if prey_totals[0] > 0:
                prey_stats['predation_reduction_percent'] = (
                    (1 - prey_totals[-1] / prey_totals[0]) * 100
                )
        
        return prey_stats
    
    @staticmethod
    def get_equilibrium_status(result: PredatorPreyResult) -> Dict[str, Any]:
        """
        Analyze equilibrium status of predator-prey system.
        
        Args:
            result: PredatorPreyResult from simulation
            
        Returns:
            Dictionary with equilibrium assessment
        """
        prey_traj = result.prey_trajectory
        
        if len(prey_traj) < 10:
            return {'status': 'insufficient_data', 'days': len(prey_traj)}
        
        # Analyze last 20% of simulation for stability
        analysis_start = int(len(prey_traj) * 0.8)
        final_segment = [p['total'] for p in prey_traj[analysis_start:]]
        
        # Calculate coefficient of variation
        mean_final = np.mean(final_segment)
        std_final = np.std(final_segment)
        cv = std_final / mean_final if mean_final > 0 else 1.0
        
        # Classify stability
        if cv < 0.05:
            stability = 'stable'
        elif cv < 0.15:
            stability = 'oscillating'
        elif final_segment[-1] > final_segment[0]:
            stability = 'growing'
        else:
            stability = 'declining'
        
        return {
            'status': stability,
            'coefficient_of_variation': float(cv),
            'mean_final': float(mean_final),
            'peak_population': result.statistics.get('prey_peak', 0),
            'extinction_risk': 'high' if final_segment[-1] < 10 else 'low'
        }
    
    @staticmethod
    def compare_with_without_predators(
        config: PredatorPreyConfig,
        use_prolog: bool = True
    ) -> Dict:
        """
        Compare simulation with and without predators.
        
        Args:
            config: Configuration (predator_species_id will be ignored for without case)
            use_prolog: Whether to use Prolog
            
        Returns:
            Dictionary with comparison results
        """
        logger.info("Running comparison: with and without predators")
        
        # Simulation WITHOUT predators
        config_without = PredatorPreyConfig(
            species_id=config.species_id,
            duration_days=config.duration_days,
            initial_eggs=config.initial_eggs,
            initial_larvae=config.initial_larvae,
            initial_pupae=config.initial_pupae,
            initial_adults=config.initial_adults,
            temperature=config.temperature,
            humidity=config.humidity,
            water_availability=config.water_availability,
            random_seed=config.random_seed,
            predator_species_id=None  # No predators
        )
        
        result_without = PredatorPreyService.simulate(config_without, use_prolog)
        
        # Simulation WITH predators
        result_with = PredatorPreyService.simulate(config, use_prolog)
        
        # Return full results objects for GUI visualization
        comparison = {
            'with_predators': result_with,
            'without_predators': result_without,
            'prey_species': config.species_id,
            'predation_impact': {
                'prey_reduction': int(result_without.statistics.get('prey_final', 0) - result_with.statistics.get('prey_final', 0)),
                'reduction_percent': round(
                    (result_without.statistics.get('prey_final', 0) - result_with.statistics.get('prey_final', 0)) / 
                    result_without.statistics.get('prey_final', 1) * 100, 2
                ) if result_without.statistics.get('prey_final', 0) > 0 else 0
            }
        }
        
        return comparison
