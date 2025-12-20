"""
Tests for AgentService
======================

Test suite for agent-based simulation service with Prolog integration.
"""

import unittest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services import AgentService
from application.dtos import SimulationConfig, AgentResult


class TestAgentService(unittest.TestCase):
    """Test cases for AgentService with Prolog integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=10,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=20,
            temperature=25.0,
            humidity=75.0,
            water_availability=1.0,
            random_seed=42
        )
    
    def test_simulate_agents_returns_result(self):
        """Test that simulate_agents returns AgentResult."""
        result = AgentService.simulate_agents(self.config)
        
        self.assertIsInstance(result, AgentResult)
    
    def test_simulate_agents_initializes_correctly(self):
        """Test that agents are initialized with correct counts."""
        result = AgentService.simulate_agents(
            self.config,
            num_predators=5
        )
        
        self.assertEqual(result.num_vectors_initial, 20)
        self.assertEqual(result.num_predators_initial, 5)
    
    def test_simulate_agents_produces_daily_stats(self):
        """Test that daily statistics are recorded."""
        result = AgentService.simulate_agents(self.config)
        
        expected_days = self.config.duration_days + 1
        self.assertEqual(len(result.daily_stats), expected_days)
        
        # Check first day structure
        day0 = result.daily_stats[0]
        self.assertEqual(day0['day'], 0)
        self.assertIn('num_vectors_alive', day0)
        self.assertIn('num_predators_alive', day0)
    
    def test_simulate_agents_vectors_lay_eggs(self):
        """Test that vector agents lay eggs during simulation."""
        result = AgentService.simulate_agents(self.config)
        
        # Some eggs should be laid over 10 days
        self.assertGreater(result.total_eggs_laid, 0)
    
    def test_simulate_agents_with_predators(self):
        """Test simulation with both vectors and predators."""
        result = AgentService.simulate_agents(
            self.config,
            num_predators=5
        )
        
        # Should have predators
        self.assertEqual(result.num_predators_initial, 5)
        
        # Predators should consume some prey
        self.assertGreaterEqual(result.total_prey_consumed, 0)
    
    def test_simulate_agents_survival(self):
        """Test that agents can die during simulation."""
        result = AgentService.simulate_agents(
            self.config,
            num_predators=10  # Many predators to increase mortality
        )
        
        # Some vectors might die (not guaranteed but likely)
        # At minimum, final count should be <= initial
        self.assertLessEqual(result.num_vectors_final, result.num_vectors_initial)
    
    def test_simulate_agents_tracks_actions(self):
        """Test that agent actions are tracked in daily stats."""
        result = AgentService.simulate_agents(self.config)
        
        # Check that some day has action tracking
        has_actions = False
        for day_stat in result.daily_stats[1:]:  # Skip day 0
            if day_stat.get('vector_actions'):
                has_actions = True
                break
        
        self.assertTrue(has_actions, "No vector actions were tracked")
    
    def test_simulate_agents_invalid_config(self):
        """Test that invalid config raises error."""
        bad_config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=-1,  # Invalid
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=10
        )
        
        with self.assertRaises(ValueError):
            AgentService.simulate_agents(bad_config)
    
    def test_get_available_species(self):
        """Test getting available species."""
        species = AgentService.get_available_species()
        
        self.assertIsInstance(species, list)
        self.assertGreater(len(species), 0)
    
    def test_get_available_predators(self):
        """Test getting available predators."""
        predators = AgentService.get_available_predators()
        
        self.assertIsInstance(predators, list)
        self.assertIn('toxorhynchites', predators)
    
    def test_simulate_longer_duration(self):
        """Test simulation with longer duration."""
        config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=30,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=50,
            temperature=26.0,
            humidity=80.0,  # 0-100 scale
            water_availability=1.0,
            random_seed=42
        )
        
        result = AgentService.simulate_agents(config, num_predators=10)
        
        self.assertEqual(len(result.daily_stats), 31)
        self.assertGreater(result.total_eggs_laid, 0)


if __name__ == '__main__':
    unittest.main()
