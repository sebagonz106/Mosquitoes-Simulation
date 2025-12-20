"""
Get Available Configurations Use Case
======================================

Retrieve available configuration options for simulations.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict

from application.use_cases.base import UseCase, BaseResponse, ValidationError
from application.services.simulation_service import SimulationService
from application.services.population_service import PopulationService


@dataclass
class SpeciesInfo:
    """
    Information about a species.
    
    Attributes:
        species_id: Unique identifier
        display_name: Human-readable name
        is_predatory: Whether species is predatory
        development_rates: Development rates for life stages
        survival_rates: Survival rates for life stages
        fecundity: Average eggs per batch
    """
    species_id: str
    display_name: str
    is_predatory: bool
    development_rates: Dict[str, float]
    survival_rates: Dict[str, float]
    fecundity: float


@dataclass
class GetAvailableSpeciesRequest:
    """Request to get available species."""
    pass  # No parameters needed


@dataclass
class GetAvailableSpeciesResponse(BaseResponse):
    """
    Response with available species information.
    
    Attributes:
        success: Whether request completed successfully
        species: List of available species with details
        species_ids: List of species identifiers only
        error: Error message if request failed
    """
    species: Optional[List[SpeciesInfo]] = None
    species_ids: Optional[List[str]] = None


@dataclass
class GetAvailablePredatorsRequest:
    """Request to get available predator species."""
    pass  # No parameters needed


@dataclass
class GetAvailablePredatorsResponse(BaseResponse):
    """
    Response with available predator species.
    
    Attributes:
        success: Whether request completed successfully
        predators: List of available predator species with details
        predator_ids: List of predator identifiers only
        error: Error message if request failed
    """
    predators: Optional[List[SpeciesInfo]] = None
    predator_ids: Optional[List[str]] = None


@dataclass
class GetSpeciesParametersRequest:
    """
    Request to get parameters for a specific species.
    
    Attributes:
        species_id: Species identifier
    """
    species_id: str


@dataclass
class GetSpeciesParametersResponse(BaseResponse):
    """
    Response with species parameters.
    
    Attributes:
        success: Whether request completed successfully
        species_info: Detailed species information
        error: Error message if request failed
    """
    species_info: Optional[SpeciesInfo] = None


class GetAvailableSpecies(UseCase[GetAvailableSpeciesRequest, GetAvailableSpeciesResponse]):
    """
    Use case for retrieving available species for simulation.
    
    Returns both simple list of IDs and detailed species information.
    """
    
    def __init__(
        self,
        simulation_service: Optional[SimulationService] = None,
        population_service: Optional[PopulationService] = None
    ):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for simulations (default: creates new instance)
            population_service: Service for population info (default: None, uses static methods)
        """
        self.simulation_service = simulation_service or SimulationService()
        self.population_service = population_service
    
    def validate_request(self, request: GetAvailableSpeciesRequest) -> None:
        """
        Validate request (no parameters to validate).
        
        Args:
            request: Request object (empty)
        """
        pass  # No validation needed
    
    def _execute(self, request: GetAvailableSpeciesRequest) -> GetAvailableSpeciesResponse:
        """
        Execute species retrieval.
        
        Args:
            request: Request object
            
        Returns:
            Response with species information
        """
        # Get species IDs
        species_ids = self.simulation_service.get_available_species()
        
        # Get detailed information for each species
        species_list = []
        for species_id in species_ids:
            info = PopulationService.get_species_info(species_id)
            if info:
                species_list.append(SpeciesInfo(
                    species_id=info['species_id'],
                    display_name=info['display_name'],
                    is_predatory=info['is_predatory'],
                    development_rates=info['development_rates'],
                    survival_rates=info['survival_rates'],
                    fecundity=info['fecundity']
                ))
        
        return GetAvailableSpeciesResponse(
            success=True,
            species=species_list,
            species_ids=species_ids
        )


class GetAvailablePredators(UseCase[GetAvailablePredatorsRequest, GetAvailablePredatorsResponse]):
    """
    Use case for retrieving available predator species.
    
    Returns both simple list of IDs and detailed predator information.
    """
    
    def __init__(
        self,
        simulation_service: Optional[SimulationService] = None,
        population_service: Optional[PopulationService] = None
    ):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for simulations (default: creates new instance)
            population_service: Service for population info (default: None, uses static methods)
        """
        self.simulation_service = simulation_service or SimulationService()
        self.population_service = population_service
    
    def validate_request(self, request: GetAvailablePredatorsRequest) -> None:
        """
        Validate request (no parameters to validate).
        
        Args:
            request: Request object (empty)
        """
        pass  # No validation needed
    
    def _execute(self, request: GetAvailablePredatorsRequest) -> GetAvailablePredatorsResponse:
        """
        Execute predator retrieval.
        
        Args:
            request: Request object
            
        Returns:
            Response with predator information
        """
        # Get predator IDs
        predator_ids = self.simulation_service.get_available_predators()
        
        # Get detailed information for each predator
        predators_list = []
        for predator_id in predator_ids:
            info = PopulationService.get_species_info(predator_id)
            if info:
                predators_list.append(SpeciesInfo(
                    species_id=info['species_id'],
                    display_name=info['display_name'],
                    is_predatory=info['is_predatory'],
                    development_rates=info['development_rates'],
                    survival_rates=info['survival_rates'],
                    fecundity=info['fecundity']
                ))
        
        return GetAvailablePredatorsResponse(
            success=True,
            predators=predators_list,
            predator_ids=predator_ids
        )


class GetSpeciesParameters(UseCase[GetSpeciesParametersRequest, GetSpeciesParametersResponse]):
    """
    Use case for retrieving parameters for a specific species.
    
    Returns detailed information about development rates, survival, and reproduction.
    """
    
    def __init__(
        self,
        simulation_service: Optional[SimulationService] = None,
        population_service: Optional[PopulationService] = None
    ):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for simulations (default: creates new instance)
            population_service: Service for population info (default: None, uses static methods)
        """
        self.simulation_service = simulation_service or SimulationService()
        self.population_service = population_service
    
    def validate_request(self, request: GetSpeciesParametersRequest) -> None:
        """
        Validate species identifier.
        
        Args:
            request: Request with species_id
            
        Raises:
            ValidationError: If species not found
        """
        # Validate species exists
        available_species = self.simulation_service.get_available_species()
        if request.species_id not in available_species:
            raise ValidationError(
                f"species_id '{request.species_id}' not found. "
                f"Available: {', '.join(available_species)}"
            )
    
    def _execute(self, request: GetSpeciesParametersRequest) -> GetSpeciesParametersResponse:
        """
        Execute parameter retrieval.
        
        Args:
            request: Request with species_id
            
        Returns:
            Response with species parameters
            
        Raises:
            ExecutionError: If species info cannot be retrieved
        """
        # Get species information
        info = PopulationService.get_species_info(request.species_id)
        
        if not info:
            # This shouldn't happen after validation, but handle gracefully
            return GetSpeciesParametersResponse(
                success=False,
                error=f"Could not retrieve information for species '{request.species_id}'"
            )
        
        species_info = SpeciesInfo(
            species_id=info['species_id'],
            display_name=info['display_name'],
            is_predatory=info['is_predatory'],
            development_rates=info['development_rates'],
            survival_rates=info['survival_rates'],
            fecundity=info['fecundity']
        )
        
        return GetSpeciesParametersResponse(
            success=True,
            species_info=species_info
        )
