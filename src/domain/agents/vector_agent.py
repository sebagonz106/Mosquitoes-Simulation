"""
Vector Agent Module
===================

Aedes aegypti female adult agent with reproductive behavior.
All decision logic in Prolog (agent_decisions.pl).

Author: Mosquito Simulation System
"""

from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from domain.agents.base_agent import BaseAgent, Action, Perception
from infrastructure.prolog_bridge import PrologBridge


class VectorAgent(BaseAgent):
    """
    Aedes aegypti female adult agent.
    
    Behavior defined in Prolog:
    - Oviposition decisions based on humidity, energy, age
    - Feeding behavior when energy is low
    - Resting to conserve energy
    
    Python only executes actions determined by Prolog logic.
    
    Attributes:
        eggs_laid: Total eggs laid by this agent
        blood_meals: Number of blood meals taken
    """
    
    def __init__(
        self,
        agent_id: str,
        age: int,
        energy: float,
        prolog_bridge: PrologBridge
    ):
        """
        Initialize vector agent.
        
        Args:
            agent_id: Unique identifier
            age: Initial age in days
            energy: Initial energy level
            prolog_bridge: Prolog inference engine
        """
        super().__init__(
            agent_id=agent_id,
            species='aedes_aegypti',
            stage='adult_female',
            age=age,
            energy=energy,
            prolog_bridge=prolog_bridge
        )
        
        self.eggs_laid = 0
        self.blood_meals = 0
    
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """
        Execute action determined by Prolog.
        
        Args:
            action: Action selected by Prolog decision rules
        
        Returns:
            Dictionary with action results
        """
        if action == Action.OVIPOSIT:
            return self._execute_oviposit()
        elif action == Action.FEED:
            return self._execute_feed()
        elif action == Action.REST:
            return self._execute_rest()
        elif action == Action.DIE:
            self.die("executed_die_action")
            return {'action': 'die', 'success': True}
        else:
            return {'action': action.value, 'success': False, 'reason': 'unknown_action'}
    
    def _execute_oviposit(self) -> Dict[str, Any]:
        """
        Execute oviposition (egg laying).
        
        Prolog determines IF to oviposit.
        Python executes HOW: energy cost, egg count, state update.
        
        Returns:
            Dict with eggs_laid, energy_cost, success
        """
        if not self.alive or self.state.reproduced:
            return {'action': 'oviposit', 'success': False, 'reason': 'cannot_reproduce'}
        
        # Energy cost from Prolog
        energy_cost = self._get_action_cost(Action.OVIPOSIT)
        
        if self.state.energy < energy_cost:
            return {'action': 'oviposit', 'success': False, 'reason': 'insufficient_energy'}
        
        # Query Prolog for eggs per batch
        eggs_query = f"eggs_per_batch_range({self.state.species}, Min, Max)"
        try:
            results = list(self.prolog.query(eggs_query))
            if results:
                min_eggs = int(results[0].get('Min', 80))
                max_eggs = int(results[0].get('Max', 150))
                import random
                eggs = random.randint(min_eggs, max_eggs)
            else:
                eggs = 100  # Default
        except Exception:
            eggs = 100
        
        # Execute oviposition
        self.state.energy -= energy_cost
        self.state.reproduced = True
        self.eggs_laid += eggs
        
        self._sync_state_to_prolog()
        
        return {
            'action': 'oviposit',
            'success': True,
            'eggs_laid': eggs,
            'energy_cost': energy_cost,
            'total_eggs': self.eggs_laid
        }
    
    def _execute_feed(self) -> Dict[str, Any]:
        """
        Execute blood meal feeding.
        
        Returns:
            Dict with energy_gained, success
        """
        if not self.alive:
            return {'action': 'feed', 'success': False, 'reason': 'dead'}
        
        energy_cost = self._get_action_cost(Action.FEED)
        
        # Blood meal provides energy
        energy_gain = 40.0  # Could be queried from Prolog
        
        self.state.energy = min(100, self.state.energy - energy_cost + energy_gain)
        self.blood_meals += 1
        
        self._sync_state_to_prolog()
        
        return {
            'action': 'feed',
            'success': True,
            'energy_gained': energy_gain - energy_cost,
            'total_meals': self.blood_meals
        }
    
    def _execute_rest(self) -> Dict[str, Any]:
        """
        Execute resting behavior.
        
        Returns:
            Dict with energy_recovered, success
        """
        if not self.alive:
            return {'action': 'rest', 'success': False, 'reason': 'dead'}
        
        energy_cost = self._get_action_cost(Action.REST)
        energy_recovery = 3.0
        
        self.state.energy = min(100, self.state.energy - energy_cost + energy_recovery)
        
        self._sync_state_to_prolog()
        
        return {
            'action': 'rest',
            'success': True,
            'energy_recovered': energy_recovery - energy_cost
        }
    
    def _get_action_cost(self, action: Action) -> float:
        """
        Query Prolog for action energy cost.
        
        Args:
            action: Action to query
        
        Returns:
            Energy cost from Prolog or default
        """
        query = f"action_energy_cost({action.value}, Cost)"
        try:
            results = list(self.prolog.query(query))
            if results:
                return float(results[0].get('Cost', 1.0))
        except Exception:
            pass
        
        # Defaults if Prolog query fails
        defaults = {
            Action.OVIPOSIT: 20.0,
            Action.FEED: 10.0,
            Action.REST: 1.0
        }
        return defaults.get(action, 1.0)
    
    def can_reproduce(self) -> bool:
        """
        Query Prolog if agent can reproduce.
        
        Returns:
            True if Prolog rules allow reproduction
        """
        if not self.alive or self.state.reproduced:
            return False
        
        # Query Prolog decision
        query = f"decide_action('{self.state.agent_id}', oviposit)"
        try:
            results = list(self.prolog.query(query))
            return len(results) > 0
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        base = super().__repr__()
        return f"{base[:-1]}, eggs={self.eggs_laid}, meals={self.blood_meals})"
