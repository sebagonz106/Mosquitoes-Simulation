"""
Application Layer - Simulation Service
=======================================

High-level orchestration service for population and agent-based simulations.

This service provides:
- Unified interface for different simulation types
- Checkpoint management (save/load simulation states)
- Scenario comparison capabilities
- Automatic checkpointing during long simulations
"""

from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import json

from application.dtos import (
    SimulationConfig,
    PopulationResult,
    AgentResult,
    HybridResult,
    ComparisonResult
)
from application.services.population_service import PopulationService
from application.services.agent_service import AgentService


class SimulationService:
    """
    Orchestration service for mosquito population simulations.
    
    Manages execution of population-based and agent-based simulations,
    provides checkpointing capabilities, and enables scenario comparisons.
    
    Methods:
        run_population_simulation: Execute population dynamics simulation
        run_agent_simulation: Execute agent-based simulation
        run_hybrid_simulation: Run both approaches and compare
        compare_scenarios: Compare multiple simulation scenarios
        save_checkpoint: Save simulation state to disk
        load_checkpoint: Load simulation state from disk
        list_checkpoints: List available checkpoint files
    """
    
    def __init__(self, checkpoint_dir: Optional[Union[str, Path]] = None):
        """
        Initialize simulation service.
        
        Args:
            checkpoint_dir: Directory for checkpoint files (default: ./checkpoints)
        """
        if checkpoint_dir is None:
            # Default to checkpoints directory in project root
            project_root = Path(__file__).parent.parent.parent.parent
            checkpoint_dir = project_root / "checkpoints"
        
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def run_population_simulation(config: SimulationConfig) -> PopulationResult:
        """
        Execute population dynamics simulation.
        
        Uses mathematical models (Leslie matrix, differential equations) to
        simulate population evolution over time.
        
        Args:
            config: Simulation configuration
            
        Returns:
            PopulationResult with temporal trajectories
            
        Raises:
            ValueError: If configuration is invalid
        """
        return PopulationService.simulate(config)
    
    @staticmethod
    def run_agent_simulation(
        config: SimulationConfig,
        num_predators: int = 0,
        predator_species: str = 'toxorhynchites'
    ) -> AgentResult:
        """
        Execute agent-based simulation with Prolog decisions.
        
        Creates individual agents that make intelligent decisions based
        on environmental conditions and internal state.
        
        Args:
            config: Simulation configuration
            num_predators: Number of predator agents
            predator_species: Predator species identifier
            
        Returns:
            AgentResult with individual agent statistics
            
        Raises:
            ValueError: If configuration is invalid
        """
        return AgentService.simulate_agents(
            config=config,
            num_predators=num_predators,
            predator_species=predator_species
        )
    
    @staticmethod
    def run_hybrid_simulation(
        config: SimulationConfig,
        num_predators: int = 0,
        predator_species: str = 'toxorhynchites'
    ) -> HybridResult:
        """
        Run both population and agent simulations in parallel for comparison.
        
        Executes both approaches independently with the same configuration
        and returns results for comparison.
        
        Args:
            config: Simulation configuration (same for both)
            num_predators: Number of predators for agent simulation
            predator_species: Predator species identifier
            
        Returns:
            HybridResult containing both simulation results and comparison data
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Run population simulation
        pop_result = PopulationService.simulate(config)
        
        # Run agent simulation with same config
        agent_result = AgentService.simulate_agents(
            config=config,
            num_predators=num_predators,
            predator_species=predator_species
        )
        
        # Get standardized statistics for comparison
        pop_stats = pop_result.statistics
        agent_stats = agent_result.get_statistics()
        
        # Calculate comparative metrics using standardized keys
        comparison = {
            'approach': 'hybrid_comparison',
            'config': config.to_dict(),
            'population_model': {
                'final_population': pop_stats['final_population'],
                'peak_population': pop_stats['peak_population'],
                'peak_day': pop_stats['peak_day'],
                'mean_population': pop_stats['mean_total'],
                'extinction_day': pop_stats.get('extinction_day')
            },
            'agent_model': {
                'final_population': agent_stats['final_population'],
                'peak_population': agent_stats['peak_population'],
                'peak_day': agent_stats['peak_day'],
                'mean_population': agent_stats['mean_population'],
                'extinction_day': agent_stats.get('extinction_day'),
                'survival_rate': agent_stats['vector_survival_rate'],
                'total_eggs': agent_stats['total_eggs'],
                'avg_eggs_per_vector': agent_stats['avg_eggs_per_vector']
            },
            'differences': {
                'final_population_diff': agent_stats['final_population'] - pop_stats['final_population'],
                'peak_population_diff': agent_stats['peak_population'] - pop_stats['peak_population'],
                'mean_population_diff': agent_stats['mean_population'] - pop_stats['mean_total'],
                'notes': [
                    f"Population model: {pop_stats['final_population']} final individuals",
                    f"Agent model: {agent_stats['final_population']} final individuals",
                    f"Difference: {agent_stats['final_population'] - pop_stats['final_population']} individuals"
                ]
            }
        }
        
        return HybridResult(
            population_result=pop_result,
            agent_result=agent_result,
            comparison_data=comparison
        )
    
    @staticmethod
    def compare_scenarios(
        scenarios: Dict[str, SimulationConfig],
        simulation_type: str = 'population'
    ) -> ComparisonResult:
        """
        Compare multiple simulation scenarios.
        
        Runs simulations for each scenario and compares results using
        key metrics like peak population, final population, etc.
        
        Args:
            scenarios: Dict mapping scenario names to configurations
            simulation_type: 'population' or 'agent'
            
        Returns:
            ComparisonResult with comparative analysis
            
        Raises:
            ValueError: If simulation_type is invalid
        """
        if simulation_type not in ['population', 'agent']:
            raise ValueError("simulation_type must be 'population' or 'agent'")
        
        results = {}
        comparison_data = {}
        
        for scenario_name, config in scenarios.items():
            if simulation_type == 'population':
                result = PopulationService.simulate(config)
                results[scenario_name] = result
                # Use standardized statistics keys
                comparison_data[scenario_name] = {
                    'final_population': result.statistics['final_population'],
                    'peak_population': result.statistics['peak_population'],
                    'mean_population': result.statistics['mean_total'],
                    'peak_day': result.statistics['peak_day'],
                    'extinction_day': result.statistics.get('extinction_day')
                }
            else:
                result = AgentService.simulate_agents(config)
                results[scenario_name] = result
                # Use standardized statistics method
                agent_stats = result.get_statistics()
                comparison_data[scenario_name] = {
                    'final_population': agent_stats['final_population'],
                    'peak_population': agent_stats['peak_population'],
                    'mean_population': agent_stats['mean_population'],
                    'peak_day': agent_stats['peak_day'],
                    'extinction_day': agent_stats.get('extinction_day'),
                    # Additional agent-specific metrics
                    'survival_rate': agent_stats['vector_survival_rate'],
                    'total_eggs': agent_stats['total_eggs'],
                    'avg_eggs_per_vector': agent_stats['avg_eggs_per_vector']
                }
        
        return ComparisonResult(
            scenario_names=list(scenarios.keys()),
            results=results,
            comparison=comparison_data
        )
    
    def save_checkpoint(
        self,
        result: Union[PopulationResult, AgentResult, HybridResult],
        config: SimulationConfig,
        simulation_type: str,
        checkpoint_name: Optional[str] = None
    ) -> Path:
        """
        Save simulation state to checkpoint file.
        
        Args:
            result: Simulation result to save (PopulationResult, AgentResult, or HybridResult)
            config: Configuration used
            simulation_type: 'population', 'agent', or 'hybrid'
            checkpoint_name: Custom name (default: auto-generated)
            
        Returns:
            Path to saved checkpoint file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Add microseconds for uniqueness
        
        if checkpoint_name is None:
            checkpoint_name = f"checkpoint_{simulation_type}_{config.species_id}_{config.duration_days}days_{timestamp}.json"
        
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        
        # If file exists, append counter to make it unique
        counter = 1
        while checkpoint_path.exists():
            base_name = checkpoint_name.rsplit('.', 1)[0]
            checkpoint_name = f"{base_name}_{counter}.json"
            checkpoint_path = self.checkpoint_dir / checkpoint_name
            counter += 1
        
        # Prepare checkpoint data
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'simulation_type': simulation_type,
            'config': config.to_dict(),
            'result': result.to_dict(),
            'metadata': {
                'version': '1.0',
                'species': config.species_id,
                'duration': config.duration_days
            }
        }
        
        # Save to JSON
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        return checkpoint_path
    
    def load_checkpoint(self, checkpoint_path: Union[str, Path]) -> Tuple[SimulationConfig, Union[PopulationResult, AgentResult, HybridResult], str]:
        """
        Load simulation state from checkpoint file.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            Tuple of (config, result, simulation_type) where result can be
            PopulationResult, AgentResult, or HybridResult
            
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
            ValueError: If checkpoint format is invalid
        """
        checkpoint_path = Path(checkpoint_path)
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        # Load from JSON
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        # Validate format
        required_keys = ['simulation_type', 'config', 'result']
        if not all(key in checkpoint_data for key in required_keys):
            raise ValueError("Invalid checkpoint format")
        
        # Reconstruct objects
        config = SimulationConfig.from_dict(checkpoint_data['config'])
        simulation_type = checkpoint_data['simulation_type']
        
        if simulation_type == 'population':
            result = PopulationResult.from_dict(checkpoint_data['result'])
        elif simulation_type == 'agent':
            result = AgentResult.from_dict(checkpoint_data['result'])
        elif simulation_type == 'hybrid':
            result = HybridResult.from_dict(checkpoint_data['result'])
        else:
            raise ValueError(f"Unknown simulation type: {simulation_type}")
        
        return config, result, simulation_type
    
    def list_checkpoints(
        self,
        species: Optional[str] = None,
        simulation_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List available checkpoint files.
        
        Args:
            species: Filter by species (optional)
            simulation_type: Filter by type (optional)
            
        Returns:
            List of checkpoint metadata dicts
        """
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Apply filters
                if species and data.get('metadata', {}).get('species') != species:
                    continue
                
                if simulation_type and data.get('simulation_type') != simulation_type:
                    continue
                
                checkpoints.append({
                    'filename': checkpoint_file.name,
                    'path': str(checkpoint_file),
                    'timestamp': data.get('timestamp'),
                    'species': data.get('metadata', {}).get('species'),
                    'duration': data.get('metadata', {}).get('duration'),
                    'simulation_type': data.get('simulation_type')
                })
            except Exception:
                continue  # Skip invalid files
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return checkpoints
    
    @staticmethod
    def get_available_species() -> List[str]:
        """Get list of available species."""
        return PopulationService.get_available_species()
    
    @staticmethod
    def get_available_predators() -> List[str]:
        """Get list of available predator species."""
        return AgentService.get_available_predators()
