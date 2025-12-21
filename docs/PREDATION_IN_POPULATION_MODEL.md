# Implementación de Depredación en Simulación Poblacional

## Estado Actual del Sistema

### Tipos de Simulación Disponibles

| Tipo | Incluye Depredación | Método | Archivo Principal |
|------|---------------------|--------|-------------------|
| **Poblacional** | ❌ No | Matrices de Leslie + EDOs | `domain/models/population_model.py` |
| **Basada en Agentes** | ✅ Sí | Agentes individuales con Prolog | `domain/agents/predator_agent.py` |
| **Híbrida** | ⚠️ Parcial | Ejecuta ambas independientemente | `application/services/simulation_service.py` |

### Situación Actual

**Simulación Poblacional** (`PopulationService.simulate()`):
- Modela únicamente la población de *Aedes aegypti* (o especie objetivo)
- Utiliza matrices de Leslie para proyección poblacional
- Considera tasas vitales (natalidad, mortalidad, desarrollo)
- **NO considera** el efecto de depredadores (*Toxorhynchites*)

**Simulación Basada en Agentes** (`AgentService.simulate_agents()`):
- Modela individuos de *Aedes aegypti* como `VectorAgent`
- Modela individuos de *Toxorhynchites* como `PredatorAgent`
- Los depredadores **SÍ consumen** presas explícitamente
- Usa Prolog para decisiones de caza
- Reduce población de vectores por depredación directa

## Propuesta de Implementación

### Enfoque: Respuesta Funcional de Holling Tipo II

Incorporar término de depredación en el modelo poblacional usando la **respuesta funcional de Holling Tipo II**, que ya está configurada en los archivos JSON.

#### Ecuación

$$
\text{Presas consumidas} = \frac{a \cdot N_{\text{presa}} \cdot N_{\text{depredador}}}{1 + a \cdot h \cdot N_{\text{presa}}}
$$

Donde:
- $a$ = tasa de ataque (`attack_rate` en config)
- $h$ = tiempo de manipulación (`handling_time` en config)
- $N_{\text{presa}}$ = población de larvas de *Aedes*
- $N_{\text{depredador}}$ = población de depredadores

#### Parámetros Disponibles

Ya configurados en `config/species/toxorhynchites.json`:

```json
"predation": {
  "functional_response": {
    "attack_rate": 0.5,
    "handling_time": 0.1
  },
  "prey_stages": ["larva_l1", "larva_l2", "larva_l3", "larva_l4"]
}
```

---

## Archivos a Modificar

### 1. `application/dtos.py`

**Cambio**: Agregar parámetro opcional `num_predators` a `SimulationConfig`

```python
@dataclass
class SimulationConfig:
    # ... campos existentes ...
    num_predators: int = 0  # Número de depredadores (0 = sin control)
    predator_species_id: Optional[str] = 'toxorhynchites'
```

**Razón**: Permitir especificar depredadores desde la configuración.

---

### 2. `domain/models/population_model.py`

**Cambio 1**: Agregar atributos de depredación a `PopulationModel`

```python
class PopulationModel:
    def __init__(
        self,
        species_config: SpeciesConfig,
        environment_model: EnvironmentModel,
        stochastic_mode: bool = True,
        seed: Optional[int] = None,
        num_predators: int = 0,  # NUEVO
        predator_config: Optional[SpeciesConfig] = None  # NUEVO
    ):
        # ... código existente ...
        
        # Parámetros de depredación
        self.num_predators = num_predators
        self.predator_config = predator_config
        
        if num_predators > 0 and predator_config:
            self._load_predation_parameters()
```

**Cambio 2**: Agregar método para cargar parámetros de depredación

```python
def _load_predation_parameters(self):
    """Carga parámetros de respuesta funcional desde config de depredador."""
    if not self.predator_config.predation:
        raise ValueError("Predator config missing predation parameters")
    
    self.attack_rate = self.predator_config.predation.functional_response.attack_rate
    self.handling_time = self.predator_config.predation.functional_response.handling_time
    self.prey_stages = self.predator_config.predation.prey_stages
```

**Cambio 3**: Modificar método `_step()` para aplicar depredación

```python
def _step(self, state: PopulationState) -> PopulationState:
    """
    Advance population one time step.
    
    Steps:
    1. Calculate vital rates (existing)
    2. Apply Leslie matrix projection (existing)
    3. Apply predation (NUEVO)
    4. Apply stochasticity (existing)
    5. Apply density dependence (existing)
    """
    # ... código existente ...
    
    # 3. Apply predation if predators present
    if self.num_predators > 0:
        new_state = self._apply_predation(new_state)
    
    # ... resto del código existente ...
```

**Cambio 4**: Implementar método `_apply_predation()`

```python
def _apply_predation(self, state: PopulationState) -> PopulationState:
    """
    Apply predation using Holling Type II functional response.
    
    Args:
        state: Current population state
        
    Returns:
        Updated state after predation
    """
    # Calculate total prey (larvae stages only)
    total_prey = state.larvae  # Simplificado: todas las larvas
    
    # Holling Type II functional response
    # Prey consumed = (a * N_prey * N_pred) / (1 + a * h * N_prey)
    numerator = self.attack_rate * total_prey * self.num_predators
    denominator = 1 + self.attack_rate * self.handling_time * total_prey
    
    prey_consumed = numerator / denominator
    
    # Ensure we don't consume more prey than available
    prey_consumed = min(prey_consumed, total_prey)
    
    # Reduce larvae population
    new_larvae = max(0, state.larvae - prey_consumed)
    
    # Create new state with reduced larvae
    return PopulationState(
        day=state.day,
        eggs=state.eggs,
        larvae=int(round(new_larvae)),
        pupae=state.pupae,
        adults=state.adults,
        total=int(round(state.eggs + new_larvae + state.pupae + state.adults)),
        temperature=state.temperature,
        humidity=state.humidity,
        carrying_capacity=state.carrying_capacity
    )
```

---

### 3. `application/services/population_service.py`

**Cambio**: Pasar parámetros de depredación al modelo

```python
@staticmethod
def create_population(
    config: SimulationConfig,
    include_predation: bool = False  # NUEVO
) -> Population:
    """
    Create a Population from a configuration DTO.
    
    Args:
        config: Simulation configuration
        include_predation: Whether to include predation effects
    """
    # ... código existente ...
    
    # Load predator config if needed
    predator_config = None
    if include_predation and config.num_predators > 0:
        predator_species_id = config.predator_species_id or 'toxorhynchites'
        predator_config = config_manager.get_species_config(predator_species_id)
    
    # Create PopulationModel with predation
    model = PopulationModel(
        species_config=species_config,
        environment_model=environment_model,
        stochastic_mode=True,
        seed=config.random_seed,
        num_predators=config.num_predators if include_predation else 0,  # NUEVO
        predator_config=predator_config  # NUEVO
    )
    
    # ... resto del código ...
```

---

### 4. `application/services/simulation_service.py`

**Cambio**: Exponer parámetro de depredación en API pública

```python
@staticmethod
def run_population_simulation(
    config: SimulationConfig,
    include_predation: bool = False  # NUEVO
) -> PopulationResult:
    """
    Execute population dynamics simulation.
    
    Args:
        config: Simulation configuration
        include_predation: Whether to include predation by Toxorhynchites
        
    Returns:
        PopulationResult with temporal trajectories
    """
    return PopulationService.simulate(config, include_predation=include_predation)
```

---

### 5. `infrastructure/config.py`

**Verificación**: Asegurar que `PredationConfig` está correctamente definido

```python
@dataclass
class FunctionalResponseConfig:
    """Holling Type II functional response parameters."""
    attack_rate: float      # a: attack rate
    handling_time: float    # h: handling time per prey

@dataclass
class PredationConfig:
    """Predation behavior configuration."""
    functional_response: FunctionalResponseConfig
    prey_stages: List[str]  # List of prey stage names
```

**Estado**: ✅ Ya implementado correctamente

---

## Casos de Uso Actualizados

### Uso Actual (Sin Depredación)

```python
from application.services.simulation_service import SimulationService
from application.dtos import SimulationConfig

service = SimulationService()

config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=90,
    initial_eggs=100,
    initial_larvae=50,
    initial_pupae=20,
    initial_adults=30,
    temperature=28.0,
    humidity=75.0
)

# Simulación sin control
result = service.run_population_simulation(config)
```

### Uso Propuesto (Con Depredación)

```python
# Opción 1: Parámetro en SimulationConfig
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=90,
    initial_eggs=100,
    initial_larvae=50,
    initial_pupae=20,
    initial_adults=30,
    temperature=28.0,
    humidity=75.0,
    num_predators=10,  # NUEVO
    predator_species_id='toxorhynchites'  # NUEVO
)

result = service.run_population_simulation(config, include_predation=True)

# Opción 2: Parámetro explícito
result_no_control = service.run_population_simulation(config, include_predation=False)
result_with_control = service.run_population_simulation(config, include_predation=True)
```

---

## Comparación de Enfoques

### Simulación Poblacional con Depredación vs. ABM

| Aspecto | Poblacional + Depredación | ABM con Depredadores |
|---------|---------------------------|----------------------|
| **Velocidad** | ⚡ Rápida (segundos) | 🐌 Más lenta (minutos) |
| **Precisión** | 📊 Promedio poblacional | 🎯 Individual detallado |
| **Estocástico** | Variación demográfica | Variación individual |
| **Decisiones** | Ecuaciones deterministas | Prolog + comportamiento |
| **Escalabilidad** | ✅ Miles de días | ⚠️ Limitado por agentes |
| **Uso** | Proyecciones largas | Mecanismos detallados |

**Recomendación**: Implementar ambos para tener:
1. **Poblacional con depredación**: Análisis rápido de tendencias
2. **ABM**: Validación mecanística detallada

---

## Validación Cruzada

Una vez implementado, se puede validar comparando:

```python
# Simulación poblacional con depredación
pop_result = service.run_population_simulation(config, include_predation=True)

# Simulación basada en agentes
agent_result = service.run_agent_simulation(config, num_predators=10)

# Comparar poblaciones finales
print(f"Poblacional: {pop_result.total_population[-1]:.0f}")
print(f"Agentes: {agent_result.get_statistics()['final_population']:.0f}")
```

**Criterio de validación**: Ambas simulaciones deben dar resultados del mismo orden de magnitud (±30%), dadas las diferencias metodológicas.

---

## Impacto en Testing

### Nuevos Tests Necesarios

```python
# test_population_model_with_predation.py

def test_predation_reduces_population():
    """Verify predators reduce prey population."""
    # Run without predation
    result_no_pred = simulate(config, num_predators=0)
    
    # Run with predation
    result_with_pred = simulate(config, num_predators=10)
    
    # Final population should be lower with predators
    assert result_with_pred.total_population[-1] < result_no_pred.total_population[-1]

def test_holling_type_ii_saturation():
    """Verify functional response saturates at high prey density."""
    # High prey density should not linearly increase consumption
    pass

def test_zero_predators_equals_baseline():
    """Verify num_predators=0 gives same results as before."""
    result_baseline = simulate_old(config)
    result_new = simulate_new(config, num_predators=0)
    
    np.testing.assert_array_almost_equal(
        result_baseline.total_population,
        result_new.total_population
    )
```

---

## Cronograma de Implementación

| Fase | Tareas | Archivos |
|------|--------|----------|
| **1. Preparación** | Actualizar DTOs, validar configs | `dtos.py`, `config.py` |
| **2. Modelo** | Implementar `_apply_predation()` | `population_model.py` |
| **3. Servicio** | Integrar con servicios | `population_service.py`, `simulation_service.py` |
| **4. Testing** | Nuevos tests unitarios | `test_population_model.py` |
| **5. Validación** | Comparar poblacional vs ABM | Jupyter notebook |

---

## Ventajas de la Implementación

1. **Consistencia**: Ambos tipos de simulación pueden evaluar control biológico
2. **Velocidad**: Simulación poblacional es más rápida para análisis exploratorio
3. **Validación**: Permite comparar resultados entre metodologías
4. **Flexibilidad**: `num_predators=0` mantiene simulación original
5. **Configurabilidad**: Usa parámetros ya definidos en JSON

---

## Limitaciones y Consideraciones

### Simplificaciones del Modelo Poblacional

1. **Agregación de estadios**: Todas las larvas se tratan como grupo (L1-L4)
   - **Realidad**: Depredadores prefieren L1-L2 (más vulnerables)
   - **Mejora futura**: Modelar estadios larvarios por separado

2. **Depredadores estáticos**: `num_predators` es constante
   - **Realidad**: Depredadores tienen su propia dinámica (nacen, mueren)
   - **Mejora futura**: Modelar población de depredadores con Leslie matrix propia

3. **Respuesta funcional fija**: Parámetros `a` y `h` constantes
   - **Realidad**: Pueden variar con temperatura, densidad
   - **Mejora futura**: Hacer `a` y `h` dependientes de ambiente

4. **Sin estructura espacial**: Población homogénea
   - **Realidad**: Depredadores y presas distribuidos en espacio
   - **Mejora futura**: Modelo metapoblacional

### Cuándo Usar Cada Tipo

| Escenario | Recomendación |
|-----------|---------------|
| Proyecciones a largo plazo (>100 días) | Poblacional con depredación |
| Análisis de sensibilidad (muchos escenarios) | Poblacional |
| Estudiar comportamiento individual | ABM |
| Validar supuestos del modelo | Ambos (comparar) |
| Publicación científica | Ambos + validación cruzada |