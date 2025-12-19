"""
Test Script for ConfigManager
==============================

Quick validation of configuration loading functionality.
Run this to verify JSON configs are loaded correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.config import load_default_config, ConfigurationError


def main():
    """Test configuration manager functionality."""
    
    print("=" * 60)
    print("CONFIG MANAGER TEST")
    print("=" * 60)
    
    try:
        # Load configuration
        print("\n[1/5] Loading configuration files...")
        config = load_default_config()
        print("✓ Configuration loaded successfully")
        
        # Test simulation config
        print("\n[2/5] Testing simulation configuration...")
        sim_config = config.get_simulation_config()
        print(f"  - Simulation days: {sim_config.default_days}")
        print(f"  - Time step: {sim_config.time_step}")
        print(f"  - Stochastic mode: {sim_config.stochastic_mode}")
        print(f"  - Random seed: {sim_config.random_seed}")
        print("✓ Simulation config OK")
        
        # Test species configs
        print("\n[3/5] Testing species configurations...")
        species_ids = config.get_all_species_ids()
        print(f"  - Loaded species: {', '.join(species_ids)}")
        
        for species_id in species_ids:
            species = config.get_species_config(species_id)
            print(f"\n  [{species.display_name}]")
            print(f"    • Life stages: {len(species.life_stages)}")
            print(f"    • Eggs per batch: {species.reproduction.eggs_per_batch_min}-{species.reproduction.eggs_per_batch_max}")
            
            # Check for predatory stages
            predatory_stages = [
                stage for stage, cfg in species.life_stages.items()
                if cfg.is_predatory
            ]
            if predatory_stages:
                print(f"    • Predatory stages: {', '.join(predatory_stages)}")
            
            # Check predation config
            if species.predation:
                print(f"    • Attack rate: {species.predation.attack_rate}")
                print(f"    • Handling time: {species.predation.handling_time}")
        
        print("\n✓ Species configs OK")
        
        # Test initial populations
        print("\n[4/5] Testing initial populations...")
        init_pops = config.get_initial_populations()
        
        for species_id, stages in init_pops.items():
            total = sum(stages.values())
            print(f"  - {species_id}: {total} individuals")
            for stage, count in stages.items():
                print(f"      • {stage}: {count}")
        
        print("✓ Initial populations OK")
        
        # Test environment config
        print("\n[5/5] Testing environment configuration...")
        env_config = config.get_environment_config()
        print(f"  - Temperature: {env_config.temperature}°C")
        print(f"  - Humidity: {env_config.humidity}%")
        print(f"  - Carrying capacity: {env_config.carrying_capacity}")
        print(f"  - Water availability: {env_config.water_availability}")
        print("✓ Environment config OK")
        
        # Validate all
        print("\n[VALIDATION] Running full validation...")
        warnings = config.validate_all()
        
        if warnings:
            print(f"⚠ Found {len(warnings)} warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("✓ All validations passed")
        
        # Test specific getters
        print("\n[ADDITIONAL TESTS] Testing specific getters...")
        
        # Test life stage duration
        duration = config.get_life_stage_duration('aedes_aegypti', 'egg')
        print(f"  - Aedes egg duration: {duration[0]}-{duration[1]} days")
        
        # Test survival rate
        survival = config.get_survival_rate('aedes_aegypti', 'egg')
        print(f"  - Aedes egg survival: {survival * 100}%")
        
        # Test predatory check
        is_pred = config.is_predatory_stage('toxorhynchites', 'larva_l4')
        print(f"  - Toxo L4 predatory: {is_pred}")
        
        # Test predation rate
        pred_rate = config.get_predation_rate('toxorhynchites', 'larva_l4')
        print(f"  - Toxo L4 predation rate: {pred_rate} prey/day")
        
        print("\n✓ All getter tests passed")
        
        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 60)
        
        return 0
        
    except ConfigurationError as e:
        print(f"\n✗ Configuration Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
