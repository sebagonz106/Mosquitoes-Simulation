"""
Predator Agent Module
=====================

Toxorhynchites predatory larva agent.
All decision logic in Prolog (agent_decisions.pl).

Author: Mosquito Simulation System
"""

from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from domain.agents.base_agent import BaseAgent, Action, Perception
from infrastructure.prolog_bridge import PrologBridge


class PredatorAgent(BaseAgent):
    """
    Toxorhynchites predatory larva agent.
    
    Behavior defined in Prolog:
    - Hunting decisions based on energy and prey availability
    - Growth/metamorphosis when energy is sufficient
    - Resting to conserve energy
    
    Python only executes actions determined by Prolog logic.
    
    Attributes:
        prey_consumed: Total prey consumed
        growth_stage: Current growth substage
    """
    
    def __init__(
        self,
        agent_id: str,
        stage: str,
        age: int,
        energy: float,
        prolog_bridge: PrologBridge
    ):
        """
        Initialize predator agent.
        
        Args:
            agent_id: Unique identifier
            stage: Life stage (e.g., 'larva_L3', 'larva_L4')
            age: Initial age in days
            energy: Initial energy level
            prolog_bridge: Prolog inference engine
        """
        super().__init__(
            agent_id=agent_id,
            species='toxorhynchites',
            stage=stage,
            age=age,
            energy=energy,
            prolog_bridge=prolog_bridge
        )
        
        self.prey_consumed = 0
        self.growth_stage = 0
    
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """
        Execute action determined by Prolog.
        
        Args:
            action: Action selected by Prolog decision rules
        
        Returns:
            Dictionary with action results
        """
        if action == Action.HUNT:
            return self._execute_hunt()
        elif action == Action.GROW:
            return self._execute_grow()
        elif action == Action.REST:
            return self._execute_rest()
        elif action == Action.DIE:
            self.die("executed_die_action")
            return {'action': 'die', 'success': True}
        else:
            return {'action': action.value, 'success': False, 'reason': 'unknown_action'}
    
    def _execute_hunt(self) -> Dict[str, Any]:
        """
        Execute hunting/predation.
        
        Prolog determines IF to hunt.
        Python executes HOW: energy cost, prey consumption, state update.
        
        Returns:
            Dict with prey_consumed, energy_gained, success
        """
        if not self.alive:
            return {'action': 'hunt', 'success': False, 'reason': 'dead'}
        
        # Energy cost from Prolog
        energy_cost = self._get_action_cost(Action.HUNT)
        
        if self.state.energy < energy_cost:
            return {'action': 'hunt', 'success': False, 'reason': 'insufficient_energy'}
        
        # Query Prolog for predation rate
        predation_query = f"predation_rate({self.state.species}, {self.state.stage}, Rate)"
        try:
            results = list(self.prolog.query(predation_query))
            if results:
                prey_count = int(results[0].get('Rate', 1))
            else:
                prey_count = 1  # Default
        except Exception:
            prey_count = 1
        
        # Execute hunting
        energy_from_prey = prey_count * 25.0  # Energy per prey
        self.state.energy = min(100, self.state.energy - energy_cost + energy_from_prey)
        self.prey_consumed += prey_count
        
        self._sync_state_to_prolog()
        
        return {
            'action': 'hunt',
            'success': True,
            'prey_consumed': prey_count,
            'energy_gained': energy_from_prey - energy_cost,
            'total_prey': self.prey_consumed
        }
    
    def _execute_grow(self) -> Dict[str, Any]:
        """
        Execute growth/metamorphosis.
        
        Returns:
            Dict with new_stage, success
        """
        if not self.alive:
            return {'action': 'grow', 'success': False, 'reason': 'dead'}
        
        energy_cost = self._get_action_cost(Action.GROW)
        
        if self.state.energy < energy_cost:
            return {'action': 'grow', 'success': False, 'reason': 'insufficient_energy'}
        
        # Advance growth stage
        old_stage = self.state.stage
        self.growth_stage += 1
        
        # Query Prolog for stage progression
        stage_query = f"next_stage({self.state.species}, {old_stage}, NextStage)"
        try:
            results = list(self.prolog.query(stage_query))
            if results:
                self.state.stage = str(results[0].get('NextStage', old_stage))
        except Exception:
            # Simple stage advancement
            if 'L3' in old_stage:
                self.state.stage = old_stage.replace('L3', 'L4')
            elif 'L4' in old_stage:
                self.state.stage = 'pupa'
        
        self.state.energy -= energy_cost
        
        self._sync_state_to_prolog()
        
        return {
            'action': 'grow',
            'success': True,
            'old_stage': old_stage,
            'new_stage': self.state.stage,
            'energy_cost': energy_cost
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
        energy_recovery = 2.0
        
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
            Action.HUNT: 15.0,
            Action.GROW: 5.0,
            Action.REST: 1.0
        }
        return defaults.get(action, 1.0)
    
    def is_predatory_stage(self) -> bool:
        """
        Query Prolog if current stage is predatory.
        
        Returns:
            True if Prolog rules indicate predatory stage
        """
        query = f"predatory_stage({self.state.species}, {self.state.stage})"
        try:
            results = list(self.prolog.query(query))
            return len(results) > 0
        except Exception:
            return 'larva' in self.state.stage.lower()
    
    def can_hunt(self, prey_available: int) -> bool:
        """
        Query Prolog if agent can hunt given prey availability.
        
        Args:
            prey_available: Number of prey in environment
        
        Returns:
            True if Prolog rules allow hunting
        """
        if not self.alive or prey_available <= 0:
            return False
        
        # Query Prolog decision
        query = f"decide_action('{self.state.agent_id}', hunt)"
        try:
            results = list(self.prolog.query(query))
            return len(results) > 0
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        base = super().__repr__()
        return f"{base[:-1]}, prey_consumed={self.prey_consumed}, growth={self.growth_stage})"
