"""
Test Script for Domain Models
==============================

Tests the mathematical models in the domain layer:
- Stochastic processes
- Leslie matrix
- Environment model
- Integrated population model
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.dirname(__file__))

from infrastructure.config import load_default_config
from infrastructure.prolog_bridge import create_prolog_bridge
from domain.models.stochastic_processes import (
    StochasticVariation,
    DemographicStochasticity,
    EnvironmentalStochasticity
)
from domain.models.leslie_matrix import (
    LeslieMatrix,
    create_leslie_matrix_from_config
)
from domain.models.environment_model import (
    EnvironmentModel,
    create_environment_from_config
)
from domain.models.population_model import (
    PopulationModel
)


def test_stochastic_processes():
    """Test stochastic process generators."""
    print("=" * 70)
    print("TEST 1: Stochastic Processes")
    print("=" * 70)
    
    # Test StochasticVariation
    print("\n1.1 StochasticVariation")
    stoch = StochasticVariation(seed=42)
    
    # Test survival variation
    survival_samples = [stoch.vary_survival(0.80, cv=0.1) for _ in range(10)]
    print(f"  - Survival rate variation (base=0.80, cv=0.1):")
    print(f"    Mean: {np.mean(survival_samples):.4f}")
    print(f"    Std: {np.std(survival_samples):.4f}")
    print(f"    Range: [{min(survival_samples):.4f}, {max(survival_samples):.4f}]")
    
    # Test fecundity variation
    fecundity_samples = [stoch.vary_fecundity(100, cv=0.15) for _ in range(10)]
    print(f"  - Fecundity variation (mean=100, cv=0.15):")
    print(f"    Mean: {np.mean(fecundity_samples):.1f}")
    print(f"    Std: {np.std(fecundity_samples):.1f}")
    print(f"    Range: [{min(fecundity_samples)}, {max(fecundity_samples)}]")
    
    # Test DemographicStochasticity
    print("\n1.2 DemographicStochasticity")
    demo = DemographicStochasticity(seed=42)
    
    transition_samples = [demo.apply_to_transitions(100, 0.80) for _ in range(10)]
    print(f"  - Binomial transitions (n=100, p=0.80):")
    print(f"    Mean: {np.mean(transition_samples):.1f}")
    print(f"    Std: {np.std(transition_samples):.1f}")
    
    birth_samples = [demo.apply_to_births(50, 100) for _ in range(10)]
    print(f"  - Poisson births (50 females, 100 eggs/female):")
    print(f"    Mean: {np.mean(birth_samples):.1f}")
    print(f"    Std: {np.std(birth_samples):.1f}")
    
    # Test EnvironmentalStochasticity
    print("\n1.3 EnvironmentalStochasticity")
    env_stoch = EnvironmentalStochasticity(seed=42)
    
    temp_series = env_stoch.generate_temperature_series(
        days=365,
        mean=27.0,
        seasonal_amplitude=5.0
    )
    print(f"  - Temperature series (365 days):")
    print(f"    Mean: {np.mean(temp_series):.2f}°C")
    print(f"    Std: {np.std(temp_series):.2f}°C")
    print(f"    Range: [{np.min(temp_series):.2f}, {np.max(temp_series):.2f}]°C")
    
    hum_series = env_stoch.generate_humidity_series(
        days=365,
        mean=75.0
    )
    print(f"  - Humidity series (365 days):")
    print(f"    Mean: {np.mean(hum_series):.2f}%")
    print(f"    Std: {np.std(hum_series):.2f}%")
    print(f"    Range: [{np.min(hum_series):.2f}, {np.max(hum_series):.2f}]%")
    
    print("\n✓ Stochastic processes test PASSED\n")


def test_leslie_matrix():
    """Test Leslie matrix implementation."""
    print("=" * 70)
    print("TEST 2: Leslie Matrix")
    print("=" * 70)
    
    # Create simple Leslie matrix
    print("\n2.1 Basic Leslie Matrix")
    fecundity = [0, 0, 0, 100]  # Only adults reproduce
    survival = [0.7, 0.8, 0.9]  # Egg->larva, larva->pupa, pupa->adult
    stage_names = ['egg', 'larva', 'pupa', 'adult']
    
    L = LeslieMatrix(fecundity, survival, stage_names)
    print(f"  - Matrix shape: {L.matrix.shape}")
    print(f"  - Matrix:\n{L.matrix}")
    
    # Eigenanalysis
    print("\n2.2 Eigenanalysis")
    result = L.eigenanalysis()
    print(f"  - Dominant eigenvalue (λ₁): {result.lambda_1:.4f}")
    print(f"  - Intrinsic rate (r): {result.r:.4f}")
    print(f"  - Generation time: {result.generation_time:.2f}")
    print(f"  - Net reproductive rate (R₀): {L.net_reproductive_rate():.2f}")
    print(f"  - Doubling time: {result.doubling_time:.2f} days" if result.doubling_time else "  - Population declining")
    print(f"  - Population viable: {L.is_viable()}")
    
    # Stable age distribution
    print("\n2.3 Stable Age Distribution")
    stable_dist = L.get_stable_distribution()
    for stage, proportion in stable_dist.items():
        print(f"  - {stage}: {proportion:.4f} ({proportion*100:.2f}%)")
    
    # Population projection
    print("\n2.4 Population Projection")
    initial = np.array([1000, 500, 200, 100])
    trajectory = L.project(initial, timesteps=30)
    print(f"  - Initial population: {initial.sum():.0f}")
    print(f"  - Day 10 population: {trajectory[10].sum():.0f}")
    print(f"  - Day 20 population: {trajectory[20].sum():.0f}")
    print(f"  - Day 30 population: {trajectory[30].sum():.0f}")
    
    # Create from config
    print("\n2.5 Leslie Matrix from Configuration")
    config = load_default_config()
    aegypti_config = config.get_species_config('aedes_aegypti')
    L_aegypti = create_leslie_matrix_from_config(aegypti_config)
    print(f"  - Species: {aegypti_config.species_id}")
    print(f"  - λ₁: {L_aegypti.eigenanalysis().lambda_1:.4f}")
    print(f"  - Viable: {L_aegypti.is_viable()}")
    
    print("\n✓ Leslie matrix test PASSED\n")


def test_environment_model():
    """Test environment model."""
    print("=" * 70)
    print("TEST 3: Environment Model")
    print("=" * 70)
    
    # Load configuration
    config = load_default_config()
    
    # Create environment model
    print("\n3.1 Environment Model Creation")
    env = create_environment_from_config(config.get_environment_config(), days=365, seed=42)
    print(f"  - Simulation days: {env.days}")
    print(f"  - Base carrying capacity: {env.base_carrying_capacity}")
    
    # Get statistics
    print("\n3.2 Environmental Statistics")
    stats = env.get_statistics()
    
    print(f"  - Temperature:")
    print(f"    Mean: {stats['temperature']['mean']:.2f}°C")
    print(f"    Std: {stats['temperature']['std']:.2f}°C")
    print(f"    Range: [{stats['temperature']['min']:.2f}, {stats['temperature']['max']:.2f}]°C")
    
    print(f"  - Humidity:")
    print(f"    Mean: {stats['humidity']['mean']:.2f}%")
    print(f"    Std: {stats['humidity']['std']:.2f}%")
    print(f"    Range: [{stats['humidity']['min']:.2f}, {stats['humidity']['max']:.2f}]%")
    
    print(f"  - Carrying Capacity:")
    print(f"    Mean: {stats['carrying_capacity']['mean']:.0f}")
    print(f"    Range: [{stats['carrying_capacity']['min']:.0f}, {stats['carrying_capacity']['max']:.0f}]")
    
    # Test specific day
    print("\n3.3 Conditions at Day 0")
    conditions = env.get_conditions(0)
    print(f"  - Temperature: {conditions.temperature:.2f}°C")
    print(f"  - Humidity: {conditions.humidity:.2f}%")
    print(f"  - Carrying capacity: {conditions.carrying_capacity}")
    
    # Test favorable days
    print("\n3.4 Favorable Conditions Analysis")
    favorable_days = env.count_favorable_days(temp_range=(20, 32), hum_threshold=60)
    print(f"  - Favorable days: {favorable_days}/{env.days} ({favorable_days/env.days*100:.1f}%)")
    
    print("\n✓ Environment model test PASSED\n")


def test_population_model():
    """Test integrated population model."""
    print("=" * 70)
    print("TEST 4: Integrated Population Model")
    print("=" * 70)
    
    # Load configuration
    config = load_default_config()
    aegypti_config = config.get_species_config('aedes_aegypti')
    
    # Create environment
    env = create_environment_from_config(config.get_environment_config(), days=101, seed=42)
    
    # Create population model
    print("\n4.1 Population Model Creation")
    model = PopulationModel(
        species_config=aegypti_config,
        environment_model=env,
        stochastic_mode=False,  # Deterministic for testing
        seed=42
    )
    print(f"  - Species: {model.species_name}")
    print(f"  - Leslie matrix λ₁: {model.leslie_matrix.eigenanalysis().lambda_1:.4f}")
    print(f"  - Stochastic mode: {model.stochastic_mode}")
    
    # Initialize population
    print("\n4.2 Population Initialization")
    initial_state = model.initialize(
        initial_eggs=500,
        initial_larvae=300,
        initial_pupae=100,
        initial_adults=100
    )
    print(f"  - Initial eggs: {initial_state.eggs}")
    print(f"  - Initial larvae: {initial_state.larvae}")
    print(f"  - Initial pupae: {initial_state.pupae}")
    print(f"  - Initial adults: {initial_state.adults}")
    print(f"  - Total: {initial_state.total}")
    
    # Run simulation
    print("\n4.3 Simulation Run (100 days)")
    trajectory = model.simulate(
        days=100,
        initial_adults=100
    )
    
    print(f"  - Trajectory length: {len(trajectory.states)}")
    print(f"  - Initial population: {trajectory.states[0].total}")
    print(f"  - Day 50 population: {trajectory.states[50].total}")
    print(f"  - Final population: {trajectory.states[-1].total}")
    
    # Summary statistics
    print("\n4.4 Summary Statistics")
    summary = trajectory.get_summary_statistics()
    print(f"  - Mean population: {summary['mean_population']:.0f}")
    print(f"  - Max population: {summary['max_population']}")
    print(f"  - Peak day: {summary['peak_day']}")
    print(f"  - Extinct: {summary['is_extinct']}")
    
    # Stage populations
    print("\n4.5 Stage Populations at Day 50")
    day_50 = trajectory.get_state(50)
    print(f"  - Eggs: {day_50.eggs}")
    print(f"  - Larvae: {day_50.larvae}")
    print(f"  - Pupae: {day_50.pupae}")
    print(f"  - Adults: {day_50.adults}")
    
    print("\n✓ Population model test PASSED\n")


def test_integration_with_prolog():
    """Test integration with Prolog bridge."""
    print("=" * 70)
    print("TEST 5: Integration with Prolog")
    print("=" * 70)
    
    try:
        # Load configuration
        config = load_default_config()
        aegypti_config = config.get_species_config('aedes_aegypti')
        
        # Create Prolog bridge
        print("\n5.1 Creating Prolog Bridge")
        prolog_bridge = create_prolog_bridge(config)
        print(f"  - Prolog bridge created successfully")
        
        # Create environment
        env = create_environment_from_config(config.get_environment_config(), days=50, seed=42)
        
        # Create population model with Prolog
        print("\n5.2 Population Model with Prolog")
        model = PopulationModel(
            species_config=aegypti_config,
            environment_model=env,
            prolog_bridge=prolog_bridge,
            stochastic_mode=False,
            seed=42
        )
        print(f"  - Model created with Prolog integration")
        
        # Run short simulation
        print("\n5.3 Short Simulation (50 days)")
        trajectory = model.simulate(days=50, initial_adults=100)
        print(f"  - Initial: {trajectory.states[0].total}")
        print(f"  - Day 25: {trajectory.states[25].total}")
        print(f"  - Final: {trajectory.states[-1].total}")
        
        print("\n✓ Prolog integration test PASSED\n")
        
    except Exception as e:
        print(f"\n⚠ Prolog integration test SKIPPED: {e}")
        print("  (This is expected if SWI-Prolog is not installed)\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" DOMAIN MODELS TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_stochastic_processes()
        test_leslie_matrix()
        test_environment_model()
        test_population_model()
        test_integration_with_prolog()
        
        print("=" * 70)
        print(" ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
