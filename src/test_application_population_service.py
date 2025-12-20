"""
Tests for PopulationService
============================

Test suite for population simulation service.
"""

import unittest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from application.services import PopulationService
from application.dtos import SimulationConfig, PopulationResult


class TestPopulationService(unittest.TestCase):
    """Test cases for PopulationService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=30,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10,
            random_seed=42
        )
    
    def test_create_population_valid(self):
        """Test creating population with valid config."""
        population = PopulationService.create_population(self.config)
        
        self.assertIsNotNone(population)
        self.assertEqual(population.species.species_id, 'aedes_aegypti')
        
        # Check initial state
        snapshot = population.get_current_snapshot()
        self.assertIsNotNone(snapshot)
        assert snapshot is not None  # Type narrowing for Pylance
        self.assertEqual(snapshot.eggs, 100)
        self.assertEqual(snapshot.larvae, 50)
        self.assertEqual(snapshot.pupae, 20)
        self.assertEqual(snapshot.adults, 10)
    
    def test_create_population_with_larvae_list(self):
        """Test creating population with larvae as list."""
        config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=30,
            initial_eggs=100,
            initial_larvae=[10, 15, 12, 8],
            initial_pupae=20,
            initial_adults=10,
            random_seed=42
        )
        
        population = PopulationService.create_population(config)
        
        # Check total larvae (list is summed in initialization)
        snapshot = population.get_current_snapshot()
        self.assertIsNotNone(snapshot)
        assert snapshot is not None  # Type narrowing for Pylance
        self.assertEqual(snapshot.larvae, 45)
    
    def test_create_population_invalid_species(self):
        """Test that invalid species raises error."""
        config = SimulationConfig(
            species_id='invalid_species',
            duration_days=30,
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValueError) as context:
            PopulationService.create_population(config)
        
        self.assertIn('Unknown species', str(context.exception))
    
    def test_create_population_invalid_config(self):
        """Test that invalid config raises error."""
        config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=-5,  # Invalid
            initial_eggs=100,
            initial_larvae=50,
            initial_pupae=20,
            initial_adults=10
        )
        
        with self.assertRaises(ValueError) as context:
            PopulationService.create_population(config)
        
        self.assertIn('Invalid configuration', str(context.exception))
    
    def test_simulate_returns_population_result(self):
        """Test that simulate returns PopulationResult DTO."""
        result = PopulationService.simulate(self.config)
        
        self.assertIsInstance(result, PopulationResult)
        self.assertEqual(result.species_id, 'aedes_aegypti')
    
    def test_simulate_trajectory_length(self):
        """Test that trajectory has correct length."""
        result = PopulationService.simulate(self.config)
        
        expected_length = self.config.duration_days + 1
        self.assertEqual(len(result.days), expected_length)
        self.assertEqual(len(result.eggs), expected_length)
        self.assertEqual(len(result.larvae), expected_length)
        self.assertEqual(len(result.pupae), expected_length)
        self.assertEqual(len(result.adults), expected_length)
    
    def test_simulate_initial_state(self):
        """Test that initial state is correctly recorded."""
        result = PopulationService.simulate(self.config)
        
        self.assertEqual(result.eggs[0], 100)
        self.assertEqual(result.larvae[0], 50)
        self.assertEqual(result.pupae[0], 20)
        self.assertEqual(result.adults[0], 10)
    
    def test_simulate_parameters_stored(self):
        """Test that simulation parameters are stored in result."""
        result = PopulationService.simulate(self.config)
        
        # Check statistics are calculated
        self.assertIn('peak_day', result.statistics)
        self.assertIn('peak_population', result.statistics)
        self.assertIn('extinction_day', result.statistics)
        self.assertIn('final_population', result.statistics)
        self.assertIn('mean_total', result.statistics)
    
    def test_simulate_different_species(self):
        """Test simulation with different species."""
        config = SimulationConfig(
            species_id='toxorhynchites',
            duration_days=20,
            initial_eggs=50,
            initial_larvae=30,
            initial_pupae=15,
            initial_adults=5,
            random_seed=42
        )
        
        result = PopulationService.simulate(config)
        
        self.assertEqual(result.species_id, 'toxorhynchites')
        self.assertEqual(len(result.days), 21)
    
    def test_simulate_population_dynamics(self):
        """Test that population shows expected dynamics."""
        result = PopulationService.simulate(self.config)
        
        # Adults should produce eggs
        # Check that total population changes over time
        initial_total = result.eggs[0] + result.larvae[0] + result.pupae[0] + result.adults[0]
        final_total = result.eggs[-1] + result.larvae[-1] + result.pupae[-1] + result.adults[-1]
        
        # Population should change (either grow or decline)
        self.assertNotEqual(initial_total, final_total)
    
    def test_get_available_species(self):
        """Test getting list of available species."""
        species = PopulationService.get_available_species()
        
        self.assertIsInstance(species, list)
        self.assertIn('aedes_aegypti', species)
        self.assertIn('toxorhynchites', species)
    
    def test_get_species_info(self):
        """Test getting species information."""
        info = PopulationService.get_species_info('aedes_aegypti')
        
        self.assertIsNotNone(info)
        if info:  # Type guard for None check
            self.assertIn('development_rates', info)
            self.assertIn('survival_rates', info)
            self.assertIn('fecundity', info)
    
    def test_get_species_info_invalid(self):
        """Test getting info for invalid species."""
        info = PopulationService.get_species_info('invalid_species')
        
        self.assertIsNone(info)
    
    def test_simulate_long_duration(self):
        """Test simulation with longer duration."""
        config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=365,
            initial_eggs=1000,
            initial_larvae=500,
            initial_pupae=200,
            initial_adults=100,
            random_seed=42
        )
        
        result = PopulationService.simulate(config)
        
        self.assertEqual(len(result.days), 366)
        # Verify arrays are correct dtype
        self.assertEqual(result.days.dtype, np.int32)
        self.assertEqual(result.eggs.dtype, np.float64)


if __name__ == '__main__':
    unittest.main()
