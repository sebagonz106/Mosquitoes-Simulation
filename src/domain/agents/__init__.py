"""
Domain Agents Module
====================

Agent-based simulation components. All decision logic resides in Prolog,
Python agents are thin wrappers that query Prolog and execute actions.

Architecture:
- Prolog (.pl files): Contains all agent decision logic and rules
- Python (.py files): Query Prolog, process results, execute actions

Modules:
    - base_agent: Abstract base agent with Prolog integration
    - vector_agent: Aedes aegypti female adult agents
    - predator_agent: Toxorhynchites predatory larva agents
"""

from .base_agent import BaseAgent, AgentState, Perception, Action
from .vector_agent import VectorAgent
from .predator_agent import PredatorAgent

__all__ = [
    'BaseAgent',
    'AgentState',
    'Perception',
    'Action',
    'VectorAgent',
    'PredatorAgent'
]
