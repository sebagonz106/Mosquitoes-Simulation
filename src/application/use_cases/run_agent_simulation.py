"""
Run Agent Simulation Use Case
==============================

Execute an agent-based simulation using Prolog decision-making.
"""

from dataclasses import dataclass
from typing import Optional

from application.use_cases.base import UseCase, BaseResponse, ValidationError
from application.dtos import SimulationConfig, AgentResult
from application.services.simulation_service import SimulationService


@dataclass
class RunAgentSimulationRequest:
    """
    Request to run an agent-based simulation.
    
    Attributes:
        species_id: Identifier of the vector species to simulate
        duration_days: Number of days to simulate
        initial_adults: Initial number of adult vector agents
        num_predators: Number of predator agents (default: 0)
        predator_species: Identifier of predator species (default: 'toxorhynchites')
        temperature: Environmental temperature in Celsius
        humidity: Environmental humidity (0-100%)
        water_availability: Water availability factor (0-1)
        random_seed: Seed for reproducibility (optional)
    """
    species_id: str
    duration_days: int
    initial_adults: int
    num_predators: int = 0
    predator_species: str = 'toxorhynchites'
    temperature: float = 25.0
    humidity: float = 70.0
    water_availability: float = 1.0
    random_seed: Optional[int] = None


@dataclass
class RunAgentSimulationResponse(BaseResponse):
    """
    Response from agent simulation.
    
    Attributes:
        success: Whether simulation completed successfully
        result: Agent simulation result with individual statistics
        error: Error message if simulation failed
        execution_time_seconds: Time taken to execute
        timestamp: ISO timestamp of execution
    """
    result: Optional[AgentResult] = None


class RunAgentSimulation(UseCase[RunAgentSimulationRequest, RunAgentSimulationResponse]):
    """
    Use case for executing agent-based simulation with Prolog decisions.
    
    Validates input parameters and delegates to SimulationService.
    """
    
    def __init__(self, simulation_service: Optional[SimulationService] = None):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for running simulations (default: creates new instance)
        """
        self.simulation_service = simulation_service or SimulationService()
    
    def validate_request(self, request: RunAgentSimulationRequest) -> None:
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
        
        # Validate initial adult population
        if request.initial_adults <= 0:
            raise ValidationError("initial_adults must be positive (need at least 1 agent)")
        if request.initial_adults > 10000:
            raise ValidationError("initial_adults cannot exceed 10000 (too many agents)")
        
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
    
    def _execute(self, request: RunAgentSimulationRequest) -> RunAgentSimulationResponse:
        """
        Execute agent-based simulation.
        
        Args:
            request: Validated simulation parameters
            
        Returns:
            Response with simulation results
            
        Raises:
            ExecutionError: If simulation fails
        """
        # Create configuration DTO
        # Note: Agent simulation uses only initial_adults (other stages not supported)
        config = SimulationConfig(
            species_id=request.species_id,
            duration_days=request.duration_days,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=request.initial_adults,
            temperature=request.temperature,
            humidity=request.humidity,
            water_availability=request.water_availability,
            random_seed=request.random_seed
        )
        
        # Execute simulation
        result = self.simulation_service.run_agent_simulation(
            config=config,
            num_predators=request.num_predators,
            predator_species=request.predator_species
        )
        
        # Return success response
        return RunAgentSimulationResponse(
            success=True,
            result=result
        )
