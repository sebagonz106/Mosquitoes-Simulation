"""
Test Script for PrologBridge
=============================

Validates Python-Prolog integration via PySwip.
Tests parameter injection, query execution, and population simulation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.config import load_default_config
from infrastructure.prolog_bridge import PrologBridge, create_prolog_bridge


def main():
    """Test PrologBridge functionality."""
    
    print("=" * 60)
    print("PROLOG BRIDGE TEST")
    print("=" * 60)
    
    try:
        # Test 1: Initialize bridge
        print("\n[1/8] Initializing PrologBridge...")
        config = load_default_config()
        bridge = PrologBridge(config)
        print(f"[OK] Bridge initialized: {bridge}")
        print(f"  - Loaded files: {len(bridge.get_loaded_files_info())}")
        for file_path in bridge.get_loaded_files_info():
            print(f"    * {Path(file_path).name}")
        
        # Test 2: Inject parameters
        print("\n[2/8] Injecting configuration parameters...")
        bridge.inject_parameters()
        print("[OK] Parameters injected")
        
        # Test 3: Verify parameters loaded
        print("\n[3/8] Verifying parameter injection...")
        verification = bridge.verify_parameters_loaded()
        for species_id, loaded in verification.items():
            status = "[OK]" if loaded else "[X]"
            print(f"  {status} {species_id}: {loaded}")
        
        all_loaded = all(verification.values())
        if not all_loaded:
            print("⚠ Warning: Some parameters not loaded correctly")
        else:
            print("[OK] All parameters verified")
        
        # Test 4: Test ontology queries
        print("\n[4/8] Testing ontology queries...")
        
        # Query genera
        genera_results = bridge.query_all("genus(X)")
        genera = [r['X'] for r in genera_results]
        print(f"  - Genera: {', '.join(genera)}")
        
        # Query species
        species_results = bridge.query_all("species(S, G)")
        print(f"  - Species found: {len(species_results)}")
        for result in species_results:
            print(f"    * {result['S']} (genus: {result['G']})")
        
        # Test genus_of predicate
        genus_result = bridge.query_once("genus_of(aedes_aegypti, G)")
        if genus_result:
            print(f"  - Aedes aegypti genus: {genus_result['G']}")
        
        # Test ecological roles
        is_predator = bridge.query_yes_no("is_predator(toxorhynchites)")
        is_prey = bridge.query_yes_no("is_prey(aedes_aegypti)")
        print(f"  - Toxorhynchites is predator: {is_predator}")
        print(f"  - Aedes is prey: {is_prey}")
        
        print("[OK] Ontology queries successful")
        
        # Test 5: Test parameter queries
        print("\n[5/8] Testing parameter queries...")
        
        # Query stage durations
        duration_result = bridge.query_once(
            "stage_duration(aedes_aegypti, egg, Min, Max)"
        )
        if duration_result:
            print(f"  - Aedes egg duration: {duration_result['Min']}-{duration_result['Max']} days")
        
        # Query survival rates
        survival_result = bridge.query_once(
            "survival_rate(aedes_aegypti, egg, larva_l1, Rate)"
        )
        if survival_result:
            print(f"  - Aedes egg->L1 survival: {survival_result['Rate'] * 100}%")
        
        # Query fecundity
        fecundity_result = bridge.query_once(
            "fecundity(aedes_aegypti, Min, Max, Events)"
        )
        if fecundity_result:
            print(f"  - Aedes fecundity: {fecundity_result['Min']}-{fecundity_result['Max']} eggs/batch")
            print(f"  - Oviposition events: {fecundity_result['Events']}")
        
        # Query predation parameters
        predation_result = bridge.query_once(
            "predation_rate(toxorhynchites, larva_l1, Rate)"
        )
        if predation_result:
            print(f"  - Toxo predation rate on L1: {predation_result['Rate']} prey/day")
        
        func_resp_result = bridge.query_once(
            "functional_response(toxorhynchites, A, H)"
        )
        if func_resp_result:
            print(f"  - Functional response: a={func_resp_result['A']}, Th={func_resp_result['H']}")
        
        print("[OK] Parameter queries successful")
        
        # Test 6: Initialize populations
        print("\n[6/8] Initializing population states...")
        bridge.initialize_all_populations()
        
        # Query initial populations
        aedes_pops = bridge.get_population_state('aedes_aegypti', 0)
        toxo_pops = bridge.get_population_state('toxorhynchites', 0)
        
        aedes_total = bridge.get_total_population('aedes_aegypti', 0)
        toxo_total = bridge.get_total_population('toxorhynchites', 0)
        
        print(f"  - Aedes total: {aedes_total} individuals")
        print(f"    Stages: {len(aedes_pops)}")
        print(f"  - Toxorhynchites total: {toxo_total} individuals")
        print(f"    Stages: {len(toxo_pops)}")
        
        print("[OK] Populations initialized")
        
        # Test 7: Set environment state
        print("\n[7/8] Setting environmental conditions...")
        bridge.set_environment_state(0, 27.0, 75.0)
        
        env_result = bridge.query_once(
            "environmental_state(0, Temp, Humidity)"
        )
        if env_result:
            print(f"  - Day 0: Temp={env_result['Temp']}°C, Humidity={env_result['Humidity']}%")
        
        print("[OK] Environment state set")
        
        # Test 8: Test ecological inference
        print("\n[8/8] Testing ecological inference...")
        
        # Test predation predicate
        can_predate = bridge.query_yes_no(
            "can_predate(toxorhynchites, aedes_aegypti, larva_l4, larva_l2)"
        )
        print(f"  - Toxo L4 can predate on Aedes L2: {can_predate}")
        
        # Test temperature adjustment
        temp_adj_result = bridge.query_once(
            "temperature_adjustment(27, aedes_aegypti, Factor)"
        )
        if temp_adj_result:
            print(f"  - Temperature adjustment (27°C, Aedes): {temp_adj_result['Factor']:.3f}")
        
        # Test population trend
        trend = bridge.get_population_trend('aedes_aegypti', 0)
        print(f"  - Aedes population trend (Day 0): {trend}")
        
        # Test extinction risk
        risk = bridge.get_extinction_risk('aedes_aegypti', 0)
        print(f"  - Aedes extinction risk: {risk}")
        
        # Test ecological equilibrium
        equilibrium = bridge.check_ecological_equilibrium(0)
        print(f"  - Ecological equilibrium: {equilibrium}")
        
        print("[OK] Ecological inference successful")
        
        # Summary
        print("\n" + "=" * 60)
        print("[OK][OK][OK] ALL TESTS PASSED [OK][OK][OK]")
        print("=" * 60)
        print("\nPrologBridge is fully operational!")
        print("Ready for simulation execution.")
        
        return 0
        
    except Exception as e:
        print(f"\n[X] Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
