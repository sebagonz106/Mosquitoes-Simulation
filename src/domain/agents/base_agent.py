"""
Base Agent Module
=================

Abstract base agent that integrates with Prolog for decision-making.
All agent logic resides in Prolog; Python only orchestrates.

Author: Mosquito Simulation System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from infrastructure.prolog_bridge import PrologBridge


class Action(Enum):
    """Agent actions (defined in agent_decisions.pl)."""
    OVIPOSIT = "oviposit"
    FEED = "feed"
    REST = "rest"
    HUNT = "hunt"
    GROW = "grow"
    DIE = "die"


@dataclass
class Perception:
    """
    Agent perception of environment.
    
    Attributes:
        temperature: Current temperature (°C)
        humidity: Current humidity (%)
        population_density: Population density ratio [0-1]
        prey_available: Number of prey available (for predators)
    """
    temperature: float
    humidity: float
    population_density: float
    prey_available: int = 0


@dataclass
class AgentState:
    """
    Internal agent state (synchronized with Prolog).
    
    Attributes:
        agent_id: Unique agent identifier
        species: Species identifier
        stage: Life stage
        age: Age in days
        energy: Energy level [0-100]
        reproduced: Whether agent has reproduced
    """
    agent_id: str
    species: str
    stage: str
    age: int
    energy: float
    reproduced: bool


class BaseAgent(ABC):
    """
    Abstract base agent with Prolog integration.
    
    This class provides the interface between Python and Prolog agents.
    All decision logic is in Prolog; Python queries and executes.
    
    Attributes:
        state: Current agent state
        prolog: PrologBridge for querying decisions
        alive: Whether agent is alive
    """
    
    def __init__(
        self,
        agent_id: str,
        species: str,
        stage: str,
        age: int,
        energy: float,
        prolog_bridge: PrologBridge
    ):
        """
        Initialize agent and register in Prolog.
        
        Args:
            agent_id: Unique identifier
            species: Species identifier (e.g., 'aedes_aegypti')
            stage: Life stage (e.g., 'adult_female')
            age: Initial age in days
            energy: Initial energy level
            prolog_bridge: Prolog inference engine
        """
        self.state = AgentState(
            agent_id=agent_id,
            species=species,
            stage=stage,
            age=age,
            energy=energy,
            reproduced=False
        )
        self.prolog = prolog_bridge
        self.alive = True
        
        # Register agent in Prolog
        self._initialize_in_prolog()
    
    def _initialize_in_prolog(self) -> None:
        """Initialize agent state in Prolog knowledge base."""
        query = (
            f"initialize_agent("
            f"'{self.state.agent_id}', "
            f"{self.state.species}, "
            f"{self.state.stage}, "
            f"{self.state.age}, "
            f"{self.state.energy})"
        )
        try:
            list(self.prolog.query(query))
        except Exception as e:
            # If Prolog predicate not available, continue without it
            pass
    
    def _sync_state_to_prolog(self) -> None:
        """Synchronize Python state to Prolog."""
        query = (
            f"update_agent_state("
            f"'{self.state.agent_id}', "
            f"{self.state.stage}, "
            f"{self.state.age}, "
            f"{self.state.energy}, "
            f"{'true' if self.state.reproduced else 'false'})"
        )
        try:
            list(self.prolog.query(query))
        except Exception:
            pass
    
    def _sync_state_from_prolog(self) -> None:
        """Synchronize Prolog state to Python."""
        query = f"agent_state('{self.state.agent_id}', Stage, Age, Energy, Reproduced)"
        try:
            results = list(self.prolog.query(query))
            if results:
                result = results[0]
                self.state.stage = str(result.get('Stage', self.state.stage))
                self.state.age = int(result.get('Age', self.state.age))
                self.state.energy = float(result.get('Energy', self.state.energy))
                reproduced_val = result.get('Reproduced', 'false')
                self.state.reproduced = str(reproduced_val).lower() == 'true'
        except Exception:
            pass
    
    def perceive(self, perception: Perception) -> None:
        """
        Update environmental perceptions in Prolog.
        
        Args:
            perception: Environmental perception data
        """
        # Update dynamic facts in Prolog
        queries = [
            f"retractall(current_temperature(_)), assertz(current_temperature({perception.temperature}))",
            f"retractall(current_humidity(_)), assertz(current_humidity({perception.humidity}))",
            f"retractall(current_population({self.state.species}, _)), "
            f"assertz(current_population({self.state.species}, {int(perception.population_density * 10000)}))"
        ]
        
        if perception.prey_available > 0:
            queries.append(
                f"retractall(current_population(aedes_aegypti, _)), "
                f"assertz(current_population(aedes_aegypti, {perception.prey_available}))"
            )
        
        for query in queries:
            try:
                list(self.prolog.query(query))
            except Exception:
                pass
    
    def decide_action(self) -> Action:
        """
        Query Prolog for best action decision.
        
        Returns:
            Action to execute (determined by Prolog)
        """
        if not self.alive:
            return Action.DIE
        
        # Query Prolog for best action
        query = f"best_action('{self.state.agent_id}', BestAction)"
        try:
            results = list(self.prolog.query(query))
            if results:
                action_str = str(results[0].get('BestAction', 'rest'))
                return self._parse_action(action_str)
        except Exception:
            pass
        
        # Fallback: query simple decision
        query = f"decide_action('{self.state.agent_id}', Action)"
        try:
            results = list(self.prolog.query(query))
            if results:
                action_str = str(results[0].get('Action', 'rest'))
                return self._parse_action(action_str)
        except Exception:
            pass
        
        return Action.REST
    
    def _parse_action(self, action_str: str) -> Action:
        """Parse action string from Prolog to Action enum."""
        action_map = {
            'oviposit': Action.OVIPOSIT,
            'feed': Action.FEED,
            'rest': Action.REST,
            'hunt': Action.HUNT,
            'grow': Action.GROW,
            'die': Action.DIE
        }
        return action_map.get(action_str.lower(), Action.REST)
    
    def calculate_utility(self, action: Action) -> float:
        """
        Query Prolog for action utility.
        
        Args:
            action: Action to evaluate
        
        Returns:
            Utility value calculated by Prolog
        """
        query = f"utility('{self.state.agent_id}', {action.value}, Utility)"
        try:
            results = list(self.prolog.query(query))
            if results:
                return float(results[0].get('Utility', 0.0))
        except Exception:
            pass
        return 0.0
    
    @abstractmethod
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """
        Execute selected action and update state.
        
        Args:
            action: Action to execute
        
        Returns:
            Dictionary with action results
        """
        pass
    
    def age_one_day(self) -> None:
        """Age agent by one day and update energy."""
        if self.alive:
            self.state.age += 1
            self.state.energy = max(0, self.state.energy - 2)  # Daily energy decay
            
            if self.state.energy <= 0:
                self.die("energy_depletion")
            
            self._sync_state_to_prolog()
    
    def die(self, cause: str = "natural") -> None:
        """
        Mark agent as dead and remove from Prolog.
        
        Args:
            cause: Cause of death
        """
        self.alive = False
        
        # Remove from Prolog
        query = f"remove_agent('{self.state.agent_id}')"
        try:
            list(self.prolog.query(query))
        except Exception:
            pass
    
    def get_perceptions(self) -> List[str]:
        """
        Query Prolog for agent's current perceptions.
        
        Returns:
            List of perception descriptions
        """
        query = f"perceive('{self.state.agent_id}', Perception)"
        perceptions = []
        try:
            results = list(self.prolog.query(query))
            for result in results:
                perception = result.get('Perception')
                if perception:
                    perceptions.append(str(perception))
        except Exception:
            pass
        return perceptions
    
    def __repr__(self) -> str:
        """String representation."""
        status = "alive" if self.alive else "dead"
        return (
            f"{self.__class__.__name__}(id='{self.state.agent_id}', "
            f"species={self.state.species}, stage={self.state.stage}, "
            f"age={self.state.age}d, energy={self.state.energy:.1f}, {status})"
        )
