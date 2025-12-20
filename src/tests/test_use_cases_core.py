"""
Tests for Use Cases - Core Sprint 1
====================================

Test suite for population, agent, and hybrid simulation use cases.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.use_cases import (
    RunPopulationSimulation,
    RunPopulationSimulationRequest,
    RunAgentSimulation,
    RunAgentSimulationRequest,
    RunHybridSimulation,
    RunHybridSimulationRequest,
    ValidationError,
    ExecutionError
)
from application.dtos import PopulationResult, AgentResult


class TestRunPopulationSimulation(unittest.TestCase):
    """Test cases for RunPopulationSimulation use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_case = RunPopulationSimulation()
        
        # Valid request
        self.valid_request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            temperature=25.0,
            humidity=70.0,
            water_availability=1.0,
            random_seed=42
        )
    
    def test_successful_execution(self):
        """Test successful population simulation."""
        response = self.use_case.execute(self.valid_request)
        
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
        self.assertIsInstance(response.result, PopulationResult)
        assert response.result is not None  # Type narrowing
        self.assertEqual(response.result.species_id, 'aedes_aegypti')
        self.assertEqual(len(response.result.days), 11)  # 0 to 10
        self.assertIsNotNone(response.execution_time_seconds)
        self.assertIsNotNone(response.timestamp)
    
    def test_validation_negative_duration(self):
        """Test validation fails for negative duration."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=-5,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("duration_days must be positive", str(ctx.exception))
    
    def test_validation_excessive_duration(self):
        """Test validation fails for excessive duration."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=15000,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("cannot exceed 10000", str(ctx.exception))
    
    def test_validation_negative_population(self):
        """Test validation fails for negative initial population."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=-10,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("cannot be negative", str(ctx.exception))
    
    def test_validation_zero_population(self):
        """Test validation fails when all populations are zero."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=0
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("At least one life stage", str(ctx.exception))
    
    def test_validation_invalid_temperature(self):
        """Test validation fails for invalid temperature."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            temperature=60.0  # Too hot
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("temperature must be between", str(ctx.exception))
    
    def test_validation_invalid_humidity(self):
        """Test validation fails for invalid humidity."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            humidity=150.0  # > 100%
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("humidity must be between", str(ctx.exception))
    
    def test_validation_invalid_water_availability(self):
        """Test validation fails for invalid water availability."""
        request = RunPopulationSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            water_availability=1.5  # > 1.0
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("water_availability must be between", str(ctx.exception))
    
    def test_validation_invalid_species(self):
        """Test validation fails for invalid species."""
        request = RunPopulationSimulationRequest(
            species_id='invalid_species',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("not found", str(ctx.exception))


class TestRunAgentSimulation(unittest.TestCase):
    """Test cases for RunAgentSimulation use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_case = RunAgentSimulation()
        
        # Valid request
        self.valid_request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=10,
            num_predators=0,
            temperature=25.0,
            humidity=70.0,
            water_availability=1.0,
            random_seed=42
        )
    
    def test_successful_execution(self):
        """Test successful agent simulation."""
        response = self.use_case.execute(self.valid_request)
        
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
        self.assertIsInstance(response.result, AgentResult)
        assert response.result is not None  # Type narrowing
        self.assertEqual(response.result.num_vectors_initial, 10)
        self.assertIsNotNone(response.execution_time_seconds)
        self.assertIsNotNone(response.timestamp)
    
    def test_successful_execution_with_predators(self):
        """Test successful agent simulation with predators."""
        request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=10,
            num_predators=5,
            predator_species='toxorhynchites',
            temperature=25.0,
            humidity=70.0,
            random_seed=42
        )
        
        response = self.use_case.execute(request)
        
        self.assertTrue(response.success)
        assert response.result is not None  # Type narrowing
        self.assertEqual(response.result.num_predators_initial, 5)
    
    def test_validation_zero_adults(self):
        """Test validation fails when initial_adults is zero."""
        request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=0
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("initial_adults must be positive", str(ctx.exception))
    
    def test_validation_excessive_adults(self):
        """Test validation fails for excessive number of adults."""
        request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=15000
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("cannot exceed 10000", str(ctx.exception))
    
    def test_validation_negative_predators(self):
        """Test validation fails for negative predators."""
        request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=10,
            num_predators=-5
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("num_predators cannot be negative", str(ctx.exception))
    
    def test_validation_invalid_predator_species(self):
        """Test validation fails for invalid predator species."""
        request = RunAgentSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_adults=10,
            num_predators=5,
            predator_species='invalid_predator'
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("predator_species", str(ctx.exception))
        self.assertIn("not found", str(ctx.exception))


class TestRunHybridSimulation(unittest.TestCase):
    """Test cases for RunHybridSimulation use case."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_case = RunHybridSimulation()
        
        # Valid request
        self.valid_request = RunHybridSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            num_predators=0,
            temperature=25.0,
            humidity=70.0,
            water_availability=1.0,
            random_seed=42
        )
    
    def test_successful_execution(self):
        """Test successful hybrid simulation."""
        response = self.use_case.execute(self.valid_request)
        
        self.assertTrue(response.success)
        self.assertIsNone(response.error)
        self.assertIsInstance(response.population_result, PopulationResult)
        self.assertIsInstance(response.agent_result, AgentResult)
        self.assertIsInstance(response.comparison, dict)
        assert response.comparison is not None  # Type narrowing
        self.assertIn('population_model', response.comparison)
        self.assertIn('agent_model', response.comparison)
        self.assertIn('differences', response.comparison)
        self.assertIsNotNone(response.execution_time_seconds)
    
    def test_successful_execution_with_predators(self):
        """Test successful hybrid simulation with predators."""
        request = RunHybridSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            num_predators=5,
            predator_species='toxorhynchites',
            temperature=25.0,
            humidity=70.0,
            random_seed=42
        )
        
        response = self.use_case.execute(request)
        
        self.assertTrue(response.success)
        assert response.agent_result is not None  # Type narrowing
        self.assertEqual(response.agent_result.num_predators_initial, 5)
    
    def test_validation_negative_adults(self):
        """Test validation fails for zero adults."""
        request = RunHybridSimulationRequest(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=0  # Invalid for agent simulation
        )
        
        with self.assertRaises(ValidationError) as ctx:
            self.use_case.execute(request)
        
        self.assertIn("initial_adults must be positive", str(ctx.exception))
    
    def test_comparison_structure(self):
        """Test comparison dictionary has expected structure."""
        response = self.use_case.execute(self.valid_request)
        
        comparison = response.comparison
        assert comparison is not None  # Type narrowing
        
        # Check population_model keys
        self.assertIn('final_population', comparison['population_model'])
        self.assertIn('peak_population', comparison['population_model'])
        self.assertIn('mean_population', comparison['population_model'])
        
        # Check agent_model keys
        self.assertIn('final_population', comparison['agent_model'])
        self.assertIn('peak_population', comparison['agent_model'])
        self.assertIn('mean_population', comparison['agent_model'])
        
        # Check differences
        self.assertIn('final_population_diff', comparison['differences'])
        self.assertIn('peak_population_diff', comparison['differences'])


if __name__ == '__main__':
    unittest.main()
