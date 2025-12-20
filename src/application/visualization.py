"""
Application Layer - Visualization
==================================

Plotting functions for simulation results.
"""

from typing import Optional, List, Dict
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np
from pathlib import Path

from application.dtos import PopulationResult, AgentResult, ComparisonResult


# ============================================================================
# POPULATION VISUALIZATION
# ============================================================================

def plot_population_evolution(
    result: PopulationResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 8)
) -> matplotlib.figure.Figure:
    """
    Plot complete population evolution across all life stages.
    
    Args:
        result: PopulationResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(f'Population Evolution - {result.species_id}', fontsize=16, fontweight='bold')
    
    # Plot each stage
    stages = [
        ('Eggs', result.eggs, axes[0, 0], 'blue', 'o'),
        ('Larvae', result.larvae, axes[0, 1], 'green', 's'),
        ('Pupae', result.pupae, axes[1, 0], 'orange', '^'),
        ('Adults', result.adults, axes[1, 1], 'red', 'd')
    ]
    
    for stage_name, data, ax, color, marker in stages:
        ax.plot(result.days, data, color=color, marker=marker, 
                markersize=4, linewidth=2, label=stage_name)
        ax.set_xlabel('Days', fontsize=10)
        ax.set_ylabel('Population', fontsize=10)
        ax.set_title(stage_name, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


def plot_population_total(
    result: PopulationResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6)
) -> matplotlib.figure.Figure:
    """
    Plot total population over time with peak marker.
    
    Args:
        result: PopulationResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot total population
    ax.plot(result.days, result.total_population, 
            color='purple', linewidth=2.5, label='Total Population')
    
    # Mark peak
    peak_day = result.statistics['peak_day']
    peak_pop = result.statistics['peak_population']
    ax.scatter([peak_day], [peak_pop], color='red', s=200, 
               marker='*', zorder=5, label=f'Peak: {peak_pop} at day {peak_day}')
    
    # Mark extinction if occurred
    if result.statistics.get('extinction_day') is not None:
        ext_day = result.statistics['extinction_day']
        ax.axvline(x=ext_day, color='black', linestyle='--', 
                  linewidth=2, label=f'Extinction: day {ext_day}')
    
    ax.set_xlabel('Days', fontsize=12)
    ax.set_ylabel('Total Population', fontsize=12)
    ax.set_title(f'Total Population Over Time - {result.species_id}', 
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10)
    
    # Add statistics text box
    stats_text = f"Mean: {result.statistics['mean_population']:.1f}\n"
    stats_text += f"Final: {result.statistics['final_population']}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           verticalalignment='top', bbox=dict(boxstyle='round', 
           facecolor='wheat', alpha=0.5), fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


def plot_population_stacked(
    result: PopulationResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 7)
) -> matplotlib.figure.Figure:
    """
    Plot population as stacked area chart showing stage composition.
    
    Args:
        result: PopulationResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Stack areas
    ax.fill_between(result.days, 0, result.eggs, 
                    label='Eggs', alpha=0.7, color='blue')
    ax.fill_between(result.days, result.eggs, 
                    result.eggs + result.larvae,
                    label='Larvae', alpha=0.7, color='green')
    ax.fill_between(result.days, result.eggs + result.larvae,
                    result.eggs + result.larvae + result.pupae,
                    label='Pupae', alpha=0.7, color='orange')
    ax.fill_between(result.days, result.eggs + result.larvae + result.pupae,
                    result.total_population,
                    label='Adults', alpha=0.7, color='red')
    
    ax.set_xlabel('Days', fontsize=12)
    ax.set_ylabel('Population', fontsize=12)
    ax.set_title(f'Population Composition Over Time - {result.species_id}',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# AGENT VISUALIZATION
# ============================================================================

def plot_agent_survival(
    result: AgentResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6)
) -> matplotlib.figure.Figure:
    """
    Plot agent survival over time.
    
    Args:
        result: AgentResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    days = [stat['day'] for stat in result.daily_stats]
    vectors_alive = [stat['vectors_alive'] for stat in result.daily_stats]
    predators_alive = [stat['predators_alive'] for stat in result.daily_stats]
    
    ax.plot(days, vectors_alive, marker='o', linewidth=2, 
            label=f'Vectors (Survival: {result.get_survival_rate_vectors():.1%})', 
            color='blue')
    ax.plot(days, predators_alive, marker='s', linewidth=2,
            label=f'Predators (Survival: {result.get_survival_rate_predators():.1%})',
            color='red')
    
    ax.set_xlabel('Days', fontsize=12)
    ax.set_ylabel('Agents Alive', fontsize=12)
    ax.set_title('Agent Survival Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


def plot_agent_metrics(
    result: AgentResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 6)
) -> matplotlib.figure.Figure:
    """
    Plot agent performance metrics (eggs laid, prey consumed).
    
    Args:
        result: AgentResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    days = [stat['day'] for stat in result.daily_stats]
    eggs_laid = [stat['total_eggs_laid'] for stat in result.daily_stats]
    prey_consumed = [stat['total_prey_consumed'] for stat in result.daily_stats]
    
    # Eggs laid
    ax1.plot(days, eggs_laid, marker='o', linewidth=2, color='green')
    ax1.set_xlabel('Days', fontsize=12)
    ax1.set_ylabel('Total Eggs Laid', fontsize=12)
    ax1.set_title('Cumulative Eggs Laid by Vectors', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    avg_eggs = result.get_average_eggs_per_vector()
    ax1.text(0.02, 0.98, f'Avg per vector: {avg_eggs:.1f}', 
            transform=ax1.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    # Prey consumed
    ax2.plot(days, prey_consumed, marker='s', linewidth=2, color='red')
    ax2.set_xlabel('Days', fontsize=12)
    ax2.set_ylabel('Total Prey Consumed', fontsize=12)
    ax2.set_title('Cumulative Prey Consumed by Predators', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    avg_prey = result.get_average_prey_per_predator()
    ax2.text(0.02, 0.98, f'Avg per predator: {avg_prey:.1f}',
            transform=ax2.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# COMPARISON VISUALIZATION
# ============================================================================

def plot_scenario_comparison(
    comparison: ComparisonResult,
    metric: str = 'total_population',
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 7)
) -> matplotlib.figure.Figure:
    """
    Compare multiple scenarios for a specific metric.
    
    Args:
        comparison: ComparisonResult to visualize
        metric: Metric to compare ('total_population', 'eggs', 'larvae', etc.)
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.get_cmap('tab10')(np.linspace(0, 1, len(comparison.scenario_names)))
    
    for i, scenario_name in enumerate(comparison.scenario_names):
        result = comparison.results[scenario_name]
        
        if metric == 'total_population':
            data = result.total_population
        elif metric == 'eggs':
            data = result.eggs
        elif metric == 'larvae':
            data = result.larvae
        elif metric == 'pupae':
            data = result.pupae
        elif metric == 'adults':
            data = result.adults
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        peak = comparison.comparison[scenario_name]['peak_population']
        ax.plot(result.days, data, linewidth=2.5, label=f'{scenario_name} (peak: {peak})',
               color=colors[i])
    
    ax.set_xlabel('Days', fontsize=12)
    ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax.set_title(f'Scenario Comparison - {metric.replace("_", " ").title()}',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add best/worst markers
    best = comparison.get_best_scenario('peak_population')
    worst = comparison.get_worst_scenario('peak_population')
    
    info_text = f"Best control: {best}\nWorst control: {worst}"
    ax.text(0.98, 0.98, info_text, transform=ax.transAxes,
           verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7),
           fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


def plot_comparison_bar(
    comparison: ComparisonResult,
    metrics: Optional[List[str]] = None,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6)
) -> matplotlib.figure.Figure:
    """
    Bar chart comparing scenarios across multiple metrics.
    
    Args:
        comparison: ComparisonResult to visualize
        metrics: Metrics to compare (default: peak, final, mean population)
        show: Whether to display the plot
        save_path: Optional path to save figure
        figsize: Figure size (width, height)
    
    Returns:
        Matplotlib Figure object
    """
    if metrics is None:
        metrics = ['peak_population', 'final_population', 'mean_population']
    
    fig, axes = plt.subplots(1, len(metrics), figsize=figsize)
    if len(metrics) == 1:
        axes = [axes]
    
    x_pos = np.arange(len(comparison.scenario_names))
    
    for i, metric in enumerate(metrics):
        values = []
        for scenario_name in comparison.scenario_names:
            if scenario_name in comparison.comparison:
                values.append(comparison.comparison[scenario_name].get(metric, 0))
            else:
                values.append(0)
        
        axes[i].bar(x_pos, values, alpha=0.7, color=plt.get_cmap('viridis')(np.linspace(0, 1, len(values))))
        axes[i].set_xticks(x_pos)
        axes[i].set_xticklabels(comparison.scenario_names, rotation=45, ha='right')
        axes[i].set_ylabel('Population', fontsize=10)
        axes[i].set_title(metric.replace('_', ' ').title(), fontsize=11, fontweight='bold')
        axes[i].grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add value labels on bars
        for j, v in enumerate(values):
            axes[i].text(j, v, f'{int(v)}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('Scenario Comparison - Key Metrics', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_all_plots(
    result: PopulationResult,
    output_dir: str,
    prefix: str = ""
) -> List[str]:
    """
    Save all population plots to a directory.
    
    Args:
        result: PopulationResult to visualize
        output_dir: Directory to save plots
        prefix: Optional prefix for filenames
    
    Returns:
        List of saved file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    # Evolution plot
    path = output_path / f"{prefix}population_evolution.png"
    plot_population_evolution(result, show=False, save_path=str(path))
    saved_files.append(str(path))
    plt.close()
    
    # Total population
    path = output_path / f"{prefix}population_total.png"
    plot_population_total(result, show=False, save_path=str(path))
    saved_files.append(str(path))
    plt.close()
    
    # Stacked plot
    path = output_path / f"{prefix}population_stacked.png"
    plot_population_stacked(result, show=False, save_path=str(path))
    saved_files.append(str(path))
    plt.close()
    
    return saved_files


def create_report_figure(
    result: PopulationResult,
    show: bool = True,
    save_path: Optional[str] = None
) -> matplotlib.figure.Figure:
    """
    Create comprehensive report figure with all key visualizations.
    
    Args:
        result: PopulationResult to visualize
        show: Whether to display the plot
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib Figure object
    """
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Total population (large, top left)
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    ax1.plot(result.days, result.total_population, linewidth=3, color='purple')
    peak_day = result.statistics['peak_day']
    peak_pop = result.statistics['peak_population']
    ax1.scatter([peak_day], [peak_pop], color='red', s=300, marker='*', zorder=5)
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Total Population')
    ax1.set_title('Total Population Evolution', fontweight='bold', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Individual stages (right column)
    stages_data = [
        ('Eggs', result.eggs, 'blue'),
        ('Larvae', result.larvae, 'green'),
        ('Pupae', result.pupae, 'orange')
    ]
    
    for i, (name, data, color) in enumerate(stages_data):
        ax = fig.add_subplot(gs[i, 2])
        ax.plot(result.days, data, color=color, linewidth=2)
        ax.set_title(name, fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if i == 2:
            ax.set_xlabel('Days', fontsize=9)
    
    # Statistics box (bottom left)
    ax_stats = fig.add_subplot(gs[2, 0:2])
    ax_stats.axis('off')
    
    stats_text = f"""
    SIMULATION STATISTICS
    
    Species: {result.species_id}
    Duration: {int(result.days[-1])} days
    
    Peak Population: {peak_pop} (day {peak_day})
    Final Population: {result.statistics['final_population']}
    Mean Population: {result.statistics['mean_population']:.1f}
    Extinction: {'Yes, day ' + str(result.statistics['extinction_day']) if result.statistics.get('extinction_day') else 'No'}
    """
    
    ax_stats.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                 verticalalignment='center',
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.suptitle(f'Population Simulation Report - {result.species_id}',
                fontsize=16, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig
