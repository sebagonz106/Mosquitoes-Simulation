"""
Application Use Cases Package
==============================

Use cases implement application business logic following Clean Architecture.

Each use case represents a single user action or system operation.
"""

from application.use_cases.base import (
    UseCase,
    BaseResponse,
    UseCaseError,
    ValidationError,
    ExecutionError
)

from application.use_cases.run_population_simulation import (
    RunPopulationSimulation,
    RunPopulationSimulationRequest,
    RunPopulationSimulationResponse
)

from application.use_cases.run_agent_simulation import (
    RunAgentSimulation,
    RunAgentSimulationRequest,
    RunAgentSimulationResponse
)

from application.use_cases.run_hybrid_simulation import (
    RunHybridSimulation,
    RunHybridSimulationRequest,
    RunHybridSimulationResponse
)

from application.use_cases.compare_scenarios import (
    CompareScenarios,
    CompareScenariosRequest,
    CompareScenariosResponse,
    ScenarioConfig
)

from application.use_cases.get_available_configurations import (
    GetAvailableSpecies,
    GetAvailableSpeciesRequest,
    GetAvailableSpeciesResponse,
    GetAvailablePredators,
    GetAvailablePredatorsRequest,
    GetAvailablePredatorsResponse,
    GetSpeciesParameters,
    GetSpeciesParametersRequest,
    GetSpeciesParametersResponse,
    SpeciesInfo
)

from application.use_cases.manage_checkpoints import (
    SaveCheckpoint,
    SaveCheckpointRequest,
    SaveCheckpointResponse,
    LoadCheckpoint,
    LoadCheckpointRequest,
    LoadCheckpointResponse,
    ListCheckpoints,
    ListCheckpointsRequest,
    ListCheckpointsResponse,
    DeleteCheckpoint,
    DeleteCheckpointRequest,
    DeleteCheckpointResponse,
    CheckpointInfo
)

__all__ = [
    # Base classes
    'UseCase',
    'BaseResponse',
    'UseCaseError',
    'ValidationError',
    'ExecutionError',
    
    # Run Population Simulation
    'RunPopulationSimulation',
    'RunPopulationSimulationRequest',
    'RunPopulationSimulationResponse',
    
    # Run Agent Simulation
    'RunAgentSimulation',
    'RunAgentSimulationRequest',
    'RunAgentSimulationResponse',
    
    # Run Hybrid Simulation
    'RunHybridSimulation',
    'RunHybridSimulationRequest',
    'RunHybridSimulationResponse',
    
    # Compare Scenarios
    'CompareScenarios',
    'CompareScenariosRequest',
    'CompareScenariosResponse',
    'ScenarioConfig',
    
    # Get Available Configurations
    'GetAvailableSpecies',
    'GetAvailableSpeciesRequest',
    'GetAvailableSpeciesResponse',
    'GetAvailablePredators',
    'GetAvailablePredatorsRequest',
    'GetAvailablePredatorsResponse',
    'GetSpeciesParameters',
    'GetSpeciesParametersRequest',
    'GetSpeciesParametersResponse',
    'SpeciesInfo',
    
    # Manage Checkpoints
    'SaveCheckpoint',
    'SaveCheckpointRequest',
    'SaveCheckpointResponse',
    'LoadCheckpoint',
    'LoadCheckpointRequest',
    'LoadCheckpointResponse',
    'ListCheckpoints',
    'ListCheckpointsRequest',
    'ListCheckpointsResponse',
    'DeleteCheckpoint',
    'DeleteCheckpointRequest',
    'DeleteCheckpointResponse',
    'CheckpointInfo',
]
