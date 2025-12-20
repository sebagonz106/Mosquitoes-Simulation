"""
Tests for Application Visualization
====================================

Tests visualization functions (without displaying plots).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt

from application.dtos import PopulationResult, AgentResult, ComparisonResult
from application.visualization import (
    plot_population_evolution,
    plot_population_total,
    plot_population_stacked,
    plot_agent_survival,
    plot_agent_metrics,
    plot_scenario_comparison,
    plot_comparison_bar,
    save_all_plots,
    create_report_figure
)


def create_sample_population_result():
    """Create sample PopulationResult for testing"""
    days = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    eggs = np.array([100, 120, 150, 180, 200, 220, 240, 250, 240, 220, 200])
    larvae = np.array([50, 60, 70, 80, 90, 100, 110, 115, 110, 100, 90])
    pupae = np.array([10, 12, 15, 18, 20, 22, 25, 26, 25, 23, 20])
    adults = np.array([5, 6, 8, 10, 12, 15, 18, 20, 22, 23, 25])
    total = eggs + larvae + pupae + adults
    
    statistics = {
        'peak_day': 7,
        'peak_population': int(total[7]),
        'extinction_day': None,
        'mean_population': float(np.mean(total)),
        'final_population': int(total[-1])
    }
    
    return PopulationResult(
        species_id='aedes_aegypti',
        days=days,
        eggs=eggs,
        larvae=larvae,
        pupae=pupae,
        adults=adults,
        total_population=total,
        statistics=statistics
    )


def create_sample_agent_result():
    """Create sample AgentResult for testing"""
    daily_stats = []
    for day in range(10):
        daily_stats.append({
            'day': day,
            'vectors_alive': 10 - day // 3,
            'predators_alive': 5 - day // 5,
            'total_eggs_laid': day * 10,
            'total_prey_consumed': day * 2
        })
    
    return AgentResult(
        num_vectors_initial=10,
        num_predators_initial=5,
        num_vectors_final=7,
        num_predators_final=4,
        total_eggs_laid=90,
        total_prey_consumed=18,
        daily_stats=daily_stats
    )


def test_population_evolution():
    """Test population evolution plot"""
    print("\n" + "="*60)
    print("Test 1: Population Evolution Plot")
    print("="*60)
    
    result = create_sample_population_result()
    
    # Test plot creation
    fig = plot_population_evolution(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check subplots
    axes = fig.get_axes()
    assert len(axes) == 4  # 2x2 grid
    print("[OK] Contains 4 subplots (eggs, larvae, pupae, adults)")
    
    plt.close(fig)
    print("\n[OK] Population evolution plot test passed")
    return True


def test_population_total():
    """Test total population plot"""
    print("\n" + "="*60)
    print("Test 2: Total Population Plot")
    print("="*60)
    
    result = create_sample_population_result()
    
    # Test plot creation
    fig = plot_population_total(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has single axis
    axes = fig.get_axes()
    assert len(axes) == 1
    print("[OK] Contains single axis")
    
    # Check peak marker exists
    ax = axes[0]
    children = ax.get_children()
    has_scatter = any(isinstance(child, matplotlib.collections.PathCollection) 
                     for child in children)
    assert has_scatter
    print("[OK] Peak marker present")
    
    plt.close(fig)
    print("\n[OK] Total population plot test passed")
    return True


def test_population_stacked():
    """Test stacked population plot"""
    print("\n" + "="*60)
    print("Test 3: Stacked Population Plot")
    print("="*60)
    
    result = create_sample_population_result()
    
    # Test plot creation
    fig = plot_population_stacked(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has single axis
    axes = fig.get_axes()
    assert len(axes) == 1
    print("[OK] Contains single axis")
    
    # Check has filled areas (PolyCollection objects)
    ax = axes[0]
    children = ax.get_children()
    poly_count = sum(1 for child in children 
                    if isinstance(child, matplotlib.collections.PolyCollection))
    assert poly_count >= 4  # At least 4 stacked areas
    print(f"[OK] Contains {poly_count} stacked areas")
    
    plt.close(fig)
    print("\n[OK] Stacked population plot test passed")
    return True


def test_agent_survival():
    """Test agent survival plot"""
    print("\n" + "="*60)
    print("Test 4: Agent Survival Plot")
    print("="*60)
    
    result = create_sample_agent_result()
    
    # Test plot creation
    fig = plot_agent_survival(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has single axis
    axes = fig.get_axes()
    assert len(axes) == 1
    print("[OK] Contains single axis")
    
    # Check has two lines (vectors and predators)
    ax = axes[0]
    lines = ax.get_lines()
    assert len(lines) == 2
    print("[OK] Contains 2 lines (vectors, predators)")
    
    plt.close(fig)
    print("\n[OK] Agent survival plot test passed")
    return True


def test_agent_metrics():
    """Test agent metrics plot"""
    print("\n" + "="*60)
    print("Test 5: Agent Metrics Plot")
    print("="*60)
    
    result = create_sample_agent_result()
    
    # Test plot creation
    fig = plot_agent_metrics(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has two subplots
    axes = fig.get_axes()
    assert len(axes) == 2
    print("[OK] Contains 2 subplots (eggs, prey)")
    
    # Each should have a line
    for ax in axes:
        lines = ax.get_lines()
        assert len(lines) >= 1
    print("[OK] Each subplot has data lines")
    
    plt.close(fig)
    print("\n[OK] Agent metrics plot test passed")
    return True


def test_scenario_comparison():
    """Test scenario comparison plot"""
    print("\n" + "="*60)
    print("Test 6: Scenario Comparison Plot")
    print("="*60)
    
    # Create two sample results
    result1 = create_sample_population_result()
    
    # Create second result with different values
    days = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    eggs2 = result1.eggs * 0.8
    larvae2 = result1.larvae * 0.8
    pupae2 = result1.pupae * 0.8
    adults2 = result1.adults * 0.8
    total2 = eggs2 + larvae2 + pupae2 + adults2
    
    result2 = PopulationResult(
        species_id='aedes_aegypti',
        days=days,
        eggs=eggs2,
        larvae=larvae2,
        pupae=pupae2,
        adults=adults2,
        total_population=total2,
        statistics={
            'peak_day': 7,
            'peak_population': int(total2[7]),
            'extinction_day': None,
            'mean_population': float(np.mean(total2)),
            'final_population': int(total2[-1])
        }
    )
    
    # Create comparison
    comparison = ComparisonResult(
        scenario_names=['baseline', 'with_control'],
        results={'baseline': result1, 'with_control': result2},
        comparison={
            'baseline': {
                'peak_population': result1.statistics['peak_population'],
                'final_population': result1.statistics['final_population'],
                'mean_population': result1.statistics['mean_population']
            },
            'with_control': {
                'peak_population': result2.statistics['peak_population'],
                'final_population': result2.statistics['final_population'],
                'mean_population': result2.statistics['mean_population']
            }
        }
    )
    
    # Test plot creation
    fig = plot_scenario_comparison(comparison, metric='total_population', show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has single axis
    axes = fig.get_axes()
    assert len(axes) == 1
    print("[OK] Contains single axis")
    
    # Check has two lines (two scenarios)
    ax = axes[0]
    lines = ax.get_lines()
    assert len(lines) == 2
    print("[OK] Contains 2 lines (two scenarios)")
    
    plt.close(fig)
    print("\n[OK] Scenario comparison plot test passed")
    return True


def test_comparison_bar():
    """Test comparison bar chart"""
    print("\n" + "="*60)
    print("Test 7: Comparison Bar Chart")
    print("="*60)
    
    # Create comparison (reuse from previous test)
    result1 = create_sample_population_result()
    result2_data = result1.total_population * 0.8
    
    result2 = PopulationResult(
        species_id='aedes_aegypti',
        days=result1.days,
        eggs=result1.eggs * 0.8,
        larvae=result1.larvae * 0.8,
        pupae=result1.pupae * 0.8,
        adults=result1.adults * 0.8,
        total_population=result2_data,
        statistics={
            'peak_day': 7,
            'peak_population': int(result2_data[7]),
            'extinction_day': None,
            'mean_population': float(np.mean(result2_data)),
            'final_population': int(result2_data[-1])
        }
    )
    
    comparison = ComparisonResult(
        scenario_names=['baseline', 'with_control'],
        results={'baseline': result1, 'with_control': result2},
        comparison={
            'baseline': result1.statistics,
            'with_control': result2.statistics
        }
    )
    
    # Test plot creation
    fig = plot_comparison_bar(comparison, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has 3 subplots (default metrics)
    axes = fig.get_axes()
    assert len(axes) == 3
    print("[OK] Contains 3 subplots (default metrics)")
    
    plt.close(fig)
    print("\n[OK] Comparison bar chart test passed")
    return True


def test_save_all_plots():
    """Test saving all plots"""
    print("\n" + "="*60)
    print("Test 8: Save All Plots")
    print("="*60)
    
    result = create_sample_population_result()
    
    # Create temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save all plots
        saved_files = save_all_plots(result, tmpdir, prefix="test_")
        
        assert len(saved_files) == 3
        print(f"[OK] Saved {len(saved_files)} plots")
        
        # Check files exist
        for filepath in saved_files:
            assert os.path.exists(filepath)
            print(f"  [OK] {os.path.basename(filepath)}")
    
    print("\n[OK] Save all plots test passed")
    return True


def test_create_report_figure():
    """Test comprehensive report figure"""
    print("\n" + "="*60)
    print("Test 9: Create Report Figure")
    print("="*60)
    
    result = create_sample_population_result()
    
    # Test plot creation
    fig = create_report_figure(result, show=False)
    assert fig is not None
    assert isinstance(fig, matplotlib.figure.Figure)
    print("[OK] Figure created successfully")
    
    # Check has multiple subplots
    axes = fig.get_axes()
    assert len(axes) >= 4  # At least 4 subplots
    print(f"[OK] Contains {len(axes)} subplots")
    
    plt.close(fig)
    print("\n[OK] Report figure test passed")
    return True


def test_plot_with_save():
    """Test plot saving functionality"""
    print("\n" + "="*60)
    print("Test 10: Plot Saving")
    print("="*60)
    
    result = create_sample_population_result()
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_plot.png")
        
        # Create and save plot
        fig = plot_population_total(result, show=False, save_path=filepath)
        
        # Check file was created
        assert os.path.exists(filepath)
        print(f"[OK] Plot saved to {filepath}")
        
        # Check file size > 0
        file_size = os.path.getsize(filepath)
        assert file_size > 0
        print(f"[OK] File size: {file_size} bytes")
        
        plt.close(fig)
    
    print("\n[OK] Plot saving test passed")
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTING APPLICATION VISUALIZATION")
    print("="*60)
    
    try:
        test_population_evolution()
        test_population_total()
        test_population_stacked()
        test_agent_survival()
        test_agent_metrics()
        test_scenario_comparison()
        test_comparison_bar()
        test_save_all_plots()
        test_create_report_figure()
        test_plot_with_save()
        
        print("\n" + "="*60)
        print("[OK] ALL VISUALIZATION TESTS PASSED")
        print("="*60)
        print("\nNote: Plots were generated but not displayed (test mode)")
        
    except AssertionError as e:
        print(f"\n[X] Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
