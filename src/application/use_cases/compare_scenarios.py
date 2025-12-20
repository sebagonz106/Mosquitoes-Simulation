"""
Compare Scenarios Use Case
===========================

Compare multiple simulation configurations to analyze different scenarios.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List

from application.use_cases.base import UseCase, BaseResponse, ValidationError
from application.dtos import SimulationConfig, ComparisonResult
from application.services.simulation_service import SimulationService


@dataclass
class ScenarioConfig:
    """
    Configuration for a single scenario.
    
    Simplified version of SimulationConfig for scenario comparison.
    """
    species_id: str
    duration_days: int
    initial_eggs: int = 0
    initial_larvae: int = 0
    initial_pupae: int = 0
    initial_adults: int = 0
    temperature: float = 25.0
    humidity: float = 70.0
    water_availability: float = 1.0
    random_seed: Optional[int] = None
    
    def to_simulation_config(self) -> SimulationConfig:
        """Convert to full SimulationConfig."""
        return SimulationConfig(
            species_id=self.species_id,
            duration_days=self.duration_days,
            initial_eggs=self.initial_eggs,
            initial_larvae=self.initial_larvae,
            initial_pupae=self.initial_pupae,
            initial_adults=self.initial_adults,
            temperature=self.temperature,
            humidity=self.humidity,
            water_availability=self.water_availability,
            random_seed=self.random_seed
        )


@dataclass
class CompareScenariosRequest:
    """
    Request to compare multiple simulation scenarios.
    
    Attributes:
        scenarios: Dict mapping scenario names to configurations
        simulation_type: Type of simulation ('population' or 'agent')
        comparison_metric: Metric to use for ranking (default: 'peak_population')
    """
    scenarios: Dict[str, ScenarioConfig]
    simulation_type: str = 'population'
    comparison_metric: str = 'peak_population'


@dataclass
class CompareScenariosResponse(BaseResponse):
    """
    Response from scenario comparison.
    
    Attributes:
        success: Whether comparison completed successfully
        result: Comparison result with all scenario results
        ranking: List of scenario names ordered by comparison_metric (best to worst)
        best_scenario: Name of the best performing scenario
        error: Error message if comparison failed
        execution_time_seconds: Time taken to execute
        timestamp: ISO timestamp of execution
    """
    result: Optional[ComparisonResult] = None
    ranking: Optional[List[str]] = None
    best_scenario: Optional[str] = None


class CompareScenarios(UseCase[CompareScenariosRequest, CompareScenariosResponse]):
    """
    Use case for comparing multiple simulation scenarios.
    
    Runs simulations for each scenario and generates comparative analysis.
    """
    
    def __init__(self, simulation_service: Optional[SimulationService] = None):
        """
        Initialize use case.
        
        Args:
            simulation_service: Service for running simulations (default: creates new instance)
        """
        self.simulation_service = simulation_service or SimulationService()
    
    def validate_request(self, request: CompareScenariosRequest) -> None:
        """
        Validate comparison parameters.
        
        Args:
            request: Comparison parameters to validate
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        # Validate number of scenarios
        if len(request.scenarios) < 2:
            raise ValidationError("At least 2 scenarios are required for comparison")
        
        if len(request.scenarios) > 20:
            raise ValidationError("Cannot compare more than 20 scenarios at once")
        
        # Validate simulation type
        if request.simulation_type not in ['population', 'agent']:
            raise ValidationError(
                f"simulation_type must be 'population' or 'agent', got '{request.simulation_type}'"
            )
        
        # Validate comparison metric
        valid_metrics = [
            'peak_population', 'final_population', 'mean_population',
            'peak_day', 'extinction_day'
        ]
        if request.comparison_metric not in valid_metrics:
            raise ValidationError(
                f"comparison_metric must be one of {valid_metrics}, "
                f"got '{request.comparison_metric}'"
            )
        
        # Validate each scenario configuration
        available_species = self.simulation_service.get_available_species()
        
        for scenario_name, config in request.scenarios.items():
            # Validate scenario name
            if not scenario_name or not scenario_name.strip():
                raise ValidationError("Scenario names cannot be empty")
            
            # Validate duration
            if config.duration_days <= 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': duration_days must be positive"
                )
            if config.duration_days > 10000:
                raise ValidationError(
                    f"Scenario '{scenario_name}': duration_days cannot exceed 10000"
                )
            
            # Validate populations (non-negative)
            if config.initial_eggs < 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': initial_eggs cannot be negative"
                )
            if config.initial_larvae < 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': initial_larvae cannot be negative"
                )
            if config.initial_pupae < 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': initial_pupae cannot be negative"
                )
            if config.initial_adults < 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': initial_adults cannot be negative"
                )
            
            # At least one stage must have population
            total = (config.initial_eggs + config.initial_larvae + 
                    config.initial_pupae + config.initial_adults)
            if total == 0:
                raise ValidationError(
                    f"Scenario '{scenario_name}': at least one life stage must have initial population > 0"
                )
            
            # Validate temperature
            if not (-10 <= config.temperature <= 50):
                raise ValidationError(
                    f"Scenario '{scenario_name}': temperature must be between -10 and 50°C"
                )
            
            # Validate humidity
            if not (0 <= config.humidity <= 100):
                raise ValidationError(
                    f"Scenario '{scenario_name}': humidity must be between 0 and 100%"
                )
            
            # Validate water availability
            if not (0 <= config.water_availability <= 1):
                raise ValidationError(
                    f"Scenario '{scenario_name}': water_availability must be between 0 and 1"
                )
            
            # Validate species exists
            if config.species_id not in available_species:
                raise ValidationError(
                    f"Scenario '{scenario_name}': species_id '{config.species_id}' not found. "
                    f"Available: {', '.join(available_species)}"
                )
    
    def _execute(self, request: CompareScenariosRequest) -> CompareScenariosResponse:
        """
        Execute scenario comparison.
        
        Args:
            request: Validated comparison parameters
            
        Returns:
            Response with comparison results and ranking
            
        Raises:
            ExecutionError: If comparison fails
        """
        # Convert ScenarioConfig to SimulationConfig
        simulation_configs = {
            name: config.to_simulation_config()
            for name, config in request.scenarios.items()
        }
        
        # Execute comparison through service
        result = self.simulation_service.compare_scenarios(
            scenarios=simulation_configs,
            simulation_type=request.simulation_type
        )
        
        # Generate ranking based on comparison metric
        ranking = self._calculate_ranking(
            result.comparison,
            request.comparison_metric
        )
        
        # Determine best scenario
        best_scenario = ranking[0] if ranking else None
        
        # Return success response
        return CompareScenariosResponse(
            success=True,
            result=result,
            ranking=ranking,
            best_scenario=best_scenario
        )
    
    def _calculate_ranking(
        self,
        comparison_data: Dict,
        metric: str
    ) -> List[str]:
        """
        Calculate ranking of scenarios based on comparison metric.
        
        Args:
            comparison_data: Dictionary with scenario comparison data
            metric: Metric to use for ranking
            
        Returns:
            List of scenario names ordered from best to worst
        """
        # Extract metric values for each scenario
        metric_values = []
        for scenario_name, data in comparison_data.items():
            value = data.get(metric)
            if value is not None:
                metric_values.append((scenario_name, value))
        
        # Sort by metric value (descending for most metrics)
        # For extinction_day, lower is worse (None means no extinction = best)
        if metric == 'extinction_day':
            # None (no extinction) is best, then higher values
            metric_values.sort(
                key=lambda x: (x[1] is not None, x[1] if x[1] is not None else float('inf')),
                reverse=False
            )
        else:
            # Higher values are better for population metrics
            metric_values.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, _ in metric_values]
