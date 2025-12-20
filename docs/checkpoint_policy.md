# Política de Checkpoints - Sistema de Simulación de Mosquitos

## Resumen

Este documento define la política de checkpoints para el sistema de simulación, incluyendo el estado actual de implementación y los requerimientos para completar el sistema de guardado automático intermedio.

---

## Política Deseada de Checkpoints

El sistema debe soportar **tres modos de guardado**:

### 1. **Guardado Manual**
- Usuario invoca explícitamente `save_checkpoint()` después de completar la simulación
- Control total sobre cuándo y qué guardar
- **Estado:** ✅ IMPLEMENTADO

### 2. **Guardado Automático al Finalizar**
- Parámetro `auto_save=True` guarda automáticamente cuando la simulación termina
- Útil para no olvidar guardar resultados importantes
- **Estado:** ❌ NO IMPLEMENTADO

### 3. **Guardado Intermedio Durante Ejecución**
- Parámetro `checkpoint_interval=N` guarda cada N días durante la simulación
- Permite recuperación ante fallos en simulaciones largas
- Habilita pausar y reanudar simulaciones
- **Estado:** ❌ NO IMPLEMENTADO

---

## Estado Actual de Implementación

### ✅ Componentes Completados

**Archivo:** `application/services/simulation_service.py`

- **Método `save_checkpoint()`**: Guarda estado completo a JSON
  - Serializa configuración, resultados y metadatos
  - Genera nombres únicos con timestamps y contadores anti-colisión
  - Ubicación: Líneas 280-320

- **Método `load_checkpoint()`**: Carga y reconstruye estado desde JSON
  - Valida formato y claves requeridas
  - Reconstruye objetos DTO desde diccionarios
  - Ubicación: Líneas 322-360

- **Método `list_checkpoints()`**: Lista checkpoints con filtrado
  - Filtro por especie y tipo de simulación
  - Ordenación por timestamp (más reciente primero)
  - Ubicación: Líneas 362-400

---

## Requerimientos para Guardado Intermedio

### Objetivo

Implementar guardado automático de checkpoints cada N días durante la ejecución de la simulación, sin interrumpir el flujo de datos.

### Casos de Uso

1. **Simulaciones largas** (>365 días): Guardar cada 100 días para evitar pérdida de progreso
2. **Depuración**: Inspeccionar estado intermedio sin modificar código
3. **Análisis evolutivo**: Comparar estados de la simulación en diferentes momentos
4. **Recuperación ante fallos**: Reanudar desde último checkpoint válido

---

## Arquitectura de Solución

### Opción A: Sistema de Callbacks (Recomendado)

**Concepto:** Los servicios de simulación aceptan una función callback que se invoca cada N días.

```python
def checkpoint_callback(day: int, state: PartialState):
    """Invocado cada checkpoint_interval días durante simulación."""
    # SimulationService guarda estado intermedio
    pass
```

**Ventajas:**
- Desacoplamiento: servicios de dominio no conocen checkpoints
- Flexible: callback puede hacer logging, notificaciones, etc.
- No rompe separación de capas

**Desventajas:**
- Requiere serialización de estados parciales

### Opción B: Generadores Python

**Concepto:** Convertir simulaciones en generadores que yieldan estados intermedios.

```python
def simulate_with_checkpoints(config, interval):
    for day, state in simulate_generator(config):
        if day % interval == 0:
            yield day, state
```

**Ventajas:**
- Pythonic, memoria eficiente
- Control fino sobre pausas

**Desventajas:**
- Cambio radical en API
- Complica manejo de errores

### Opción C: Sistema de Estado Persistente

**Concepto:** Simulaciones guardan estado interno y pueden reanudarse.

```python
class ResumableSimulation:
    def run_until(self, target_day: int):
        # Ejecuta hasta día específico
        pass
    
    def save_state(self):
        # Guarda estado actual
        pass
```

**Ventajas:**
- Máximo control y flexibilidad
- Soporta pausar/reanudar nativamente

**Desventajas:**
- Mayor complejidad de implementación
- Más refactoring requerido

---

## Archivos y Métodos a Modificar

### 1. `application/services/population_service.py`

**Método actual:**
```python
@staticmethod
def simulate(config: SimulationConfig) -> PopulationResult:
    # Ejecuta toda la simulación de una vez
```

**Modificación propuesta (Opción A):**
```python
@staticmethod
def simulate(
    config: SimulationConfig,
    progress_callback: Optional[Callable[[int, Dict], None]] = None,
    callback_interval: Optional[int] = None
) -> PopulationResult:
    """
    Args:
        progress_callback: Función invocada cada callback_interval días
        callback_interval: Frecuencia de invocación del callback (días)
    """
    # Dentro del bucle de simulación:
    for day in range(config.duration_days + 1):
        # ... lógica de simulación ...
        
        if progress_callback and callback_interval:
            if day > 0 and day % callback_interval == 0:
                partial_state = {
                    'day': day,
                    'eggs': eggs_trajectory[day],
                    'larvae': larvae_trajectory[day],
                    'pupae': pupae_trajectory[day],
                    'adults': adults_trajectory[day],
                    'total': total_trajectory[day]
                }
                progress_callback(day, partial_state)
```

**Ubicación:** Línea 110-190

### 2. `application/services/agent_service.py`

**Método actual:**
```python
@staticmethod
def simulate_agents(
    config: SimulationConfig,
    num_predators: int = 0,
    predator_species: str = 'toxorhynchites'
) -> AgentResult:
```

**Modificación propuesta:**
```python
@staticmethod
def simulate_agents(
    config: SimulationConfig,
    num_predators: int = 0,
    predator_species: str = 'toxorhynchites',
    progress_callback: Optional[Callable[[int, Dict], None]] = None,
    callback_interval: Optional[int] = None
) -> AgentResult:
    # Dentro del bucle día por día:
    for day in range(config.duration_days + 1):
        # ... lógica de agentes ...
        
        if progress_callback and callback_interval:
            if day > 0 and day % callback_interval == 0:
                partial_state = {
                    'day': day,
                    'num_vectors_alive': len([a for a in vector_agents if a.alive]),
                    'num_predators_alive': len([a for a in predator_agents if a.alive]),
                    'total_eggs_laid': total_eggs_laid,
                    'total_prey_consumed': total_prey_consumed
                }
                progress_callback(day, partial_state)
```

**Ubicación:** Línea 50-230

### 3. `application/services/simulation_service.py`

**Métodos a actualizar:**

#### `run_population_simulation()`
```python
def run_population_simulation(
    self,
    config: SimulationConfig,
    auto_save: bool = False,
    checkpoint_interval: Optional[int] = None
) -> PopulationResult:
    
    # Crear callback si checkpoint_interval especificado
    checkpoint_counter = 0
    def checkpoint_callback(day: int, state: Dict):
        nonlocal checkpoint_counter
        checkpoint_counter += 1
        
        # Crear resultado parcial para guardar
        partial_result = self._create_partial_result(state, config, day)
        
        checkpoint_name = (
            f"partial_{config.species_id}_day{day}_"
            f"{checkpoint_counter}.json"
        )
        
        self.save_checkpoint(
            result=partial_result,
            config=config,
            simulation_type='population',
            checkpoint_name=checkpoint_name
        )
    
    # Ejecutar con callback si especificado
    if checkpoint_interval:
        result = PopulationService.simulate(
            config,
            progress_callback=checkpoint_callback,
            callback_interval=checkpoint_interval
        )
    else:
        result = PopulationService.simulate(config)
    
    # Auto-save final si solicitado
    if auto_save:
        self.save_checkpoint(result, config, 'population')
    
    return result
```

**Ubicación:** Línea 60-100

#### `run_agent_simulation()` 
Similar a `run_population_simulation()`, aplicar misma lógica.

**Ubicación:** Línea 102-145

#### `run_hybrid_simulation()`
Aplicar callbacks a ambas simulaciones.

**Ubicación:** Línea 147-220

### 4. Nuevo método auxiliar

**Agregar a `SimulationService`:**
```python
def _create_partial_result(
    self,
    partial_state: Dict,
    config: SimulationConfig,
    current_day: int
) -> Union[PopulationResult, AgentResult]:
    """
    Crea un resultado parcial desde estado intermedio.
    
    Nota: Los arrays/estadísticas estarán incompletos.
    El día final será current_day, no config.duration_days.
    """
    # Implementar conversión de partial_state a Result DTO
    pass
```

---

## Consideraciones de Diseño

### 1. **Formato de Checkpoints Intermedios**

Los checkpoints intermedios deben marcarse claramente:

```json
{
  "timestamp": "2026-01-11T10:30:45.123456",
  "simulation_type": "population",
  "is_partial": true,
  "current_day": 150,
  "total_days": 365,
  "config": { ... },
  "partial_result": { ... },
  "metadata": {
    "checkpoint_type": "intermediate",
    "checkpoint_number": 2
  }
}
```

### 2. **Gestión de Espacio en Disco**

**Problema:** Checkpoints intermedios pueden acumular muchos archivos.

**Soluciones:**

- **Rotación automática:** Mantener solo los últimos N checkpoints intermedios
- **Compresión:** Usar `gzip` para archivos JSON
- **Limpieza al finalizar:** Eliminar checkpoints intermedios si la simulación completa exitosamente

**Implementar en:**
```python
def cleanup_intermediate_checkpoints(self, config: SimulationConfig, keep_last: int = 3):
    """Elimina checkpoints intermedios antiguos."""
    pass
```

### 3. **Reanudación de Simulaciones**

Para soportar reanudación, agregar:

```python
def resume_from_checkpoint(
    self,
    checkpoint_path: Path,
    target_day: Optional[int] = None
) -> Union[PopulationResult, AgentResult]:
    """
    Reanuda simulación desde checkpoint.
    
    Args:
        checkpoint_path: Checkpoint desde donde reanudar
        target_day: Día objetivo (None = completar configuración original)
    """
    # Cargar checkpoint
    config, partial_result, sim_type = self.load_checkpoint(checkpoint_path)
    
    # Extraer día actual desde partial_result
    current_day = partial_result.get_current_day()
    
    # Crear nueva config ajustada
    remaining_days = (target_day or config.duration_days) - current_day
    resumed_config = config.clone()
    resumed_config.duration_days = remaining_days
    
    # Reanudar simulación con estado inicial desde checkpoint
    # ... implementación específica por tipo ...
```

### 4. **Notificaciones de Progreso**

Además de guardar, el callback puede notificar progreso:

```python
def simulate_with_progress(
    self,
    config: SimulationConfig,
    checkpoint_interval: int = 50,
    progress_callback: Optional[Callable[[int, int], None]] = None
):
    """
    Args:
        progress_callback: callback(current_day, total_days)
    """
    def combined_callback(day, state):
        # Guardar checkpoint
        self._save_intermediate_checkpoint(day, state, config)
        
        # Notificar progreso
        if progress_callback:
            progress_callback(day, config.duration_days)
```

### 5. **Manejo de Errores**

Si la simulación falla después de generar checkpoints intermedios:

- **Marcar último checkpoint como "incomplete"**
- **Incluir información de error** en metadatos
- **Permitir inspección** del estado hasta el fallo

```json
{
  "is_partial": true,
  "status": "failed",
  "error": {
    "day": 287,
    "exception": "ValueError: Negative population detected",
    "traceback": "..."
  }
}
```

---

## Plan de Implementación Sugerido

### Fase 1: Callbacks en Servicios de Dominio
1. Agregar parámetros `progress_callback` y `callback_interval` a `PopulationService.simulate()`
2. Agregar parámetros `progress_callback` y `callback_interval` a `AgentService.simulate_agents()`
3. Invocar callbacks en puntos apropiados del bucle de simulación
4. **Testing:** Verificar que callbacks se invocan correctamente

### Fase 2: Integración en SimulationService
1. Implementar `_create_partial_result()` para convertir estados parciales a DTOs
2. Conectar callbacks con sistema de guardado en `run_population_simulation()`
3. Conectar callbacks con sistema de guardado en `run_agent_simulation()`
4. Actualizar `run_hybrid_simulation()` para soportar checkpoints intermedios
5. **Testing:** Verificar que se generan archivos durante ejecución

### Fase 3: Gestión de Checkpoints Intermedios
1. Implementar `cleanup_intermediate_checkpoints()`
2. Agregar lógica de rotación automática (mantener últimos N)
3. Implementar compresión opcional para ahorrar espacio
4. **Testing:** Verificar limpieza y compresión

### Fase 4: Reanudación (Opcional, Avanzado)
1. Implementar `resume_from_checkpoint()`
2. Agregar soporte en servicios de dominio para inicialización desde estado parcial
3. Crear tests de reanudación completos
4. **Testing:** Verificar que simulaciones reanudadas producen resultados equivalentes

---

## Ejemplo de Uso Esperado

```python
# Crear servicio
service = SimulationService(checkpoint_dir="./checkpoints")

# Configuración
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=1000,  # Simulación larga
    initial_adults=100,
    temperature=28.0,
    humidity=80.0
)

# Ejecutar con checkpointing intermedio cada 100 días
result = service.run_population_simulation(
    config=config,
    auto_save=True,              # Guardar al finalizar
    checkpoint_interval=100       # Guardar cada 100 días durante ejecución
)

# Resultado: 11 checkpoints generados (días 100, 200, ..., 1000)
# Ubicación: ./checkpoints/partial_aedes_aegypti_day100_1.json, ...
```

---

## Beneficios del Sistema Completo

1. **Resiliencia:** Recuperación automática ante fallos
2. **Monitoreo:** Inspección de estado intermedio sin interrumpir
3. **Depuración:** Análisis de comportamiento evolutivo
4. **Flexibilidad:** Pausar/reanudar simulaciones largas
5. **Auditoría:** Registro completo de progreso temporal

---

## Referencias

- **Archivo de implementación actual:** `application/services/simulation_service.py`
- **Tests relacionados:** `test_application_simulation_service.py`
- **DTOs involucrados:** `application/dtos.py` (PopulationResult, AgentResult, SimulationConfig)
