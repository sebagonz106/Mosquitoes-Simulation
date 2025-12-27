# Mosquitoes-Simulation

## Sistema de Simulación de Dinámicas Poblacionales de Mosquitos

Sistema computacional para modelar y simular la dinámica poblacional de mosquitos vectores (*Aedes aegypti*) y su interacción con depredadores naturales (*Toxorhynchites* spp.). El software integra modelos matemáticos poblacionales con simulaciones basadas en agentes inteligentes, permitiendo evaluar estrategias de control biológico mediante la introducción de especies depredadoras.

---

## Tabla de Contenidos

1. [Motivación Científica](#motivación-científica)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Requisitos del Sistema](#requisitos-del-sistema)
5. [Instalación](#instalación)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Guía de Uso](#guía-de-uso)
8. [Especies Modeladas](#especies-modeladas)
9. [Configuración](#configuración)
10. [API y Casos de Uso](#api-y-casos-de-uso)
11. [Pruebas](#pruebas)
12. [Licencia](#licencia)

---

## Motivación Científica

### Contexto Epidemiológico

*Aedes aegypti* es el principal vector de enfermedades virales de alto impacto en salud pública, incluyendo:

- **Dengue**: 390 millones de infecciones anuales estimadas (OMS)
- **Zika**: Asociado a microcefalia y síndrome de Guillain-Barré
- **Chikungunya**: Enfermedad articular debilitante
- **Fiebre amarilla**: Mortalidad del 20-50% en casos severos

El control químico mediante insecticidas enfrenta limitaciones crecientes debido al desarrollo de resistencia en poblaciones de mosquitos. Esto ha impulsado la investigación de alternativas sostenibles como el **control biológico**.

### Control Biológico con Toxorhynchites

El género *Toxorhynchites* comprende mosquitos cuyas larvas son depredadores obligados de otras larvas de mosquitos, mientras que los adultos son exclusivamente nectarívoros (no pican a humanos ni transmiten enfermedades).

**Características relevantes:**
- Larvas L3-L4 consumen 10-20 presas/día
- Cohabitan en los mismos contenedores que *Aedes aegypti*
- No desarrollan resistencia a insecticidas (estrategia biológica)
- Liberaciones pueden reducir poblaciones larvarias 40-90%

Este sistema permite modelar computacionalmente la efectividad de introducir *Toxorhynchites* como agente de control en diferentes escenarios ambientales.

---

## Características Principales

### Paradigmas de Simulación

| Característica | Simulación Poblacional | Simulación Basada en Agentes |
|----------------|------------------------|------------------------------|
| **Enfoque** | Poblaciones agregadas | Individuos discretos |
| **Escala** | Macroscópica | Microscópica |
| **Determinismo** | Determinístico/Estocástico | Estocástico |
| **Interacciones** | Implícitas (tasas) | Explícitas (agente-agente) |
| **Uso** | Tendencias generales | Comportamientos emergentes |

### Funcionalidades

#### Backend (Completado)
- **Simulación poblacional**: Modelo basado en matrices de Leslie con integración Prolog
- **Simulación depredador-presa**: Modelado completo de interacciones *Toxorhynchites*-*Aedes aegypti*
- **Tasas de supervivencia dinámicas**: Motor Prolog ajusta tasas según condiciones ambientales en tiempo real
- **Comparación automática**: Evaluación de escenarios con y sin depredadores
- **Análisis de impacto**: Cálculo de reducción poblacional por depredación
- **Persistencia**: Sistema de checkpoints para guardar/restaurar simulaciones
- **Configuración flexible**: Parámetros biológicos externalizados en JSON
- **Visualización avanzada**: Gráficos multi-panel con dinámicas de presa y depredador
- **Arquitectura limpia**: Separación de responsabilidades en capas independientes

#### Frontend (Completado)
- **Interfaz gráfica (GUI)**: Aplicación de escritorio con tkinter
- **Simulación de especies únicas**: Configuración completa para *Aedes aegypti* y *Toxorhynchites*
- **Simulación presa-depredador**: Pestaña dedicada con parámetros duales sincronizados
- **Validación en tiempo real**: Indicadores visuales (✓/⚠/✗) para rangos de parámetros
- **Tooltips informativos**: Ayuda contextual detallada en todos los parámetros
- **Presets ambientales**: 6 configuraciones predefinidas (Tropical, Templado, Extremo, Monzón)
- **Presets depredador-presa**: 9 escenarios de interacción (Balanceado, Control débil/fuerte, Presión, Brote)
- **Visualización de resultados**: Gráficos integrados de evolución poblacional por estadio
- **Comparación visual**: Gráficas de impacto de depredación con estadísticas overlay
- **Exportación de datos**: Funcionalidad CSV y PNG para resultados y gráficas

#### En Desarrollo
- **Simulación basada en agentes**: Arquitectura implementada, pendiente integración GUI
- **Simulación híbrida**: Comparación poblacional vs. agentes pendiente

---

## Arquitectura del Sistema

El sistema implementa **Clean Architecture** (Arquitectura Limpia), separando responsabilidades en capas independientes con dependencias unidireccionales.

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│         GUI (Tkinter) - Vistas, Controladores, Widgets      │
│   Validación | Tooltips | Presets | Visualización Gráfica  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Casos de  │  │  Servicios  │  │        DTOs         │  │
│  │     Uso     │  │             │  │ (Data Transfer Obj) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE DOMINIO                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Modelos   │  │  Entidades  │  │      Agentes        │  │
│  │ Matemáticos │  │  de Negocio │  │    Inteligentes     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE INFRAESTRUCTURA                    │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │ Gestión de Config   │  │     Puente Python-Prolog    │   │
│  │      (JSON)         │  │         (PySwip)            │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE CONOCIMIENTO                     │
│                        (Prolog)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Ontología  │  │   Hechos    │  │       Reglas        │  │
│  │  Taxonómica │  │  Biológicos │  │    de Inferencia    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Descripción de Capas

#### Capa de Dominio
Núcleo del sistema con la lógica de negocio biológica:
- **Modelos**: Matrices de Leslie, procesos estocásticos, dinámica ambiental
- **Entidades**: Especies, mosquitos individuales, poblaciones, hábitats
- **Agentes**: Agentes racionales con decisiones basadas en Prolog

#### Capa de Aplicación
Orquestación de operaciones y transformación de datos:
- **Casos de Uso**: Operaciones completas (ejecutar simulación, comparar escenarios)
- **Servicios**: Coordinación entre dominio e infraestructura
- **DTOs**: Estructuras de transferencia entre capas

#### Capa de Infraestructura
Comunicación con recursos externos:
- **ConfigManager**: Carga y validación de configuraciones JSON
- **PrologBridge**: Interfaz Python-SWI-Prolog vía PySwip

#### Capa de Presentación
Interfaces de usuario implementadas y en desarrollo:
- **GUI**: Aplicación de escritorio con Tkinter (implementada)
- **Vistas**: SimulationView, ResultsView, HomeView
- **Widgets**: Tooltips, validación en tiempo real, presets de escenarios
- **CLI**: Interfaz de línea de comandos (pendiente)
- **API REST**: Endpoints para integración (pendiente)

---

## Requisitos del Sistema

### Software

| Componente | Versión Mínima | Notas |
|------------|----------------|-------|
| Python | 3.10+ | Type hints, dataclasses |
| SWI-Prolog | 8.0+ | Motor de inferencia |
| NumPy | 1.21+ | Cálculos matriciales |
| Matplotlib | 3.5+ | Visualización |
| PySwip | 0.2.10+ | Bridge Python-Prolog |
| Pandas | 1.3+ | Análisis de datos |
| Seaborn | 0.11+ | Visualización estadística |
| Tkinter | Incluido en Python | GUI (incluido en instalación estándar) |

### Hardware Recomendado

- **RAM**: 4 GB mínimo (8 GB para simulaciones grandes)
- **CPU**: Procesador multi-núcleo para simulaciones paralelas
- **Almacenamiento**: 500 MB para instalación + espacio para checkpoints

---

## Instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/usuario/Mosquitoes-Simulation.git
cd Mosquitoes-Simulation
```

### 2. Instalar SWI-Prolog

**Windows:**
```bash
# Descargar instalador desde https://www.swi-prolog.org/download/stable
# Agregar al PATH: C:\Program Files\swipl\bin
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-add-repository ppa:swi-prolog/stable
sudo apt-get update
sudo apt-get install swi-prolog
```

**macOS:**
```bash
brew install swi-prolog
```

### 3. Crear Entorno Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Verificar Instalación

```bash
cd src
python -c "from infrastructure import PrologBridge; print('Prolog OK')"
python -c "from domain.models import PopulationModel; print('Modelos OK')"
python -m unittest discover tests -v
```

---

## Estructura del Proyecto

```
Mosquitoes-Simulation/
├── config/                      # Configuraciones JSON
│   ├── default_config.json      # Configuración general
│   ├── species/                 # Parámetros por especie
│   │   ├── aedes_aegypti.json
│   │   └── toxorhynchites.json
│   └── environment/             # Condiciones ambientales
│       └── default_environment.json
│
├── src/                         # Código fuente
│   ├── domain/                  # Capa de Dominio
│   │   ├── models/              # Modelos matemáticos
│   │   ├── entities/            # Entidades de negocio
│   │   └── agents/              # Agentes inteligentes
│   │
│   ├── application/             # Capa de Aplicación
│   │   ├── services/            # Servicios de negocio
│   │   ├── use_cases/           # Casos de uso
│   │   ├── dtos.py              # Data Transfer Objects
│   │   └── visualization.py     # Funciones de graficación
│   │
│   ├── infrastructure/          # Capa de Infraestructura
│   │   ├── config.py            # Gestión de configuración
│   │   └── prolog_bridge.py     # Puente Python-Prolog
│   │
│   ├── presentation/            # Capa de Presentación
│   │   ├── views/               # Vistas de la aplicación
│   │   ├── controllers/         # Controladores MVC
│   │   ├── components/          # Componentes reutilizables
│   │   ├── widgets/             # Widgets personalizados (tooltips)
│   │   ├── data/                # Datos estáticos (presets, rangos)
│   │   ├── styles/              # Temas y estilos visuales
│   │   └── main.py              # Punto de entrada GUI
│   │
│   ├── prolog/                  # Base de Conocimiento Prolog
│   │   ├── knowledge_base/      # Ontología y hechos
│   │   └── inference/           # Reglas de inferencia
│   │
│   └── tests/                   # Pruebas unitarias
│
├── checkpoints/                 # Checkpoints de simulaciones
├── docs/                        # Documentación adicional
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## Guía de Uso

### Interfaz Gráfica (GUI)

La aplicación cuenta con una interfaz gráfica completa que permite configurar y ejecutar simulaciones sin código:

```bash
cd src/presentation
python main.py
```

#### Características de la GUI:

1. **Simulación de Especie Única**
   - Configuración para *Aedes aegypti* o *Toxorhynchites* individualmente
   - 10 escenarios predefinidos en 5 categorías (Base, Estrés, Control, Óptimas, Brote)
   - Poblaciones iniciales por estadio (huevos, larvas L1-L4, pupas, adultos)
   - Condiciones ambientales unificadas
   - Visualización de evolución temporal completa

2. **Simulación Presa-Depredador**
   - Pestaña dedicada "🦁 Presa-Depredador"
   - Parámetros ambientales compartidos entre especies
   - Configuración dual: poblaciones de presa (4 estadios) y depredador (3 estadios)
   - 6 presets ambientales: Tropical Óptimo, Tropical Seco, Templado, Calor Extremo, Invierno, Monzón
   - 9 presets de interacción: Balanceado, Control Débil, Control Fuerte, Presión sobre Presa, Introducción Tardía, Seco, Óptimo, Largo Plazo, Brote
   - Comparación automática con y sin depredadores
   - Uso obligatorio de Prolog para inferencia dinámica

3. **Validación en Tiempo Real**
   - Indicadores visuales: ✓ (válido), ⚠ (fuera de rango), ✗ (error)
   - Actualización instantánea al modificar valores
   - Tooltips con mensajes de error específicos

4. **Ayuda Contextual**
   - Tooltips informativos en todos los parámetros
   - Información sobre rangos válidos y valores típicos
   - Guías de referencia para configuraciones

5. **Visualización de Resultados**
   - **Especie única**: Gráficos de evolución poblacional por estadio con estadísticas
   - **Presa-Depredador**: Visualización dual con dos modos:
     * **Dinámicas Completas**: Grid 2×2 con poblaciones totales, composición por estadio (presa y depredador), y estadísticas overlay
     * **Comparación con/sin Depredadores**: Gráficas lado a lado mostrando impacto de depredación con porcentaje de reducción
   - Estadísticas detalladas: poblaciones inicial/final, picos, promedios, desviación estándar
   - Botones para alternar entre vistas de gráficas

6. **Exportación de Datos**
   - **CSV**: Exportación de trayectorias completas (día, poblaciones por estadio, condiciones ambientales)
   - **PNG**: Guardado de todas las gráficas disponibles (dinámicas y comparaciones)
   - Selección de carpeta de destino mediante diálogo

### Ejemplo Básico: Simulación Poblacional (API)

```python
from application.services.simulation_service import SimulationService
from application.dtos import SimulationConfig

# Crear servicio de simulación
service = SimulationService()

# Configurar simulación de Aedes aegypti
config = SimulationConfig(
    species_id='aedes_aegypti',
    duration_days=90,
    initial_eggs=100,
    initial_larvae=50,
    initial_pupae=20,
    initial_adults=30,
    temperature=28.0,      # °C
    humidity=75.0,         # %
    water_availability=0.8 # Disponibilidad de sitios de oviposición
)

# Ejecutar simulación
result = service.run_population_simulation(config)

# Analizar resultados
print(f"Población final: {result.total_population[-1]:.0f}")
print(f"Pico poblacional: {result.statistics['peak_population']:.0f}")
print(f"Día del pico: {result.statistics['peak_day']}")
```

### Simulación con Depredadores (Modelo Poblacional)

```python
from application.services.population_service import PopulationService
from application.dtos import PredatorPreyConfig

# Servicio de simulación
service = PopulationService()

# Configurar simulación presa-depredador
config = PredatorPreyConfig(
    species_id='aedes_aegypti',           # Presa
    predator_species_id='toxorhynchites', # Depredador
    duration_days=90,
    
    # Poblaciones iniciales de presa
    initial_eggs=1000,
    initial_larvae=500,
    initial_pupae=100,
    initial_adults=100,
    
    # Poblaciones iniciales de depredador (estadios larvales únicamente)
    predator_initial_larvae=20,
    predator_initial_pupae=5,
    predator_initial_adults=10,
    
    # Ambiente compartido
    temperature=28.0,
    humidity=75.0,
    water_availability=0.8
)

# Ejecutar simulación con depredadores
result = service.simulate_predator_prey(config, use_prolog=True)

print(f"Presa - Población inicial: {result.statistics['prey_initial']:.0f}")
print(f"Presa - Población final: {result.statistics['prey_final']:.0f}")
print(f"Presa - Reducción por depredación: {result.statistics['predation_reduction_percent']:.1f}%")
print(f"Depredador - Población final: {result.statistics['predator_final']:.0f}")

# Comparar con y sin depredadores
comparison = service.compare_predation_effect(config, use_prolog=True)

with_pred = comparison['with_predators']
without_pred = comparison['without_predators']

print(f"\nCon depredadores: {with_pred.statistics['prey_final']:.0f} presas")
print(f"Sin depredadores: {without_pred.statistics['prey_final']:.0f} presas")
print(f"Efectividad del control: {comparison['reduction_percentage']:.1f}%")
```

### Simulación Basada en Agentes (Código Implementado, GUI Pendiente)

```python
# Simulación con Toxorhynchites como control biológico
result = service.run_agent_simulation(
    config=config,
    num_predators=10,
    predator_species_id='toxorhynchites'
)

print(f"Vectores supervivientes: {result.num_vectors_final}")
print(f"Tasa de supervivencia: {result.get_survival_rate_vectors():.2%}")
print(f"Presas consumidas: {result.total_prey_consumed}")
```

### Simulación Híbrida (Comparativa)

```python
# Ejecutar ambos modelos en paralelo
hybrid_result = service.run_hybrid_simulation(
    config=config,
    num_predators=10,
    predator_species_id='toxorhynchites'
)

# Comparar resultados
summary = hybrid_result.get_comparison_summary()
print(f"Pico (Poblacional: {summary['population_peak']:.0f}")
print(f"Pico (Agentes): {summary['agent_peak']:.0f}")
print(f"Diferencia: {summary[Comparativa]:.0f}")
```

### Comparación de Escenarios

```python
from application.use_cases.compare_scenarios import (
    CompareScenarios,
    CompareScenariosRequest,
    ScenarioConfig
)

# Definir escenarios con diferentes temperaturas
scenarios = {
    "temp_25C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=25.0,
        humidity=75.0,
        water_availability=0.8
    ),
    "temp_30C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=30.0,
        humidity=75.0,
        water_availability=0.8
    ),
    "temp_35C": ScenarioConfig(
        species_id='aedes_aegypti',
        duration_days=60,
        initial_adults=50,
        temperature=35.0,
        humidity=75.0,
        water_availability=0.8
    )
}

# Comparar escenarios
use_case = CompareScenarios(service)
request = CompareScenariosRequest(
    scenarios=scenarios,
    simulation_type='population',
    comparison_metric='peak_population'
)
response = use_case.execute(request)

# Resultados
print(f"Mejor escenario para crecimiento: {response.best_scenario}")
print(f"Ranking: {response.ranking}")
```

### Gestión de Checkpoints

```python
from application.use_cases.manage_checkpoints import (
    SaveCheckpoint, LoadCheckpoint,
    SaveCheckpointRequest, LoadCheckpointRequest
)

# Guardar checkpoint
save_use_case = SaveCheckpoint(service)
save_request = SaveCheckpointRequest(
    result=result,
    config=config,
    simulation_type='population',
    checkpoint_name='aedes_90dias.json'
)
save_response = save_use_case.execute(save_request)
print(f"Guardado en: {save_response.checkpoint_path}")

# Cargar checkpoint
load_use_case = LoadCheckpoint(service)
load_request = LoadCheckpointRequest(
    checkpoint_path=save_response.checkpoint_path
)
load_response = load_use_case.execute(load_request)
loaded_result = load_response.result
```

### Visualización de Resultados

```python
from application.visualization import (
    plot_population_evolution,
    plot_scenario_comparison,
    plot_predator_prey_interaction,
    plot_predation_impact_comparison
)

# Gráfico de evolución poblacional (especie única)
fig = plot_population_evolution(
    result=result,
    save_path='results/population_evolution.png'
)

# Gráfico de comparación de escenarios
fig = plot_scenario_comparison(
    comparison_result=response.result,
    metric='peak_population',
    save_path='results/scenario_comparison.png'
)

# Gráfico de interacción presa-depredador (2×2 grid)
fig = plot_predator_prey_interaction(
    result=predator_prey_result,
    show=True,
    save_path='results/predator_prey_dynamics.png'
)

# Gráfico de comparación con/sin depredadores
fig = plot_predation_impact_comparison(
    with_predators=comparison['with_predators'],
    without_predators=comparison['without_predators'],
    show=True,
    save_path='results/predation_impact.png'
)
```

---

## Especies Modeladas

### Aedes aegypti (Vector)

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **Ciclo de vida** | 8-14 días | Huevo a adulto |
| **Estadios larvarios** | L1, L2, L3, L4 | 4 estadios |
| **Huevos por lote** | 80-150 | Por evento de oviposición |
| **Eventos de oviposición** | 3 | Por hembra en su vida |
| **Supervivencia diaria adulto** | 95% | En condiciones óptimas |
| **Temperatura óptima** | 25-28°C | Desarrollo máximo |
| **Temperatura letal** | <10°C, >40°C | Mortalidad significativa |
| **Humedad óptima** | 80% | Para oviposición |

### Toxorhynchites spp. (Depredador)

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **Ciclo de vida** | 14-25 días | Desarrollo más lento |
| **Estadios depredadores** | L3, L4 | Larvas grandes |
| **Tasa de depredación** | 15-20/día | Presas por día |
| **Respuesta funcional** | Tipo II | Holling (saturación) |
| **Presas vulnerables** | L1, L2, L3, L4 | Larvas de Aedes |
| **Supervivencia diaria adulto** | 97% | Mayor longevidad |
| **Huevos por lote** | 40-80 | Menor fecundidad |

---

## Configuración

### Archivo de Configuración Principal

`config/default_config.json`:

```json
{
  "simulation": {
    "default_days": 365,
    "time_step": 1,
    "random_seed": null,
    "stochastic_mode": true
  },
  "initial_populations": {
    "aedes_aegypti": {
      "egg": 200,
      "larva_l1": 150,
      "larva_l2": 120,
      "larva_l3": 100,
      "larva_l4": 80,
      "pupa": 50,
      "adult_female": 100,
      "adult_male": 100
    }
  },
  "species_configs": [
    "species/aedes_aegypti.json",
    "species/toxorhynchites.json"
  ],
  "environment_config": "environment/default_environment.json"
}
```

### Configuración de Especie

`config/species/aedes_aegypti.json`:

```json
{
  "species_id": "aedes_aegypti",
  "display_name": "Aedes aegypti",
  "life_stages": {
    "egg": {
      "duration_days": {"min": 2, "max": 7},
      "survival_to_next": 0.80
    },
    "larva_l1": {
      "duration_days": {"min": 1, "max": 2},
      "survival_to_next": 0.85
    }
    // ... más estadios
  },
  "reproduction": {
    "eggs_per_batch": {"min": 80, "max": 150},
    "oviposition_events": 3,
    "min_age_reproduction_days": 3
  },
  "environmental_sensitivity": {
    "optimal_temperature": {"min": 25, "max": 28},
    "lethal_temperature": {"min": 10, "max": 40},
    "optimal_humidity": 80
  }
}
```

### Parámetros de SimulationConfig

| Parámetro | Tipo | Rango | Descripción |
|-----------|------|-------|-------------|
| `species_id` | str | - | Identificador de especie |
| `duration_days` | int | 1-3650 | Duración en días |
| `initial_eggs` | int | ≥0 | Huevos iniciales |
| `initial_larvae` | int/list | ≥0 | Larvas iniciales (total o [L1,L2,L3,L4]) |
| `initial_pupae` | int | ≥0 | Pupas iniciales |
| `initial_adults` | int | ≥0 | Adultos iniciales |
| `temperature` | float | -10 a 50 | Temperatura (°C) |
| `humidity` | float | 0-100 | Humedad relativa (%) |
| `water_availability` | float | 0-1 | Disponibilidad de agua |
| `random_seed` | int | - | Semilla para reproducibilidad |

---

## API y Casos de Uso

### Casos de Uso Disponibles

| Caso de Uso | Descripción | Request | Response |
|-------------|-------------|---------|----------|
| `RunPopulationSimulation` | Ejecuta simulación poblacional | `config` | `PopulationResult` |
| `RunAgentSimulation` | Ejecuta simulación basada en agentes | `config`, `num_predators` | `AgentResult` |
| `RunHybridSimulation` | Ejecuta ambos modelos en paralelo | `config`, `num_predators` | `HybridResult` |
| `CompareScenarios` | Compara múltiples escenarios | `scenarios`, `metric` | `ComparisonResult` |
| `SaveCheckpoint` | Guarda estado de simulación | `result`, `config` | `checkpoint_path` |
| `LoadCheckpoint` | Carga checkpoint guardado | `checkpoint_path` | `config`, `result` |
| `ListCheckpoints` | Lista checkpoints disponibles | `filters` | `List[CheckpointInfo]` |
| `DeleteCheckpoint` | Elimina checkpoint | `checkpoint_path` | `success` |
| `GetAvailableSpecies` | Obtiene especies configuradas | - | `List[SpeciesInfo]` |
| `GetAvailablePredators` | Obtiene especies depredadoras | - | `List[SpeciesInfo]` |
| `GetSpeciesParameters` | Obtiene parámetros de especie | `species_id` | `SpeciesInfo` |

### DTOs Principales

| DTO | Descripción | Campos Clave |
|-----|-------------|--------------|
| `SimulationConfig` | Configuración de simulación | `species_id`, `duration_days`, poblaciones iniciales, ambiente |
| `PopulationResult` | Resultado de simulación poblacional | `days`, `eggs`, `larvae`, `adults`, `statistics` |
| `AgentResult` | Resultado de simulación por agentes | `num_vectors_final`, `total_eggs_laid`, `prey_consumed` |
| `HybridResult` | Resultado de simulación híbrida | `population_result`, `agent_result`, `comparison_data` |
| `ComparisonResult` | Resultado de comparación | `scenario_names`, `results`, `ranking` |

---

## Pruebas

### Ejecutar Suite Completa

```bash
cd src
python -m unittest discover tests -v
```

### Ejecutar Pruebas por Módulo

```bash
# Pruebas de casos de uso
python -m unittest tests.test_use_cases_core -v

# Pruebas de servicios
python -m unittest tests.test_application_simulation_service -v

# Pruebas de checkpoints
python -m unittest tests.test_use_cases_checkpoints -v
```

### Cobertura de Pruebas

| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| Casos de Uso (Core) | 36 | Simulaciones completas |
| Casos de Uso (Comparación) | 17 | Comparación de escenarios |
| Casos de Uso (Checkpoints) | 24 | Gestión de persistencia |
| Servicios | 33 | Lógica de negocio |
| **Total** | **99+** | - |

---

## Capa de Presentación

La capa de presentación cuenta con una **interfaz gráfica completa** implementada en Tkinter:
  - **GUI (Graphical User Interface)**: Aplicación de escritorio funcional
  - Vista principal con navegación por pestañas
  - Vista de configuración de simulación con validación
  - Vista de resultados con gráficos integrados
  - Sistema de tooltips contextual
  - Presets de escenarios predefinidos
  - Tema visual profesional y consistente

### Arquitectura de Presentación

La GUI implementa el patrón **Modelo-Vista-Controlador (MVC)**:

- **Vistas** (`views/`): Componentes visuales (SimulationView, ResultsView, HomeView)
- **Controladores** (`controllers/`): Lógica de interacción (SimulationController)
- **Componentes** (`components/`): Elementos reutilizables (Sidebar, StatusBar)
- **Widgets** (`widgets/`): Controles personalizados (ToolTip)
- **Datos** (`data/`): Configuraciones estáticas (scenario_presets, parameter_ranges)
- **Estilos** (`styles/`): Temas visuales (theme.py con paleta de colores profesional)

---

## Estado del Proyecto

### Backend: Completado ✓

| Componente | Estado | Descripción |
|------------|--------|-------------|
| **Modelos poblacionales** | ✓ Operativo | Matrices de Leslie con tasas dinámicas |
| **Integración Prolog** | ✓ Operativo | Tasas de supervivencia ajustadas por ambiente |
| **Servicios de simulación** | ✓ Operativo | PopulationService con fallback a tasas estáticas |
| **Sistema de checkpoints** | ✓ Operativo | Guardar/cargar simulaciones |
| **Casos de uso** | ✓ Operativo | 10+ casos de uso implementados |
| **Configuración JSON** | ✓ Operativo | Parámetros externalizados por especie |
| **Visualización** | ✓ Operativo | Matplotlib/Seaborn integrados |

### Frontend: Completado ✓

| Componente | Estado | Descripción |
|------------|--------|-------------|
| **Interfaz gráfica** | ✓ Operativo | Tkinter con arquitectura MVC |
| **Validación de parámetros** | ✓ Operativo | Tiempo real con indicadores visuales |
| **Tooltips informativos** | ✓ Operativo | Ayuda contextual en 9 parámetros |
| **Presets de escenarios** | ✓ Operativo | 10 escenarios en 5 categorías |
| **Configuración de simulación** | ✓ Operativo | Formularios con validación |
| **Visualización de resultados** | ✓ Operativo | Gráficos integrados en GUI |
| **Tema visual** | ✓ Operativo | Paleta profesional científica |

### Funcionalidades Pendientes

| Componente | Prioridad | Estado |
|------------|-----------|--------|
| **Simulación basada en agentes** | Alta | Código implementado, pendiente GUI |
| **Simulación híbrida** | Media | Backend listo, pendiente interfaz |
| **CLI** | Media | Por implementar |
| **API REST** | Baja | Por implementar |
| **Exportación avanzada** | Baja | Por implementar |

### Integración Prolog

El sistema Prolog está **totalmente integrado** para ajustar dinámicamente las tasas de supervivencia:

- **Consulta activa**: Cada paso de simulación consulta `effective_survival/6`
- **Factores ambientales**: Temperatura, humedad, disponibilidad de agua
- **Fallback robusto**: Si Prolog falla, usa tasas estáticas del JSON
- **Validación**: Tasas fuera de [0,1] son rechazadas automáticamente
- **Impacto medido**: Tests muestran diferencias de +14,000% en población con tasas dinámicas

#### Arquitectura de Depredación (Preparada)

Las bases para depredación están implementadas pero inactivas:

- **Reglas Prolog**: `predation_risk/5`, `predation_rate/4` definidas
- **Método en modelo**: `_apply_predation_effects()` preparado
- **Falta**: Activar llamada en `step()` y crear GUI para configuración

---

## Documentación Adicional

Cada capa del sistema cuenta con documentación detallada:

- [Capa de Dominio](src/domain/README.md) - Modelos, entidades y agentes
- [Capa de Aplicación](src/application/README.md) - Servicios, casos de uso y DTOs
- [Capa de Infraestructura](src/infrastructure/README.md) - Configuración y Prolog bridge
- [Sistema Prolog](src/prolog/PROLOG_DOCUMENTATION.md) - Base de conocimiento

---

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## Contacto

Para preguntas, sugerencias o reportes de bugs, por favor abrir un Issue en el repositorio.
