"""
Tests for Application Layer DTOs
=================================

Tests Data Transfer Objects for the application layer.

Author: Mosquito Simulation System
Date: January 2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from application.dtos import (
    SimulationConfig,
    PopulationResult,
    AgentResult,
    ComparisonResult
)


def test_simulation_config():
    """Test SimulationConfig DTO"""
    print("\n" + "="*60)
    print("Test 1: SimulationConfig")
    print("="*60)
    
    # Test basic creation
    config = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=90,
        initial_eggs=100,
        initial_larvae=[50, 40, 30, 20],
        initial_pupae=10,
        initial_adults=5,
        random_seed=42
    )
    
    assert config.species_id == 'aedes_aegypti'
    assert config.duration_days == 90
    assert config.initial_larvae == [50, 40, 30, 20]
    print("✓ Basic creation works")
    
    # Test validation - valid config
    is_valid, errors = config.validate()
    assert is_valid == True
    assert len(errors) == 0
    print("✓ Valid config passes validation")
    
    # Test validation - invalid duration
    config_invalid = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=0,
        initial_eggs=100,
        initial_larvae=[50, 40, 30, 20],
        initial_pupae=10,
        initial_adults=5
    )
    is_valid, errors = config_invalid.validate()
    assert is_valid == False
    assert len(errors) > 0
    assert any('duration_days' in err for err in errors)
    print("✓ Invalid duration detected")
    
    # Test validation - negative eggs
    config_neg = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=90,
        initial_eggs=-10,
        initial_larvae=[50, 40, 30, 20],
        initial_pupae=10,
        initial_adults=5
    )
    is_valid, errors = config_neg.validate()
    assert is_valid == False
    assert any('eggs' in err for err in errors)
    print("✓ Negative values detected")
    
    # Test validation - wrong larvae format
    config_wrong_larvae = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=90,
        initial_eggs=100,
        initial_larvae=[50, 40, 30],  # Should be 4 elements
        initial_pupae=10,
        initial_adults=5
    )
    is_valid, errors = config_wrong_larvae.validate()
    assert is_valid == False
    assert any('4 elements' in err for err in errors)
    print("✓ Incorrect larvae array detected")
    
    # Test to_dict and from_dict
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict['species_id'] == 'aedes_aegypti'
    print("✓ to_dict() works")
    
    config_restored = SimulationConfig.from_dict(config_dict)
    assert config_restored.species_id == config.species_id
    assert config_restored.duration_days == config.duration_days
    print("✓ from_dict() works")
    
    # Test with int larvae
    config_int_larvae = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=90,
        initial_eggs=100,
        initial_larvae=140,  # Total as int
        initial_pupae=10,
        initial_adults=5
    )
    is_valid, errors = config_int_larvae.validate()
    assert is_valid == True
    print("✓ Integer larvae format accepted")
    
    print("\n✅ SimulationConfig test passed")
    return True


def test_population_result():
    """Test PopulationResult DTO"""
    print("\n" + "="*60)
    print("Test 2: PopulationResult")
    print("="*60)
    
    # Create sample data
    days = np.array([0, 1, 2, 3, 4, 5])
    eggs = np.array([100, 120, 150, 180, 200, 220])
    larvae = np.array([50, 60, 70, 80, 90, 100])
    pupae = np.array([10, 12, 15, 18, 20, 22])
    adults = np.array([5, 6, 8, 10, 12, 15])
    total = eggs + larvae + pupae + adults
    
    statistics = {
        'peak_day': 5,
        'peak_population': int(total[5]),
        'extinction_day': None,
        'mean_population': float(np.mean(total)),
        'final_population': int(total[-1])
    }
    
    result = PopulationResult(
        species_id='aedes_aegypti',
        days=days,
        eggs=eggs,
        larvae=larvae,
        pupae=pupae,
        adults=adults,
        total_population=total,
        statistics=statistics
    )
    
    assert result.species_id == 'aedes_aegypti'
    assert len(result.days) == 6
    assert result.statistics['peak_day'] == 5
    print("✓ Basic creation works")
    
    # Test to_dict
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert isinstance(result_dict['days'], list)
    assert isinstance(result_dict['eggs'], list)
    print("✓ to_dict() converts arrays to lists")
    
    # Test from_dict
    result_restored = PopulationResult.from_dict(result_dict)
    assert isinstance(result_restored.days, np.ndarray)
    assert isinstance(result_restored.eggs, np.ndarray)
    assert len(result_restored.days) == len(result.days)
    print("✓ from_dict() converts lists back to arrays")
    
    # Test get_final_state
    final_state = result.get_final_state()
    assert final_state['day'] == 5
    assert final_state['eggs'] == 220.0
    assert final_state['larvae'] == 100.0
    assert final_state['pupae'] == 22.0
    assert final_state['adults'] == 15.0
    print("✓ get_final_state() works")
    
    print("\n✅ PopulationResult test passed")
    return True


def test_agent_result():
    """Test AgentResult DTO"""
    print("\n" + "="*60)
    print("Test 3: AgentResult")
    print("="*60)
    
    # Create sample agent result
    daily_stats = [
        {'day': 0, 'vectors_alive': 10, 'predators_alive': 5, 'total_eggs_laid': 0, 'total_prey_consumed': 0},
        {'day': 1, 'vectors_alive': 10, 'predators_alive': 5, 'total_eggs_laid': 50, 'total_prey_consumed': 5},
        {'day': 2, 'vectors_alive': 9, 'predators_alive': 5, 'total_eggs_laid': 100, 'total_prey_consumed': 10},
    ]
    
    result = AgentResult(
        num_vectors_initial=10,
        num_predators_initial=5,
        num_vectors_final=9,
        num_predators_final=5,
        total_eggs_laid=100,
        total_prey_consumed=10,
        daily_stats=daily_stats
    )
    
    assert result.num_vectors_initial == 10
    assert result.num_vectors_final == 9
    assert result.total_eggs_laid == 100
    print("✓ Basic creation works")
    
    # Test survival rates
    vector_survival = result.get_survival_rate_vectors()
    assert vector_survival == 0.9
    print(f"✓ Vector survival rate: {vector_survival}")
    
    predator_survival = result.get_survival_rate_predators()
    assert predator_survival == 1.0
    print(f"✓ Predator survival rate: {predator_survival}")
    
    # Test averages
    avg_eggs = result.get_average_eggs_per_vector()
    assert avg_eggs == 10.0
    print(f"✓ Average eggs per vector: {avg_eggs}")
    
    avg_prey = result.get_average_prey_per_predator()
    assert avg_prey == 2.0
    print(f"✓ Average prey per predator: {avg_prey}")
    
    # Test to_dict and from_dict
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    print("✓ to_dict() works")
    
    result_restored = AgentResult.from_dict(result_dict)
    assert result_restored.num_vectors_initial == result.num_vectors_initial
    assert len(result_restored.daily_stats) == len(result.daily_stats)
    print("✓ from_dict() works")
    
    # Test edge case: zero agents
    result_zero = AgentResult(
        num_vectors_initial=0,
        num_predators_initial=0,
        num_vectors_final=0,
        num_predators_final=0,
        total_eggs_laid=0,
        total_prey_consumed=0,
        daily_stats=[]
    )
    assert result_zero.get_survival_rate_vectors() == 0.0
    assert result_zero.get_average_eggs_per_vector() == 0.0
    print("✓ Edge case (zero agents) handled")
    
    print("\n✅ AgentResult test passed")
    return True


def test_comparison_result():
    """Test ComparisonResult DTO"""
    print("\n" + "="*60)
    print("Test 4: ComparisonResult")
    print("="*60)
    
    # Create sample comparison results
    days = np.array([0, 1, 2, 3, 4, 5])
    
    # Scenario 1: baseline
    result1 = PopulationResult(
        species_id='aedes_aegypti',
        days=days,
        eggs=np.array([100, 120, 150, 180, 200, 220]),
        larvae=np.array([50, 60, 70, 80, 90, 100]),
        pupae=np.array([10, 12, 15, 18, 20, 22]),
        adults=np.array([5, 6, 8, 10, 12, 15]),
        total_population=np.array([165, 198, 243, 288, 322, 357]),
        statistics={'peak_day': 5, 'peak_population': 357, 'final_population': 357, 'mean_population': 262.17}
    )
    
    # Scenario 2: with_control (lower populations)
    result2 = PopulationResult(
        species_id='aedes_aegypti',
        days=days,
        eggs=np.array([100, 110, 120, 130, 140, 150]),
        larvae=np.array([50, 55, 60, 65, 70, 75]),
        pupae=np.array([10, 11, 12, 13, 14, 15]),
        adults=np.array([5, 5, 6, 6, 7, 8]),
        total_population=np.array([165, 181, 198, 214, 231, 248]),
        statistics={'peak_day': 5, 'peak_population': 248, 'final_population': 248, 'mean_population': 206.17}
    )
    
    comparison = {
        'baseline': {
            'peak_population': 357,
            'peak_day': 5,
            'final_population': 357,
            'mean_population': 262.17
        },
        'with_control': {
            'peak_population': 248,
            'peak_day': 5,
            'final_population': 248,
            'mean_population': 206.17
        }
    }
    
    comp_result = ComparisonResult(
        scenario_names=['baseline', 'with_control'],
        results={'baseline': result1, 'with_control': result2},
        comparison=comparison,
        checkpoint_paths={
            'baseline': 'checkpoint_baseline_5days_20260109.json',
            'with_control': 'checkpoint_with_control_5days_20260109.json'
        }
    )
    
    assert len(comp_result.scenario_names) == 2
    assert 'baseline' in comp_result.results
    assert 'with_control' in comp_result.results
    print("✓ Basic creation works")
    
    # Test get_best_scenario
    best = comp_result.get_best_scenario('peak_population')
    assert best == 'with_control'  # Lower peak is better
    print(f"✓ Best scenario (peak_population): {best}")
    
    # Test get_worst_scenario
    worst = comp_result.get_worst_scenario('peak_population')
    assert worst == 'baseline'  # Higher peak is worse
    print(f"✓ Worst scenario (peak_population): {worst}")
    
    # Test get_scenario_ranking
    ranking = comp_result.get_scenario_ranking('peak_population')
    assert len(ranking) == 2
    assert ranking[0][0] == 'with_control'  # Best first
    assert ranking[1][0] == 'baseline'  # Worst last
    print(f"✓ Scenario ranking: {[name for name, _ in ranking]}")
    
    # Test to_dict
    comp_dict = comp_result.to_dict()
    assert isinstance(comp_dict, dict)
    assert 'scenario_names' in comp_dict
    assert 'comparison' in comp_dict
    assert 'checkpoint_paths' in comp_dict
    print("✓ to_dict() works")
    
    print("\n✅ ComparisonResult test passed")
    return True


def test_serialization():
    """Test JSON serialization compatibility"""
    print("\n" + "="*60)
    print("Test 5: JSON Serialization")
    print("="*60)
    
    import json
    
    # Test SimulationConfig serialization
    config = SimulationConfig(
        species_id='aedes_aegypti',
        duration_days=90,
        initial_eggs=100,
        initial_larvae=[50, 40, 30, 20],
        initial_pupae=10,
        initial_adults=5,
        random_seed=42
    )
    
    config_dict = config.to_dict()
    json_str = json.dumps(config_dict)
    config_restored_dict = json.loads(json_str)
    config_restored = SimulationConfig.from_dict(config_restored_dict)
    
    assert config_restored.species_id == config.species_id
    assert config_restored.random_seed == config.random_seed
    print("✓ SimulationConfig JSON serialization works")
    
    # Test PopulationResult serialization
    result = PopulationResult(
        species_id='aedes_aegypti',
        days=np.array([0, 1, 2]),
        eggs=np.array([100, 120, 150]),
        larvae=np.array([50, 60, 70]),
        pupae=np.array([10, 12, 15]),
        adults=np.array([5, 6, 8]),
        total_population=np.array([165, 198, 243]),
        statistics={'peak_day': 2, 'peak_population': 243}
    )
    
    result_dict = result.to_dict()
    json_str = json.dumps(result_dict)
    result_restored_dict = json.loads(json_str)
    result_restored = PopulationResult.from_dict(result_restored_dict)
    
    assert np.array_equal(result_restored.days, result.days)
    assert np.array_equal(result_restored.eggs, result.eggs)
    print("✓ PopulationResult JSON serialization works")
    
    print("\n✅ JSON Serialization test passed")
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTING APPLICATION LAYER DTOs")
    print("="*60)
    
    try:
        test_simulation_config()
        test_population_result()
        test_agent_result()
        test_comparison_result()
        test_serialization()
        
        print("\n" + "="*60)
        print("✅ ALL DTO TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
