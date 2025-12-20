"""
Application Layer - Agent Service
==================================

Service for executing agent-based simulations with Prolog decision-making.

This service creates and manages VectorAgent and PredatorAgent instances
that use Prolog for intelligent decision-making.
"""

from typing import Dict, List, Optional
import numpy as np

from domain.agents.vector_agent import VectorAgent
from domain.agents.predator_agent import PredatorAgent
from domain.agents.base_agent import Action, Perception
from infrastructure.prolog_bridge import PrologBridge
from application.dtos import SimulationConfig, AgentResult


class AgentService:
    """
    Service for agent-based simulations with Prolog integration.
    
    This service creates real VectorAgent and PredatorAgent instances
    that use Prolog for decision-making, providing intelligent behavior
    based on environmental conditions and agent state.
    
    Methods:
        simulate_agents: Execute full agent simulation with Prolog decisions
        get_available_species: List available vector species
        get_available_predators: List available predator species
    """
    
    
    @staticmethod
    def simulate_agents(
        config: SimulationConfig,
        num_predators: int = 0,
        predator_species: str = 'toxorhynchites'
    ) -> AgentResult:
        """
        Execute agent-based simulation with Prolog decision-making.
        
        Creates real VectorAgent and PredatorAgent instances that use
        Prolog to make intelligent decisions based on their state and
        environmental conditions.
        
        Args:
            config: Simulation configuration
            num_predators: Number of predator agents (optional)
            predator_species: Predator species identifier
            
        Returns:
            AgentResult with simulation statistics
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
        
        # Set random seed if provided
        if config.random_seed is not None:
            np.random.seed(config.random_seed)
        
        # Initialize Prolog bridge with config manager
        from application.helpers import get_config_manager
        config_manager = get_config_manager()
        prolog_bridge = PrologBridge(config_manager=config_manager)
        
        # Load species parameters into Prolog
        prolog_bridge.inject_parameters()
        
        # Get environmental parameters (use config values or defaults from environment_config)
        env_config = config_manager.get_environment_config()
        temperature = config.temperature if config.temperature is not None else env_config.temperature
        humidity = config.humidity if config.humidity is not None else env_config.humidity
        
        # Convert humidity to 0-1 scale for Perception (Prolog uses 0-100 internally)
        humidity_normalized = humidity / 100.0
        
        # Create vector agents
        vector_agents = []
        num_vectors_initial = config.initial_adults
        
        for i in range(num_vectors_initial):
            agent = VectorAgent(
                agent_id=f"vector_{i}",
                age=np.random.randint(1, 10),  # Random age 1-10 days
                energy=np.random.uniform(60, 100),  # Initial energy 60-100
                prolog_bridge=prolog_bridge
            )
            vector_agents.append(agent)
        
        # Create predator agents
        predator_agents = []
        num_predators_initial = num_predators
        
        for i in range(num_predators):
            agent = PredatorAgent(
                agent_id=f"predator_{i}",
                stage='larva_L4',  # Predators are L4 larvae
                age=np.random.randint(5, 15),
                energy=np.random.uniform(70, 100),
                prolog_bridge=prolog_bridge
            )
            predator_agents.append(agent)
        
        # Initialize tracking variables
        total_eggs_laid = 0
        total_prey_consumed = 0
        daily_stats = []
        
        # Simulate day by day
        for day in range(config.duration_days + 1):
            # Daily statistics
            daily_stat = {
                'day': day,
                'num_vectors_alive': len([a for a in vector_agents if a.alive]),
                'num_predators_alive': len([a for a in predator_agents if a.alive]),
                'eggs_laid_today': 0,
                'prey_consumed_today': 0,
                'vector_actions': {},
                'predator_actions': {}
            }
            
            if day > 0:  # Skip actions on day 0 (initial state)
                # Vector agents act
                for agent in vector_agents:
                    if not agent.alive:
                        continue
                    
                    # Create perception for agent
                    num_vectors_alive = len([a for a in vector_agents if a.alive])
                    population_density = num_vectors_alive / max(num_vectors_initial, 1)
                    
                    perception = Perception(
                        temperature=temperature,
                        humidity=humidity_normalized,  # 0-1 scale for consistency
                        population_density=population_density,
                        prey_available=0  # Vectors don't track prey
                    )
                    
                    # Agent perceives environment
                    agent.perceive(perception)
                    
                    # Agent decides action using Prolog
                    action = agent.decide_action()
                    
                    # Execute action
                    result = agent.execute_action(action)
                    
                    # Track action
                    action_name = action.value if hasattr(action, 'value') else str(action)
                    daily_stat['vector_actions'][action_name] = \
                        daily_stat['vector_actions'].get(action_name, 0) + 1
                    
                    # Track eggs laid
                    if result.get('success') and result.get('action') == 'oviposit':
                        eggs_today = result.get('eggs_laid', 0)
                        total_eggs_laid += eggs_today
                        daily_stat['eggs_laid_today'] += eggs_today
                    
                    # Age agent
                    agent.age_one_day()
                
                # Predator agents act
                prey_consumed_today = 0
                vectors_to_remove = []
                
                for agent in predator_agents:
                    if not agent.alive:
                        continue
                    
                    # Create perception
                    num_prey = len([a for a in vector_agents if a.alive])
                    num_predators_alive = len([a for a in predator_agents if a.alive])
                    population_density = num_predators_alive / max(num_predators_initial, 1)
                    
                    perception = Perception(
                        temperature=temperature,
                        humidity=humidity_normalized,
                        population_density=population_density,
                        prey_available=num_prey
                    )
                    
                    # Agent perceives and decides
                    agent.perceive(perception)
                    action = agent.decide_action()
                    
                    # Execute action
                    result = agent.execute_action(action)
                    
                    # Track action
                    action_name = action.value if hasattr(action, 'value') else str(action)
                    daily_stat['predator_actions'][action_name] = \
                        daily_stat['predator_actions'].get(action_name, 0) + 1
                    
                    # Track prey consumed
                    if result.get('success') and result.get('action') == 'hunt':
                        prey_count = result.get('prey_consumed', 0)
                        prey_consumed_today += prey_count
                        
                        # Mark random vectors as consumed
                        alive_vectors = [a for a in vector_agents if a.alive]
                        for _ in range(min(prey_count, len(alive_vectors))):
                            if alive_vectors:
                                victim = np.random.choice(alive_vectors)
                                victim.die("predated")
                                alive_vectors.remove(victim)
                    
                    # Age agent
                    agent.age_one_day()
                
                total_prey_consumed += prey_consumed_today
                daily_stat['prey_consumed_today'] = prey_consumed_today
            
            daily_stats.append(daily_stat)
        
        # Count final living agents
        num_vectors_final = len([a for a in vector_agents if a.alive])
        num_predators_final = len([a for a in predator_agents if a.alive])
        
        # Build result DTO
        result = AgentResult(
            num_vectors_initial=num_vectors_initial,
            num_predators_initial=num_predators_initial,
            num_vectors_final=num_vectors_final,
            num_predators_final=num_predators_final,
            total_eggs_laid=total_eggs_laid,
            total_prey_consumed=total_prey_consumed,
            daily_stats=daily_stats
        )
        
        return result
    
    @staticmethod
    def get_available_species() -> List[str]:
        """
        Get list of available vector species.
        
        Returns:
            List of species identifiers
        """
        from application.helpers import get_config_manager
        config_manager = get_config_manager()
        return config_manager.get_all_species_ids()
    
    @staticmethod
    def get_available_predators() -> List[str]:
        """
        Get list of available predator species.
        
        Returns:
            List of predator identifiers
        """
        from application.helpers import get_config_manager
        config_manager = get_config_manager()
        
        predators = []
        for species_id in config_manager.get_all_species_ids():
            try:
                species_config = config_manager.get_species_config(species_id)
                # Check if any life stage is predatory
                if any(stage.is_predatory for stage in species_config.life_stages.values()):
                    predators.append(species_id)
            except Exception:
                continue
        
        return predators
