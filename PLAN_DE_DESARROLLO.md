# Plan de Desarrollo: Simulador de Dinámica Poblacional
## Interacción *Toxorhynchites* (Mosquito Elefante) - *Aedes aegypti*

---

## 1. Resumen Ejecutivo

### 1.1 Objetivo del Proyecto
Desarrollar un simulador basado en agentes que modele la dinámica poblacional y las interacciones ecológicas entre *Toxorhynchites* spp. (mosquito elefante, depredador) y *Aedes aegypti* (vector de enfermedades), utilizando programación lógica (Prolog) como núcleo del sistema de razonamiento e inferencia.

### 1.2 Justificación Científica
*Toxorhynchites* es un género de mosquitos cuyas larvas son depredadores obligados de otras larvas de mosquitos, incluyendo *Aedes aegypti*. Esta relación depredador-presa representa una estrategia de control biológico de interés epidemiológico. El modelado computacional de esta interacción permite:

- Evaluar escenarios de introducción de *Toxorhynchites* como agente de biocontrol
- Predecir dinámicas poblacionales bajo diferentes condiciones ambientales
- Analizar la viabilidad de estrategias de control vectorial

### 1.3 Marco Teórico Computacional
El proyecto se fundamenta en:
- **"Artificial Intelligence: A Modern Approach" (Russell & Norvig)**: Capítulos 1-2 (Agentes Inteligentes y Entornos) - arquitectura de agentes racionales, percepciones, acciones y funciones de utilidad
- **Programación Lógica (Prolog)**: Paradigma declarativo para representación del conocimiento, inferencia basada en reglas y razonamiento sobre relaciones ecológicas
- **Matrices de Leslie**: Para modelado demográfico estructurado por edad/estadio
- **Procesos Estocásticos**: Para incorporar variabilidad ambiental y demográfica

---

## 2. Especificaciones Técnicas

### 2.1 Stack Tecnológico

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Motor de Inferencia | SWI-Prolog | Estándar en programación lógica, amplia documentación |
| Interfaz Python-Prolog | PySwip | Integración nativa, permite llamadas bidireccionales |
| Backend | Python 3.10+ | Ecosistema científico (NumPy, SciPy) |
| Frontend | Tkinter + Matplotlib | Simplicidad, integración nativa con Python |
| Persistencia | JSON/CSV | Portabilidad, legibilidad humana |
| Visualización | Matplotlib + Seaborn | Gráficos científicos de alta calidad |

### 2.2 Requisitos del Sistema
```
- Python >= 3.10
- SWI-Prolog >= 8.4
- PySwip >= 0.2.10
- NumPy >= 1.21
- Matplotlib >= 3.5
- Seaborn >= 0.11
```

---

## 3. Funcionalidades del Simulador

### 3.1 Resumen de Funcionalidades

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FUNCIONALIDADES DEL SIMULADOR                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CONFIGURACIÓN              SIMULACIÓN              ANÁLISIS        │
│  ─────────────              ──────────              ────────        │
│  • Cargar parámetros        • Ejecutar N días      • Consultas      │
│    desde JSON               • Pausar/Reanudar        Prolog         │
│  • Editar en GUI            • Paso a paso          • Tendencias     │
│  • Guardar config           • Reiniciar            • Viabilidad     │
│  • Restaurar defaults                                biocontrol     │
│                                                                     │
│  VISUALIZACIÓN              PERSISTENCIA           EXPORTACIÓN      │
│  ─────────────              ────────────           ───────────      │
│  • Gráfico temporal         • Guardar simulación   • CSV datos      │
│  • Distribución estadios    • Cargar simulación    • PNG gráficos   │
│  • Razón depredador/presa   • Historial            • JSON reporte   │
│  • Indicadores de estado                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Panel de Configuración (Parámetros Editables)

| Categoría | Parámetros | Editable en GUI |
|-----------|------------|-----------------|
| **Población Inicial** | Cantidad por especie y estadio | ✓ Sliders/Inputs |
| **Ciclo de Vida** | Duración de cada estadio (min/max días) | ✓ Spinboxes |
| **Supervivencia** | Tasas de transición entre estadios | ✓ Inputs (0-1) |
| **Fecundidad** | Huevos por hembra, eventos de oviposición | ✓ Inputs |
| **Depredación** | Tasa de ataque, tiempo de manipulación | ✓ Inputs |
| **Ambiente** | Temperatura, humedad, capacidad de carga | ✓ Sliders |
| **Simulación** | Días a simular, semilla aleatoria | ✓ Inputs |

### 3.3 Acciones de Simulación

| Acción | Descripción | Atajo |
|--------|-------------|-------|
| **Ejecutar** | Correr simulación completa (N días) | `F5` |
| **Pausar/Reanudar** | Detener/continuar simulación en curso | `Space` |
| **Paso a Paso** | Avanzar un día de simulación | `F10` |
| **Reiniciar** | Volver a condiciones iniciales | `Ctrl+R` |
| **Detener** | Cancelar simulación en curso | `Esc` |

### 3.4 Consultas Disponibles (Sistema Prolog)

El usuario podrá realizar consultas declarativas al sistema:

| Consulta | Descripción | Ejemplo de Respuesta |
|----------|-------------|---------------------|
| `population_trend/3` | Tendencia poblacional | `growing`, `stable`, `declining` |
| `predator_prey_ratio/2` | Razón depredador-presa | `0.045` |
| `biocontrol_viable/2` | Evaluación de biocontrol | `effective`, `ineffective` |
| `ecological_equilibrium/1` | ¿Hay equilibrio? | `true/false` |
| `extinction_risk/3` | Riesgo de extinción | `low`, `moderate`, `high`, `critical` |

### 3.5 Visualizaciones

1. **Gráfico Temporal de Poblaciones**: Líneas mostrando evolución de ambas especies
2. **Distribución por Estadios**: Barras apiladas con proporción de cada estadio
3. **Razón Depredador-Presa**: Evolución temporal del ratio
4. **Mapa de Calor Ambiental**: Condiciones de temperatura/humedad vs supervivencia

### 3.6 Exportación

| Formato | Contenido |
|---------|-----------|
| **CSV** | Series temporales de poblaciones, parámetros usados |
| **PNG** | Gráficos generados (300 DPI para publicación) |
| **JSON** | Reporte completo de simulación (reproducible) |

---

## 4. Sistema de Configuración

### 4.1 Flujo de Configuración

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   config/*.json  │────►│  Python carga    │────►│  Prolog recibe   │
│   (parámetros    │     │  ConfigManager   │     │  hechos vía      │
│    por defecto)  │     │                  │     │  assertz()       │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   GUI muestra    │
                         │   y permite      │◄───── Usuario modifica
                         │   editar         │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Al ejecutar:    │
                         │  Python inyecta  │────► Prolog actualizado
                         │  params a Prolog │
                         └──────────────────┘
```

### 4.2 Estructura de Archivos de Configuración

#### `config/species/aedes_aegypti.json`
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
    },
    "larva_l2": {
      "duration_days": {"min": 1, "max": 2},
      "survival_to_next": 0.85
    },
    "larva_l3": {
      "duration_days": {"min": 2, "max": 3},
      "survival_to_next": 0.80
    },
    "larva_l4": {
      "duration_days": {"min": 2, "max": 4},
      "survival_to_next": 0.80
    },
    "pupa": {
      "duration_days": {"min": 1, "max": 3},
      "survival_to_next": 0.90
    },
    "adult": {
      "duration_days": {"min": 14, "max": 30},
      "survival_daily": 0.95
    }
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

#### `config/species/toxorhynchites.json`
```json
{
  "species_id": "toxorhynchites",
  "display_name": "Toxorhynchites spp.",
  "life_stages": {
    "egg": {
      "duration_days": {"min": 2, "max": 4},
      "survival_to_next": 0.85
    },
    "larva_l1": {
      "duration_days": {"min": 2, "max": 3},
      "survival_to_next": 0.90
    },
    "larva_l2": {
      "duration_days": {"min": 2, "max": 4},
      "survival_to_next": 0.90
    },
    "larva_l3": {
      "duration_days": {"min": 3, "max": 5},
      "survival_to_next": 0.88,
      "is_predatory": true,
      "predation_rate": 15
    },
    "larva_l4": {
      "duration_days": {"min": 4, "max": 8},
      "survival_to_next": 0.85,
      "is_predatory": true,
      "predation_rate": 20
    },
    "pupa": {
      "duration_days": {"min": 2, "max": 5},
      "survival_to_next": 0.92
    },
    "adult": {
      "duration_days": {"min": 30, "max": 60},
      "survival_daily": 0.97
    }
  },
  "reproduction": {
    "eggs_per_batch": {"min": 40, "max": 80},
    "oviposition_events": 2,
    "min_age_reproduction_days": 5
  },
  "predation": {
    "functional_response": {
      "attack_rate": 0.5,
      "handling_time": 0.1
    },
    "prey_stages": ["larva_l1", "larva_l2", "larva_l3", "larva_l4"]
  }
}
```

#### `config/environment/default_environment.json`
```json
{
  "environment_id": "tropical_urban",
  "display_name": "Ambiente Urbano Tropical",
  "temperature": {
    "mean": 27,
    "std_dev": 3,
    "seasonal_variation": true
  },
  "humidity": {
    "mean": 75,
    "std_dev": 10
  },
  "habitat": {
    "carrying_capacity": 10000,
    "breeding_sites": 50,
    "quality": 0.8
  },
  "seasonality": {
    "wet_season_months": [5, 6, 7, 8, 9, 10],
    "dry_season_months": [11, 12, 1, 2, 3, 4],
    "wet_season_multiplier": 1.3,
    "dry_season_multiplier": 0.7
  }
}
```

#### `config/default_config.json`
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
    },
    "toxorhynchites": {
      "egg": 20,
      "larva_l1": 15,
      "larva_l2": 12,
      "larva_l3": 10,
      "larva_l4": 8,
      "pupa": 5,
      "adult_female": 10,
      "adult_male": 10
    }
  },
  "species_configs": [
    "species/aedes_aegypti.json",
    "species/toxorhynchites.json"
  ],
  "environment_config": "environment/default_environment.json"
}
```

---

## 5. Arquitectura del Sistema

### 5.1 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE PRESENTACIÓN                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Frontend (Tkinter)                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │  Panel de   │  │  Panel de   │  │ Panel de Resultados │   │  │
│  │  │ Parámetros  │  │  Control    │  │   y Visualización   │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CAPA DE APLICACIÓN                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  Controlador Principal                       │    │
│  │         (Orquestación de Simulación y Eventos)              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                   │                                  │
│         ┌─────────────────────────┼─────────────────────────┐       │
│         ▼                         ▼                         ▼       │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐   │
│  │  Servicio   │         │  Servicio   │         │  Servicio   │   │
│  │ Simulación  │         │ Inferencia  │         │Persistencia │   │
│  └─────────────┘         └─────────────┘         └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CAPA DE DOMINIO                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Motor de Agentes                          │   │
│  │  ┌────────────────┐    ┌────────────────┐                   │   │
│  │  │ Agente Aedes   │    │Agente Toxorhyn.│                   │   │
│  │  └────────────────┘    └────────────────┘                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Modelos Matemáticos (Python)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │Matriz Leslie │  │  Procesos    │  │  Modelo      │       │   │
│  │  │  Aedes/Toxo  │  │ Estocásticos │  │  Ambiental   │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE RAZONAMIENTO (PROLOG)                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Base de Conocimiento                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │   Hechos     │  │   Reglas     │  │  Ontología   │       │   │
│  │  │  Biológicos  │  │ Ecológicas   │  │   Especies   │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Motor de Inferencia                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │  Decisiones  │  │  Dinámica    │  │ Evaluación   │       │   │
│  │  │   Agentes    │  │ Poblacional  │  │  Aptitud     │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Estructura de Directorios

```
Mosquitoes-Simulation/
│
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── PLAN_DE_DESARROLLO.md
│
├── src/
│   ├── __init__.py
│   │
│   ├── prolog/                          # Capa de Razonamiento
│   │   ├── knowledge_base/
│   │   │   ├── species_ontology.pl      # Ontología de especies
│   │   │   ├── biological_facts.pl      # Hechos biológicos
│   │   │   ├── ecological_rules.pl      # Reglas ecológicas
│   │   │   └── environmental_facts.pl   # Condiciones ambientales
│   │   │
│   │   ├── inference/
│   │   │   ├── agent_decisions.pl       # Lógica de decisión de agentes
│   │   │   ├── state_transitions.pl     # Transiciones de estado
│   │   │   ├── population_dynamics.pl   # Dinámica poblacional declarativa
│   │   │   └── fitness_evaluation.pl    # Evaluación de aptitud
│   │   │
│   │   └── queries/
│   │       ├── population_queries.pl    # Consultas poblacionales
│   │       └── simulation_queries.pl    # Consultas de simulación
│   │
│   ├── domain/                          # Capa de Dominio
│   │   ├── __init__.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py            # Clase base de agentes
│   │   │   ├── aedes_agent.py           # Agente Aedes aegypti
│   │   │   └── toxorhynchites_agent.py  # Agente Toxorhynchites
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── leslie_matrix.py         # Implementación matriz de Leslie
│   │   │   ├── stochastic_processes.py  # Procesos estocásticos
│   │   │   ├── population_model.py      # Modelo poblacional integrado
│   │   │   └── environment_model.py     # Modelo ambiental
│   │   │
│   │   └── entities/
│   │       ├── __init__.py
│   │       ├── mosquito.py              # Entidad mosquito
│   │       ├── population.py            # Entidad población
│   │       └── habitat.py               # Entidad hábitat
│   │
│   ├── application/                     # Capa de Aplicación
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── simulation_service.py    # Servicio de simulación
│   │   │   ├── inference_service.py     # Servicio de inferencia Prolog
│   │   │   └── persistence_service.py   # Servicio de persistencia
│   │   │
│   │   └── controllers/
│   │       ├── __init__.py
│   │       └── simulation_controller.py # Controlador principal
│   │
│   ├── presentation/                    # Capa de Presentación
│   │   ├── __init__.py
│   │   ├── main_window.py               # Ventana principal
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── parameter_panel.py       # Panel de parámetros
│   │   │   ├── control_panel.py         # Panel de control
│   │   │   ├── results_panel.py         # Panel de resultados
│   │   │   └── visualization_panel.py   # Panel de visualización
│   │   │
│   │   └── styles/
│   │       └── theme.py                 # Configuración visual
│   │
│   └── infrastructure/                  # Capa de Infraestructura
│       ├── __init__.py
│       ├── prolog_bridge.py             # Puente PySwip
│       ├── file_manager.py              # Gestión de archivos
│       └── config.py                    # Configuración global
│
├── data/
│   ├── parameters/                      # Parámetros biológicos
│   │   ├── aedes_params.json
│   │   └── toxorhynchites_params.json
│   │
│   ├── simulations/                     # Simulaciones guardadas
│   │   └── .gitkeep
│   │
│   └── exports/                         # Exportaciones
│       └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_prolog/
│   ├── test_domain/
│   ├── test_application/
│   └── test_integration/
│
└── docs/
    ├── biological_model.md              # Documentación del modelo biológico
    ├── prolog_reference.md              # Referencia de predicados Prolog
    └── user_manual.md                   # Manual de usuario
```

---

## 6. Modelo Biológico

### 6.1 Ciclo de Vida - *Aedes aegypti*

```
                    CICLO DE VIDA Aedes aegypti
                    ══════════════════════════
    
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   HUEVO ──────► LARVA (L1-L4) ──────► PUPA ──────► ADULTO  │
    │     │            │    │    │           │             │      │
    │   2-7 días     5-14 días total      1-3 días    14-30 días │
    │                  │    │    │                         │      │
    │                  ▼    ▼    ▼                         │      │
    │              [DEPREDACIÓN POR                        │      │
    │               Toxorhynchites]                        │      │
    │                                                      │      │
    │                                           ♀ Oviposición     │
    │                                                  │          │
    └──────────────────────────────────────────────────┘          │
                              ▲                                   │
                              └───────────────────────────────────┘
```

**Parámetros demográficos (condiciones óptimas: 25-28°C, HR >80%):**
- Tasa de oviposición: 100-200 huevos/hembra/vida
- Supervivencia huevo→larva: 0.70-0.90
- Supervivencia larva→pupa: 0.75-0.85
- Supervivencia pupa→adulto: 0.85-0.95
- Proporción sexual: ~1:1

### 6.2 Ciclo de Vida - *Toxorhynchites* spp.

```
                 CICLO DE VIDA Toxorhynchites
                 ════════════════════════════
    
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   HUEVO ──────► LARVA (L1-L4) ──────► PUPA ──────► ADULTO  │
    │     │            │                     │             │      │
    │   2-4 días    10-20 días            2-5 días    30-60 días │
    │                  │                                   │      │
    │                  ▼                                   │      │
    │           [DEPREDADOR ACTIVO]                        │      │
    │         Consume 10-20 larvas/día              Nectarívoro   │
    │         (estadios L3-L4)                             │      │
    │                                           ♀ Oviposición     │
    │                                                  │          │
    └──────────────────────────────────────────────────┘          │
                              ▲                                   │
                              └───────────────────────────────────┘
```

**Parámetros demográficos:**
- Tasa de oviposición: 50-100 huevos/hembra/vida
- Tasa de depredación larval: 10-20 larvas presa/día (L3-L4)
- Supervivencia general más alta que *Aedes*

### 6.3 Matriz de Leslie - Formulación

Para cada especie, la matriz de Leslie $\mathbf{L}$ se define como:

$$\mathbf{L} = \begin{pmatrix} F_1 & F_2 & F_3 & F_4 \\ P_1 & 0 & 0 & 0 \\ 0 & P_2 & 0 & 0 \\ 0 & 0 & P_3 & P_4 \end{pmatrix}$$

Donde:
- $F_i$: Fecundidad del estadio $i$
- $P_i$: Probabilidad de transición del estadio $i$ al $i+1$
- $P_4$: Probabilidad de supervivencia adulta

**Proyección poblacional:**

$$\mathbf{n}(t+1) = \mathbf{L} \cdot \mathbf{n}(t)$$

### 6.4 Interacción Depredador-Presa

La tasa de depredación se modela mediante una **respuesta funcional tipo II** (Holling):

$$C = \frac{a \cdot N}{1 + a \cdot T_h \cdot N}$$

Donde:
- $C$: Número de presas consumidas
- $a$: Tasa de ataque
- $N$: Densidad de presas
- $T_h$: Tiempo de manipulación

### 6.5 Factores Ambientales

| Factor | Efecto en *Aedes* | Efecto en *Toxorhynchites* |
|--------|-------------------|----------------------------|
| Temperatura | Óptimo: 25-28°C | Óptimo: 24-30°C |
| Humedad Relativa | >80% favorece oviposición | Similar |
| Precipitación | Crea criaderos | Crea criaderos |
| Disponibilidad de criaderos | Limita capacidad de carga | Limita capacidad de carga |

---

## 7. Diseño del Sistema en Prolog

### 7.1 Ontología de Especies (`species_ontology.pl`)

```prolog
%% ══════════════════════════════════════════════════════════════════
%% ONTOLOGÍA DE ESPECIES - Base de Conocimiento Taxonómica
%% ══════════════════════════════════════════════════════════════════

%% Jerarquía taxonómica
kingdom(animalia).
phylum(arthropoda).
class(insecta).
order(diptera).
family(culicidae).

%% Géneros de interés
genus(aedes).
genus(toxorhynchites).

%% Especies modeladas
species(aedes_aegypti, aedes).
species(toxorhynchites_rutilus, toxorhynchites).
species(toxorhynchites_amboinensis, toxorhynchites).

%% Roles ecológicos
ecological_role(aedes_aegypti, prey).
ecological_role(aedes_aegypti, disease_vector).
ecological_role(toxorhynchites_rutilus, predator).
ecological_role(toxorhynchites_amboinensis, predator).

%% Estadios de vida
life_stage(egg).
life_stage(larva_l1).
life_stage(larva_l2).
life_stage(larva_l3).
life_stage(larva_l4).
life_stage(pupa).
life_stage(adult_male).
life_stage(adult_female).

%% Estadios acuáticos (vulnerables/depredadores)
aquatic_stage(egg).
aquatic_stage(larva_l1).
aquatic_stage(larva_l2).
aquatic_stage(larva_l3).
aquatic_stage(larva_l4).
aquatic_stage(pupa).

%% Estadios que pueden depredar
predatory_stage(toxorhynchites, larva_l3).
predatory_stage(toxorhynchites, larva_l4).

%% Estadios vulnerables a depredación
vulnerable_stage(aedes, larva_l1).
vulnerable_stage(aedes, larva_l2).
vulnerable_stage(aedes, larva_l3).
vulnerable_stage(aedes, larva_l4).
```

### 7.2 Hechos Biológicos Dinámicos (`biological_facts.pl`)

Los parámetros biológicos se declaran como hechos dinámicos que Python inyecta en Prolog al iniciar la simulación desde los archivos JSON de configuración.

```prolog
%% ══════════════════════════════════════════════════════════════════
%% HECHOS BIOLÓGICOS - Cargados Dinámicamente desde Configuración
%% ══════════════════════════════════════════════════════════════════

%% Declaración de predicados dinámicos (modificables en runtime)
:- dynamic stage_duration/4.      % stage_duration(Species, Stage, MinDays, MaxDays)
:- dynamic survival_rate/4.       % survival_rate(Species, FromStage, ToStage, Rate)
:- dynamic fecundity/4.           % fecundity(Species, MinEggs, MaxEggs, Events)
:- dynamic predation_rate/3.      % predation_rate(Predator, PreyStage, Rate)
:- dynamic functional_response/3. % functional_response(Predator, AttackRate, HandlingTime)
:- dynamic environmental_param/2. % environmental_param(Name, Value)

%% ══════════════════════════════════════════════════════════════════
%% PREDICADOS DE CARGA - Llamados desde Python vía PySwip
%% ══════════════════════════════════════════════════════════════════

%% Limpiar todos los parámetros antes de recargar
clear_all_parameters :-
    retractall(stage_duration(_, _, _, _)),
    retractall(survival_rate(_, _, _, _)),
    retractall(fecundity(_, _, _, _)),
    retractall(predation_rate(_, _, _)),
    retractall(functional_response(_, _, _)),
    retractall(environmental_param(_, _)).

%% Cargar un parámetro de duración de estadio
load_stage_duration(Species, Stage, Min, Max) :-
    assertz(stage_duration(Species, Stage, Min, Max)).

%% Cargar tasa de supervivencia
load_survival_rate(Species, From, To, Rate) :-
    assertz(survival_rate(Species, From, To, Rate)).

%% Cargar fecundidad
load_fecundity(Species, Min, Max, Events) :-
    assertz(fecundity(Species, Min, Max, Events)).

%% Cargar tasa de depredación
load_predation_rate(Predator, PreyStage, Rate) :-
    assertz(predation_rate(Predator, PreyStage, Rate)).

%% Cargar respuesta funcional
load_functional_response(Predator, AttackRate, HandlingTime) :-
    assertz(functional_response(Predator, AttackRate, HandlingTime)).

%% Cargar parámetro ambiental
load_environmental_param(Name, Value) :-
    assertz(environmental_param(Name, Value)).

%% ══════════════════════════════════════════════════════════════════
%% CONSULTAS DE VALIDACIÓN
%% ══════════════════════════════════════════════════════════════════

%% Verificar que todos los parámetros requeridos están cargados
parameters_loaded(Species) :-
    stage_duration(Species, egg, _, _),
    stage_duration(Species, larva_l1, _, _),
    survival_rate(Species, egg, larva_l1, _),
    fecundity(Species, _, _, _).

%% Listar todos los parámetros cargados para una especie
list_species_params(Species, Params) :-
    findall(
        param(Type, Data),
        (
            (stage_duration(Species, S, Min, Max), Type = duration, Data = [S, Min, Max]);
            (survival_rate(Species, F, T, R), Type = survival, Data = [F, T, R]);
            (fecundity(Species, MinE, MaxE, Ev), Type = fecundity, Data = [MinE, MaxE, Ev])
        ),
        Params
    ).
```

### 7.3 Reglas Ecológicas (`ecological_rules.pl`)

```prolog
%% ══════════════════════════════════════════════════════════════════
%% REGLAS ECOLÓGICAS - Inferencia de Interacciones
%% ══════════════════════════════════════════════════════════════════

%% Regla: Determinar si puede ocurrir depredación
can_predate(Predator, Prey, PredatorStage, PreyStage) :-
    species(Predator, GenusP),
    species(Prey, GenusY),
    predatory_stage(GenusP, PredatorStage),
    vulnerable_stage(GenusY, PreyStage),
    ecological_role(Predator, predator),
    ecological_role(Prey, prey).

%% Regla: Calcular supervivencia ajustada por temperatura
%% temperature_adjustment(Temp, Species, AdjustmentFactor)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp >= 20, Temp =< 35,
    OptimalTemp = 27,
    Diff is abs(Temp - OptimalTemp),
    Factor is max(0.5, 1 - (Diff * 0.03)).

temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp >= 18, Temp =< 35,
    OptimalTemp = 28,
    Diff is abs(Temp - OptimalTemp),
    Factor is max(0.5, 1 - (Diff * 0.025)).

%% Regla: Supervivencia efectiva considerando ambiente
effective_survival(Species, FromStage, ToStage, Temp, Humidity, EffRate) :-
    survival_rate(Species, FromStage, ToStage, BaseRate),
    temperature_adjustment(Temp, Species, TempFactor),
    humidity_adjustment(Humidity, HumFactor),
    EffRate is BaseRate * TempFactor * HumFactor.

%% Ajuste por humedad
humidity_adjustment(Humidity, Factor) :-
    Humidity >= 60,
    Factor is min(1.0, 0.7 + (Humidity - 60) * 0.0075).
humidity_adjustment(Humidity, Factor) :-
    Humidity < 60,
    Factor is max(0.3, Humidity / 100).

%% Regla: Capacidad de carga del hábitat
carrying_capacity(Habitat, Species, Capacity) :-
    habitat_size(Habitat, Size),
    habitat_quality(Habitat, Quality),
    species_density_factor(Species, DensityFactor),
    Capacity is Size * Quality * DensityFactor.

%% Regla: Determinar si población está en equilibrio
population_equilibrium(Species, Population, Capacity, Status) :-
    Ratio is Population / Capacity,
    (Ratio < 0.8 -> Status = growing ;
     Ratio > 1.2 -> Status = declining ;
     Status = stable).

%% Regla: Evaluar impacto de depredación
predation_impact(PredatorPop, PreyPop, PreyStage, Impact) :-
    predation_rate(toxorhynchites, PreyStage, RatePerPredator),
    functional_response(toxorhynchites, AttackRate, HandlingTime),
    TotalPotential is PredatorPop * RatePerPredator,
    % Aplicar respuesta funcional tipo II
    Impact is (AttackRate * PreyPop) / (1 + AttackRate * HandlingTime * PreyPop),
    Impact =< TotalPotential.
```

### 7.4 Decisiones de Agentes (`agent_decisions.pl`)

```prolog
%% ══════════════════════════════════════════════════════════════════
%% DECISIONES DE AGENTES - Basado en AIMA Cap. 1
%% ══════════════════════════════════════════════════════════════════

%% Percepciones del agente
%% perceive(AgentID, Perception)
perceive(Agent, temperature(T)) :- current_temperature(T).
perceive(Agent, humidity(H)) :- current_humidity(H).
perceive(Agent, population_density(Species, D)) :- 
    current_population(Species, Pop),
    habitat_capacity(Cap),
    D is Pop / Cap.
perceive(Agent, prey_available(N)) :-
    agent_species(Agent, toxorhynchites),
    current_population(aedes_aegypti, N).

%% Estado interno del agente
%% agent_state(AgentID, Stage, Age, Energy, Reproduced)
:- dynamic agent_state/5.

%% Reglas de decisión para Aedes
decide_action(Agent, oviposit) :-
    agent_species(Agent, aedes_aegypti),
    agent_state(Agent, adult_female, Age, Energy, NotReproduced),
    Age > 3,
    Energy > 50,
    perceive(Agent, humidity(H)), H > 70,
    suitable_oviposition_site_available.

decide_action(Agent, feed) :-
    agent_species(Agent, aedes_aegypti),
    agent_state(Agent, adult_female, _, Energy, _),
    Energy < 40.

decide_action(Agent, rest) :-
    agent_species(Agent, aedes_aegypti),
    agent_state(Agent, _, _, Energy, _),
    Energy >= 40,
    \+ decide_action(Agent, oviposit).

%% Reglas de decisión para Toxorhynchites (larva depredadora)
decide_action(Agent, hunt) :-
    agent_species(Agent, toxorhynchites),
    agent_state(Agent, Stage, _, Energy, _),
    (Stage = larva_l3 ; Stage = larva_l4),
    Energy < 70,
    perceive(Agent, prey_available(N)), N > 0.

decide_action(Agent, grow) :-
    agent_species(Agent, toxorhynchites),
    agent_state(Agent, Stage, _, Energy, _),
    aquatic_stage(Stage),
    Energy >= 70.

%% Función de utilidad del agente
utility(Agent, Action, Utility) :-
    agent_state(Agent, _, _, Energy, _),
    action_energy_cost(Action, Cost),
    action_benefit(Agent, Action, Benefit),
    Utility is Benefit - Cost + Energy * 0.1.

%% Seleccionar mejor acción (agente racional)
best_action(Agent, BestAction) :-
    findall(U-A, (possible_action(Agent, A), utility(Agent, A, U)), Actions),
    sort(Actions, Sorted),
    reverse(Sorted, [_-BestAction|_]).
```

### 7.5 Dinámica Poblacional Declarativa (`population_dynamics.pl`)

```prolog
%% ══════════════════════════════════════════════════════════════════
%% DINÁMICA POBLACIONAL - Razonamiento Declarativo sobre Poblaciones
%% ══════════════════════════════════════════════════════════════════

%% ============== REPRESENTACIÓN DEL ESTADO POBLACIONAL ==============

%% Estado poblacional dinámico
:- dynamic population_state/4.  % population_state(Species, Stage, Count, Day)
:- dynamic environmental_state/3.  % environmental_state(Day, Temp, Humidity)

%% Inicializar población
initialize_population(Species, Stage, Count, Day) :-
    retractall(population_state(Species, Stage, _, _)),
    assertz(population_state(Species, Stage, Count, Day)).

%% ============== INFERENCIA DE TRANSICIONES POBLACIONALES ==============

%% Regla: Calcular siguiente generación para un estadio
next_generation(Species, Stage, Day, NewCount) :-
    population_state(Species, Stage, CurrentCount, Day),
    environmental_state(Day, Temp, Humidity),
    findall(PrevStage, 
            stage_transition(Species, PrevStage, Stage), 
            PrevStages),
    calculate_incoming(Species, PrevStages, Stage, Day, Temp, Humidity, Incoming),
    calculate_mortality(Species, Stage, CurrentCount, Temp, Humidity, Deaths),
    calculate_outgoing(Species, Stage, CurrentCount, Temp, Humidity, Outgoing),
    NewCount is max(0, CurrentCount + Incoming - Deaths - Outgoing).

%% Calcular individuos entrantes desde estadios anteriores
calculate_incoming(_, [], _, _, _, _, 0).
calculate_incoming(Species, [PrevStage|Rest], Stage, Day, Temp, Hum, Total) :-
    population_state(Species, PrevStage, PrevCount, Day),
    effective_survival(Species, PrevStage, Stage, Temp, Hum, SurvRate),
    transition_probability(Species, PrevStage, TransProb),
    Incoming is PrevCount * SurvRate * TransProb,
    calculate_incoming(Species, Rest, Stage, Day, Temp, Hum, RestIncoming),
    Total is Incoming + RestIncoming.

%% ============== INFERENCIA DE INTERACCIONES DEPREDADOR-PRESA ==============

%% Calcular mortalidad por depredación usando inferencia
predation_mortality(PreySpecies, PreyStage, Day, PredationDeaths) :-
    vulnerable_stage(PreySpecies, PreyStage),
    population_state(PreySpecies, PreyStage, PreyCount, Day),
    findall(PredCount,
            (predatory_stage(PredSpecies, PredStage),
             population_state(PredSpecies, PredStage, PredCount, Day)),
            PredatorCounts),
    sum_list(PredatorCounts, TotalPredators),
    calculate_functional_response(TotalPredators, PreyCount, PredationDeaths).

predation_mortality(PreySpecies, PreyStage, _, 0) :-
    \+ vulnerable_stage(PreySpecies, PreyStage).

%% Respuesta funcional tipo II (Holling) implementada declarativamente
calculate_functional_response(Predators, Prey, Consumed) :-
    functional_response(toxorhynchites, AttackRate, HandlingTime),
    Consumed is (Predators * AttackRate * Prey) / (1 + AttackRate * HandlingTime * Prey).

%% ============== CONSULTAS ANALÍTICAS ==============

%% Consulta: ¿La población está creciendo, estable o declinando?
population_trend(Species, Day, Trend) :-
    total_population(Species, Day, Pop1),
    PrevDay is Day - 1,
    total_population(Species, PrevDay, Pop0),
    ( Pop1 > Pop0 * 1.05 -> Trend = growing
    ; Pop1 < Pop0 * 0.95 -> Trend = declining
    ; Trend = stable
    ).

%% Consulta: Población total de una especie
total_population(Species, Day, Total) :-
    findall(Count, population_state(Species, _, Count, Day), Counts),
    sum_list(Counts, Total).

%% Consulta: Razón depredador-presa
predator_prey_ratio(Day, Ratio) :-
    total_population(toxorhynchites, Day, PredPop),
    total_population(aedes_aegypti, Day, PreyPop),
    PreyPop > 0,
    Ratio is PredPop / PreyPop.

%% Consulta: ¿Es viable el control biológico?
biocontrol_viable(Day, Assessment) :-
    predator_prey_ratio(Day, Ratio),
    population_trend(aedes_aegypti, Day, AedesTrend),
    population_trend(toxorhynchites, Day, ToxoTrend),
    assess_biocontrol(Ratio, AedesTrend, ToxoTrend, Assessment).

assess_biocontrol(Ratio, declining, growing, highly_effective) :- Ratio > 0.05.
assess_biocontrol(Ratio, declining, stable, effective) :- Ratio > 0.03.
assess_biocontrol(Ratio, stable, growing, promising) :- Ratio > 0.02.
assess_biocontrol(_, growing, declining, ineffective).
assess_biocontrol(_, _, _, requires_analysis).

%% ============== REGLAS DE EQUILIBRIO ECOLÓGICO ==============

%% Inferir si se alcanzó equilibrio poblacional
ecological_equilibrium(Day) :-
    population_trend(aedes_aegypti, Day, stable),
    population_trend(toxorhynchites, Day, stable),
    predator_prey_ratio(Day, Ratio),
    Ratio > 0.01,
    Ratio < 0.5.

%% Inferir riesgo de extinción
extinction_risk(Species, Day, Risk) :-
    total_population(Species, Day, Pop),
    minimum_viable_population(Species, MVP),
    ( Pop < MVP * 0.5 -> Risk = critical
    ; Pop < MVP -> Risk = high
    ; Pop < MVP * 2 -> Risk = moderate
    ; Risk = low
    ).

minimum_viable_population(aedes_aegypti, 50).
minimum_viable_population(toxorhynchites, 20).

%% ============== PROYECCIÓN TEMPORAL (RECURSIVA) ==============

%% Proyectar población N días hacia adelante
project_population(Species, CurrentDay, TargetDay, Projection) :-
    CurrentDay >= TargetDay,
    findall(stage_pop(Stage, Count), 
            population_state(Species, Stage, Count, CurrentDay), 
            Projection).

project_population(Species, CurrentDay, TargetDay, Projection) :-
    CurrentDay < TargetDay,
    NextDay is CurrentDay + 1,
    advance_all_stages(Species, CurrentDay, NextDay),
    project_population(Species, NextDay, TargetDay, Projection).

%% Avanzar todos los estadios un día
advance_all_stages(Species, CurrentDay, NextDay) :-
    forall(
        life_stage(Stage),
        (
            next_generation(Species, Stage, CurrentDay, NewCount),
            assertz(population_state(Species, Stage, NewCount, NextDay))
        )
    ).
```

---

## 8. Cronograma de Desarrollo

### 8.1 Diagrama de Gantt

```
SEMANA 1: Fundamentos
══════════════════════════════════════════════════════════════════
│ Día 1-2  │ Configuración del entorno y estructura del proyecto │
│ Día 3-4  │ Implementación base de conocimiento Prolog          │
│ Día 5-6  │ Desarrollo del puente PySwip                        │
│ Día 7    │ Testing unitario de componentes Prolog              │
══════════════════════════════════════════════════════════════════

SEMANA 2: Modelos Matemáticos y Dominio
══════════════════════════════════════════════════════════════════
│ Día 8-9  │ Implementación matrices de Leslie                   │
│ Día 10-11│ Desarrollo de procesos estocásticos                 │
│ Día 12-13│ Implementación de agentes (base + específicos)      │
│ Día 14   │ Integración modelo ambiental                        │
══════════════════════════════════════════════════════════════════

SEMANA 3: Capa de Aplicación y Servicios
══════════════════════════════════════════════════════════════════
│ Día 15-16│ Servicio de simulación                              │
│ Día 17-18│ Servicio de inferencia Prolog                       │
│ Día 19-20│ Servicio de persistencia (JSON/CSV)                 │
│ Día 21   │ Controlador principal e integración                 │
══════════════════════════════════════════════════════════════════

SEMANA 4: Frontend y Entrega
══════════════════════════════════════════════════════════════════
│ Día 22-23│ Interfaz Tkinter - paneles básicos                  │
│ Día 24-25│ Visualización con Matplotlib                        │
│ Día 26-27│ Testing de integración y corrección de bugs         │
│ Día 28-29│ Documentación final                                 │
│ Día 30   │ Entrega y presentación                              │
══════════════════════════════════════════════════════════════════
```

### 8.2 Entregables por Semana

| Semana | Entregables | Criterio de Aceptación |
|--------|-------------|------------------------|
| 1 | Base de conocimiento Prolog funcional, puente PySwip operativo | Consultas básicas desde Python exitosas |
| 2 | Modelos matemáticos implementados, agentes funcionales | Simulación de 100 días sin errores |
| 3 | Servicios completos, persistencia operativa | Guardar/cargar simulaciones correctamente |
| 4 | Aplicación completa con GUI | Demo funcional de simulación completa |

---

## 9. Métricas de Calidad

### 9.1 Criterios de Evaluación del Uso de Prolog

| Aspecto | Peso | Descripción |
|---------|------|-------------|
| Extensión de la base de conocimiento | 20% | Cantidad y calidad de hechos y reglas |
| Complejidad de inferencias | 25% | Uso de recursión, backtracking, unificación, meta-predicados (findall, forall) |
| Integración con modelo | 25% | Prolog como núcleo de decisiones |
| Consultas y análisis | 15% | Variedad de consultas implementadas |
| Documentación Prolog | 15% | Comentarios y explicaciones |

### 9.2 Criterios de Rigor Científico

| Aspecto | Peso | Descripción |
|---------|------|-------------|
| Precisión biológica | 25% | Parámetros basados en literatura |
| Validez del modelo matemático | 25% | Matrices de Leslie correctas |
| Reproducibilidad | 20% | Semillas aleatorias, configuración exportable |
| Análisis de sensibilidad | 15% | Variación de parámetros |
| Interpretación de resultados | 15% | Significado biológico de outputs |

---

## 10. Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Problemas de integración PySwip | Media | Alto | Testing temprano, documentación de PySwip |
| Complejidad excesiva del modelo | Media | Medio | Desarrollo incremental, simplificaciones justificadas |
| Performance en simulaciones largas | Baja | Medio | Optimización de consultas Prolog, caching |
| Errores en parámetros biológicos | Baja | Alto | Revisión con literatura científica |

---

## 11. Referencias Bibliográficas

### 11.1 Inteligencia Artificial
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.

### 11.2 Programación Lógica
- Clocksin, W. F., & Mellish, C. S. (2003). *Programming in Prolog* (5th ed.). Springer.
- Bratko, I. (2012). *Prolog Programming for Artificial Intelligence* (4th ed.). Pearson.

### 11.3 Ecología y Biología de Mosquitos
- Focks, D. A. (2003). A review of entomological sampling methods and indicators for dengue vectors. *WHO Special Programme for Research and Training in Tropical Diseases*.
- Collins, L. E., & Blackwell, A. (2000). The biology of Toxorhynchites mosquitoes and their potential as biocontrol agents. *Biocontrol News and Information*, 21(4), 105N-116N.
- Caswell, H. (2001). *Matrix Population Models: Construction, Analysis, and Interpretation* (2nd ed.). Sinauer Associates.

### 11.4 Modelado Poblacional
- Leslie, P. H. (1945). On the use of matrices in certain population mathematics. *Biometrika*, 33(3), 183-212.
- Holling, C. S. (1959). The components of predation as revealed by a study of small-mammal predation of the European pine sawfly. *The Canadian Entomologist*, 91(5), 293-320.

---

## 12. Apéndices

### Apéndice A: Instalación del Entorno

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias Python
pip install pyswip numpy matplotlib seaborn

# Verificar instalación de SWI-Prolog
swipl --version
```

### Apéndice B: Ejemplo de Consulta Python-Prolog

```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("src/prolog/knowledge_base/biological_facts.pl")

# Consultar tasa de supervivencia
for result in prolog.query("survival_rate(aedes_aegypti, egg, larva_l1, Rate)"):
    print(f"Tasa de supervivencia huevo→L1: {result['Rate']}")
```

### Apéndice C: Estructura de Archivo de Simulación (JSON)

```json
{
  "simulation_id": "sim_20260109_001",
  "created_at": "2026-01-09T10:30:00",
  "parameters": {
    "initial_aedes_population": 1000,
    "initial_toxo_population": 50,
    "simulation_days": 365,
    "temperature_mean": 27,
    "humidity_mean": 75
  },
  "results": {
    "daily_populations": [...],
    "final_aedes": 234,
    "final_toxo": 67,
    "reduction_percentage": 76.6
  }
}
```

---

**Documento preparado para el Proyecto Final de Programación Declarativa**  
**Universidad de La Habana - Curso 2025-2026**