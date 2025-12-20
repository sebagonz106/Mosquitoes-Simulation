"""
Test script for Domain Entities
================================

Tests all entity classes: Species, Mosquito, Population, Habitat

Author: Mosquito Simulation System
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from infrastructure.config import ConfigManager
from domain.entities import Species, Mosquito, LifeStage, Population, PopulationSnapshot, Habitat
from domain.models.population_model import PopulationModel
from domain.models.environment_model import EnvironmentModel
from infrastructure.prolog_bridge import PrologBridge


def test_species_entity():
    """Test Species entity functionality."""
    print("\n" + "="*60)
    print("Test 1: Species Entity")
    print("="*60)
    
    # Load configuration
    config = ConfigManager()
    species_config = config.get_species_config("aedes_aegypti")
    
    # Create species entity
    species = Species(species_config)
    
    print(f"\nSpecies: {species}")
    print(f"ID: {species.species_id}")
    print(f"Display name: {species.display_name}")
    print(f"Is predatory: {species.is_predatory}")
    
    # Test life stage access
    print(f"\nLife stages: {species.get_all_stages()}")
    
    adult_stage = species.get_life_stage("adult")
    if adult_stage:
        print(f"Adult survival rate: {species.get_survival_rate('adult'):.4f}")
    
    # Test reproduction
    repro_params = species.get_reproduction_params()
    print(f"\nReproduction parameters:")
    print(f"  Eggs per batch: {repro_params['eggs_per_batch_min']}-{repro_params['eggs_per_batch_max']}")
    print(f"  Min reproductive age: {repro_params['min_age_reproduction_days']} days")
    
    # Test temperature tolerance
    optimal_temp = species.get_temperature_tolerance()
    lethal_temp = species.get_lethal_temperature_range()
    print(f"\nTemperature ranges:")
    print(f"  Optimal: {optimal_temp}")
    print(f"  Lethal: {lethal_temp}")
    
    # Test temperature checks
    test_temps = [15.0, 25.0, 35.0, 45.0]
    for temp in test_temps:
        is_lethal = species.is_temperature_lethal(temp)
        is_optimal = species.is_temperature_optimal(temp)
        print(f"  {temp}°C: lethal={is_lethal}, optimal={is_optimal}")
    
    print("\nOK Species entity test passed")


def test_mosquito_entity():
    """Test Mosquito entity functionality."""
    print("\n" + "="*60)
    print("Test 2: Mosquito Entity")
    print("="*60)
    
    # Create a mosquito
    mosquito = Mosquito(
        mosquito_id="M001",
        species_id="aedes_aegypti",
        life_stage=LifeStage.EGG,
        birth_day=0
    )
    
    print(f"\nInitial state: {mosquito}")
    print(f"Is aquatic: {mosquito.is_aquatic_stage()}")
    print(f"Is larval: {mosquito.is_larval_stage()}")
    print(f"Is adult: {mosquito.is_adult_stage()}")
    
    # Advance through life stages
    print("\nLife cycle progression:")
    for _ in range(3):
        mosquito.advance_age(1)
        print(f"  Day {mosquito.age_days}: {mosquito.life_stage.value}, age in stage={mosquito.age_in_stage}")
    
    # Transition to next stage
    next_stage = mosquito.life_stage.next_stage()
    if next_stage:
        mosquito.transition_to_stage(next_stage)
        print(f"  Transitioned to {mosquito.life_stage.value}, age in stage={mosquito.age_in_stage}")
    
    # Test reproduction capability
    mosquito.transition_to_stage(LifeStage.ADULT)
    mosquito.age_days = 10
    can_reproduce = mosquito.can_reproduce(min_reproductive_age=7)
    print(f"\nAdult at {mosquito.age_days} days, can reproduce: {can_reproduce}")
    
    # Test death
    mosquito.die(current_day=15)
    print(f"After death: {mosquito}")
    print(f"Lifespan: {mosquito.lifespan_days()} days")
    
    print("\nOK Mosquito entity test passed")


def test_population_entity():
    """Test Population entity functionality."""
    print("\n" + "="*60)
    print("Test 3: Population Entity")
    print("="*60)
    
    # Load configuration
    config = ConfigManager()
    species_config = config.get_species_config("aedes_aegypti")
    env_config = config.get_environment_config()
    
    # Create entities
    species = Species(species_config)
    
    # Create environment model
    prolog_bridge = PrologBridge(config)
    prolog_bridge.inject_parameters()  # Cargar parámetros antes de usar
    environment_model = EnvironmentModel(env_config, days=31)  # 30-day simulation
    
    # Create population model
    population_model = PopulationModel(
        species_config=species_config,
        environment_model=environment_model,
        prolog_bridge=prolog_bridge
    )
    
    # Create population entity
    population = Population(species=species, model=population_model)
    
    print(f"\nPopulation: {population}")
    
    # Initialize with some individuals (using array for larvae by stage)
    initial_larvae = np.array([50, 40, 30, 20])  # L1, L2, L3, L4
    population.initialize(
        initial_eggs=100,
        initial_larvae=initial_larvae,
        initial_pupae=30,
        initial_adults=20
    )
    
    # Get initial snapshot
    initial_snapshot = population.get_current_snapshot()
    print(f"\nInitial state: {initial_snapshot}")
    print(f"Stage proportions: {initial_snapshot.stage_proportions()}")
    
    # Run simulation
    print("\nRunning 30-day simulation...")
    trajectory = population.simulate(days=30)
    
    # Get final snapshot
    final_snapshot = population.get_current_snapshot()
    print(f"Final state: {final_snapshot}")
    
    # Get statistics
    stats = population.get_population_statistics()
    print(f"\nPopulation statistics:")
    print(f"  Mean population: {stats['mean_population']:.1f}")
    print(f"  Max population: {stats['max_population']:.0f}")
    print(f"  Final population: {stats['final_population']:.0f}")
    print(f"  Peak day: {stats['peak_day']}, size: {stats['peak_size']}")
    
    if stats['extinction_day'] >= 0:
        print(f"  Extinction day: {stats['extinction_day']}")
    
    # Get stage dynamics
    stage_dynamics = population.get_stage_dynamics()
    print(f"\nStage dynamics (first 5 days):")
    for i in range(min(5, len(stage_dynamics['total']))):
        print(f"  Day {i}: E={stage_dynamics['eggs'][i]}, "
              f"L={stage_dynamics['larvae'][i]}, "
              f"P={stage_dynamics['pupae'][i]}, "
              f"A={stage_dynamics['adults'][i]}, "
              f"Total={stage_dynamics['total'][i]}")
    
    print("\nOK Population entity test passed")


def test_habitat_entity():
    """Test Habitat entity functionality."""
    print("\n" + "="*60)
    print("Test 4: Habitat Entity")
    print("="*60)
    
    # Load configuration
    config = ConfigManager()
    env_config = config.get_environment_config()
    species_config = config.get_species_config("aedes_aegypti")
    
    # Create environment model
    environment_model = EnvironmentModel(env_config, days=365)
    
    # Create habitat entity
    habitat = Habitat(
        habitat_id="HAB001",
        name="Urban breeding site",
        environment_model=environment_model,
        config=env_config,
        location="Tropical city"
    )
    
    print(f"\nHabitat: {habitat}")
    
    # Get species temperature ranges
    species = Species(species_config)
    optimal_temp = species.get_temperature_tolerance()
    lethal_temp = species.get_lethal_temperature_range()
    
    # Get conditions at specific days
    print(f"\nConditions samples:")
    for day in [0, 30, 60, 90]:
        conditions = habitat.get_conditions_at_day(day, optimal_temp, lethal_temp)
        print(f"  Day {day}: {conditions}")
    
    # Get habitat statistics
    stats = habitat.get_habitat_statistics(optimal_temp, lethal_temp)
    print(f"\nHabitat statistics:")
    print(f"  Name: {stats['name']}")
    print(f"  Location: {stats['location']}")
    print(f"  Total days: {stats['total_days']}")
    print(f"  Favorable days: {stats['favorable_days']} ({stats['favorable_fraction']*100:.1f}%)")
    print(f"  Mean temperature: {stats['mean_temperature']:.1f}°C")
    print(f"  Temperature range: {stats['temperature_range'][0]:.1f}-{stats['temperature_range'][1]:.1f}°C")
    print(f"  Mean humidity: {stats['mean_humidity']:.1f}%")
    print(f"  Mean carrying capacity: {stats['mean_carrying_capacity']:.0f}")
    print(f"  Mean quality index: {stats['mean_quality_index']:.3f}")
    
    # Check suitability
    is_suitable = habitat.is_suitable_for_species(optimal_temp, lethal_temp, min_favorable_fraction=0.8)
    print(f"\nSuitable for species (>=80% favorable days): {is_suitable}")
    
    print("\nOK Habitat entity test passed")


def test_entity_integration():
    """Test integration between entities."""
    print("\n" + "="*60)
    print("Test 5: Entity Integration")
    print("="*60)
    
    # Load configuration
    config = ConfigManager()
    species_config = config.get_species_config("aedes_aegypti")
    env_config = config.get_environment_config()
    
    # Create all entities
    species = Species(species_config)
    
    environment_model = EnvironmentModel(env_config, days=51)  # 51 days for 50-day simulation
    habitat = Habitat(
        habitat_id="HAB001",
        name="Test habitat",
        environment_model=environment_model,
        config=env_config
    )
    
    prolog_bridge = PrologBridge(config)
    prolog_bridge.inject_parameters()  # Cargar parámetros antes de usar
    population_model = PopulationModel(
        species_config=species_config,
        environment_model=environment_model,
        prolog_bridge=prolog_bridge
    )
    
    population = Population(species=species, model=population_model)
    
    print(f"\nIntegrated simulation:")
    print(f"  Species: {species}")
    print(f"  Habitat: {habitat}")
    
    # Check habitat suitability for species
    optimal_temp = species.get_temperature_tolerance()
    lethal_temp = species.get_lethal_temperature_range()
    
    is_suitable = habitat.is_suitable_for_species(optimal_temp, lethal_temp)
    print(f"  Habitat suitable: {is_suitable}")
    
    # Initialize population (using total for larvae)
    population.initialize(
        initial_eggs=200,
        initial_larvae=280,  # Total larvae as single int
        initial_pupae=50,
        initial_adults=30
    )
    
    initial = population.get_current_snapshot()
    print(f"  Initial population: {initial.total}")
    
    # Run simulation
    print(f"\nRunning 50-day simulation...")
    trajectory = population.simulate(days=50)
    
    final = population.get_current_snapshot()
    print(f"  Final population: {final.total}")
    
    # Get habitat conditions at peak population day
    peak_day, peak_size = population.get_peak_population()
    print(f"  Peak: {peak_size} individuals on day {peak_day}")
    
    peak_conditions = habitat.get_conditions_at_day(peak_day, optimal_temp, lethal_temp)
    print(f"  Conditions at peak: T={peak_conditions.temperature:.1f}°C, "
          f"quality={peak_conditions.quality_index:.2f}")
    
    print("\nOK Entity integration test passed")


if __name__ == "__main__":
    print("="*60)
    print("TESTING DOMAIN ENTITIES")
    print("="*60)
    
    try:
        test_species_entity()
        test_mosquito_entity()
        test_population_entity()
        test_habitat_entity()
        test_entity_integration()
        
        print("\n" + "="*60)
        print("ALL ENTITY TESTS PASSED OK")
        print("="*60)
        
    except Exception as e:
        print(f"\nERROR Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
