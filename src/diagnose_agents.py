"""
Diagnostic test for Prolog-Python state synchronization
========================================================

This test diagnoses the state synchronization issue between Python and Prolog.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from infrastructure.config import ConfigManager
from infrastructure.prolog_bridge import PrologBridge
from domain.agents import VectorAgent, Perception


def diagnose_state_sync():
    """Diagnose state synchronization between Python and Prolog."""
    print("="*60)
    print("DIAGNOSTIC: State Synchronization")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    # Create agent
    agent = VectorAgent(
        agent_id='diag_001',
        age=5,
        energy=80.0,
        prolog_bridge=prolog
    )
    
    print("\n1. Initial state in Python:")
    print(f"   Energy: {agent.state.energy}")
    print(f"   Reproduced: {agent.state.reproduced}")
    
    # Check Prolog state
    print("\n2. Initial state in Prolog:")
    query = f"agent_state('{agent.state.agent_id}', Stage, Age, Energy, Reproduced)"
    results = list(prolog.query(query))
    if results:
        result = results[0]
        print(f"   Stage: {result.get('Stage')}")
        print(f"   Age: {result.get('Age')}")
        print(f"   Energy: {result.get('Energy')}")
        print(f"   Reproduced: {result.get('Reproduced')}")
    else:
        print("   ERROR: No state found in Prolog!")
    
    # Set up environment
    try:
        list(prolog.query("assertz(suitable_oviposition_site_available)"))
    except:
        pass
    
    perception = Perception(temperature=26.0, humidity=80.0, population_density=0.3)
    agent.perceive(perception)
    
    # Scenario 1: Check decision with high energy
    print("\n3. TEST: High energy (80.0), not reproduced")
    print("   Checking decide_action directly in Prolog:")
    query = f"decide_action('{agent.state.agent_id}', Action)"
    results = list(prolog.query(query))
    print(f"   Prolog results: {[r.get('Action') for r in results]}")
    
    # Now change energy to low
    print("\n4. TEST: Changing energy to 25.0 (LOW)")
    agent.state.energy = 25.0
    print(f"   Python energy: {agent.state.energy}")
    
    # Sync to Prolog
    agent._sync_state_to_prolog()
    
    # Check if it actually updated
    print("\n5. Checking Prolog state AFTER sync:")
    query = f"agent_state('{agent.state.agent_id}', Stage, Age, Energy, Reproduced)"
    results = list(prolog.query(query))
    if results:
        result = results[0]
        prolog_energy = result.get('Energy')
        print(f"   Prolog Energy: {prolog_energy}")
        print(f"   Python Energy: {agent.state.energy}")
        print(f"   MATCH: {float(prolog_energy if prolog_energy else 0) == agent.state.energy}")
    
    # Now check decision rules
    print("\n6. Checking which decide_action rules match:")
    
    # Rule for feed (Energy < 40)
    query = f"decide_action('{agent.state.agent_id}', feed)"
    results = list(prolog.query(query))
    print(f"   decide_action(..., feed): {len(results) > 0} ({len(results)} results)")
    
    # Rule for oviposit (Energy > 50)
    query = f"decide_action('{agent.state.agent_id}', oviposit)"
    results = list(prolog.query(query))
    print(f"   decide_action(..., oviposit): {len(results) > 0} ({len(results)} results)")
    
    # Rule for rest
    query = f"decide_action('{agent.state.agent_id}', rest)"
    results = list(prolog.query(query))
    print(f"   decide_action(..., rest): {len(results) > 0} ({len(results)} results)")
    
    # Check all actions
    print("\n7. Checking ALL possible actions:")
    query = f"decide_action('{agent.state.agent_id}', Action)"
    results = list(prolog.query(query))
    for result in results:
        print(f"   - {result.get('Action')}")
    
    # Test best_action
    print("\n8. Testing best_action (with utilities):")
    query = f"best_action('{agent.state.agent_id}', BestAction)"
    results = list(prolog.query(query))
    if results:
        print(f"   Best action: {results[0].get('BestAction')}")
    else:
        print("   ERROR: No best action found!")
    
    # Check energy condition directly
    print("\n9. Direct energy check in Prolog:")
    query = f"agent_state('{agent.state.agent_id}', _, _, Energy, _), Energy < 40"
    results = list(prolog.query(query))
    print(f"   Energy < 40: {len(results) > 0}")
    
    query = f"agent_state('{agent.state.agent_id}', _, _, Energy, _), Energy > 50"
    results = list(prolog.query(query))
    print(f"   Energy > 50: {len(results) > 0}")


if __name__ == "__main__":
    diagnose_state_sync()
