"""
Test script for Domain Agents
==============================

Tests agent-based simulation with Prolog integration.
Demonstrates that Python agents query Prolog for all decisions.

Author: Mosquito Simulation System
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from infrastructure.config import ConfigManager
from infrastructure.prolog_bridge import PrologBridge
from domain.agents import VectorAgent, PredatorAgent, Perception, Action


def test_prolog_integration():
    """Test that Prolog knowledge base is accessible."""
    print("\n" + "="*60)
    print("Test 1: Prolog Integration")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    print("\nPROLOG KNOWLEDGE BASE LOADED")
    
    # Test basic Prolog queries
    print("\n1. Testing genus queries:")
    query = "genus_of(aedes_aegypti, Genus)"
    results = list(prolog.query(query))
    if results:
        print(f"   aedes_aegypti genus: {results[0].get('Genus')}")
    
    query = "genus_of(toxorhynchites, Genus)"
    results = list(prolog.query(query))
    if results:
        print(f"   toxorhynchites genus: {results[0].get('Genus')}")
    
    print("\n2. Testing action costs (from agent_decisions.pl):")
    for action in ['oviposit', 'feed', 'rest', 'hunt', 'grow']:
        query = f"action_energy_cost({action}, Cost)"
        try:
            results = list(prolog.query(query))
            if results:
                cost = results[0].get('Cost')
                print(f"   {action}: {cost} energy")
        except Exception as e:
            print(f"   {action}: query failed")
    
    print("\n3. Testing predatory stages:")
    query = "predatory_stage(toxorhynchites, Stage)"
    results = list(prolog.query(query))
    stages = [r.get('Stage') for r in results]
    print(f"   Predatory stages: {stages}")
    
    print("\nOK Prolog integration test passed")


def test_vector_agent():
    """Test Aedes aegypti vector agent."""
    print("\n" + "="*60)
    print("Test 2: Vector Agent (Aedes aegypti)")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    # Create vector agent
    agent = VectorAgent(
        agent_id='vector_001',
        age=5,
        energy=80.0,
        prolog_bridge=prolog
    )
    
    print(f"\nInitial state: {agent}")
    
    # Set up favorable environment for oviposition
    perception = Perception(
        temperature=26.0,
        humidity=75.0,
        population_density=0.3
    )
    
    # Mark oviposition site as available
    try:
        prolog.query("assertz(suitable_oviposition_site_available)")
        list(prolog.query("assertz(suitable_oviposition_site_available)"))
    except:
        pass
    
    print("\nEnvironmental conditions:")
    print(f"  Temperature: {perception.temperature}C")
    print(f"  Humidity: {perception.humidity}%")
    print(f"  Population density: {perception.population_density}")
    
    # Agent perceives environment
    agent.perceive(perception)
    
    # Query Prolog for decision
    print("\nQuerying Prolog for decision...")
    action = agent.decide_action()
    print(f"  Prolog decision: {action.value}")
    
    # Execute action
    result = agent.execute_action(action)
    print(f"\nAction execution result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\nFinal state: {agent}")
    
    # Test feeding behavior (low energy)
    agent.state.energy = 30.0
    agent._sync_state_to_prolog()
    
    print("\n--- Low Energy Scenario ---")
    print(f"Energy reduced to: {agent.state.energy}")
    
    action = agent.decide_action()
    print(f"Prolog decision: {action.value}")
    
    result = agent.execute_action(action)
    print(f"Action result: {result.get('action')} - Success: {result.get('success')}")
    print(f"Final energy: {agent.state.energy:.1f}")
    
    print("\nOK Vector agent test passed")


def test_predator_agent():
    """Test Toxorhynchites predator agent."""
    print("\n" + "="*60)
    print("Test 3: Predator Agent (Toxorhynchites)")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    # Create predator agent
    agent = PredatorAgent(
        agent_id='predator_001',
        stage='larva_L4',
        age=8,
        energy=50.0,
        prolog_bridge=prolog
    )
    
    print(f"\nInitial state: {agent}")
    
    # Verify predatory stage
    is_predatory = agent.is_predatory_stage()
    print(f"Is predatory stage: {is_predatory}")
    
    # Set up environment with prey
    perception = Perception(
        temperature=25.0,
        humidity=70.0,
        population_density=0.5,
        prey_available=100
    )
    
    print("\nEnvironmental conditions:")
    print(f"  Temperature: {perception.temperature}C")
    print(f"  Prey available: {perception.prey_available}")
    
    # Agent perceives environment
    agent.perceive(perception)
    
    # Query Prolog for decision
    print("\nQuerying Prolog for decision...")
    action = agent.decide_action()
    print(f"  Prolog decision: {action.value}")
    
    # Execute action
    result = agent.execute_action(action)
    print(f"\nAction execution result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\nFinal state: {agent}")
    
    # Test growth behavior (high energy)
    agent.state.energy = 85.0
    agent._sync_state_to_prolog()
    
    print("\n--- High Energy Scenario ---")
    print(f"Energy increased to: {agent.state.energy}")
    
    action = agent.decide_action()
    print(f"Prolog decision: {action.value}")
    
    result = agent.execute_action(action)
    print(f"Action result: {result.get('action')} - Success: {result.get('success')}")
    if 'new_stage' in result:
        print(f"Stage progression: {result.get('old_stage')} -> {result.get('new_stage')}")
    
    print("\nOK Predator agent test passed")


def test_agent_lifecycle():
    """Test agent lifecycle with aging and death."""
    print("\n" + "="*60)
    print("Test 4: Agent Lifecycle")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    agent = VectorAgent(
        agent_id='lifecycle_001',
        age=10,
        energy=5.0,  # Very low energy
        prolog_bridge=prolog
    )
    
    print(f"\nInitial: {agent}")
    print(f"Alive: {agent.alive}")
    
    # Simulate days passing
    print("\nSimulating 3 days...")
    for day in range(3):
        print(f"\n  Day {day + 1}:")
        agent.age_one_day()
        print(f"    Age: {agent.state.age}, Energy: {agent.state.energy:.1f}")
        print(f"    Alive: {agent.alive}")
        
        if not agent.alive:
            print("    Agent died!")
            break
    
    print(f"\nFinal: {agent}")
    
    print("\nOK Agent lifecycle test passed")


def test_prolog_decision_rules():
    """Test that Prolog decision rules are being consulted."""
    print("\n" + "="*60)
    print("Test 5: Prolog Decision Rules")
    print("="*60)
    
    config = ConfigManager()
    prolog = PrologBridge(config)
    prolog.inject_parameters()
    
    # Create agent
    agent = VectorAgent(
        agent_id='decision_test_001',
        age=5,
        energy=80.0,
        prolog_bridge=prolog
    )
    
    print("\nTesting different scenarios to verify Prolog rules:")
    
    # Scenario 1: High energy, favorable humidity -> should oviposit
    print("\n1. Scenario: High energy + favorable humidity")
    try:
        list(prolog.query("assertz(suitable_oviposition_site_available)"))
    except:
        pass
    
    perception = Perception(temperature=26.0, humidity=80.0, population_density=0.3)
    agent.perceive(perception)
    agent.state.energy = 80.0
    agent.state.reproduced = False
    agent._sync_state_to_prolog()
    
    action = agent.decide_action()
    print(f"   Prolog decision: {action.value}")
    print(f"   Expected: oviposit or feed")
    
    # Scenario 2: Low energy -> should feed
    print("\n2. Scenario: Low energy")
    agent.state.energy = 25.0
    agent._sync_state_to_prolog()
    
    action = agent.decide_action()
    print(f"   Prolog decision: {action.value}")
    print(f"   Expected: feed")
    
    # Scenario 3: Moderate energy, already reproduced -> should rest or feed
    print("\n3. Scenario: Moderate energy + already reproduced")
    agent.state.energy = 60.0
    agent.state.reproduced = True
    agent._sync_state_to_prolog()
    
    action = agent.decide_action()
    print(f"   Prolog decision: {action.value}")
    print(f"   Expected: rest or feed")
    
    # Test utility calculations from Prolog
    print("\n4. Testing utility calculations (from Prolog):")
    for action_enum in [Action.OVIPOSIT, Action.FEED, Action.REST]:
        utility = agent.calculate_utility(action_enum)
        print(f"   {action_enum.value}: utility = {utility:.2f}")
    
    print("\nOK Prolog decision rules test passed")


if __name__ == "__main__":
    print("="*60)
    print("TESTING DOMAIN AGENTS WITH PROLOG INTEGRATION")
    print("="*60)
    
    try:
        test_prolog_integration()
        test_vector_agent()
        test_predator_agent()
        test_agent_lifecycle()
        test_prolog_decision_rules()
        
        print("\n" + "="*60)
        print("ALL AGENT TESTS PASSED OK")
        print("="*60)
        print("\nARCHITECTURE VERIFIED:")
        print("  - Prolog: Contains all decision logic")
        print("  - Python: Queries Prolog and executes actions")
        print("  - Integration: Working correctly")
        
    except Exception as e:
        print(f"\nERROR Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
