"""
Prolog Bridge Module
====================

Python-Prolog interface using PySwip. Manages SWI-Prolog engine initialization,
loads knowledge base files, injects configuration parameters as dynamic facts,
and provides query execution methods.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator, Union
from pyswip import Prolog

from .config import ConfigManager, ConfigurationError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrologBridgeError(Exception):
    """Custom exception for Prolog bridge-related errors."""
    pass


class PrologBridge:
    """
    Bridge between Python and SWI-Prolog knowledge base.
    
    Manages Prolog engine lifecycle, loads knowledge base files (.pl),
    injects configuration parameters as dynamic facts, and executes queries.
    
    Attributes:
        prolog: PySwip Prolog instance
        config_manager: Configuration manager instance
        prolog_dir: Path to Prolog source files
        loaded_files: List of loaded .pl files
        parameters_loaded: Flag indicating if parameters are injected
    """
    
    def __init__(
        self, 
        config_manager: ConfigManager,
        prolog_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize Prolog bridge.
        
        Args:
            config_manager: ConfigManager instance with loaded configurations
            prolog_dir: Path to Prolog source directory. If None, uses
                       default '../prolog' relative to project root.
        
        Raises:
            PrologBridgeError: If Prolog initialization fails
        """
        self.config_manager = config_manager
        
        # Determine Prolog directory
        if prolog_dir is None:
            project_root = Path(__file__).parent.parent.parent
            prolog_dir = project_root / "src" / "prolog"
        
        self.prolog_dir = Path(prolog_dir)
        
        if not self.prolog_dir.exists():
            raise PrologBridgeError(
                f"Prolog directory not found: {self.prolog_dir}"
            )
        
        # Initialize Prolog engine
        try:
            self.prolog = Prolog()
            logger.info("Prolog engine initialized successfully")
        except Exception as e:
            raise PrologBridgeError(f"Failed to initialize Prolog: {str(e)}")
        
        self.loaded_files: List[Path] = []
        self.parameters_loaded = False
        
        # Load knowledge base
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """
        Load all Prolog knowledge base files in correct order.
        
        Order matters: ontology → facts → rules → inference
        
        Raises:
            PrologBridgeError: If file loading fails
        """
        logger.info("Loading Prolog knowledge base...")
        
        # Define load order
        kb_files = [
            self.prolog_dir / "knowledge_base" / "species_ontology.pl",
            self.prolog_dir / "knowledge_base" / "biological_facts.pl",
            self.prolog_dir / "knowledge_base" / "ecological_rules.pl",
            self.prolog_dir / "inference" / "population_dynamics.pl",
            self.prolog_dir / "inference" / "agent_decisions.pl"
        ]
        
        for file_path in kb_files:
            if not file_path.exists():
                raise PrologBridgeError(f"Prolog file not found: {file_path}")
            
            try:
                self.prolog.consult(str(file_path))
                self.loaded_files.append(file_path)
                logger.info(f"  ✓ Loaded: {file_path.name}")
            except Exception as e:
                raise PrologBridgeError(
                    f"Failed to load {file_path.name}: {str(e)}"
                )
        
        logger.info(f"Knowledge base loaded: {len(self.loaded_files)} files")
    
    def inject_parameters(self):
        """
        Inject all configuration parameters into Prolog as dynamic facts.
        
        Loads parameters from ConfigManager and asserts them into Prolog
        using the load_* predicates defined in biological_facts.pl.
        
        Raises:
            PrologBridgeError: If parameter injection fails
        """
        logger.info("Injecting configuration parameters into Prolog...")
        
        # Clear existing parameters first
        self._clear_parameters()
        
        # Inject species parameters
        for species_id in self.config_manager.get_all_species_ids():
            self._inject_species_parameters(species_id)
        
        # Inject environmental parameters
        self._inject_environment_parameters()
        
        self.parameters_loaded = True
        logger.info("✓ All parameters injected successfully")
    
    def _clear_parameters(self):
        """Clear all dynamic parameters in Prolog."""
        try:
            list(self.prolog.query("clear_all_parameters"))
            logger.debug("  Cleared existing parameters")
        except Exception as e:
            logger.warning(f"Failed to clear parameters: {e}")
    
    def _inject_species_parameters(self, species_id: str):
        """
        Inject parameters for a specific species.
        
        Args:
            species_id: Species identifier
        
        Raises:
            PrologBridgeError: If injection fails
        """
        logger.info(f"  Injecting parameters for: {species_id}")
        
        try:
            species = self.config_manager.get_species_config(species_id)
            
            # Inject life stage durations and survival rates
            for stage, stage_config in species.life_stages.items():
                # Stage duration
                self._assert(
                    f"load_stage_duration({species_id}, {stage}, "
                    f"{stage_config.duration_min}, {stage_config.duration_max})"
                )
                
                # Survival rate (if defined)
                if stage_config.survival_to_next is not None:
                    # Determine next stage
                    next_stage = self._get_next_stage(stage)
                    if next_stage:
                        self._assert(
                            f"load_survival_rate({species_id}, {stage}, "
                            f"{next_stage}, {stage_config.survival_to_next})"
                        )
                elif stage_config.survival_daily is not None:
                    # For adult stages with daily survival
                    self._assert(
                        f"load_survival_rate({species_id}, {stage}, "
                        f"adult, {stage_config.survival_daily})"
                    )
                
                # Predation rate (if predatory)
                if stage_config.is_predatory and stage_config.predation_rate:
                    self._assert(
                        f"load_predation_rate({species_id}, {stage}, "
                        f"{stage_config.predation_rate})"
                    )
            
            # Inject fecundity
            repro = species.reproduction
            self._assert(
                f"load_fecundity({species_id}, "
                f"{repro.eggs_per_batch_min}, {repro.eggs_per_batch_max}, "
                f"{repro.oviposition_events})"
            )
            
            # Inject functional response (if predator)
            if species.predation:
                pred = species.predation
                self._assert(
                    f"load_functional_response({species_id}, "
                    f"{pred.attack_rate}, {pred.handling_time})"
                )
            
            logger.debug(f"    ✓ {species_id} parameters injected")
            
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to inject {species_id} parameters: {str(e)}"
            )
    
    def _inject_environment_parameters(self):
        """
        Inject environmental parameters.
        
        Raises:
            PrologBridgeError: If injection fails
        """
        logger.info("  Injecting environmental parameters")
        
        try:
            env = self.config_manager.get_environment_config()
            
            # Extract temperature (handle dict or float)
            if isinstance(env.temperature, dict):
                temp_value = env.temperature.get('mean', 27)
            else:
                temp_value = env.temperature
            
            # Extract humidity (handle dict or float)
            if isinstance(env.humidity, dict):
                humidity_value = env.humidity.get('mean', 75)
            else:
                humidity_value = env.humidity
            
            self._assert(
                f"load_environmental_param(temperature, {temp_value})"
            )
            self._assert(
                f"load_environmental_param(humidity, {humidity_value})"
            )
            self._assert(
                f"load_environmental_param(carrying_capacity, {env.carrying_capacity})"
            )
            self._assert(
                f"load_environmental_param(water_availability, {env.water_availability})"
            )
            
            logger.debug("    ✓ Environmental parameters injected")
            
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to inject environment parameters: {str(e)}"
            )
    
    def _get_next_stage(self, current_stage: str) -> Optional[str]:
        """
        Determine next life stage in sequence.
        
        Args:
            current_stage: Current life stage name
        
        Returns:
            Next stage name or None if terminal stage
        """
        stage_sequence = [
            'egg', 'larva_l1', 'larva_l2', 'larva_l3', 
            'larva_l4', 'pupa', 'adult_female', 'adult_male'
        ]
        
        try:
            idx = stage_sequence.index(current_stage)
            if idx < len(stage_sequence) - 2:  # Not adult stages
                return stage_sequence[idx + 1]
        except ValueError:
            pass
        
        return None
    
    def _assert(self, fact: str):
        """
        Assert a fact into Prolog knowledge base.
        
        Args:
            fact: Prolog fact/predicate to assert (without 'assertz')
        
        Raises:
            PrologBridgeError: If assertion fails
        """
        try:
            # Call the load_* predicate which internally uses assertz
            list(self.prolog.query(fact))
        except Exception as e:
            raise PrologBridgeError(f"Failed to assert '{fact}': {str(e)}")
    
    def query(self, query_string: str) -> Iterator[Dict[str, Any]]:
        """
        Execute a Prolog query and return results as iterator.
        
        Args:
            query_string: Prolog query string
        
        Returns:
            Iterator of dictionaries with variable bindings
        
        Raises:
            PrologBridgeError: If query execution fails
        
        Example:
            >>> for result in bridge.query("species(X, aedes)"):
            >>>     print(result['X'])
        """
        if not self.parameters_loaded:
            logger.warning("Parameters not loaded yet, results may be incomplete")
        
        try:
            return self.prolog.query(query_string)
        except Exception as e:
            raise PrologBridgeError(f"Query failed: {str(e)}")
    
    def query_once(self, query_string: str) -> Optional[Dict[str, Any]]:
        """
        Execute query and return first result only.
        
        Args:
            query_string: Prolog query string
        
        Returns:
            Dictionary with variable bindings or None if no results
        
        Example:
            >>> result = bridge.query_once("genus_of(aedes_aegypti, G)")
            >>> print(result['G'])  # 'aedes'
        """
        try:
            results = list(self.prolog.query(query_string, maxresult=1))
            return results[0] if results else None
        except Exception as e:
            raise PrologBridgeError(f"Query failed: {str(e)}")
    
    def query_all(self, query_string: str) -> List[Dict[str, Any]]:
        """
        Execute query and return all results as list.
        
        Args:
            query_string: Prolog query string
        
        Returns:
            List of dictionaries with variable bindings
        
        Example:
            >>> results = bridge.query_all("life_stage(X)")
            >>> stages = [r['X'] for r in results]
        """
        try:
            return list(self.prolog.query(query_string))
        except Exception as e:
            raise PrologBridgeError(f"Query failed: {str(e)}")
    
    def query_yes_no(self, query_string: str) -> bool:
        """
        Execute query and return True if it succeeds, False otherwise.
        
        Args:
            query_string: Prolog query string (typically without variables)
        
        Returns:
            True if query succeeds, False otherwise
        
        Example:
            >>> if bridge.query_yes_no("is_predator(toxorhynchites)"):
            >>>     print("Toxorhynchites is a predator")
        """
        try:
            results = list(self.prolog.query(query_string, maxresult=1))
            return len(results) > 0
        except Exception:
            return False
    
    def initialize_population(
        self, 
        species_id: str, 
        stage: str, 
        count: int, 
        day: int = 0
    ):
        """
        Initialize population state in Prolog.
        
        Args:
            species_id: Species identifier
            stage: Life stage
            count: Population count
            day: Simulation day (default 0)
        
        Raises:
            PrologBridgeError: If initialization fails
        """
        try:
            query = (
                f"initialize_population({species_id}, {stage}, {count}, {day})"
            )
            list(self.prolog.query(query))
            logger.debug(f"  Initialized: {species_id}.{stage} = {count}")
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to initialize population: {str(e)}"
            )
    
    def initialize_all_populations(self):
        """
        Initialize all populations from configuration.
        
        Uses initial_populations from ConfigManager to set up
        population_state/4 facts in Prolog.
        
        Raises:
            PrologBridgeError: If initialization fails
        """
        logger.info("Initializing population states in Prolog...")
        
        init_pops = self.config_manager.get_initial_populations()
        
        for species_id, stages in init_pops.items():
            for stage, count in stages.items():
                self.initialize_population(species_id, stage, count, 0)
        
        logger.info("✓ All populations initialized")
    
    def set_environment_state(
        self, 
        day: int, 
        temperature: float, 
        humidity: float
    ):
        """
        Set environmental state for a specific day.
        
        Args:
            day: Simulation day
            temperature: Temperature in °C
            humidity: Relative humidity (%)
        
        Raises:
            PrologBridgeError: If state update fails
        """
        try:
            query = (
                f"assertz(environmental_state({day}, {temperature}, {humidity}))"
            )
            list(self.prolog.query(query))
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to set environment state: {str(e)}"
            )
    
    def get_population_state(
        self, 
        species_id: str, 
        day: int
    ) -> Dict[str, int]:
        """
        Get population state for all stages of a species on a given day.
        
        Args:
            species_id: Species identifier
            day: Simulation day
        
        Returns:
            Dictionary mapping stage names to population counts
        
        Example:
            >>> pops = bridge.get_population_state('aedes_aegypti', 10)
            >>> print(pops['larva_l3'])  # Population of L3 larvae on day 10
        """
        try:
            query = (
                f"population_state({species_id}, Stage, Count, {day})"
            )
            results = self.query_all(query)
            
            return {
                result['Stage']: result['Count'] 
                for result in results
            }
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to get population state: {str(e)}"
            )
    
    def get_total_population(self, species_id: str, day: int) -> int:
        """
        Get total population for a species on a given day.
        
        Args:
            species_id: Species identifier
            day: Simulation day
        
        Returns:
            Total population count across all stages
        """
        try:
            result = self.query_once(
                f"total_population({species_id}, {day}, Total)"
            )
            return result['Total'] if result else 0
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to get total population: {str(e)}"
            )
    
    def get_population_trend(self, species_id: str, day: int) -> str:
        """
        Get population trend analysis.
        
        Args:
            species_id: Species identifier
            day: Simulation day
        
        Returns:
            Trend: 'growing', 'stable', 'declining', or 'initial'
        """
        try:
            result = self.query_once(
                f"population_trend({species_id}, {day}, Trend)"
            )
            return result['Trend'] if result else 'unknown'
        except Exception as e:
            logger.warning(f"Failed to get trend: {e}")
            return 'unknown'
    
    def advance_population(self, species_id: str, from_day: int, to_day: int):
        """
        Advance population simulation from one day to another.
        
        Uses project_population/4 to simulate population dynamics.
        
        Args:
            species_id: Species identifier
            from_day: Starting day
            to_day: Ending day
        
        Raises:
            PrologBridgeError: If projection fails
        """
        try:
            query = (
                f"project_population({species_id}, {from_day}, {to_day}, _)"
            )
            list(self.prolog.query(query))
        except Exception as e:
            raise PrologBridgeError(
                f"Failed to advance population: {str(e)}"
            )
    
    def evaluate_biocontrol(self, day: int) -> Optional[str]:
        """
        Evaluate biocontrol effectiveness.
        
        Args:
            day: Simulation day to evaluate
        
        Returns:
            Assessment: 'highly_effective', 'effective', 'promising',
                       'ineffective', or 'requires_analysis'
        """
        try:
            result = self.query_once(
                f"biocontrol_viable({day}, Assessment)"
            )
            return result['Assessment'] if result else None
        except Exception as e:
            logger.warning(f"Failed to evaluate biocontrol: {e}")
            return None
    
    def check_ecological_equilibrium(self, day: int) -> bool:
        """
        Check if system is in ecological equilibrium.
        
        Args:
            day: Simulation day
        
        Returns:
            True if in equilibrium, False otherwise
        """
        return self.query_yes_no(f"ecological_equilibrium({day})")
    
    def get_extinction_risk(self, species_id: str, day: int) -> Optional[str]:
        """
        Assess extinction risk for a species.
        
        Args:
            species_id: Species identifier
            day: Simulation day
        
        Returns:
            Risk level: 'critical', 'high', 'moderate', or 'low'
        """
        try:
            result = self.query_once(
                f"extinction_risk({species_id}, {day}, Risk)"
            )
            return result['Risk'] if result else None
        except Exception as e:
            logger.warning(f"Failed to assess extinction risk: {e}")
            return None
    
    def verify_parameters_loaded(self) -> Dict[str, bool]:
        """
        Verify that all parameters were loaded correctly.
        
        Returns:
            Dictionary with verification results per species
        """
        verification = {}
        
        for species_id in self.config_manager.get_all_species_ids():
            try:
                result = self.query_once(
                    f"parameters_loaded({species_id})"
                )
                verification[species_id] = result is not None
            except Exception:
                verification[species_id] = False
        
        return verification
    
    def reset(self):
        """
        Reset Prolog state (clear dynamic predicates).
        
        Useful for running multiple simulations.
        """
        logger.info("Resetting Prolog state...")
        
        try:
            # Clear population states
            self.prolog.query("retractall(population_state(_, _, _, _))")
            
            # Clear environment states
            self.prolog.query("retractall(environmental_state(_, _, _))")
            
            # Clear agent states
            self.prolog.query("retractall(agent_state(_, _, _, _, _))")
            self.prolog.query("retractall(agent_species(_, _))")
            
            # Clear parameters
            self._clear_parameters()
            
            self.parameters_loaded = False
            logger.info("✓ Prolog state reset")
            
        except Exception as e:
            logger.warning(f"Reset incomplete: {e}")
    
    def get_loaded_files_info(self) -> List[str]:
        """
        Get list of loaded Prolog files.
        
        Returns:
            List of loaded file paths (as strings)
        """
        return [str(f) for f in self.loaded_files]
    
    def get_survival_rates(
        self, 
        species: str, 
        day: int,
        temp: float, 
        humidity: float
    ) -> Dict[tuple, float]:
        """
        Query Prolog to obtain environmentally-adjusted survival rates.
        
        Queries the effective_survival/6 predicate for all relevant life stage
        transitions, applying temperature and humidity factors to base survival rates.
        
        Args:
            species: Species identifier (e.g., 'aedes_aegypti')
            day: Current simulation day
            temp: Current temperature (°C)
            humidity: Current relative humidity (%)
        
        Returns:
            Dictionary mapping stage transitions to adjusted survival rates:
            {
                ('egg', 'larva_l1'): 0.75,
                ('larva_l1', 'larva_l2'): 0.82,
                ('larva_l2', 'larva_l3'): 0.85,
                ('larva_l3', 'larva_l4'): 0.87,
                ('larva_l4', 'pupa'): 0.80,
                ('pupa', 'adult_female'): 0.90
            }
            
            Returns empty dict if Prolog query fails (allows fallback to static rates).
        
        Example:
            >>> rates = bridge.get_survival_rates('aedes_aegypti', 50, 28.0, 75.0)
            >>> rates[('egg', 'larva_l1')]
            0.748
        """
        survival_dict = {}
        
        # Definir todas las transiciones relevantes para mosquitos
        transitions = [
            ('egg', 'larva_l1'),
            ('larva_l1', 'larva_l2'),
            ('larva_l2', 'larva_l3'),
            ('larva_l3', 'larva_l4'),
            ('larva_l4', 'pupa'),
            ('pupa', 'adult_female'),
            ('pupa', 'adult_male')
        ]
        
        try:
            # Actualizar estado ambiental en Prolog
            self.set_environment_state(day, temp, humidity)
            
            # Consultar cada transición
            for from_stage, to_stage in transitions:
                query = (
                    f"effective_survival({species}, {from_stage}, {to_stage}, "
                    f"{temp}, {humidity}, Rate)"
                )
                
                try:
                    result = self.query_once(query)
                    if result and 'Rate' in result:
                        rate = float(result['Rate'])
                        # Validar que esté en rango [0, 1]
                        if 0 <= rate <= 1:
                            survival_dict[(from_stage, to_stage)] = rate
                        else:
                            logger.warning(
                                f"Prolog returned out-of-range survival rate "
                                f"for {from_stage}→{to_stage}: {rate}"
                            )
                except Exception as e:
                    logger.debug(
                        f"Could not query survival for {from_stage}→{to_stage}: {e}"
                    )
                    # Continuar con la siguiente transición
                    continue
            
            if survival_dict:
                logger.debug(
                    f"Retrieved {len(survival_dict)} survival rates from Prolog "
                    f"(Day {day}, T={temp:.1f}°C, H={humidity:.0f}%)"
                )
            else:
                logger.debug(
                    f"No survival rates retrieved from Prolog (Day {day}) - "
                    f"will use static rates"
                )
                
        except Exception as e:
            logger.warning(
                f"Failed to retrieve survival rates from Prolog: {e} - "
                f"falling back to static rates"
            )
        
        return survival_dict
    
    def get_predation_rate(
        self,
        stage: str,
        predator_density: float,
        base_rate: float,
        temperature: float
    ) -> float:
        """
        Query Prolog for predation-adjusted survival rate.
        
        Consults predation_rate/4 predicate to adjust survival based on
        predator density and environmental conditions.
        
        Args:
            stage: Life stage being predated (e.g., 'larva', 'larva_l3')
            predator_density: Ratio of predators to prey
            base_rate: Base survival rate without predation
            temperature: Current temperature (°C, affects predator activity)
        
        Returns:
            Adjusted survival rate after predation (0.0 to 1.0)
            Falls back to simple reduction if Prolog query fails.
        
        Example:
            >>> rate = bridge.get_predation_rate('larva', 0.2, 0.85, 28.0)
            >>> # Returns lower rate due to predation pressure
            >>> rate < 0.85
            True
        
        Note:
            Prolog predicate: predation_rate(Stage, Density, BaseRate, AdjustedRate)
            Defined in population_dynamics.pl:
                predation_rate(Stage, Density, BaseRate, AdjustedRate) :-
                    prey_vulnerability(Stage, Vulnerability),
                    predation_risk(Density, Risk),
                    Reduction is Vulnerability * Risk,
                    AdjustedRate is BaseRate * (1 - Reduction).
        """
        try:
            # Query Prolog for adjusted rate
            query = (
                f"predation_rate({stage}, {predator_density}, "
                f"{base_rate}, AdjustedRate)"
            )
            
            result = self.query_once(query)
            if result and 'AdjustedRate' in result:
                adjusted_rate = float(result['AdjustedRate'])
                
                # Validate range
                if 0 <= adjusted_rate <= 1:
                    logger.debug(
                        f"Predation: {stage} survival {base_rate:.3f} → "
                        f"{adjusted_rate:.3f} (density={predator_density:.3f})"
                    )
                    return adjusted_rate
                else:
                    logger.warning(
                        f"Prolog returned out-of-range predation rate: {adjusted_rate}"
                    )
            
        except Exception as e:
            logger.debug(f"Predation query failed: {e}, using fallback calculation")
        
        # Fallback: simple multiplicative reduction
        # Higher density → more predation → lower survival
        reduction_factor = 1.0 / (1.0 + predator_density)
        adjusted_rate = base_rate * reduction_factor
        
        return adjusted_rate

    def __repr__(self) -> str:
        """String representation of PrologBridge."""
        return (
            f"PrologBridge("
            f"files={len(self.loaded_files)}, "
            f"parameters_loaded={self.parameters_loaded})"
        )


# ========== CONVENIENCE FUNCTIONS ==========

def create_prolog_bridge(
    config_manager: Optional[ConfigManager] = None
) -> PrologBridge:
    """
    Create PrologBridge with default configuration.
    
    Args:
        config_manager: Optional ConfigManager instance. If None, creates new one.
    
    Returns:
        Initialized PrologBridge instance
    
    Raises:
        PrologBridgeError: If initialization fails
    """
    if config_manager is None:
        from .config import load_default_config
        config_manager = load_default_config()
    
    bridge = PrologBridge(config_manager)
    bridge.inject_parameters()
    bridge.initialize_all_populations()
    
    return bridge
