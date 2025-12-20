"""
Run Population Simulation Use Case
===================================

Execute a population dynamics simulation using mathematical models.
"""

from dataclasses import dataclass
from typing import Optional

from application.use_cases.base import UseCase, BaseResponse, ValidationError
from application.dtos import SimulationConfig, PopulationResult
from application.services.simulation_service import SimulationService


@dataclass
class RunPopulationSimulationRequest:
    """
    Request to run a population-based simulation.
    
    Attributes:
        species_id: Identifier of the species to simulate
        duration_days: Number of days to simulate
        initial_eggs: Initial number of eggs
        initial_larvae: Initial number of larvae
        initial_pupae: Initial number of pupae
        initial_adults: Initial number of adults
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
    temperature: float = 25.0
    humidity: float = 70.0
    water_availability: float = 1.0
    random_seed: Optional[int] = None


@dataclass
class RunPopulationSimulationResponse(BaseResponse):
    """
    Response from population simulation.
    
    Attributes:
        success: Whether simulation completed successfully
        result: Population simulation result with trajectories
        error: Error message if simulation failed
        execution_time_seconds: Time taken to execute
        timestamp: ISO timestamp of execution
    """
    result: Optional[PopulationResult] = None


class RunPopulationSimulation(UseCase[RunPopulationSimulationRequest, RunPopulationSimulationResponse]):
    """
    Use case for executing population dynamics simulation.
    
    Validates input parameters and delegates to SimulationService.
    """
    
    def __init__(self, simulation_service: Optional[SimulationService] = None):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for running simulations (default: creates new instance)
        """
        self.simulation_service = simulation_service or SimulationService()
    
    def validate_request(self, request: RunPopulationSimulationRequest) -> None:
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
        if request.initial_adults < 0:
            raise ValidationError("initial_adults cannot be negative")
        
        # At least one stage must have population
        total_initial = (request.initial_eggs + request.initial_larvae + 
                        request.initial_pupae + request.initial_adults)
        if total_initial == 0:
            raise ValidationError("At least one life stage must have initial population > 0")
        
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
    
    def _execute(self, request: RunPopulationSimulationRequest) -> RunPopulationSimulationResponse:
        """
        Execute population simulation.
        
        Args:
            request: Validated simulation parameters
            
        Returns:
            Response with simulation results
            
        Raises:
            ExecutionError: If simulation fails
        """
        # Create configuration DTO
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
        
        # Execute simulation
        result = self.simulation_service.run_population_simulation(config)
        
        # Return success response
        return RunPopulationSimulationResponse(
            success=True,
            result=result
        )
