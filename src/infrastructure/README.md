# Infrastructure Layer - README

**Directorio:** `src/infrastructure/`  
**Propósito:** Capa de infraestructura que gestiona la comunicación con recursos externos (archivos JSON y motor Prolog) 
---

## 📁 Estructura del Directorio

```
src/infrastructure/
├── __init__.py              # Exportaciones públicas del módulo
├── config.py                # Gestión de configuraciones JSON
├── prolog_bridge.py         # Puente Python-Prolog via PySwip
└── README.md                # Este archivo
```

---

## 📄 Archivos del Módulo

### `__init__.py`

**Propósito:** Define la API pública del módulo infrastructure, exportando clases y funciones principales.

**Exportaciones:**

```python
from infrastructure import (
    # Gestión de configuración
    ConfigManager,
    ConfigurationError,
    SimulationConfig,
    SpeciesConfig,
    EnvironmentConfig,
    load_default_config,
    load_config_from_dir,
    
    # Puente Prolog
    PrologBridge,
    PrologBridgeError,
    create_prolog_bridge
)
```

---

## 🔧 config.py - Gestión de Configuraciones

**Líneas de código:** 568  
**Dependencias:** `json`, `pathlib`, `dataclasses`

### Descripción General

Módulo responsable de cargar, validar y proporcionar acceso tipado a todos los parámetros de configuración del simulador, almacenados en archivos JSON.

### Arquitectura de Clases

```
ConfigurationError (Exception)
    └── Excepción personalizada para errores de configuración

Dataclasses (modelos de datos):
    ├── SimulationConfig        # Parámetros de simulación
    ├── LifeStageConfig         # Parámetros de estadio de vida
    ├── ReproductionConfig      # Parámetros reproductivos
    ├── EnvironmentalSensitivity # Sensibilidad ambiental
    ├── PredationConfig         # Parámetros de depredación
    ├── SpeciesConfig           # Configuración completa de especie
    └── EnvironmentConfig       # Condiciones ambientales

ConfigManager (clase principal)
    └── Gestor central de configuraciones
```

---

### Dataclasses (Modelos de Datos)

#### 1. `SimulationConfig`

**Propósito:** Almacena parámetros generales de la simulación.

**Atributos:**
- `default_days: int` - Duración predeterminada de la simulación en días
- `time_step: int` - Paso de tiempo para avance temporal (usualmente 1 día)
- `random_seed: Optional[int]` - Semilla para reproducibilidad estocástica
- `stochastic_mode: bool` - Activa/desactiva variación estocástica

**Ejemplo de uso:**
```python
sim_config = config_manager.get_simulation_config()
print(f"Simulación: {sim_config.default_days} días")
```

---

#### 2. `LifeStageConfig`

**Propósito:** Parámetros biológicos de un estadio de vida específico.

**Atributos:**
- `duration_min: int` - Duración mínima del estadio (días)
- `duration_max: int` - Duración máxima del estadio (días)
- `survival_to_next: Optional[float]` - Tasa de supervivencia al siguiente estadio [0.0-1.0]
- `survival_daily: Optional[float]` - Supervivencia diaria (para adultos) [0.0-1.0]
- `is_predatory: bool` - Indica si el estadio es depredador
- `predation_rate: Optional[int]` - Presas consumidas por día (si depredador)

**Uso típico:**
```python
species = config_manager.get_species_config('aedes_aegypti')
egg_config = species.life_stages['egg']
print(f"Huevo dura {egg_config.duration_min}-{egg_config.duration_max} días")
```

---

#### 3. `ReproductionConfig`

**Propósito:** Parámetros reproductivos de una especie.

**Atributos:**
- `eggs_per_batch_min: int` - Mínimo de huevos por evento de oviposición
- `eggs_per_batch_max: int` - Máximo de huevos por evento de oviposición
- `oviposition_events: int` - Número de eventos reproductivos en la vida
- `min_age_reproduction_days: int` - Edad mínima para reproducción

**Ejemplo:**
```python
repro = species.reproduction
print(f"Fecundidad: {repro.eggs_per_batch_min}-{repro.eggs_per_batch_max} huevos")
```

---

#### 4. `EnvironmentalSensitivity`

**Propósito:** Define rangos ambientales óptimos y letales para una especie.

**Atributos:**
- `optimal_temperature_min: float` - Temperatura óptima mínima (°C)
- `optimal_temperature_max: float` - Temperatura óptima máxima (°C)
- `lethal_temperature_min: float` - Temperatura letal mínima (°C)
- `lethal_temperature_max: float` - Temperatura letal máxima (°C)
- `optimal_humidity: float` - Humedad relativa óptima (%)

---

#### 5. `PredationConfig`

**Propósito:** Parámetros de la respuesta funcional de Holling tipo II.

**Atributos:**
- `attack_rate: float` - Tasa de ataque (a) en ecuación de Holling
- `handling_time: float` - Tiempo de manipulación (Th)
- `prey_stages: List[str]` - Estadios de presa vulnerables

**Ecuación implementada:**
$$C = \frac{a \cdot N}{1 + a \cdot T_h \cdot N}$$

---

#### 6. `SpeciesConfig`

**Propósito:** Configuración completa de una especie (contenedor maestro).

**Atributos:**
- `species_id: str` - Identificador único (e.g., 'aedes_aegypti')
- `display_name: str` - Nombre para visualización
- `life_stages: Dict[str, LifeStageConfig]` - Diccionario de estadios
- `reproduction: ReproductionConfig` - Parámetros reproductivos
- `environmental_sensitivity: Optional[EnvironmentalSensitivity]` - Sensibilidad ambiental
- `predation: Optional[PredationConfig]` - Configuración de depredación (solo depredadores)

---

#### 7. `EnvironmentConfig`

**Propósito:** Condiciones ambientales iniciales de la simulación.

**Atributos:**
- `temperature: float` - Temperatura ambiental (°C) o diccionario con parámetros estocásticos
- `humidity: float` - Humedad relativa (%) o diccionario con parámetros estocásticos
- `carrying_capacity: int` - Capacidad de carga del hábitat
- `water_availability: float` - Disponibilidad de agua [0.0-1.0]

---

### Clase Principal: `ConfigManager`

**Propósito:** Gestor central que carga, valida y proporciona acceso a todas las configuraciones.

#### Constructor

```python
def __init__(self, config_dir: Optional[Union[str, Path]] = None)
```

**Parámetros:**
- `config_dir` - Ruta al directorio de configuración (default: `<proyecto>/config`)

**Comportamiento:**
1. Valida que el directorio de configuración existe
2. Carga `default_config.json`
3. Carga todas las configuraciones de especies referenciadas
4. Carga configuración ambiental
5. Valida integridad de datos

**Raises:**
- `ConfigurationError` - Si el directorio no existe o archivos son inválidos

---

#### Métodos Privados (Internos)

##### `_load_json_file(file_path: Path) -> Dict[str, Any]`

Carga y parsea un archivo JSON con manejo de errores robusto.

**Validaciones:**
- Existencia del archivo
- Sintaxis JSON válida
- Codificación UTF-8

---

##### `_load_all_configs()`

Orquesta la carga secuencial de todas las configuraciones:
1. `default_config.json`
2. Archivos de especies (según referencia en default_config)
3. Archivo de ambiente

---

##### `_load_default_config()`

Carga y valida el archivo maestro de configuración.

**Validaciones:**
- Presencia de campos requeridos: `simulation`, `initial_populations`
- Formato correcto de datos

---

##### `_load_species_config(file_path: Path)`

Carga configuración de una especie y la transforma en objetos `SpeciesConfig`.

**Proceso:**
1. Lee JSON de especie
2. Parsea estadios de vida → `LifeStageConfig`
3. Parsea reproducción → `ReproductionConfig`
4. Parsea sensibilidad ambiental (opcional)
5. Parsea depredación (opcional para depredadores)
6. Valida consistencia de datos
7. Almacena en `self.species_configs[species_id]`

---

##### `_load_environment_config(file_path: Path)`

Carga configuración ambiental y la transforma en `EnvironmentConfig`.

---

#### Métodos Públicos (API Principal)

##### `get_simulation_config() -> SimulationConfig`

Retorna parámetros de simulación como objeto tipado.

**Ejemplo:**
```python
sim = config.get_simulation_config()
for day in range(sim.default_days):
    # Ejecutar simulación
```

---

##### `get_initial_populations() -> Dict[str, Dict[str, int]]`

Retorna poblaciones iniciales para todas las especies.

**Estructura retornada:**
```python
{
    'aedes_aegypti': {
        'egg': 200,
        'larva_l1': 150,
        ...
    },
    'toxorhynchites': {
        'egg': 20,
        ...
    }
}
```

---

##### `get_species_config(species_id: str) -> SpeciesConfig`

Obtiene configuración completa de una especie.

**Parámetros:**
- `species_id` - Identificador de especie (e.g., 'aedes_aegypti')

**Raises:**
- `ConfigurationError` - Si la especie no existe

**Ejemplo:**
```python
aedes = config.get_species_config('aedes_aegypti')
print(aedes.display_name)  # "Aedes aegypti"
```

---

##### `get_all_species_ids() -> List[str]`

Lista todos los IDs de especies cargadas.

**Retorna:** `['aedes_aegypti', 'toxorhynchites']`

---

##### `get_environment_config() -> EnvironmentConfig`

Retorna configuración ambiental.

**Ejemplo:**
```python
env = config.get_environment_config()
print(f"Temperatura: {env.temperature}°C")
print(f"Capacidad de carga: {env.carrying_capacity}")
```

---

##### `get_life_stage_duration(species_id: str, stage: str) -> tuple[int, int]`

Obtiene rango de duración para un estadio específico.

**Retorna:** `(min_days, max_days)`

**Ejemplo:**
```python
min_days, max_days = config.get_life_stage_duration('aedes_aegypti', 'egg')
print(f"Huevo: {min_days}-{max_days} días")  # "Huevo: 2-7 días"
```

---

##### `get_survival_rate(species_id: str, stage: str) -> float`

Obtiene tasa de supervivencia para un estadio.

**Retorna:** Valor entre 0.0 y 1.0

**Ejemplo:**
```python
survival = config.get_survival_rate('aedes_aegypti', 'egg')
print(f"Supervivencia: {survival * 100}%")  # "Supervivencia: 80%"
```

---

##### `is_predatory_stage(species_id: str, stage: str) -> bool`

Verifica si un estadio es depredador.

**Ejemplo:**
```python
is_pred = config.is_predatory_stage('toxorhynchites', 'larva_l4')
print(is_pred)  # True
```

---

##### `get_predation_rate(species_id: str, stage: str) -> Optional[int]`

Obtiene tasa de depredación (presas/día) si el estadio es depredador.

**Retorna:** Número entero o `None` si no es depredador

---

##### `reload_configs()`

Recarga todas las configuraciones desde disco.

**Uso:** Útil para cambios dinámicos sin reiniciar la aplicación.

---

##### `validate_all() -> List[str]`

Ejecuta validación exhaustiva de todas las configuraciones cargadas.

**Validaciones realizadas:**
- Días de simulación > 0
- Time step > 0
- Duraciones min ≤ max
- Tasas de supervivencia en rango [0, 1]
- Fecundidad min ≤ max
- Poblaciones iniciales corresponden a especies existentes

**Retorna:** Lista de warnings/errores (vacía si todo es válido)

**Ejemplo:**
```python
warnings = config.validate_all()
if warnings:
    for warning in warnings:
        print(f"⚠ {warning}")
else:
    print("✓ Configuración válida")
```

---

### Funciones de Conveniencia

#### `load_default_config() -> ConfigManager`

Crea un `ConfigManager` usando rutas predeterminadas.

**Uso:**
```python
from infrastructure import load_default_config

config = load_default_config()
```

---

#### `load_config_from_dir(config_dir: Union[str, Path]) -> ConfigManager`

Crea un `ConfigManager` desde un directorio específico.

**Parámetros:**
- `config_dir` - Ruta al directorio de configuración

**Uso:**
```python
config = load_config_from_dir('/path/to/custom/config')
```

---

## 🌉 prolog_bridge.py - Puente Python-Prolog

**Líneas de código:** 714  
**Dependencias:** `pyswip`, `pathlib`, `logging`, `config.py`

### Descripción General

Implementa la interfaz entre Python y el motor de inferencia SWI-Prolog. Gestiona la inicialización del motor, carga de archivos `.pl`, inyección de parámetros como hechos dinámicos, y ejecución de consultas lógicas.

### Arquitectura

```
PrologBridgeError (Exception)
    └── Excepción para errores de Prolog

PrologBridge (clase principal)
    ├── Inicialización de PySwip
    ├── Carga de knowledge base (.pl files)
    ├── Inyección de parámetros (JSON → Prolog)
    ├── Métodos de consulta (query, query_once, query_all)
    ├── Gestión de poblaciones
    ├── Análisis ecológico
    └── Reset de estado

create_prolog_bridge() (función de conveniencia)
```

---

### Clase: `PrologBridge`

**Propósito:** Puente bidireccional entre Python y Prolog para simulación de dinámica poblacional.

#### Atributos

- `prolog: Prolog` - Instancia de PySwip
- `config_manager: ConfigManager` - Gestor de configuración
- `prolog_dir: Path` - Directorio de archivos `.pl`
- `loaded_files: List[Path]` - Archivos Prolog cargados
- `parameters_loaded: bool` - Flag de parámetros inyectados

---

#### Constructor

```python
def __init__(
    self, 
    config_manager: ConfigManager,
    prolog_dir: Optional[Union[str, Path]] = None
)
```

**Parámetros:**
- `config_manager` - Instancia de ConfigManager con configuraciones cargadas
- `prolog_dir` - Ruta a archivos Prolog (default: `<proyecto>/src/prolog`)

**Proceso de inicialización:**
1. Valida que el directorio Prolog existe
2. Inicializa motor SWI-Prolog via PySwip
3. Carga knowledge base en orden correcto
4. Prepara para inyección de parámetros

**Raises:**
- `PrologBridgeError` - Si falla inicialización o carga de archivos

---

#### Métodos Privados

##### `_load_knowledge_base()`

Carga archivos `.pl` en el orden correcto para evitar dependencias no resueltas.

**Orden de carga:**
1. `species_ontology.pl` - Taxonomía y roles ecológicos
2. `biological_facts.pl` - Contenedor de parámetros dinámicos
3. `ecological_rules.pl` - Reglas de inferencia ecológica
4. `population_dynamics.pl` - Dinámica poblacional
5. `agent_decisions.pl` - Decisiones de agentes AIMA

**Logging:** Registra cada archivo cargado exitosamente

---

##### `_clear_parameters()`

Limpia todos los parámetros dinámicos en Prolog.

**Implementación:** Ejecuta `clear_all_parameters/0` definido en `biological_facts.pl`

---

##### `_inject_species_parameters(species_id: str)`

Inyecta todos los parámetros de una especie en Prolog.

**Parámetros inyectados:**
- Duraciones de estadios → `load_stage_duration/4`
- Tasas de supervivencia → `load_survival_rate/4`
- Fecundidad → `load_fecundity/4`
- Tasas de depredación → `load_predation_rate/3`
- Respuesta funcional → `load_functional_response/3`

**Mecanismo:** Usa predicados `load_*` que internamente llaman `assertz/1`

---

##### `_inject_environment_parameters()`

Inyecta parámetros ambientales en Prolog.

**Parámetros:**
- Temperatura media
- Humedad media
- Capacidad de carga
- Disponibilidad de agua

**Target:** Predicado `environmental_param/2`

---

##### `_get_next_stage(current_stage: str) -> Optional[str]`

Determina el siguiente estadio en la secuencia de desarrollo.

**Secuencia:**
`egg → larva_l1 → larva_l2 → larva_l3 → larva_l4 → pupa → adult_female/male`

---

##### `_assert(fact: str)`

Ejecuta un predicado de carga que internamente usa `assertz/1`.

**Ejemplo:**
```python
self._assert("load_stage_duration(aedes_aegypti, egg, 2, 7)")
```

---

#### Métodos Públicos - Gestión de Parámetros

##### `inject_parameters()`

Inyecta todos los parámetros de configuración en Prolog.

**Proceso:**
1. Limpia parámetros existentes
2. Itera sobre todas las especies
3. Inyecta parámetros de cada especie
4. Inyecta parámetros ambientales
5. Marca `parameters_loaded = True`

**Uso:**
```python
bridge = PrologBridge(config_manager)
bridge.inject_parameters()
```

---

##### `verify_parameters_loaded() -> Dict[str, bool]`

Verifica que todos los parámetros fueron cargados correctamente.

**Retorna:**
```python
{
    'aedes_aegypti': True,
    'toxorhynchites': True
}
```

**Mecanismo:** Consulta `parameters_loaded(Species)` en Prolog

---

#### Métodos Públicos - Consultas Prolog

##### `query(query_string: str) -> Iterator[Dict[str, Any]]`

Ejecuta consulta Prolog y retorna iterador de resultados.

**Ejemplo:**
```python
for result in bridge.query("species(X, aedes)"):
    print(result['X'])  # 'aedes_aegypti'
```

---

##### `query_once(query_string: str) -> Optional[Dict[str, Any]]`

Ejecuta consulta y retorna solo el primer resultado.

**Ejemplo:**
```python
result = bridge.query_once("genus_of(aedes_aegypti, G)")
print(result['G'])  # 'aedes'
```

---

##### `query_all(query_string: str) -> List[Dict[str, Any]]`

Ejecuta consulta y retorna todos los resultados como lista.

**Ejemplo:**
```python
stages = bridge.query_all("life_stage(X)")
stage_names = [r['X'] for r in stages]
```

---

##### `query_yes_no(query_string: str) -> bool`

Ejecuta consulta booleana (sin variables).

**Retorna:** `True` si la consulta tiene éxito, `False` en caso contrario

**Ejemplo:**
```python
if bridge.query_yes_no("is_predator(toxorhynchites)"):
    print("Toxorhynchites es depredador")
```

---

#### Métodos Públicos - Gestión de Poblaciones

##### `initialize_population(species_id: str, stage: str, count: int, day: int = 0)`

Inicializa el estado poblacional de un estadio en Prolog.

**Efecto:** Crea hecho `population_state(Species, Stage, Count, Day)`

**Ejemplo:**
```python
bridge.initialize_population('aedes_aegypti', 'egg', 200, 0)
```

---

##### `initialize_all_populations()`

Inicializa todas las poblaciones desde `initial_populations` de la configuración.

**Uso:**
```python
bridge.initialize_all_populations()
```

---

##### `set_environment_state(day: int, temperature: float, humidity: float)`

Establece condiciones ambientales para un día específico.

**Efecto:** Crea hecho `environmental_state(Day, Temp, Humidity)`

---

##### `get_population_state(species_id: str, day: int) -> Dict[str, int]`

Obtiene población de todos los estadios de una especie en un día.

**Retorna:**
```python
{
    'egg': 200,
    'larva_l1': 150,
    'larva_l2': 120,
    ...
}
```

---

##### `get_total_population(species_id: str, day: int) -> int`

Calcula población total de una especie en un día.

**Implementación:** Consulta `total_population(Species, Day, Total)` en Prolog

---

##### `get_population_trend(species_id: str, day: int) -> str`

Obtiene tendencia poblacional.

**Valores posibles:** `'growing'`, `'stable'`, `'declining'`, `'initial'`

---

##### `advance_population(species_id: str, from_day: int, to_day: int)`

Avanza la simulación poblacional de un día a otro.

**Implementación:** Llama a `project_population/4` en Prolog

**Ejemplo:**
```python
# Avanzar del día 0 al día 10
bridge.advance_population('aedes_aegypti', 0, 10)
```

---

#### Métodos Públicos - Análisis Ecológico

##### `evaluate_biocontrol(day: int) -> Optional[str]`

Evalúa efectividad del biocontrol.

**Retorna:** `'highly_effective'`, `'effective'`, `'promising'`, `'ineffective'`, `'requires_analysis'`

**Implementación:** Consulta `biocontrol_viable(Day, Assessment)`

---

##### `check_ecological_equilibrium(day: int) -> bool`

Verifica si el sistema está en equilibrio ecológico.

**Criterios:**
- Ambas especies con tendencia estable
- Ratio depredador-presa en rango biológico (0.01-0.5)

---

##### `get_extinction_risk(species_id: str, day: int) -> Optional[str]`

Evalúa riesgo de extinción según MVP (Minimum Viable Population).

**Retorna:** `'critical'`, `'high'`, `'moderate'`, `'low'`

---

#### Métodos Públicos - Utilidades

##### `reset()`

Reinicia el estado de Prolog eliminando todos los hechos dinámicos.

**Elimina:**
- `population_state/4`
- `environmental_state/3`
- `agent_state/5`
- `agent_species/2`
- Todos los parámetros cargados

**Uso:** Para ejecutar múltiples simulaciones sin reiniciar Python

---

##### `get_loaded_files_info() -> List[str]`

Retorna lista de archivos `.pl` cargados.

---

##### `__repr__() -> str`

Representación en string del objeto.

**Ejemplo:** `"PrologBridge(files=5, parameters_loaded=True)"`

---

### Función de Conveniencia

#### `create_prolog_bridge(config_manager: Optional[ConfigManager] = None) -> PrologBridge`

Crea y configura completamente un PrologBridge listo para usar.

**Proceso:**
1. Carga configuración (si no se proporciona)
2. Inicializa PrologBridge
3. Inyecta parámetros
4. Inicializa poblaciones

**Uso:**
```python
from infrastructure import create_prolog_bridge

bridge = create_prolog_bridge()
# Bridge listo para simulación
```

---

## 🚀 Flujo de Uso Típico

### Ejemplo Completo

```python
from infrastructure import load_default_config, PrologBridge

# 1. Cargar configuración
config = load_default_config()

# 2. Validar configuración
warnings = config.validate_all()
if warnings:
    print("Advertencias de configuración:")
    for w in warnings:
        print(f"  - {w}")

# 3. Inicializar Prolog bridge
bridge = PrologBridge(config)

# 4. Inyectar parámetros en Prolog
bridge.inject_parameters()

# 5. Verificar inyección
verification = bridge.verify_parameters_loaded()
assert all(verification.values()), "Falló carga de parámetros"

# 6. Inicializar poblaciones
bridge.initialize_all_populations()

# 7. Configurar ambiente inicial
bridge.set_environment_state(0, 27.0, 75.0)

# 8. Ejecutar simulación
for day in range(1, 31):  # 30 días
    bridge.advance_population('aedes_aegypti', day-1, day)
    bridge.advance_population('toxorhynchites', day-1, day)
    
    # Análisis diario
    aedes_pop = bridge.get_total_population('aedes_aegypti', day)
    toxo_pop = bridge.get_total_population('toxorhynchites', day)
    
    print(f"Día {day}: Aedes={aedes_pop}, Toxo={toxo_pop}")
    
    # Evaluar biocontrol cada 7 días
    if day % 7 == 0:
        assessment = bridge.evaluate_biocontrol(day)
        print(f"  Biocontrol: {assessment}")

# 9. Análisis final
equilibrium = bridge.check_ecological_equilibrium(30)
risk_aedes = bridge.get_extinction_risk('aedes_aegypti', 30)
risk_toxo = bridge.get_extinction_risk('toxorhynchites', 30)

print(f"\nEquilibrio ecológico: {equilibrium}")
print(f"Riesgo extinción Aedes: {risk_aedes}")
print(f"Riesgo extinción Toxo: {risk_toxo}")

# 10. Reset para nueva simulación
bridge.reset()
```

---

## 📊 Diagrama de Flujo de Datos

```
┌──────────────────────┐
│  JSON Config Files   │
│  • default_config    │
│  • species configs   │
│  • environment       │
└──────────┬───────────┘
           │ read & parse
           ▼
┌──────────────────────┐
│   ConfigManager      │
│  • Load & validate   │
│  • Type conversion   │
│  • Provide getters   │
└──────────┬───────────┘
           │ provide configs
           ▼
┌──────────────────────┐
│   PrologBridge       │
│  • Init PySwip       │
│  • Load .pl files    │
│  • Inject params     │
└──────────┬───────────┘
           │ assertz()
           ▼
┌──────────────────────┐
│  Prolog Knowledge    │
│  Base (SWI-Prolog)   │
│  • Dynamic facts     │
│  • Inference rules   │
│  • Query execution   │
└──────────────────────┘
```

---

## 🔍 Validación y Testing

### Scripts de Prueba

1. **`test_config.py`**
   - Valida carga de JSON
   - Verifica conversión a dataclasses
   - Prueba todos los getters
   - Ejecuta validación completa

2. **`test_prolog_bridge.py`**
   - Verifica inicialización de PySwip
   - Prueba carga de archivos .pl
   - Valida inyección de parámetros
   - Ejecuta consultas de prueba
   - Simula dinámica poblacional básica

### Ejecutar Tests

```bash
cd src
python test_config.py
python test_prolog_bridge.py
```

---

## ⚙️ Configuración de Logging

El módulo `prolog_bridge.py` usa logging estándar de Python:

```python
import logging

# Ajustar nivel de detalle
logging.basicConfig(level=logging.DEBUG)  # Muy detallado
logging.basicConfig(level=logging.INFO)   # Normal (default)
logging.basicConfig(level=logging.WARNING) # Solo advertencias
```

---

## 🐛 Manejo de Errores

### Excepciones Personalizadas

1. **`ConfigurationError`**
   - Lanzada por: `ConfigManager`
   - Causas: Archivo no encontrado, JSON inválido, datos inconsistentes
   - Manejo: Verificar rutas y estructura de JSON

2. **`PrologBridgeError`**
   - Lanzada por: `PrologBridge`
   - Causas: Fallo en PySwip, archivo .pl no encontrado, query inválida
   - Manejo: Verificar instalación de SWI-Prolog y sintaxis Prolog

### Ejemplo de Manejo

```python
from infrastructure import (
    load_default_config,
    ConfigurationError,
    PrologBridge,
    PrologBridgeError
)

try:
    config = load_default_config()
    bridge = PrologBridge(config)
    bridge.inject_parameters()
except ConfigurationError as e:
    print(f"Error de configuración: {e}")
    # Revisar archivos JSON
except PrologBridgeError as e:
    print(f"Error de Prolog: {e}")
    # Revisar instalación de SWI-Prolog
```

---

## 📝 Notas Técnicas

### Dependencias Externas

- **PySwip:** Requiere SWI-Prolog instalado en el sistema
- **dataclasses:** Incluido en Python 3.7+
- **pathlib:** Incluido en Python 3.4+

### Compatibilidad

- Python >= 3.10 (type hints con `|` y `tuple[...]`)
- SWI-Prolog >= 8.4

### Performance

- **ConfigManager:** Carga instantánea (~50ms para 4 archivos JSON)
- **PrologBridge:** Inicialización ~200ms (carga de 5 archivos .pl)
- **Inyección de parámetros:** ~100ms (40+ hechos dinámicos)

---

## 🔗 Referencias

- **Documentación Prolog:** Ver `src/prolog/PROLOG_DOCUMENTATION.md`
- **Plan de Desarrollo:** Ver `PLAN_DE_DESARROLLO.md`
- **Configuraciones JSON:** Ver `config/`

---

**Versión:** 1.0  
**Estado:** Producción - Completamente funcional
