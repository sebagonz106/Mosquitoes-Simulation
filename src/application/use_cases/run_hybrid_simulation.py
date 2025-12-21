"""
Run Hybrid Simulation Use Case
===============================

Execute both population and agent simulations in parallel for comparison.
"""

from dataclasses import dataclass
from typing import Optional, Dict

from application.use_cases.base import UseCase, BaseResponse, ValidationError
from application.dtos import SimulationConfig, HybridResult
from application.services.simulation_service import SimulationService


@dataclass
class RunHybridSimulationRequest:
    """
    Request to run both simulation approaches for comparison.
    
    Attributes:
        species_id: Identifier of the species to simulate
        duration_days: Number of days to simulate
        initial_eggs: Initial number of eggs (population model)
        initial_larvae: Initial number of larvae (population model)
        initial_pupae: Initial number of pupae (population model)
        initial_adults: Initial number of adults (both models)
        num_predators: Number of predator agents (agent model only)
        predator_species: Identifier of predator species
        temperature: Environmental temperature in Celsius
        humidity: Environmental humidity (0-100%)
        water_availability: Water availability factor (0-1)
        random_seed: Seed for reproducibility (optional)
    """
    species_id: str
    duration_days: int
    initial_eggs: int
    initial_larvae: int
    initial_pupae: int
    initial_adults: int
    num_predators: int = 0
    predator_species: str = 'toxorhynchites'
    temperature: float = 25.0
    humidity: float = 70.0
    water_availability: float = 1.0
    random_seed: Optional[int] = None


@dataclass
class RunHybridSimulationResponse(BaseResponse):
    """
    Response from hybrid simulation with both approaches.
    
    Attributes:
        success: Whether simulation completed successfully
        result: HybridResult containing both simulation results and comparison
        error: Error message if simulation failed
        execution_time_seconds: Time taken to execute
        timestamp: ISO timestamp of execution
    """
    result: Optional[HybridResult] = None


class RunHybridSimulation(UseCase[RunHybridSimulationRequest, RunHybridSimulationResponse]):
    """
    Use case for executing both simulation approaches and comparing results.
    
    Validates input parameters and delegates to SimulationService.
    """
    
    def __init__(self, simulation_service: Optional[SimulationService] = None):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for running simulations (default: creates new instance)
        """
        self.simulation_service = simulation_service or SimulationService()
    
    def validate_request(self, request: RunHybridSimulationRequest) -> None:
        """
        Validate simulation parameters.
        
        Args:
            request: Simulation parameters to validate
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        # Validate duration
        if request.duration_days <= 0:
            raise ValidationError("duration_days must be positive")
        if request.duration_days > 10000:
            raise ValidationError("duration_days cannot exceed 10000 (too long)")
        
        # Validate initial populations (must be non-negative)
        if request.initial_eggs < 0:
            raise ValidationError("initial_eggs cannot be negative")
        if request.initial_larvae < 0:
            raise ValidationError("initial_larvae cannot be negative")
        if request.initial_pupae < 0:
            raise ValidationError("initial_pupae cannot be negative")
        if request.initial_adults <= 0:
            raise ValidationError("initial_adults must be positive (need at least 1 agent)")
        
        # Validate adults is reasonable for agent simulation
        if request.initial_adults > 10000:
            raise ValidationError("initial_adults cannot exceed 10000 (too many agents)")
        
        # At least one stage must have population for population model
        total_initial = (request.initial_eggs + request.initial_larvae + 
                        request.initial_pupae + request.initial_adults)
        if total_initial == 0:
            raise ValidationError("At least one life stage must have initial population > 0")
        
        # Validate predators
        if request.num_predators < 0:
            raise ValidationError("num_predators cannot be negative")
        if request.num_predators > 1000:
            raise ValidationError("num_predators cannot exceed 1000 (too many)")
        
        # Validate temperature range
        if not (-10 <= request.temperature <= 50):
            raise ValidationError("temperature must be between -10 and 50 degrees Celsius")
        
        # Validate humidity percentage
        if not (0 <= request.humidity <= 100):
            raise ValidationError("humidity must be between 0 and 100%")
        
        # Validate water availability
        if not (0 <= request.water_availability <= 1):
            raise ValidationError("water_availability must be between 0 and 1")
        
        # Validate species exists
        available_species = self.simulation_service.get_available_species()
        if request.species_id not in available_species:
            raise ValidationError(
                f"species_id '{request.species_id}' not found. "
                f"Available: {', '.join(available_species)}"
            )
        
        # Validate predator species if predators specified
        if request.num_predators > 0:
            available_predators = self.simulation_service.get_available_predators()
            if request.predator_species not in available_predators:
                raise ValidationError(
                    f"predator_species '{request.predator_species}' not found. "
                    f"Available: {', '.join(available_predators)}"
                )
    
    def _execute(self, request: RunHybridSimulationRequest) -> RunHybridSimulationResponse:
        """
        Execute both simulation approaches and compare.
        
        Args:
            request: Validated simulation parameters
            
        Returns:
            Response with both results and comparison
            
        Raises:
            ExecutionError: If simulation fails
        """
        # Create configuration DTO (same for both)
        config = SimulationConfig(
            species_id=request.species_id,
            duration_days=request.duration_days,
            initial_eggs=request.initial_eggs,
            initial_larvae=request.initial_larvae,
            initial_pupae=request.initial_pupae,
            initial_adults=request.initial_adults,
            temperature=request.temperature,
            humidity=request.humidity,
            water_availability=request.water_availability,
            random_seed=request.random_seed
        )
        
        # Execute hybrid simulation
        hybrid_result = self.simulation_service.run_hybrid_simulation(
            config=config,
            num_predators=request.num_predators,
            predator_species=request.predator_species
        )
        
        # Return success response
        return RunHybridSimulationResponse(
            success=True,
            result=hybrid_result
        )
