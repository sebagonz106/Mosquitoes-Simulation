"""
Tests for SimulationService
============================

Test suite for high-level simulation orchestration and checkpointing.
"""

import unittest
from pathlib import Path
import sys
import tempfile
import shutil
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services.simulation_service import SimulationService
from application.dtos import SimulationConfig, PopulationResult, AgentResult, HybridResult


class TestSimulationService(unittest.TestCase):
    """Test cases for SimulationService orchestration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary checkpoint directory
        self.temp_dir = tempfile.mkdtemp()
        self.service = SimulationService(checkpoint_dir=self.temp_dir)
        
        # Standard test configuration
        self.config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            temperature=25.0,
            humidity=75.0,
            random_seed=42
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_run_population_simulation(self):
        """Test running population simulation through service."""
        result = self.service.run_population_simulation(self.config)
        
        self.assertIsInstance(result, PopulationResult)
        self.assertEqual(result.species_id, 'aedes_aegypti')
        self.assertEqual(len(result.days), 11)
    
    def test_run_agent_simulation(self):
        """Test running agent simulation through service."""
        result = self.service.run_agent_simulation(self.config)
        
        self.assertIsInstance(result, AgentResult)
        self.assertEqual(result.num_vectors_initial, 10)
    
    def test_run_hybrid_simulation(self):
        """Test running both simulations in parallel."""
        hybrid_result = self.service.run_hybrid_simulation(self.config)
        
        self.assertIsInstance(hybrid_result, HybridResult)
        self.assertIsInstance(hybrid_result.population_result, PopulationResult)
        self.assertIsInstance(hybrid_result.agent_result, AgentResult)
        self.assertIsInstance(hybrid_result.comparison_data, dict)
        
        # Check comparison structure (updated keys)
        self.assertIn('population_model', hybrid_result.comparison_data)
        self.assertIn('agent_model', hybrid_result.comparison_data)
        self.assertIn('differences', hybrid_result.comparison_data)
    
    def test_save_and_load_checkpoint_population(self):
        """Test saving and loading population simulation checkpoint."""
        # Run simulation
        result = self.service.run_population_simulation(self.config)
        
        # Save checkpoint
        checkpoint_path = self.service.save_checkpoint(
            result=result,
            config=self.config,
            simulation_type='population'
        )
        
        self.assertTrue(checkpoint_path.exists())
        
        # Load checkpoint
        loaded_config, loaded_result, sim_type = self.service.load_checkpoint(checkpoint_path)
        
        self.assertEqual(sim_type, 'population')
        self.assertEqual(loaded_config.species_id, self.config.species_id)
        self.assertIsInstance(loaded_result, PopulationResult)
    
    def test_save_and_load_checkpoint_agent(self):
        """Test saving and loading agent simulation checkpoint."""
        # Run simulation
        result = self.service.run_agent_simulation(self.config)
        
        # Save checkpoint
        checkpoint_path = self.service.save_checkpoint(
            result=result,
            config=self.config,
            simulation_type='agent',
            checkpoint_name='test_agent.json'
        )
        
        self.assertTrue(checkpoint_path.exists())
        
        # Load checkpoint
        loaded_config, loaded_result, sim_type = self.service.load_checkpoint(checkpoint_path)
        
        self.assertEqual(sim_type, 'agent')
        self.assertIsInstance(loaded_result, AgentResult)
    
    def test_list_checkpoints(self):
        """Test listing checkpoint files."""
        # Create multiple checkpoints
        result1 = self.service.run_population_simulation(self.config)
        self.service.save_checkpoint(result1, self.config, 'population')
        
        result2 = self.service.run_agent_simulation(self.config)
        self.service.save_checkpoint(result2, self.config, 'agent')
        
        # List all checkpoints
        checkpoints = self.service.list_checkpoints()
        self.assertEqual(len(checkpoints), 2)
        
        # Filter by type
        pop_checkpoints = self.service.list_checkpoints(simulation_type='population')
        self.assertEqual(len(pop_checkpoints), 1)
        
        agent_checkpoints = self.service.list_checkpoints(simulation_type='agent')
        self.assertEqual(len(agent_checkpoints), 1)
    
    def test_compare_scenarios_population(self):
        """Test comparing multiple population scenarios."""
        scenarios = {
            'baseline': SimulationConfig(
                species_id='aedes_aegypti',
                duration_days=10,
                initial_eggs=100,
                initial_larvae=50,
                initial_pupae=20,
                initial_adults=10,
                random_seed=42
            ),
            'high_temperature': SimulationConfig(
                species_id='aedes_aegypti',
                duration_days=10,
                initial_eggs=100,
                initial_larvae=50,
                initial_pupae=20,
                initial_adults=10,
                temperature=30.0,
                random_seed=42
            )
        }
        
        comparison = self.service.compare_scenarios(scenarios, simulation_type='population')
        
        self.assertEqual(len(comparison.scenario_names), 2)
        self.assertIn('baseline', comparison.results)
        self.assertIn('high_temperature', comparison.results)
    
    def test_checkpoint_directory_creation(self):
        """Test that checkpoint directory is created automatically."""
        temp_checkpoint_dir = Path(self.temp_dir) / "new_checkpoints"
        service = SimulationService(checkpoint_dir=temp_checkpoint_dir)
        
        self.assertTrue(temp_checkpoint_dir.exists())
    
    def test_invalid_checkpoint_format(self):
        """Test loading invalid checkpoint raises error."""
        # Create invalid JSON file
        invalid_path = Path(self.temp_dir) / "invalid.json"
        with open(invalid_path, 'w') as f:
            json.dump({'invalid': 'data'}, f)
        
        with self.assertRaises(ValueError):
            self.service.load_checkpoint(invalid_path)
    
    def test_checkpoint_not_found(self):
        """Test loading non-existent checkpoint raises error."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError):
            self.service.load_checkpoint(nonexistent_path)
    
    def test_get_available_species(self):
        """Test getting available species."""
        species = self.service.get_available_species()
        
        self.assertIsInstance(species, list)
        self.assertGreater(len(species), 0)
        self.assertIn('aedes_aegypti', species)
    
    def test_get_available_predators(self):
        """Test getting available predators."""
        predators = self.service.get_available_predators()
        
        self.assertIsInstance(predators, list)
        self.assertIn('toxorhynchites', predators)
    
    def test_hybrid_simulation_with_predators(self):
        """Test hybrid simulation with predator agents."""
        hybrid_result = self.service.run_hybrid_simulation(
            config=self.config,
            num_predators=5
        )
        
        self.assertEqual(hybrid_result.agent_result.num_predators_initial, 5)
        self.assertIn('agent_model', hybrid_result.comparison_data)
    
    def test_checkpoint_metadata(self):
        """Test that checkpoint metadata is properly saved."""
        result = self.service.run_population_simulation(self.config)
        checkpoint_path = self.service.save_checkpoint(result, self.config, 'population')
        
        # Read checkpoint file
        with open(checkpoint_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('metadata', data)
        self.assertEqual(data['metadata']['species'], 'aedes_aegypti')
        self.assertEqual(data['metadata']['duration'], 10)


if __name__ == '__main__':
    unittest.main()
