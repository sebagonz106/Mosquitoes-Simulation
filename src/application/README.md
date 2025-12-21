# Capa de Aplicación - Sistema de Simulación de Mosquitos

## Descripción General

La capa de aplicación constituye el núcleo de la lógica de negocio del sistema de simulación de poblaciones de mosquitos. Implementa los principios de **Clean Architecture** (Arquitectura Limpia), separando las reglas de negocio de los detalles de implementación y garantizando la independencia de frameworks, bases de datos e interfaces externas.

Esta capa actúa como intermediaria entre la capa de presentación (interfaces de usuario) y las capas de dominio e infraestructura, orquestando las operaciones del sistema mediante **Casos de Uso** (Use Cases) bien definidos. Cada caso de uso representa una operación completa del sistema, como ejecutar una simulación, comparar escenarios o gestionar checkpoints.


### Responsabilidades

La capa de aplicación es responsable de:

- **Orquestación**: Coordinar servicios de dominio e infraestructura
- **Validación**: Verificar integridad de datos de entrada antes de procesamiento
- **Transformación**: Convertir datos entre formatos (DTOs) apropiados para cada capa
- **Gestión de Estado**: Mantener checkpoints y restaurar simulaciones
- **Análisis Comparativo**: Comparar múltiples escenarios de simulación
- **Configuración**: Proporcionar acceso a parámetros biológicos de especies


## Estructura de Directorios

```
application/
├── services/              # Servicios de negocio
│   ├── simulation_service.py
│   ├── population_service.py
│   └── agent_service.py
├── use_cases/             # Casos de uso (operaciones del sistema)
│   ├── base.py
│   ├── run_population_simulation.py
│   ├── run_agent_simulation.py
│   ├── run_hybrid_simulation.py
│   ├── compare_scenarios.py
│   ├── manage_checkpoints.py
│   └── get_available_configurations.py
├── checkpoints/           # Almacenamiento de checkpoints (JSON)
├── dtos.py               # Data Transfer Objects
├── helpers.py            # Utilidades auxiliares
└── visualization.py      # Funciones de visualización
```

---

## Módulos y Componentes

### 1. Data Transfer Objects (`dtos.py`)

Define estructuras de datos inmutables para transferencia de información entre capas del sistema.

#### 1.1 SimulationConfig

**Descripción**: Encapsula todos los parámetros necesarios para configurar y ejecutar una simulación poblacional o basada en agentes.

**Atributos**:
- `species_id` (str): Identificador de especie (ej. 'aedes_aegypti', 'anopheles_gambiae')
- `duration_days` (int): Duración de simulación en días (1-3650)
- `initial_eggs` (int): Población inicial de huevos
- `initial_larvae` (Union[List[int], int]): Población inicial de larvas (puede ser [L1,L2,L3,L4] o total)
- `initial_pupae` (int): Población inicial de pupas
- `initial_adults` (int): Población inicial de adultos
- `temperature` (Optional[float]): Temperatura ambiental en °C (-10 a 50)
- `humidity` (Optional[float]): Humedad relativa (0-100%)
- `water_availability` (float): Disponibilidad de agua para oviposición (0-1)
- `random_seed` (Optional[int]): Semilla para reproducibilidad estocástica

**Métodos principales**:

```python
def validate(self) -> tuple[bool, List[str]]:
    """
    Valida parámetros de configuración.
    
    Returns:
        (is_valid, error_messages): Tupla con validez y lista de errores
    """
```

**Ejemplo de uso**:

```python
from application.dtos import SimulationConfig

# Configuración para simulación de Aedes aegypti
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=100,
    initial_eggs=0,
    initial_larvae=0,
    initial_pupae=0,
    initial_adults=50,
    temperature=28.0,      # Temperatura óptima para desarrollo
    humidity=80.0,         # Humedad favorable
    water_availability=0.8 # 80% disponibilidad de sitios de oviposición
)

# Validar configuración
is_valid, errors = config.validate()
if not is_valid:
    print(f"Errores de validación: {errors}")
```

#### 1.2 PopulationResult

**Descripción**: Contiene resultados completos de una simulación poblacional, incluyendo trayectorias temporales y estadísticas agregadas.

**Atributos**:
- `species_id` (str): Identificador de especie simulada
- `days` (np.ndarray): Vector de días [0, 1, 2, ..., N]
- `eggs` (np.ndarray): Evolución temporal de huevos
- `larvae` (np.ndarray): Evolución temporal de larvas totales
- `pupae` (np.ndarray): Evolución temporal de pupas
- `adults` (np.ndarray): Evolución temporal de adultos
- `total_population` (np.ndarray): Evolución temporal de población total
- `statistics` (Dict): Estadísticas de resumen (pico, extinción, promedios)

**Métodos principales**:

```python
def to_dict(self) -> Dict:
    """Convierte a diccionario para serialización JSON."""

def from_dict(cls, data: Dict) -> 'PopulationResult':
    """Crea instancia desde diccionario."""

def get_final_state(self) -> Dict:
    """Obtiene estado final para checkpointing."""
```

**Ejemplo de uso**:

```python
from application.services.simulation_service import SimulationService

service = SimulationService()
result = service.run_population_simulation(config)

# Acceder a trayectorias
print(f"Día final: {result.days[-1]}")
print(f"Población final: {result.total_population[-1]:.0f}")

# Estadísticas
print(f"Pico poblacional: {result.statistics['peak_population']} "
      f"en día {result.statistics['peak_day']}")

if result.statistics.get('extinction_day'):
    print(f"Extinción en día: {result.statistics['extinction_day']}")
```

#### 1.3 AgentResult

**Descripción**: Contiene resultados de una simulación basada en agentes, con estadísticas de agentes individuales (vectores y depredadores).

**Atributos**:
- `num_vectors_initial` (int): Número inicial de vectores
- `num_predators_initial` (int): Número inicial de depredadores
- `num_vectors_final` (int): Número final de vectores vivos
- `num_predators_final` (int): Número final de depredadores vivos
- `total_eggs_laid` (int): Total de huevos depositados
- `total_prey_consumed` (int): Total de presas consumidas por depredadores
- `daily_stats` (List[Dict]): Estadísticas diarias detalladas

**Métodos principales**:

```python
def get_survival_rate_vectors(self) -> float:
    """Calcula tasa de supervivencia de vectores."""

def get_survival_rate_predators(self) -> float:
    """Calcula tasa de supervivencia de depredadores."""

def get_average_eggs_per_vector(self) -> float:
    """Calcula promedio de huevos por vector."""

def get_average_prey_per_predator(self) -> float:
    """Calcula promedio de presas por depredador."""

def get_statistics(self) -> Dict:
    """Obtiene estadísticas estandarizadas comparables con PopulationResult."""
```

**Ejemplo de uso**:

```python
result = service.run_agent_simulation(config, num_predators=5)

# Métricas de supervivencia
print(f"Supervivencia vectores: {result.get_survival_rate_vectors():.2%}")
print(f"Supervivencia depredadores: {result.get_survival_rate_predators():.2%}")

# Métricas de comportamiento
print(f"Huevos por vector: {result.get_average_eggs_per_vector():.1f}")
print(f"Presas por depredador: {result.get_average_prey_per_predator():.1f}")
```

#### 1.4 HybridResult

**Descripción**: Encapsula resultados de una simulación híbrida, combinando resultados de simulaciones poblacional y basada en agentes ejecutadas en paralelo con parámetros idénticos.

**Atributos**:
- `population_result` (PopulationResult): Resultado de simulación poblacional
- `agent_result` (AgentResult): Resultado de simulación basada en agentes
- `comparison_data` (Dict[str, Any]): Datos comparativos entre ambos enfoques

**Métodos principales**:

```python
def get_comparison_summary(self) -> Dict:
    """
    Obtiene resumen comparativo entre enfoques poblacional y basado en agentes.
    
    Returns:
        Diccionario con métricas comparativas (picos, finales, diferencias)
    """
```

**Ejemplo de uso**:

```python
hybrid_result = service.run_hybrid_simulation(config, num_predators=5)

# Acceder a resultados individuales
pop_result = hybrid_result.population_result
agent_result = hybrid_result.agent_result

# Obtener resumen comparativo
summary = hybrid_result.get_comparison_summary()
print(f"Pico poblacional (EDO): {summary['population_peak']:.0f}")
print(f"Pico poblacional (ABM): {summary['agent_peak']:.0f}")
print(f"Diferencia absoluta: {summary['difference_peak']:.0f}")
```

#### 1.5 ComparisonResult

**Descripción**: Contiene resultados de comparación de múltiples escenarios de simulación, permitiendo análisis de sensibilidad y optimización de parámetros.

**Atributos**:
- `scenario_names` (List[str]): Nombres de escenarios comparados
- `results` (Dict[str, Union[PopulationResult, AgentResult]]): Resultados por escenario
- `comparison` (Dict[str, Any]): Métricas comparativas agregadas

**Métodos principales**:

```python
def get_best_scenario(self, metric: str = 'peak_population') -> str:
    """Identifica mejor escenario según métrica especificada."""

def get_worst_scenario(self, metric: str = 'peak_population') -> str:
    """Identifica peor escenario según métrica especificada."""

def get_scenario_ranking(self, metric: str = 'peak_population') -> List[tuple]:
    """Obtiene ranking de escenarios ordenados por métrica."""
```

---

### 2. Servicios (`services/`)

Los servicios contienen la lógica de negocio principal y coordinan operaciones entre capas de dominio e infraestructura.

#### 2.1 SimulationService (`simulation_service.py`)

**Descripción**: Servicio principal de orquestación que coordina ejecución de simulaciones, gestión de checkpoints y comparación de escenarios.

**Métodos principales**:

```python
def run_population_simulation(
    self,
    config: SimulationConfig
) -> PopulationResult:
    """
    Ejecuta simulación poblacional basada en EDOs.
    
    Utiliza el modelo matemático de la capa de dominio para resolver
    ecuaciones diferenciales que describen dinámicas poblacionales.
    
    Args:
        config: Configuración de simulación
        
    Returns:
        PopulationResult con trayectorias y estadísticas
    """
```

```python
def run_agent_simulation(
    self,
    config: SimulationConfig,
    num_predators: int = 0,
    predator_species_id: Optional[str] = None
) -> AgentResult:
    """
    Ejecuta simulación basada en agentes.
    
    Modela individuos discretos con comportamientos autónomos,
    incluyendo interacciones depredador-presa.
    
    Args:
        config: Configuración de simulación
        num_predators: Número de agentes depredadores
        predator_species_id: ID de especie depredadora
        
    Returns:
        AgentResult con estadísticas de agentes
    """
```

```python
def run_hybrid_simulation(
    self,
    config: SimulationConfig,
    num_predators: int = 0,
    predator_species_id: Optional[str] = None
) -> HybridResult:
    """
    Ejecuta simulación híbrida (poblacional + agentes en paralelo).
    
    Permite validación cruzada y análisis comparativo entre
    enfoques determinístico (EDOs) y estocástico (ABM).
    
    Args:
        config: Configuración de simulación
        num_predators: Número de depredadores para simulación ABM
        predator_species_id: ID de especie depredadora
        
    Returns:
        HybridResult con ambos resultados y datos comparativos
    """
```

```python
def save_checkpoint(
    self,
    result: Union[PopulationResult, AgentResult, HybridResult],
    config: SimulationConfig,
    simulation_type: str,
    checkpoint_name: Optional[str] = None
) -> Path:
    """
    Guarda checkpoint de simulación en formato JSON.
    
    Los checkpoints permiten persistir estado completo de simulación
    para análisis posterior o reanudación.
    
    Args:
        result: Resultado de simulación a guardar
        config: Configuración utilizada
        simulation_type: Tipo ('population', 'agent', 'hybrid')
        checkpoint_name: Nombre personalizado (opcional)
        
    Returns:
        Path al archivo de checkpoint creado
    """
```

```python
def load_checkpoint(
    self,
    checkpoint_path: Union[str, Path]
) -> Tuple[SimulationConfig, Union[PopulationResult, AgentResult, HybridResult], str]:
    """
    Carga checkpoint desde archivo JSON.
    
    Args:
        checkpoint_path: Ruta al archivo de checkpoint
        
    Returns:
        Tupla (config, result, simulation_type)
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el archivo está corrupto
    """
```

```python
def compare_scenarios(
    self,
    scenarios: Dict[str, SimulationConfig],
    simulation_type: str = 'population',
    num_predators: int = 0
) -> ComparisonResult:
    """
    Compara múltiples escenarios de simulación.
    
    Útil para análisis de sensibilidad, optimización de parámetros
    y estudios de control vectorial.
    
    Args:
        scenarios: Diccionario {nombre: config} de escenarios
        simulation_type: Tipo de simulación ('population' o 'agent')
        num_predators: Número de depredadores (solo para 'agent')
        
    Returns:
        ComparisonResult con resultados y comparaciones
    """
```

**Ejemplo de uso completo**:

```python
from application.services.simulation_service import SimulationService
from application.dtos import SimulationConfig

service = SimulationService()

# Configurar simulación
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=60,
    initial_eggs=0,
    initial_larvae=0,
    initial_pupae=0,
    initial_adults=50,
    temperature=28.0,
    humidity=80.0,
    water_availability=0.8
)

# Ejecutar simulación poblacional
result = service.run_population_simulation(config)
print(f"Pico poblacional: {result.statistics['peak_population']}")

# Guardar checkpoint
checkpoint_path = service.save_checkpoint(
    result=result,
    config=config,
    simulation_type='population',
    checkpoint_name='aedes_60dias.json'
)
print(f"Checkpoint guardado en: {checkpoint_path}")

# Cargar checkpoint posteriormente
loaded_config, loaded_result, sim_type = service.load_checkpoint(checkpoint_path)
print(f"Checkpoint cargado: {sim_type}")
```

#### 2.2 PopulationService (`population_service.py`)

**Descripción**: Servicio especializado en simulaciones poblacionales basadas en modelos matemáticos (EDOs). Encapsula acceso a parámetros biológicos de especies y configuración del modelo.

**Métodos principales**:

```python
def run_simulation(self, config: SimulationConfig) -> PopulationResult:
    """
    Ejecuta simulación poblacional utilizando solver de EDOs.
    
    Implementa modelo de dinámica poblacional estructurado por estadios:
    - Huevos: Oviposición y eclosión
    - Larvas: Desarrollo larvario (L1-L4)
    - Pupas: Metamorfosis
    - Adultos: Reproducción y mortalidad
    
    Args:
        config: Configuración de simulación
        
    Returns:
        PopulationResult con trayectorias temporales
    """
```

```python
def get_species_info(self, species_id: str) -> Dict:
    """
    Obtiene información biológica completa de una especie.
    
    Incluye tasas de desarrollo, supervivencia, fecundidad y otros
    parámetros parametrizados según literatura científica.
    
    Args:
        species_id: Identificador de especie
        
    Returns:
        Diccionario con parámetros biológicos
    """
```

**Ejemplo de uso**:

```python
from application.services.population_service import PopulationService

service = PopulationService()

# Obtener parámetros biológicos de Aedes aegypti
info = service.get_species_info('aedes_aegypti')
print(f"Fecundidad: {info['fecundity']} huevos/hembra/día")
print(f"Tasa desarrollo huevo→larva: {info['development_rates']['egg_to_larva']}")
print(f"Supervivencia larvaria: {info['survival_rates']['larva']:.2%}")
```

#### 2.3 AgentService (`agent_service.py`)

**Descripción**: Servicio especializado en simulaciones basadas en agentes (ABM). Gestiona creación, actualización y eliminación de agentes individuales con comportamientos autónomos.

**Métodos principales**:

```python
def run_simulation(
    self,
    config: SimulationConfig,
    num_predators: int = 0,
    predator_species_id: Optional[str] = None
) -> AgentResult:
    """
    Ejecuta simulación basada en agentes con modelo de comportamiento individual.
    
    Cada agente posee estado interno (edad, energía, posición) y comportamientos
    (búsqueda de pareja, oviposición, depredación, mortalidad estocástica).
    
    Args:
        config: Configuración de simulación
        num_predators: Número de agentes depredadores
        predator_species_id: Especie de depredadores
        
    Returns:
        AgentResult con estadísticas agregadas
    """
```

---

### 3. Casos de Uso (`use_cases/`)

Los casos de uso representan operaciones completas del sistema, implementando el patrón Command con Request/Response.

#### 3.1 Clase Base: UseCase (`base.py`)

**Descripción**: Clase abstracta que define interfaz común para todos los casos de uso del sistema.

```python
class UseCase(ABC, Generic[TRequest, TResponse]):
    """
    Clase base abstracta para casos de uso.
    
    Implementa patrón Template Method:
    1. execute(): Punto de entrada público
    2. _validate(): Validación de request (abstracto)
    3. _execute(): Lógica de negocio (abstracto)
    4. _handle_error(): Manejo de errores
    """
    
    @abstractmethod
    def _validate(self, request: TRequest) -> None:
        """Valida request. Lanza ValidationError si inválido."""
        pass
    
    @abstractmethod
    def _execute(self, request: TRequest) -> TResponse:
        """Ejecuta lógica de negocio. Retorna Response."""
        pass
    
    def execute(self, request: TRequest) -> TResponse:
        """
        Ejecuta caso de uso completo.
        
        Flujo:
        1. Validar request
        2. Ejecutar lógica
        3. Manejar errores
        4. Retornar response
        """
        try:
            self._validate(request)
            return self._execute(request)
        except Exception as e:
            return self._handle_error(e)
```

**Excepciones**:

- `UseCaseError`: Excepción base
- `ValidationError`: Error de validación de entrada
- `ExecutionError`: Error durante ejecución

#### 3.2 RunPopulationSimulation (`run_population_simulation.py`)

**Descripción**: Caso de uso para ejecutar simulación poblacional basada en EDOs.

**Request**:
```python
@dataclass
class RunPopulationSimulationRequest:
    config: SimulationConfig
```

**Response**:
```python
@dataclass
class RunPopulationSimulationResponse(BaseResponse):
    success: bool
    result: Optional[PopulationResult]
    error_message: Optional[str]
    execution_time_seconds: Optional[float]
```

**Ejemplo de uso**:

```python
from application.use_cases.run_population_simulation import (
    RunPopulationSimulation,
    RunPopulationSimulationRequest
)

# Crear caso de uso con servicio de simulación
use_case = RunPopulationSimulation(simulation_service)

# Crear request
request = RunPopulationSimulationRequest(config=config)

# Ejecutar
response = use_case.execute(request)

if response.success:
    print(f"Simulación completada en {response.execution_time_seconds:.2f}s")
    result = response.result
    print(f"Población final: {result.total_population[-1]:.0f}")
else:
    print(f"Error: {response.error_message}")
```

#### 3.3 RunAgentSimulation (`run_agent_simulation.py`)

**Descripción**: Caso de uso para ejecutar simulación basada en agentes.

**Request**:
```python
@dataclass
class RunAgentSimulationRequest:
    config: SimulationConfig
    num_predators: int = 0
    predator_species_id: Optional[str] = None
```

**Response**:
```python
@dataclass
class RunAgentSimulationResponse(BaseResponse):
    success: bool
    result: Optional[AgentResult]
    error_message: Optional[str]
    execution_time_seconds: Optional[float]
```

#### 3.4 RunHybridSimulation (`run_hybrid_simulation.py`)

**Descripción**: Caso de uso para ejecutar simulación híbrida (poblacional + agentes en paralelo).

**Request**:
```python
@dataclass
class RunHybridSimulationRequest:
    config: SimulationConfig
    num_predators: int = 0
    predator_species_id: Optional[str] = None
```

**Response**:
```python
@dataclass
class RunHybridSimulationResponse(BaseResponse):
    success: bool
    result: Optional[HybridResult]  # Contiene ambos resultados
    error_message: Optional[str]
```

**Ejemplo de uso**:

```python
from application.use_cases.run_hybrid_simulation import (
    RunHybridSimulation,
    RunHybridSimulationRequest
)

use_case = RunHybridSimulation(simulation_service)
request = RunHybridSimulationRequest(
    config=config,
    num_predators=5,
    predator_species_id='toxorhynchites'
)

response = use_case.execute(request)

if response.success:
    hybrid = response.result
    summary = hybrid.get_comparison_summary()
    
    print("Comparación EDO vs ABM:")
    print(f"  Pico EDO: {summary['population_peak']:.0f}")
    print(f"  Pico ABM: {summary['agent_peak']:.0f}")
    print(f"  Diferencia: {summary['difference_peak']:.0f}")
```

#### 3.5 CompareScenarios (`compare_scenarios.py`)

**Descripción**: Caso de uso para comparar múltiples escenarios de simulación. Útil para análisis de sensibilidad y optimización de estrategias de control.

**Request**:
```python
@dataclass
class CompareScenariosRequest:
    scenarios: Dict[str, ScenarioConfig]  # {nombre: configuración}
    simulation_type: Literal['population', 'agent']
    comparison_metric: str = 'final_population'  # Métrica de comparación
```

**Response**:
```python
@dataclass
class CompareScenariosResponse(BaseResponse):
    success: bool
    result: Optional[ComparisonResult]
    ranking: Optional[List[str]]  # Escenarios ordenados (mejor→peor)
    best_scenario: Optional[str]
    error_message: Optional[str]
```

**Ejemplo de uso**:

```python
from application.use_cases.compare_scenarios import (
    CompareScenarios,
    CompareScenariosRequest,
    ScenarioConfig
)

# Definir escenarios a comparar
scenarios = {
    "temp_25C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=25.0,
        humidity=80.0,
        water_availability=0.8
    ),
    "temp_30C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=30.0,
        humidity=80.0,
        water_availability=0.8
    ),
    "temp_35C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=35.0,
        humidity=80.0,
        water_availability=0.8
    )
}

# Comparar escenarios
use_case = CompareScenarios(simulation_service)
request = CompareScenariosRequest(
    scenarios=scenarios,
    simulation_type='population',
    comparison_metric='peak_population'
)

response = use_case.execute(request)

if response.success:
    print(f"Mejor escenario: {response.best_scenario}")
    print("\nRanking (mejor→peor):")
    for i, scenario in enumerate(response.ranking, 1):
        result = response.result.results[scenario]
        print(f"  {i}. {scenario}: pico={result.statistics['peak_population']:.0f}")
```

#### 3.6 Gestión de Checkpoints (`manage_checkpoints.py`)

**Descripción**: Conjunto de casos de uso para gestión completa del ciclo de vida de checkpoints (guardar, cargar, listar, eliminar).

##### 3.6.1 SaveCheckpoint

Guarda estado completo de simulación en archivo JSON.

**Request**:
```python
@dataclass
class SaveCheckpointRequest:
    result: Union[PopulationResult, AgentResult, HybridResult]
    config: SimulationConfig
    simulation_type: Literal['population', 'agent', 'hybrid']
    checkpoint_name: Optional[str] = None  # Nombre personalizado
```

**Response**:
```python
@dataclass
class SaveCheckpointResponse:
    success: bool
    checkpoint_path: Optional[Path]
    error_message: Optional[str]
```

**Ejemplo**:
```python
from application.use_cases.manage_checkpoints import SaveCheckpoint, SaveCheckpointRequest

use_case = SaveCheckpoint(simulation_service)
request = SaveCheckpointRequest(
    result=simulation_result,
    config=config,
    simulation_type='population',
    checkpoint_name='aedes_control_scenario1.json'
)

response = use_case.execute(request)
if response.success:
    print(f"Checkpoint guardado: {response.checkpoint_path}")
```

##### 3.6.2 LoadCheckpoint

Carga checkpoint desde archivo JSON.

**Request**:
```python
@dataclass
class LoadCheckpointRequest:
    checkpoint_path: Path
```

**Response**:
```python
@dataclass
class LoadCheckpointResponse:
    success: bool
    config: Optional[SimulationConfig]
    result: Optional[Union[PopulationResult, AgentResult, HybridResult]]
    simulation_type: Optional[str]
    metadata: Optional[Dict]
    error_message: Optional[str]
```

##### 3.6.3 ListCheckpoints

Lista checkpoints disponibles con filtros opcionales.

**Request**:
```python
@dataclass
class ListCheckpointsRequest:
    species_id: Optional[str] = None  # Filtrar por especie
    simulation_type: Optional[str] = None  # Filtrar por tipo
```

**Response**:
```python
@dataclass
class ListCheckpointsResponse:
    success: bool
    checkpoints: List[CheckpointInfo]
    count: int
    error_message: Optional[str]
```

**Ejemplo**:
```python
from application.use_cases.manage_checkpoints import ListCheckpoints, ListCheckpointsRequest

use_case = ListCheckpoints(simulation_service)
request = ListCheckpointsRequest(
    species_id='aedes_aegypti',
    simulation_type='population'
)

response = use_case.execute(request)
if response.success:
    print(f"Encontrados {response.count} checkpoints:")
    for cp in response.checkpoints:
        print(f"  - {cp.filename}: {cp.species_id}, {cp.duration_days} días")
```

##### 3.6.4 DeleteCheckpoint

Elimina checkpoint específico del sistema.

**Request**:
```python
@dataclass
class DeleteCheckpointRequest:
    checkpoint_path: Path
```

**Response**:
```python
@dataclass
class DeleteCheckpointResponse:
    success: bool
    deleted_path: Optional[Path]
    error_message: Optional[str]
```

#### 3.7 Consulta de Configuraciones (`get_available_configurations.py`)

**Descripción**: Casos de uso para obtener información sobre especies disponibles y sus parámetros biológicos.

##### 3.7.1 GetAvailableSpecies

Obtiene lista de todas las especies configuradas en el sistema.

**Request**:
```python
@dataclass
class GetAvailableSpeciesRequest:
    pass  # Sin parámetros
```

**Response**:
```python
@dataclass
class GetAvailableSpeciesResponse(BaseResponse):
    success: bool
    species: Optional[List[SpeciesInfo]]
    error_message: Optional[str]
```

##### 3.7.2 GetAvailablePredators

Obtiene lista de especies depredadoras disponibles.

**Response**:
```python
@dataclass
class GetAvailablePredatorsResponse(BaseResponse):
    success: bool
    predators: Optional[List[SpeciesInfo]]
    error_message: Optional[str]
```

##### 3.7.3 GetSpeciesParameters

Obtiene parámetros biológicos detallados de una especie específica.

**Request**:
```python
@dataclass
class GetSpeciesParametersRequest:
    species_id: str
```

**Response**:
```python
@dataclass
class GetSpeciesParametersResponse(BaseResponse):
    success: bool
    species_info: Optional[SpeciesInfo]
    error_message: Optional[str]
```

**Ejemplo de uso**:

```python
from application.use_cases.get_available_configurations import (
    GetAvailableSpecies,
    GetSpeciesParameters,
    GetAvailableSpeciesRequest,
    GetSpeciesParametersRequest
)

# Listar especies disponibles
use_case1 = GetAvailableSpecies(simulation_service)
response1 = use_case1.execute(GetAvailableSpeciesRequest())

if response1.success:
    print("Especies disponibles:")
    for species in response1.species:
        print(f"  - {species.species_id}: {species.display_name}")

# Obtener parámetros de especie específica
use_case2 = GetSpeciesParameters(simulation_service)
request2 = GetSpeciesParametersRequest(species_id='aedes_aegypti')
response2 = use_case2.execute(request2)

if response2.success:
    info = response2.species_info
    print(f"\nParámetros de {info.display_name}:")
    print(f"  Fecundidad: {info.fecundity}")
    print(f"  Tasas de desarrollo: {info.development_rates}")
    print(f"  Tasas de supervivencia: {info.survival_rates}")
    print(f"  Depredadora: {info.is_predatory}")
```

---

### 4. Visualización (`visualization.py`)

**Descripción**: Funciones de alto nivel para visualización de resultados de simulaciones utilizando Matplotlib.

#### Funciones principales

```python
def plot_population_evolution(
    result: PopulationResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 8)
) -> matplotlib.figure.Figure:
    """
    Grafica evolución temporal de población por estadios de vida.
    
    Crea gráfico multi-panel mostrando:
    - Panel superior: Población total
    - Paneles inferiores: Huevos, Larvas, Pupas, Adultos (separados)
    
    Args:
        result: Resultado de simulación poblacional
        show: Si mostrar gráfico inmediatamente
        save_path: Ruta para guardar figura (opcional)
        figsize: Tamaño de figura (ancho, alto) en pulgadas
        
    Returns:
        Objeto Figure de matplotlib
    """
```

```python
def plot_agent_statistics(
    result: AgentResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 8)
) -> matplotlib.figure.Figure:
    """
    Grafica estadísticas diarias de simulación basada en agentes.
    
    Muestra:
    - Evolución de número de vectores y depredadores
    - Tasas de oviposición
    - Eventos de depredación
    - Mortalidad diaria
    
    Args:
        result: Resultado de simulación basada en agentes
        show: Si mostrar gráfico inmediatamente
        save_path: Ruta para guardar figura
        figsize: Tamaño de figura
        
    Returns:
        Objeto Figure de matplotlib
    """
```

```python
def plot_hybrid_comparison(
    hybrid_result: HybridResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 6)
) -> matplotlib.figure.Figure:
    """
    Grafica comparación entre simulación poblacional y basada en agentes.
    
    Visualiza lado a lado:
    - Trayectorias poblacionales (EDO vs ABM)
    - Diferencias absolutas entre enfoques
    - Métricas comparativas clave
    
    Args:
        hybrid_result: Resultado de simulación híbrida
        show: Si mostrar gráfico
        save_path: Ruta para guardar
        figsize: Tamaño de figura
        
    Returns:
        Objeto Figure de matplotlib
    """
```

```python
def plot_scenario_comparison(
    comparison_result: ComparisonResult,
    metric: str = 'peak_population',
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6)
) -> matplotlib.figure.Figure:
    """
    Grafica comparación de múltiples escenarios.
    
    Crea gráfico de barras o líneas comparando escenarios según
    métrica especificada (pico poblacional, población final, etc.)
    
    Args:
        comparison_result: Resultado de comparación
        metric: Métrica a graficar ('peak_population', 'final_population', etc.)
        show: Si mostrar gráfico
        save_path: Ruta para guardar
        figsize: Tamaño de figura
        
    Returns:
        Objeto Figure de matplotlib
    """
```

**Ejemplo de uso**:

```python
from application.visualization import (
    plot_population_evolution,
    plot_hybrid_comparison,
    plot_scenario_comparison
)

# Visualizar simulación poblacional
fig1 = plot_population_evolution(
    result=population_result,
    save_path='results/aedes_population.png'
)

# Visualizar comparación híbrida
fig2 = plot_hybrid_comparison(
    hybrid_result=hybrid_result,
    save_path='results/hybrid_comparison.png'
)

# Visualizar comparación de escenarios
fig3 = plot_scenario_comparison(
    comparison_result=comparison_result,
    metric='peak_population',
    save_path='results/scenario_comparison.png'
)
```

---

### 5. Utilidades (`helpers.py`)

**Descripción**: Funciones auxiliares para configuración y utilidades comunes.

```python
def get_config_manager() -> ConfigManager:
    """
    Obtiene instancia singleton de ConfigManager.
    
    Proporciona acceso global a configuración del sistema (parámetros
    de especies, configuración ambiental, rutas de archivos).
    
    Returns:
        ConfigManager: Instancia global de gestor de configuración
    """
```

**Ejemplo de uso**:

```python
from application.helpers import get_config_manager

config_manager = get_config_manager()

# Acceder a configuración de especie
species_config = config_manager.get_species_config('aedes_aegypti')
print(f"Parámetros de Aedes aegypti: {species_config}")

# Acceder a configuración ambiental
env_config = config_manager.get_environment_config()
print(f"Temperatura por defecto: {env_config['default_temperature']}°C")
```

---

## Patrones de Diseño Implementados

### 1. Clean Architecture

La capa de aplicación actúa como núcleo independiente:

- **Regla de Dependencia**: Las dependencias apuntan hacia adentro (dominio/entidades)
- **Inversión de Dependencias**: Servicios dependen de abstracciones, no implementaciones
- **Independencia de Frameworks**: No hay dependencias hard-coded a frameworks externos

### 2. Command Pattern (UseCase)

Cada operación del sistema se encapsula como un comando (caso de uso):

- **Request**: Parámetros de entrada
- **Response**: Resultado de operación
- **UseCase**: Ejecutor del comando

### 3. Data Transfer Object (DTO)

Estructuras inmutables para transferencia de datos entre capas:

- Desacoplan representación interna de formato de transporte
- Facilitan serialización/deserialización
- Proporcionan validación de datos

### 4. Service Layer

Servicios encapsulan lógica de negocio compleja:

- **SimulationService**: Orquestación de alto nivel
- **PopulationService**: Lógica de simulación poblacional
- **AgentService**: Lógica de simulación basada en agentes

### 5. Template Method

La clase base `UseCase` define algoritmo con pasos personalizables:

```python
def execute(self, request):
    self._validate(request)      # Paso 1: Validar
    return self._execute(request) # Paso 2: Ejecutar
```

---

## Flujo de Ejecución Típico

### Ejemplo: Ejecutar simulación poblacional con checkpoint

```python
# 1. Importar dependencias
from application.services.simulation_service import SimulationService
from application.use_cases.run_population_simulation import (
    RunPopulationSimulation, RunPopulationSimulationRequest
)
from application.use_cases.manage_checkpoints import (
    SaveCheckpoint, SaveCheckpointRequest
)
from application.dtos import SimulationConfig

# 2. Crear servicio de simulación
service = SimulationService()

# 3. Configurar simulación
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=90,
    initial_eggs=0,
    initial_larvae=0,
    initial_pupae=0,
    initial_adults=100,
    temperature=28.0,
    humidity=75.0,
    water_availability=0.9,
    random_seed=42
)

# 4. Validar configuración
is_valid, errors = config.validate()
if not is_valid:
    print(f"Configuración inválida: {errors}")
    exit(1)

# 5. Ejecutar simulación
use_case_run = RunPopulationSimulation(service)
request_run = RunPopulationSimulationRequest(config=config)
response_run = use_case_run.execute(request_run)

if not response_run.success:
    print(f"Error en simulación: {response_run.error_message}")
    exit(1)

result = response_run.result
print(f"Simulación completada en {response_run.execution_time_seconds:.2f}s")

# 6. Analizar resultados
stats = result.statistics
print(f"\nEstadísticas:")
print(f"  Pico poblacional: {stats['peak_population']:.0f} en día {stats['peak_day']}")
print(f"  Población final: {stats['final_population']:.0f}")
print(f"  Población promedio: {stats['mean_total']:.1f}")

if stats.get('extinction_day'):
    print(f"  Extinción en día: {stats['extinction_day']}")

# 7. Guardar checkpoint
use_case_save = SaveCheckpoint(service)
request_save = SaveCheckpointRequest(
    result=result,
    config=config,
    simulation_type='population',
    checkpoint_name='aedes_90dias_temp28.json'
)
response_save = use_case_save.execute(request_save)

if response_save.success:
    print(f"\nCheckpoint guardado: {response_save.checkpoint_path}")
else:
    print(f"Error guardando checkpoint: {response_save.error_message}")

# 8. Visualizar resultados
from application.visualization import plot_population_evolution

fig = plot_population_evolution(
    result=result,
    save_path=f'results/aedes_90dias.png'
)
print("\nGráfico guardado en results/aedes_90dias.png")
```

---

## Manejo de Errores

La capa de aplicación implementa manejo robusto de errores mediante excepciones tipadas:

### Jerarquía de Excepciones

```
Exception
└── UseCaseError
    ├── ValidationError      # Error de validación de entrada
    └── ExecutionError       # Error durante ejecución
```

### Ejemplo de Manejo de Errores

```python
from application.use_cases.base import ValidationError, ExecutionError
from application.use_cases.run_population_simulation import (
    RunPopulationSimulation, RunPopulationSimulationRequest
)

try:
    use_case = RunPopulationSimulation(service)
    request = RunPopulationSimulationRequest(config=invalid_config)
    response = use_case.execute(request)
    
    if not response.success:
        print(f"Simulación falló: {response.error_message}")
        
except ValidationError as e:
    print(f"Error de validación: {e}")
    # Manejar datos de entrada inválidos
    
except ExecutionError as e:
    print(f"Error de ejecución: {e}")
    # Manejar fallo durante simulación
    
except Exception as e:
    print(f"Error inesperado: {e}")
    # Manejar errores no anticipados
```

---

## Consideraciones de Rendimiento

### Simulaciones Poblacionales

- **Complejidad temporal**: O(N × M) donde N = días, M = número de ecuaciones
- **Complejidad espacial**: O(N) para almacenar trayectorias
- **Optimizaciones**:
  - Uso de NumPy para operaciones vectorizadas
  - Solver adaptativo (Runge-Kutta) para EDOs stiff
  - Pre-cálculo de parámetros dependientes de temperatura

### Simulaciones Basadas en Agentes

- **Complejidad temporal**: O(N × A) donde N = días, A = número de agentes
- **Complejidad espacial**: O(A) para estado de agentes
- **Optimizaciones**:
  - Eliminación eficiente de agentes muertos
  - Cacheo de vecindarios para interacciones locales
  - Muestreo Monte Carlo para eventos estocásticos

### Checkpoints

- **Formato JSON**: Balance entre legibilidad y rendimiento
- **Compresión**: Arrays NumPy serializados como listas (sin compresión adicional)
- **Tamaño típico**: 
  - Simulación 100 días: ~50-100 KB
  - Simulación 1000 días: ~500 KB - 1 MB

---

## Validación de Datos

Todos los DTOs implementan validación exhaustiva:

### SimulationConfig

- `duration_days`: [1, 3650]
- `temperature`: [-10, 50] °C
- `humidity`: [0, 100] %
- `water_availability`: [0, 1]
- Poblaciones iniciales: ≥ 0

### Especies

- `species_id` debe existir en configuración
- Parámetros biológicos dentro de rangos fisiológicos
- Depredadores válidos para simulaciones con depredación

---

## Extensibilidad

La arquitectura permite extensión sin modificación de código existente:

### Añadir Nueva Especie

1. Agregar configuración en `config/species_config.json`
2. No requiere cambios en código de aplicación

### Añadir Nuevo Tipo de Simulación

1. Crear nuevo servicio: `NewSimulationService`
2. Crear casos de uso: `RunNewSimulation`
3. Extender DTOs: `NewSimulationResult`

### Añadir Nueva Métrica de Comparación

1. Actualizar `ComparisonResult.get_best_scenario()` con nueva métrica
2. Actualizar validación en `CompareScenarios._validate()`

---

## Resumen de Componentes

| Componente | Responsabilidad | Archivos |
|-----------|----------------|----------|
| **DTOs** | Estructuras de datos | `dtos.py` |
| **Servicios** | Lógica de negocio | `services/*.py` |
| **Casos de Uso** | Operaciones del sistema | `use_cases/*.py` |
| **Visualización** | Generación de gráficos | `visualization.py` |
| **Utilidades** | Funciones auxiliares | `helpers.py` |
| **Checkpoints** | Persistencia de estado | `checkpoints/` (directorio) |

---

## Métricas de Cobertura

El sistema cuenta con cobertura exhaustiva de pruebas:

- **Casos de Uso**: 99 tests (100% cobertura)
  - Core: 36 tests (simulaciones)
  - Comparación: 17 tests
  - Checkpoints: 24 tests
  - Configuración: 22 tests

- **Servicios**: Tests unitarios completos
  - SimulationService: 15 tests
  - PopulationService: 8 tests
  - AgentService: 10 tests

- **DTOs**: Validación y serialización testeada
  - Validación de parámetros
  - Conversión dict ↔ objeto
  - Manejo de casos límite

---