"""
Tests for Sprint 2 Use Cases
=============================

Tests for scenario comparison and configuration query use cases.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
from application.use_cases.base import ValidationError
from application.dtos import PopulationResult, ComparisonResult


class TestCompareScenarios(unittest.TestCase):
    """Test suite for CompareScenarios use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulation_service = Mock()
        self.simulation_service.get_available_species = Mock(return_value=['aedes_aegypti', 'anopheles_gambiae', 'culex_pipiens', 'toxorhynchites'])
        self.use_case = CompareScenarios(self.simulation_service)
    
    def test_compare_two_scenarios_population_simulation(self):
        """Test comparing two scenarios with population simulation."""
        # Arrange
        scenario1 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            temperature=25.0,
            humidity=70.0,
            water_availability=0.5
        )
        
        scenario2 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=10,
            initial_eggs=200,
            initial_larvae=100,
            initial_pupae=40,
            initial_adults=20,
            temperature=28.0,
            humidity=80.0,
            water_availability=1.0
        )
        
        request = CompareScenariosRequest(
            scenarios={
                "scenario_1": scenario1,
                "scenario_2": scenario2
            },
            simulation_type="population",
            comparison_metric="final_population"
        )
        
        # Mock simulation results
        result1 = Mock(spec=PopulationResult)
        result1.final_population = 1000
        result1.peak_population = 1200
        result1.extinction_day = None
        
        result2 = Mock(spec=PopulationResult)
        result2.final_population = 1500
        result2.peak_population = 1800
        result2.extinction_day = None
        
        # Mock ComparisonResult
        comparison_result = Mock(spec=ComparisonResult)
        comparison_result.scenario_names = ["scenario_1", "scenario_2"]
        comparison_result.results = {
            "scenario_1": result1,
            "scenario_2": result2
        }
        comparison_result.comparison = {
            "scenario_1": {"final_population": 1000, "peak_population": 1200},
            "scenario_2": {"final_population": 1500, "peak_population": 1800}
        }
        
        self.simulation_service.compare_scenarios = Mock(return_value=comparison_result)
        
        # Act
        response = self.use_case.execute(request)
        
        # Assert
        self.assertTrue(response.success)
        assert response.result is not None
        self.assertEqual(len(response.result.results), 2)
        self.assertIn("scenario_1", response.result.results)
        self.assertIn("scenario_2", response.result.results)
        
        assert response.ranking is not None
        self.assertEqual(len(response.ranking), 2)
        self.assertEqual(response.ranking[0], "scenario_2")  # Higher final_population
        self.assertEqual(response.ranking[1], "scenario_1")
        
        assert response.best_scenario is not None
        self.assertEqual(response.best_scenario, "scenario_2")
    
    def test_compare_scenarios_agent_simulation(self):
        """Test comparing scenarios with agent simulation."""
        # Arrange
        scenario1 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=10,
            initial_adults=50,
            temperature=25.0,
            humidity=70.0,
            water_availability=0.5
        )
        
        scenario2 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=10,
            initial_adults=50,
            temperature=25.0,
            humidity=70.0,
            water_availability=0.5
        )
        
        request = CompareScenariosRequest(
            scenarios={
                "low_predators": scenario1,
                "high_predators": scenario2
            },
            simulation_type="agent",
            comparison_metric="peak_population"
        )
        
        # Mock simulation results
        result1 = Mock(spec=PopulationResult)
        result1.final_population = 800
        result1.peak_population = 1000
        
        result2 = Mock(spec=PopulationResult)
        result2.final_population = 500
        result2.peak_population = 700
        
        # Mock ComparisonResult
        comparison_result = Mock(spec=ComparisonResult)
        comparison_result.scenario_names = ["low_predators", "high_predators"]
        comparison_result.results = {
            "low_predators": result1,
            "high_predators": result2
        }
        comparison_result.comparison = {
            "low_predators": {"peak_population": 1000},
            "high_predators": {"peak_population": 700}
        }
        
        self.simulation_service.compare_scenarios = Mock(return_value=comparison_result)
        
        # Act
        response = self.use_case.execute(request)
        
        # Assert
        self.assertTrue(response.success)
        assert response.ranking is not None
        self.assertEqual(response.ranking[0], "low_predators")  # Higher peak_population
        self.assertEqual(response.ranking[1], "high_predators")
    
    def test_compare_scenarios_extinction_day_metric(self):
        """Test ranking by extinction_day (lower is better)."""
        # Arrange
        scenario1 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=30,
            initial_adults=10,
            temperature=15.0,  # Cold
            humidity=50.0,
            water_availability=0.1
        )
        
        scenario2 = ScenarioConfig(
            species_id="aedes_aegypti",
            duration_days=30,
            initial_adults=10,
            temperature=10.0,  # Colder
            humidity=50.0,
            water_availability=0.1
        )
        
        request = CompareScenariosRequest(
            scenarios={
                "cold": scenario1,
                "very_cold": scenario2
            },
            simulation_type="population",
            comparison_metric="extinction_day"
        )
        
        # Mock simulation results
        result1 = Mock(spec=PopulationResult)
        result1.extinction_day = 15
        
        result2 = Mock(spec=PopulationResult)
        result2.extinction_day = 10  # Earlier extinction
        
        # Mock ComparisonResult
        comparison_result = Mock(spec=ComparisonResult)
        comparison_result.scenario_names = ["cold", "very_cold"]
        comparison_result.results = {
            "cold": result1,
            "very_cold": result2
        }
        comparison_result.comparison = {
            "cold": {"extinction_day": 15},
            "very_cold": {"extinction_day": 10}
        }
        
        self.simulation_service.compare_scenarios = Mock(return_value=comparison_result)
        
        # Act
        response = self.use_case.execute(request)
        
        # Assert
        self.assertTrue(response.success)
        assert response.ranking is not None
        # For extinction_day, the implementation sorts with reverse=False
        # So lower values (earlier extinction) rank first
        self.assertEqual(response.ranking[0], "very_cold")  # Dies earlier (day 10)
        self.assertEqual(response.ranking[1], "cold")  # Dies later (day 15)
    
    def test_compare_scenarios_with_many_scenarios(self):
        """Test comparing 10 scenarios."""
        # Arrange
        scenarios = {}
        expected_results = {}
        comparison_data = {}
        scenario_names = []
        
        for i in range(10):
            scenario_name = f"scenario_{i}"
            scenario_names.append(scenario_name)
            scenarios[scenario_name] = ScenarioConfig(
                species_id="aedes_aegypti",
                duration_days=10,
                initial_adults=50,
                temperature=20.0 + i,  # Varying temperature
                humidity=70.0,
                water_availability=0.5
            )
            
            result = Mock(spec=PopulationResult)
            result.final_population = 1000 + (i * 100)
            expected_results[scenario_name] = result
            comparison_data[scenario_name] = {"final_population": 1000 + (i * 100)}
        
        request = CompareScenariosRequest(
            scenarios=scenarios,
            simulation_type="population",
            comparison_metric="final_population"
        )
        
        # Mock ComparisonResult
        comparison_result = Mock(spec=ComparisonResult)
        comparison_result.scenario_names = scenario_names
        comparison_result.results = expected_results
        comparison_result.comparison = comparison_data
        
        self.simulation_service.compare_scenarios = Mock(return_value=comparison_result)
        
        # Act
        response = self.use_case.execute(request)
        
        # Assert
        self.assertTrue(response.success)
        assert response.result is not None
        self.assertEqual(len(response.result.results), 10)
        
        assert response.ranking is not None
        self.assertEqual(len(response.ranking), 10)
        self.assertEqual(response.ranking[0], "scenario_9")  # Highest final_population
        self.assertEqual(response.ranking[-1], "scenario_0")  # Lowest final_population
    
    def test_validation_too_few_scenarios(self):
        """Test validation error when less than 2 scenarios."""
        # Arrange
        request = CompareScenariosRequest(
            scenarios={
                "only_one": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=25.0,
                    humidity=70.0,
                    water_availability=0.5
                )
            },
            simulation_type="population",
            comparison_metric="final_population"
        )
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("At least 2 scenarios", str(context.exception))
    
    def test_validation_too_many_scenarios(self):
        """Test validation error when more than 20 scenarios."""
        # Arrange
        scenarios = {}
        for i in range(21):
            scenarios[f"scenario_{i}"] = ScenarioConfig(
                species_id="aedes_aegypti",
                duration_days=10,
                initial_adults=50,
                temperature=25.0,
                humidity=70.0,
                water_availability=0.5
            )
        
        request = CompareScenariosRequest(
            scenarios=scenarios,
            simulation_type="population",
            comparison_metric="final_population"
        )
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("Cannot compare more than 20 scenarios", str(context.exception))
    
    def test_validation_invalid_simulation_type(self):
        """Test validation error for invalid simulation type."""
        # Arrange
        request = CompareScenariosRequest(
            scenarios={
                "s1": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=25.0,
                    humidity=70.0,
                    water_availability=0.5
                ),
                "s2": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=28.0,
                    humidity=70.0,
                    water_availability=0.5
                )
            },
            simulation_type="invalid_type",  # type: ignore
            comparison_metric="final_population"
        )
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("simulation_type", str(context.exception).lower())
    
    def test_validation_invalid_metric(self):
        """Test validation error for invalid comparison metric."""
        # Arrange
        request = CompareScenariosRequest(
            scenarios={
                "s1": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=25.0,
                    humidity=70.0,
                    water_availability=0.5
                ),
                "s2": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=28.0,
                    humidity=70.0,
                    water_availability=0.5
                )
            },
            simulation_type="population",
            comparison_metric="invalid_metric"  # type: ignore
        )
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("comparison_metric", str(context.exception).lower())
    
    def test_validation_scenario_invalid_duration(self):
        """Test validation error for scenario with invalid duration."""
        # Arrange
        request = CompareScenariosRequest(
            scenarios={
                "valid": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=10,
                    initial_adults=50,
                    temperature=25.0,
                    humidity=70.0,
                    water_availability=0.5
                ),
                "invalid": ScenarioConfig(
                    species_id="aedes_aegypti",
                    duration_days=0,  # Invalid
                    initial_adults=50,
                    temperature=25.0,
                    humidity=70.0,
                    water_availability=0.5
                )
            },
            simulation_type="population",
            comparison_metric="final_population"
        )
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("duration_days", str(context.exception).lower())


class TestGetAvailableSpecies(unittest.TestCase):
    """Test suite for GetAvailableSpecies use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulation_service = Mock()
        self.simulation_service.get_available_species = Mock(return_value=['aedes_aegypti', 'anopheles_gambiae', 'culex_pipiens', 'toxorhynchites'])
        self.use_case = GetAvailableSpecies(self.simulation_service)
    
    def test_get_available_species_success(self):
        """Test successful retrieval of available species."""
        # Arrange
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            mock_get_species.return_value = {
                'species_id': 'aedes_aegypti',
                'display_name': 'Aedes aegypti',
                'is_predatory': False,
                'development_rates': {
                    'egg_to_larva': 0.15,
                    'larva_to_pupa': 0.12,
                    'pupa_to_adult': 0.2
                },
                'survival_rates': {
                    'egg': 0.8,
                    'larva': 0.7,
                    'pupa': 0.85,
                    'adult': 0.95
                },
                'fecundity': 100.0
            }
            
            request = GetAvailableSpeciesRequest()
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            self.assertTrue(response.success)
            assert response.species is not None
            self.assertGreater(len(response.species), 0)
            
            # Check if aedes_aegypti is in the list
            species_ids = [s.species_id for s in response.species]
            self.assertIn('aedes_aegypti', species_ids)
    
    def test_get_available_species_contains_required_species(self):
        """Test that all required species are returned."""
        # Arrange
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            mock_get_species.side_effect = lambda x: {
                'species_id': x,
                'display_name': x.replace('_', ' ').title(),
                'is_predatory': x == 'toxorhynchites',
                'development_rates': {},
                'survival_rates': {},
                'fecundity': 100.0
            }
            
            request = GetAvailableSpeciesRequest()
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            self.assertTrue(response.success)
            assert response.species is not None
            species_ids = [s.species_id for s in response.species]
            
            # Check for known species
            self.assertIn('aedes_aegypti', species_ids)
            self.assertIn('anopheles_gambiae', species_ids)
            self.assertIn('culex_pipiens', species_ids)


class TestGetAvailablePredators(unittest.TestCase):
    """Test suite for GetAvailablePredators use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulation_service = Mock()
        self.simulation_service.get_available_species = Mock(return_value=['aedes_aegypti', 'anopheles_gambiae', 'culex_pipiens', 'toxorhynchites'])
        self.simulation_service.get_available_predators = Mock(return_value=['toxorhynchites'])
        self.use_case = GetAvailablePredators(self.simulation_service)
    
    def test_get_available_predators_success(self):
        """Test successful retrieval of predator species."""
        # Arrange
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            mock_get_species.return_value = {
                'species_id': 'toxorhynchites',
                'display_name': 'Toxorhynchites',
                'is_predatory': True,
                'development_rates': {},
                'survival_rates': {},
                'fecundity': 50.0
            }
            
            request = GetAvailablePredatorsRequest()
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            self.assertTrue(response.success)
            assert response.predators is not None
            self.assertGreater(len(response.predators), 0)
            
            # Check if toxorhynchites is in the list
            predator_ids = [p.species_id for p in response.predators]
            self.assertIn('toxorhynchites', predator_ids)
            
            # Verify all returned species are predatory
            for predator in response.predators:
                self.assertTrue(predator.is_predatory)
    
    def test_get_available_predators_excludes_non_predators(self):
        """Test that non-predatory species are excluded."""
        # Arrange - Even if aedes_aegypti info is requested, it should be filtered
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            def mock_species_info(species_id: str) -> Dict:
                return {
                    'species_id': species_id,
                    'display_name': species_id.replace('_', ' ').title(),
                    'is_predatory': species_id == 'toxorhynchites',
                    'development_rates': {},
                    'survival_rates': {},
                    'fecundity': 100.0
                }
            
            mock_get_species.side_effect = mock_species_info
            
            request = GetAvailablePredatorsRequest()
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            assert response.predators is not None
            predator_ids = [p.species_id for p in response.predators]
            
            # Non-predatory species should not be in the list
            self.assertNotIn('aedes_aegypti', predator_ids)
            self.assertNotIn('anopheles_gambiae', predator_ids)
            self.assertNotIn('culex_pipiens', predator_ids)


class TestGetSpeciesParameters(unittest.TestCase):
    """Test suite for GetSpeciesParameters use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulation_service = Mock()
        self.simulation_service.get_available_species = Mock(return_value=['aedes_aegypti', 'anopheles_gambiae', 'culex_pipiens', 'toxorhynchites'])
        self.use_case = GetSpeciesParameters(self.simulation_service)
    
    def test_get_species_parameters_success(self):
        """Test successful retrieval of species parameters."""
        # Arrange
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            mock_get_species.return_value = {
                'species_id': 'aedes_aegypti',
                'display_name': 'Aedes aegypti',
                'is_predatory': False,
                'development_rates': {
                    'egg_to_larva': 0.15,
                    'larva_to_pupa': 0.12,
                    'pupa_to_adult': 0.2
                },
                'survival_rates': {
                    'egg': 0.8,
                    'larva': 0.7,
                    'pupa': 0.85,
                    'adult': 0.95
                },
                'fecundity': 100.0
            }
            
            request = GetSpeciesParametersRequest(species_id='aedes_aegypti')
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            self.assertTrue(response.success)
            assert response.species_info is not None
            self.assertEqual(response.species_info.species_id, 'aedes_aegypti')
            self.assertEqual(response.species_info.display_name, 'Aedes aegypti')
            self.assertFalse(response.species_info.is_predatory)
            self.assertEqual(response.species_info.fecundity, 100.0)
            
            # Check development rates
            self.assertIn('egg_to_larva', response.species_info.development_rates)
            self.assertEqual(response.species_info.development_rates['egg_to_larva'], 0.15)
            
            # Check survival rates
            self.assertIn('egg', response.species_info.survival_rates)
            self.assertEqual(response.species_info.survival_rates['egg'], 0.8)
    
    def test_get_species_parameters_predator(self):
        """Test retrieval of predator species parameters."""
        # Arrange
        with patch('application.services.population_service.PopulationService.get_species_info') as mock_get_species:
            mock_get_species.return_value = {
                'species_id': 'toxorhynchites',
                'display_name': 'Toxorhynchites',
                'is_predatory': True,
                'development_rates': {
                    'egg_to_larva': 0.1,
                    'larva_to_pupa': 0.08,
                    'pupa_to_adult': 0.15
                },
                'survival_rates': {
                    'egg': 0.75,
                    'larva': 0.65,
                    'pupa': 0.8,
                    'adult': 0.9
                },
                'fecundity': 50.0
            }
            
            request = GetSpeciesParametersRequest(species_id='toxorhynchites')
            
            # Act
            response = self.use_case.execute(request)
            
            # Assert
            self.assertTrue(response.success)
            assert response.species_info is not None
            self.assertEqual(response.species_info.species_id, 'toxorhynchites')
            self.assertTrue(response.species_info.is_predatory)
            self.assertEqual(response.species_info.fecundity, 50.0)
    
    def test_validation_empty_species_id(self):
        """Test validation error for empty species_id."""
        # Arrange
        request = GetSpeciesParametersRequest(species_id='')
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        self.assertIn("species_id", str(context.exception).lower())
    
    def test_get_species_parameters_invalid_species(self):
        """Test error handling for invalid species."""
        # Arrange
        request = GetSpeciesParametersRequest(species_id='invalid_species')
        
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            self.use_case.execute(request)
        
        # Should raise ValidationError because invalid_species is not in available list
        self.assertIn("invalid_species", str(context.exception))


if __name__ == '__main__':
    unittest.main()
