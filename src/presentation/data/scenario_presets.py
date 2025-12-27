"""
Scenario Presets Module
=======================

Predefined simulation scenarios for common use cases and testing.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ScenarioPreset:
    """
    Predefined scenario configuration.
    
    Attributes:
        name: Display name
        description: Brief description of scenario purpose
        species: Species identifier
        duration: Simulation duration in days
        initial_eggs: Initial egg population
        initial_larvae: Initial larva population
        initial_pupae: Initial pupa population
        initial_adults: Initial adult population
        temperature: Temperature in Celsius
        humidity: Humidity percentage
        water_availability: Water availability factor (0-1)
        category: Scenario category for grouping
    """
    name: str
    description: str
    species: str
    duration: int
    initial_eggs: int
    initial_larvae: int
    initial_pupae: int
    initial_adults: int
    temperature: float
    humidity: float
    water_availability: float
    category: str


@dataclass
class PredatorPreyPreset:
    """
    Predefined predator-prey scenario configuration.
    
    Attributes:
        name: Display name
        description: Brief description of scenario purpose
        prey_species: Prey species identifier
        predator_species: Predator species identifier
        duration: Simulation duration in days
        prey_eggs/larvae/pupae/adults: Initial prey populations
        predator_larvae/pupae/adults: Initial predator populations
        temperature: Temperature in Celsius (shared)
        humidity: Humidity percentage (shared)
        water_availability: Water availability factor (0-1, shared)
        category: Scenario category for grouping
    """
    name: str
    description: str
    prey_species: str
    predator_species: str
    duration: int
    prey_initial_eggs: int
    prey_initial_larvae: int
    prey_initial_pupae: int
    prey_initial_adults: int
    predator_initial_larvae: int
    predator_initial_pupae: int
    predator_initial_adults: int
    temperature: float
    humidity: float
    water_availability: float
    category: str


# Validation ranges for parameters
PARAMETER_RANGES = {
    'duration': {
        'min': 1,
        'max': 365,
        'default': 90,
        'description': 'Simulation duration in days'
    },
    'initial_eggs': {
        'min': 0,
        'max': 100000,
        'default': 1000,
        'description': 'Initial egg population'
    },
    'initial_larvae': {
        'min': 0,
        'max': 50000,
        'default': 500,
        'description': 'Initial larva population'
    },
    'initial_pupae': {
        'min': 0,
        'max': 10000,
        'default': 100,
        'description': 'Initial pupa population'
    },
    'initial_adults': {
        'min': 0,
        'max': 10000,
        'default': 50,
        'description': 'Initial adult population'
    },
    'temperature': {
        'min': 10.0,
        'max': 40.0,
        'default': 25.0,
        'description': 'Environmental temperature (optimal: 22-32°C)'
    },
    'humidity': {
        'min': 0.0,
        'max': 100.0,
        'default': 70.0,
        'description': 'Relative humidity percentage (optimal: >60%)'
    },
    'water_availability': {
        'min': 0.0,
        'max': 1.0,
        'default': 1.0,
        'description': 'Water availability factor (0=none, 1=abundant)'
    }
}


# Información de tooltips para parámetros
PARAMETER_TOOLTIPS = {
    'species': (
        'Selección de Especie\n\n'
        'Aedes aegypti: Mosquito vector de enfermedades, transmite dengue, zika, chikungunya.\n'
        '  - Ciclo de cría: 8-10 días\n'
        '  - Esperanza de vida: 2-4 semanas\n'
        '  - Temperatura óptima: 22-32°C\n\n'
        'Toxorhynchites: Mosquito depredador, agente de control biológico.\n'
        '  - Ciclo de cría: 15-20 días\n'
        '  - Esperanza de vida: 4-8 semanas\n'
        '  - Depreda larvas de Aedes'
    ),
    'duration': (
        'Duración de Simulación\n\n'
        'Número de días a simular.\n\n'
        'Duraciones típicas:\n'
        '  - Corto plazo (30-60 días): Establecimiento poblacional\n'
        '  - Medio plazo (90-180 días): Dinámicas estacionales\n'
        '  - Largo plazo (180-365 días): Patrones anuales\n\n'
        'Rango válido: 1-365 días'
    ),
    'initial_eggs': (
        'Población Inicial de Huevos\n\n'
        'Número de huevos al inicio de la simulación.\n\n'
        'Guía de referencia:\n'
        '  - Colonia pequeña: 100-500\n'
        '  - Colonia mediana: 1,000-5,000\n'
        '  - Infestación grande: 10,000+\n\n'
        'Los huevos eclosionan en 2-3 días bajo condiciones óptimas.\n'
        'Rango válido: 0-100,000'
    ),
    'initial_larvae': (
        'Población Inicial de Larvas\n\n'
        'Número de larvas al inicio de la simulación.\n\n'
        'Guía de referencia:\n'
        '  - Colonia pequeña: 50-200\n'
        '  - Colonia mediana: 500-2,000\n'
        '  - Infestación grande: 5,000+\n\n'
        'El desarrollo larval toma 5-7 días.\n'
        'Rango válido: 0-50,000'
    ),
    'initial_pupae': (
        'Población Inicial de Pupas\n\n'
        'Número de pupas al inicio de la simulación.\n\n'
        'Guía de referencia:\n'
        '  - Colonia pequeña: 10-50\n'
        '  - Colonia mediana: 100-500\n'
        '  - Infestación grande: 1,000+\n\n'
        'La etapa pupal dura 1-2 días.\n'
        'Rango válido: 0-10,000'
    ),
    'initial_adults': (
        'Población Inicial de Adultos\n\n'
        'Número de mosquitos adultos al inicio de la simulación.\n\n'
        'Guía de referencia:\n'
        '  - Colonia pequeña: 10-50\n'
        '  - Colonia mediana: 100-500\n'
        '  - Infestación grande: 1,000+\n\n'
        'Los adultos viven 2-4 semanas y se reproducen cada 3-4 días.\n'
        'Rango válido: 0-10,000'
    ),
    'temperature': (
        'Temperatura Ambiental\n\n'
        'Temperatura promedio en grados Celsius.\n\n'
        'Efectos de la temperatura:\n'
        '  - 10-18°C: El desarrollo se ralentiza significativamente\n'
        '  - 18-22°C: Subóptimo, desarrollo más lento\n'
        '  - 22-32°C: Rango ÓPTIMO para desarrollo\n'
        '  - 32-35°C: Estresante, supervivencia reducida\n'
        '  - 35-40°C: Alta mortalidad\n\n'
        'Rango válido: 10-40°C'
    ),
    'humidity': (
        'Humedad Relativa\n\n'
        'Porcentaje de humedad atmosférica.\n\n'
        'Efectos de la humedad:\n'
        '  - <40%: Alto estrés por desecación\n'
        '  - 40-60%: Condiciones moderadas\n'
        '  - 60-80%: Rango ÓPTIMO\n'
        '  - 80-100%: Excelente para mosquitos\n\n'
        'Baja humedad reduce la eclosión de huevos y supervivencia de adultos.\n'
        'Rango válido: 0-100%'
    ),
    'water_availability': (
        'Disponibilidad de Agua\n\n'
        'Factor de disponibilidad de agua en sitios de cría.\n\n'
        'Escala:\n'
        '  - 0.0: Sin agua (colapso poblacional)\n'
        '  - 0.3-0.5: Sitios de cría limitados\n'
        '  - 0.7-0.9: Buenas condiciones\n'
        '  - 1.0: Sitios de cría abundantes\n\n'
        'Afecta la capacidad de puesta de huevos y supervivencia larval.\n'
        'Rango válido: 0.0-1.0'
    )
}


# Predefined scenarios grouped by category
SCENARIO_PRESETS: List[ScenarioPreset] = [
    # ========== BASELINE SCENARIOS ==========
    ScenarioPreset(
        name="Condiciones Estándar",
        description="Ambiente urbano típico con condiciones óptimas",
        species='aedes_aegypti',
        duration=90,
        initial_eggs=1000,
        initial_larvae=500,
        initial_pupae=100,
        initial_adults=50,
        temperature=27.0,
        humidity=75.0,
        water_availability=1.0,
        category='baseline'
    ),
    
    ScenarioPreset(
        name="Establecimiento Colonia Pequeña",
        description="Colonización inicial con pocos mosquitos",
        species='aedes_aegypti',
        duration=60,
        initial_eggs=100,
        initial_larvae=50,
        initial_pupae=10,
        initial_adults=10,
        temperature=28.0,
        humidity=70.0,
        water_availability=0.8,
        category='baseline'
    ),
    
    # ========== ENVIRONMENTAL STRESS ==========
    ScenarioPreset(
        name="Estación Seca Caliente",
        description="Estrés por alta temperatura y baja humedad",
        species='aedes_aegypti',
        duration=90,
        initial_eggs=1000,
        initial_larvae=500,
        initial_pupae=100,
        initial_adults=50,
        temperature=35.0,
        humidity=40.0,
        water_availability=0.4,
        category='stress'
    ),
    
    ScenarioPreset(
        name="Clima Frío",
        description="Condiciones de temperatura subóptima",
        species='aedes_aegypti',
        duration=90,
        initial_eggs=1000,
        initial_larvae=500,
        initial_pupae=100,
        initial_adults=50,
        temperature=18.0,
        humidity=60.0,
        water_availability=0.7,
        category='stress'
    ),
    
    ScenarioPreset(
        name="Condiciones de Sequía",
        description="Escasez severa de agua",
        species='aedes_aegypti',
        duration=60,
        initial_eggs=500,
        initial_larvae=300,
        initial_pupae=50,
        initial_adults=30,
        temperature=32.0,
        humidity=30.0,
        water_availability=0.2,
        category='stress'
    ),
    
    # ========== CONTROL SCENARIOS ==========
    ScenarioPreset(
        name="Introducción de Biocontrol",
        description="Toxorhynchites para control biológico",
        species='toxorhynchites',
        duration=120,
        initial_eggs=200,
        initial_larvae=100,
        initial_pupae=20,
        initial_adults=20,
        temperature=26.0,
        humidity=80.0,
        water_availability=1.0,
        category='control'
    ),
    
    # ========== OPTIMAL SCENARIOS ==========
    ScenarioPreset(
        name="Condiciones Ideales de Cría",
        description="Condiciones perfectas para proliferación de mosquitos",
        species='aedes_aegypti',
        duration=90,
        initial_eggs=2000,
        initial_larvae=1000,
        initial_pupae=200,
        initial_adults=100,
        temperature=28.0,
        humidity=85.0,
        water_availability=1.0,
        category='optimal'
    ),
    
    ScenarioPreset(
        name="Pico Temporada de Lluvias",
        description="Máxima disponibilidad de sitios de cría",
        species='aedes_aegypti',
        duration=120,
        initial_eggs=5000,
        initial_larvae=2000,
        initial_pupae=500,
        initial_adults=200,
        temperature=27.0,
        humidity=90.0,
        water_availability=1.0,
        category='optimal'
    ),
    
    # ========== OUTBREAK SCENARIOS ==========
    ScenarioPreset(
        name="Brote Urbano",
        description="Gran infestación en área urbana",
        species='aedes_aegypti',
        duration=180,
        initial_eggs=10000,
        initial_larvae=5000,
        initial_pupae=1000,
        initial_adults=500,
        temperature=29.0,
        humidity=80.0,
        water_availability=1.0,
        category='outbreak'
    ),
    
    ScenarioPreset(
        name="Crecimiento Poblacional Rápido",
        description="Monitoreo de fase de crecimiento exponencial",
        species='aedes_aegypti',
        duration=45,
        initial_eggs=100,
        initial_larvae=50,
        initial_pupae=10,
        initial_adults=100,
        temperature=30.0,
        humidity=85.0,
        water_availability=1.0,
        category='outbreak'
    )
]


# ============================================================================
# ENVIRONMENTAL PRESETS (GENERALIZED, REUSABLE)
# ============================================================================

ENVIRONMENTAL_PRESETS = {
    'tropical_optimal': {
        'name': 'Tropical Óptimo',
        'temperature': 28.0,
        'humidity': 80.0,
        'water_availability': 1.0,
        'description': 'Condiciones ideales tropicales para reproducción'
    },
    'tropical_dry': {
        'name': 'Tropical Seco',
        'temperature': 30.0,
        'humidity': 50.0,
        'water_availability': 0.6,
        'description': 'Estación seca tropical con estrés hídrico'
    },
    'temperate': {
        'name': 'Templado',
        'temperature': 20.0,
        'humidity': 65.0,
        'water_availability': 0.8,
        'description': 'Clima templado estacional'
    },
    'extreme_hot': {
        'name': 'Extremo Calor',
        'temperature': 38.0,
        'humidity': 30.0,
        'water_availability': 0.4,
        'description': 'Condiciones extremas de calor y sequía'
    },
    'winter': {
        'name': 'Invierno',
        'temperature': 12.0,
        'humidity': 75.0,
        'water_availability': 0.5,
        'description': 'Condiciones de invierno con baja actividad'
    },
    'monsoon': {
        'name': 'Monzón',
        'temperature': 26.0,
        'humidity': 95.0,
        'water_availability': 1.0,
        'description': 'Período de monzón con lluvia abundante'
    }
}


# ============================================================================
# PREDATOR-PREY PRESETS
# ============================================================================

PREDATOR_PREY_PRESETS = [
    PredatorPreyPreset(
        name="Control Balanceado",
        description="Poblaciones equivalentes de presa y depredador en condiciones óptimas",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=1000,
        prey_initial_larvae=500,
        prey_initial_pupae=100,
        prey_initial_adults=100,
        predator_initial_larvae=20,
        predator_initial_pupae=5,
        predator_initial_adults=10,
        temperature=28.0,
        humidity=80.0,
        water_availability=1.0,
        category='balanced'
    ),
    
    PredatorPreyPreset(
        name="Control Débil (Pocos Depredadores)",
        description="Introducción minimal de depredadores, control moderado",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=2000,
        prey_initial_larvae=1000,
        prey_initial_pupae=200,
        prey_initial_adults=150,
        predator_initial_larvae=5,
        predator_initial_pupae=2,
        predator_initial_adults=3,
        temperature=28.0,
        humidity=80.0,
        water_availability=1.0,
        category='weak_control'
    ),
    
    PredatorPreyPreset(
        name="Control Fuerte (Muchos Depredadores)",
        description="Alta densidad de depredadores, control agresivo",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=1000,
        prey_initial_larvae=500,
        prey_initial_pupae=100,
        prey_initial_adults=100,
        predator_initial_larvae=60,
        predator_initial_pupae=20,
        predator_initial_adults=30,
        temperature=28.0,
        humidity=80.0,
        water_availability=1.0,
        category='strong_control'
    ),
    
    PredatorPreyPreset(
        name="Alta Presión de Presa",
        description="Muchas presas, depredadores insuficientes, compresión de control",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=5000,
        prey_initial_larvae=2500,
        prey_initial_pupae=500,
        prey_initial_adults=300,
        predator_initial_larvae=10,
        predator_initial_pupae=3,
        predator_initial_adults=5,
        temperature=28.0,
        humidity=80.0,
        water_availability=1.0,
        category='prey_pressure'
    ),
    
    PredatorPreyPreset(
        name="Depredador Introducido Tarde",
        description="Población de presa establecida, depredador agregado a mitad de ciclo",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=120,
        prey_initial_eggs=3000,
        prey_initial_larvae=1500,
        prey_initial_pupae=300,
        prey_initial_adults=200,
        predator_initial_larvae=15,
        predator_initial_pupae=5,
        predator_initial_adults=8,
        temperature=28.0,
        humidity=80.0,
        water_availability=1.0,
        category='late_introduction'
    ),
    
    PredatorPreyPreset(
        name="Condiciones Secas",
        description="Control en condiciones de estrés hídrico",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=500,
        prey_initial_larvae=250,
        prey_initial_pupae=50,
        prey_initial_adults=50,
        predator_initial_larvae=10,
        predator_initial_pupae=3,
        predator_initial_adults=5,
        temperature=32.0,
        humidity=40.0,
        water_availability=0.4,
        category='stress'
    ),
    
    PredatorPreyPreset(
        name="Condiciones Tropicales Óptimas",
        description="Máxima interacción depredador-presa en condiciones ideales",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=120,
        prey_initial_eggs=2000,
        prey_initial_larvae=1000,
        prey_initial_pupae=200,
        prey_initial_adults=150,
        predator_initial_larvae=30,
        predator_initial_pupae=10,
        predator_initial_adults=15,
        temperature=28.0,
        humidity=85.0,
        water_availability=1.0,
        category='optimal'
    ),
    
    PredatorPreyPreset(
        name="Largo Plazo (180 días)",
        description="Simulación a largo plazo para evaluar ciclos estacionales",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=180,
        prey_initial_eggs=1000,
        prey_initial_larvae=500,
        prey_initial_pupae=100,
        prey_initial_adults=100,
        predator_initial_larvae=20,
        predator_initial_pupae=5,
        predator_initial_adults=10,
        temperature=26.0,
        humidity=75.0,
        water_availability=0.9,
        category='long_term'
    ),
    
    PredatorPreyPreset(
        name="Escenario de Epidemia",
        description="Gran brote sin control, luego introducción de depredadores",
        prey_species='aedes_aegypti',
        predator_species='toxorhynchites',
        duration=90,
        prey_initial_eggs=10000,
        prey_initial_larvae=5000,
        prey_initial_pupae=1000,
        prey_initial_adults=500,
        predator_initial_larvae=50,
        predator_initial_pupae=15,
        predator_initial_adults=25,
        temperature=29.0,
        humidity=80.0,
        water_availability=1.0,
        category='outbreak'
    ),
]


# Category display names and descriptions
SCENARIO_CATEGORIES = {
    'baseline': {
        'name': 'Escenarios Base',
        'description': 'Condiciones estándar para referencia y comparación'
    },
    'stress': {
        'name': 'Estrés Ambiental',
        'description': 'Condiciones desfavorables que prueban resiliencia poblacional'
    },
    'control': {
        'name': 'Estrategias de Control',
        'description': 'Escenarios de control biológico e intervención'
    },
    'optimal': {
        'name': 'Condiciones Óptimas',
        'description': 'Escenarios ideales de cría y proliferación'
    },
    'outbreak': {
        'name': 'Escenarios de Brote',
        'description': 'Infestaciones a gran escala y condiciones epidémicas'
    }
}

PREDATOR_PREY_CATEGORIES = {
    'balanced': {
        'name': 'Control Balanceado',
        'description': 'Equilibrio entre poblaciones de presa y depredador'
    },
    'weak_control': {
        'name': 'Control Débil',
        'description': 'Depredadores insuficientes para control robusto'
    },
    'strong_control': {
        'name': 'Control Fuerte',
        'description': 'Alta densidad de depredadores para supresión de presa'
    },
    'prey_pressure': {
        'name': 'Alta Presión de Presa',
        'description': 'Poblaciones de presa que superan capacidad de depredador'
    },
    'late_introduction': {
        'name': 'Introducción Tardía',
        'description': 'Depredadores introducidos cuando presa está establecida'
    },
    'stress': {
        'name': 'Estrés Ambiental',
        'description': 'Condiciones adversas reducen eficiencia de control'
    },
    'long_term': {
        'name': 'Largo Plazo',
        'description': 'Simulaciones extendidas para patrones estacionales'
    },
    'outbreak': {
        'name': 'Control de Epidemia',
        'description': 'Respuesta depredadora a brotes de presa'
    }
}


def get_presets_by_category(category: Optional[str] = None) -> Union[List[ScenarioPreset], Dict[str, List[ScenarioPreset]]]:
    """
    Get scenarios organized by category.
    
    Args:
        category: Optional category to filter by. If None, returns all organized.
    
    Returns:
        If category specified: List of scenarios in that category
        If category is None: Dictionary mapping category names to lists of scenarios
    """
    if category is not None:
        # Return presets for specific category
        return [preset for preset in SCENARIO_PRESETS if preset.category == category]
    
    # Return all presets organized by category
    organized: Dict[str, List[ScenarioPreset]] = {}
    for preset in SCENARIO_PRESETS:
        if preset.category not in organized:
            organized[preset.category] = []
        organized[preset.category].append(preset)
    return organized


def get_preset_by_name(name: str) -> Optional[ScenarioPreset]:
    """
    Get scenario preset by name.
    
    Args:
        name: Scenario name
    
    Returns:
        ScenarioPreset instance, or None if not found
    """
    for preset in SCENARIO_PRESETS:
        if preset.name == name:
            return preset
    return None


def validate_parameter(param_name: str, value: float) -> tuple[bool, str]:
    """
    Validate parameter value against defined ranges.
    
    Args:
        param_name: Parameter name (e.g., 'temperature')
        value: Value to validate
    
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    if param_name not in PARAMETER_RANGES:
        return True, ""
    
    range_info = PARAMETER_RANGES[param_name]
    min_val = range_info['min']
    max_val = range_info['max']
    
    if value < min_val or value > max_val:
        return False, f"Value must be between {min_val} and {max_val}"
    
    return True, ""


# ============================================================================
# PREDATOR-PREY HELPER FUNCTIONS
# ============================================================================

def get_predator_prey_presets_by_category(category: Optional[str] = None) -> Union[List[PredatorPreyPreset], Dict[str, List[PredatorPreyPreset]]]:
    """
    Get predator-prey presets organized by category.
    
    Args:
        category: Optional category filter
    
    Returns:
        List of presets if category specified, dict of categories if not
    """
    if category:
        return [p for p in PREDATOR_PREY_PRESETS if p.category == category]
    
    organized = {}
    for preset in PREDATOR_PREY_PRESETS:
        if preset.category not in organized:
            organized[preset.category] = []
        organized[preset.category].append(preset)
    return organized


def get_predator_prey_preset_by_name(name: str) -> Optional[PredatorPreyPreset]:
    """
    Get predator-prey preset by name.
    
    Args:
        name: Preset name
    
    Returns:
        PredatorPreyPreset instance, or None if not found
    """
    for preset in PREDATOR_PREY_PRESETS:
        if preset.name == name:
            return preset
    return None


def get_environmental_preset_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get environmental preset by name.
    
    Args:
        name: Preset name (e.g., 'tropical_optimal')
    
    Returns:
        Dictionary with temperature, humidity, water_availability, or None
    """
    for key, preset in ENVIRONMENTAL_PRESETS.items():
        if preset['name'] == name or key == name:
            return preset
    return None


def get_all_environmental_preset_names() -> List[str]:
    """Get all environmental preset display names."""
    return [p['name'] for p in ENVIRONMENTAL_PRESETS.values()]


def get_all_predator_prey_preset_names() -> List[str]:
    """Get all predator-prey preset display names."""
    return [p.name for p in PREDATOR_PREY_PRESETS]
