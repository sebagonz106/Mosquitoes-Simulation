# Documentación del Sistema Prolog
## Simulador de Dinámica Poblacional: Mosquitos

**Directorio:** `src/prolog/`
---

## Estructura del Directorio

```
src/prolog/
├── knowledge_base/          # Base de Conocimiento Estática y Dinámica
│   ├── species_ontology.pl      # Ontología taxonómica y roles ecológicos
│   ├── biological_facts.pl      # Parámetros biológicos dinámicos (JSON→Prolog)
│   └── ecological_rules.pl      # Reglas de inferencia ecológica
│
├── inference/               # Motor de Inferencia y Razonamiento
│   ├── population_dynamics.pl   # Dinámica poblacional declarativa
│   └── agent_decisions.pl       # Arquitectura de agentes racionales (AIMA)
│
└── queries/                 # Consultas Predefinidas (En desarrollo)
    └── [Consultas de alto nivel para el usuario]
```

---

## 1. Base de Conocimiento (`knowledge_base/`)

### 1.1 `species_ontology.pl`

**Propósito:** Define la estructura taxonómica y características fundamentales de las especies modeladas.

#### Predicados Principales

| Predicado | Aridad | Descripción | Ejemplo |
|-----------|--------|-------------|---------|
| `kingdom/1` | 1 | Reino taxonómico | `kingdom(animalia)` |
| `phylum/1` | 1 | Filo taxonómico | `phylum(arthropoda)` |
| `class/1` | 1 | Clase taxonómica | `class(insecta)` |
| `order/1` | 1 | Orden taxonómico | `order(diptera)` |
| `family/1` | 1 | Familia taxonómica | `family(culicidae)` |
| `genus/1` | 1 | Género de mosquito | `genus(aedes)` |
| `species/2` | 2 | Relaciona especie con género | `species(aedes_aegypti, aedes)` |
| `ecological_role/2` | 2 | Rol ecológico de especie | `ecological_role(aedes_aegypti, prey)` |
| `life_stage/1` | 1 | Estadios del ciclo de vida | `life_stage(larva_l3)` |
| `aquatic_stage/1` | 1 | Estadios acuáticos | `aquatic_stage(pupa)` |
| `predatory_stage/2` | 2 | Estadios depredadores | `predatory_stage(toxorhynchites, larva_l4)` |
| `vulnerable_stage/2` | 2 | Estadios vulnerables | `vulnerable_stage(aedes, larva_l1)` |

#### Predicados Auxiliares

| Predicado | Descripción | Uso |
|-----------|-------------|-----|
| `is_predator/1` | Verifica si es depredador | `is_predator(toxorhynchites_rutilus)` |
| `is_prey/1` | Verifica si es presa | `is_prey(aedes_aegypti)` |
| `is_vector/1` | Verifica si es vector | `is_vector(aedes_aegypti)` |
| `genus_of/2` | Obtiene género de especie | `genus_of(aedes_aegypti, G)` → `G = aedes` |

#### Especies Modeladas
- **Aedes aegypti** (Género: *Aedes*) - Presa y vector de enfermedades
- **Toxorhynchites** (Género: *Toxorhynchites*) - Depredador (incluye T. rutilus y T. amboinensis)

---

### 1.2 `biological_facts.pl`

**Propósito:** Gestiona parámetros biológicos cargados dinámicamente desde archivos JSON de configuración.

**Flujo de Datos:**
```
config/*.json → Python (ConfigManager) → PySwip → assertz() → Prolog (hechos dinámicos)
```

#### Predicados Dinámicos (Parámetros)

| Predicado | Aridad | Descripción | Ejemplo de Uso |
|-----------|--------|-------------|----------------|
| `stage_duration/4` | 4 | Duración de estadio (min-max días) | `stage_duration(aedes_aegypti, egg, 2, 7)` |
| `survival_rate/4` | 4 | Tasa de supervivencia entre estadios | `survival_rate(aedes_aegypti, egg, larva_l1, 0.80)` |
| `fecundity/4` | 4 | Fecundidad (huevos/hembra) | `fecundity(aedes_aegypti, 80, 150, 3)` |
| `predation_rate/3` | 3 | Tasa de depredación diaria | `predation_rate(toxorhynchites, larva_l1, 20)` |
| `functional_response/3` | 3 | Parámetros de Holling tipo II | `functional_response(toxorhynchites, 0.5, 0.1)` |
| `environmental_param/2` | 2 | Parámetros ambientales | `environmental_param(carrying_capacity, 10000)` |

#### Predicados de Gestión (Cargados desde Python)

| Predicado | Propósito | Llamado por |
|-----------|-----------|-------------|
| `clear_all_parameters/0` | Limpia todos los parámetros | Python antes de recargar config |
| `load_stage_duration/4` | Carga duración de estadio | `ConfigManager` (Python) |
| `load_survival_rate/4` | Carga tasa de supervivencia | `ConfigManager` (Python) |
| `load_fecundity/4` | Carga fecundidad | `ConfigManager` (Python) |
| `load_predation_rate/3` | Carga depredación | `ConfigManager` (Python) |
| `load_functional_response/3` | Carga respuesta funcional | `ConfigManager` (Python) |
| `load_environmental_param/2` | Carga parámetro ambiental | `ConfigManager` (Python) |

#### Predicados de Validación

| Predicado | Propósito | Retorna |
|-----------|-----------|---------|
| `parameters_loaded/1` | Verifica carga mínima | `true` si parámetros esenciales presentes |
| `list_species_params/2` | Lista todos los parámetros de especie | Lista de `param(Tipo, Datos)` |
| `count_loaded_params/2` | Cuenta parámetros por tipo | Número entero |

**Ejemplo de Uso desde Python:**
```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("biological_facts.pl")

# Cargar parámetros desde JSON
prolog.assertz("load_stage_duration(aedes_aegypti, egg, 2, 7)")
prolog.assertz("load_survival_rate(aedes_aegypti, egg, larva_l1, 0.80)")

# Validar carga
list(prolog.query("parameters_loaded(aedes_aegypti)"))
```

---

### 1.3 `ecological_rules.pl`

**Propósito:** Reglas de inferencia para interacciones ecológicas y efectos ambientales.

#### Secciones del Archivo

##### A. Inferencia de Depredación

| Predicado | Descripción | Uso |
|-----------|-------------|-----|
| `can_predate/4` | Determina si puede ocurrir depredación | `can_predate(toxo_rutilus, aedes_aegypti, larva_l4, larva_l2)` |

**Criterios evaluados:**
- Especie depredadora tiene rol `predator`
- Especie presa tiene rol `prey`
- Estadio del depredador es depredatorio (`predatory_stage/2`)
- Estadio de presa es vulnerable (`vulnerable_stage/2`)

##### B. Ajustes Ambientales

| Predicado | Descripción | Fórmula/Lógica |
|-----------|-------------|----------------|
| `temperature_adjustment/3` | Factor por temperatura | `Factor = max(0.5, 1 - Diff*0.03)` (Aedes) |
| `humidity_adjustment/2` | Factor por humedad | `Factor = min(1.0, 0.7 + (H-60)*0.0075)` si H≥60% |
| `effective_survival/6` | Supervivencia ajustada | `EffRate = BaseRate * TempFactor * HumFactor` |

**Temperaturas óptimas:**
- *Aedes aegypti*: 27°C (rango: 20-35°C)
- *Toxorhynchites*: 28°C (rango: 18-35°C)

##### C. Capacidad de Carga

| Predicado | Descripción | Uso |
|-----------|-------------|-----|
| `carrying_capacity/1` | Obtiene capacidad de carga | `carrying_capacity(K)` → recupera de `environmental_param/2` |
| `population_equilibrium/4` | Clasifica estado poblacional | Retorna: `growing`, `stable`, `declining` |

**Umbrales de equilibrio:**
- `growing`: Población < 80% de capacidad
- `stable`: Población entre 80-120% de capacidad
- `declining`: Población > 120% de capacidad

##### D. Modelado de Depredación

| Predicado | Descripción | Modelo |
|-----------|-------------|--------|
| `predation_impact/4` | Impacto por depredación | Respuesta funcional tipo II (Holling) |

**Ecuación de Holling tipo II:**
$$C = \min\left(\frac{a \cdot N}{1 + a \cdot T_h \cdot N}, P \cdot R\right)$$

Donde:
- $C$ = presas consumidas (limitado por potencial máximo)
- $a$ = tasa de ataque
- $T_h$ = tiempo de manipulación
- $N$ = densidad de presas
- $P$ = población de depredadores
- $R$ = tasa de depredación por individuo

---

## 2. Motor de Inferencia (`inference/`)

### 2.1 `population_dynamics.pl`

**Propósito:** Núcleo del simulador poblacional usando razonamiento declarativo.

#### A. Representación de Estado

| Predicado Dinámico | Descripción | Ejemplo |
|--------------------|-------------|---------|
| `population_state/4` | Estado poblacional | `population_state(aedes_aegypti, larva_l3, 150, 10)` |
| `environmental_state/3` | Condiciones ambientales | `environmental_state(10, 27, 75)` |

**Formato:**
- `population_state(Especie, Estadio, Cantidad, Día)`
- `environmental_state(Día, Temperatura, Humedad)`

#### B. Transiciones Poblacionales

| Predicado | Descripción | Función |
|-----------|-------------|---------|
| `initialize_population/4` | Inicializa población | Establece estado inicial |
| `next_generation/4` | Calcula siguiente paso | Integra entrada, mortalidad, salida |
| `stage_transition/3` | Define transiciones válidas | `egg → larva_l1 → ... → adult` |

**Transiciones definidas:**
```prolog
% Aedes aegypti
egg → larva_l1 → larva_l2 → larva_l3 → larva_l4 → pupa → adult_female/male

% Toxorhynchites
egg → larva_l1 → larva_l2 → larva_l3 → larva_l4 → pupa → adult_female/male
```

#### C. Cálculos de Dinámica

| Predicado | Propósito | Componentes |
|-----------|-----------|-------------|
| `calculate_incoming/7` | Individuos entrantes | Suma contribuciones de estadios previos con supervivencia |
| `calculate_mortality/7` | Mortalidad total | Natural + depredación |
| `calculate_outgoing/6` | Individuos salientes | Basado en duración promedio de estadio |

**Fórmula de balance poblacional:**
$$N_{t+1} = N_t + \text{Entrantes} - \text{Muertes} - \text{Salientes}$$

#### D. Interacciones Depredador-Presa

| Predicado | Descripción | Modelo |
|-----------|-------------|--------|
| `predation_mortality/4` | Mortalidad por depredación | Busca depredadores activos, aplica Holling II |
| `calculate_functional_response/3` | Respuesta funcional | Implementa ecuación de Holling |

**Proceso:**
1. Identificar estadios vulnerables del género presa
2. Contar depredadores activos en estadios depredatorios
3. Aplicar respuesta funcional tipo II
4. Retornar número de presas consumidas

#### E. Consultas Analíticas

| Predicado | Descripción | Retorno |
|-----------|-------------|---------|
| `total_population/3` | Población total de especie | Suma de todos los estadios |
| `population_trend/3` | Tendencia poblacional | `growing` / `stable` / `declining` / `initial` |
| `predator_prey_ratio/2` | Ratio Toxo/Aedes | Valor decimal (ej: 0.045) |
| `biocontrol_viable/2` | Viabilidad de biocontrol | Clasificación experta |
| `ecological_equilibrium/1` | Estado de equilibrio | `true` si ambas especies estables |
| `extinction_risk/3` | Riesgo de extinción | `critical` / `high` / `moderate` / `low` |

**Criterios de biocontrol:**
- `highly_effective`: Aedes declinando, Toxo creciendo, ratio > 0.05
- `effective`: Aedes declinando, Toxo estable, ratio > 0.03
- `promising`: Aedes estable, Toxo creciendo, ratio > 0.02
- `ineffective`: Aedes creciendo, Toxo declinando
- `requires_analysis`: Otros casos

#### F. Proyección Temporal

| Predicado | Descripción | Método |
|-----------|-------------|--------|
| `project_population/4` | Proyecta N días hacia adelante | Recursión con backtracking |
| `advance_all_stages/3` | Avanza un día todos los estadios | Itera con `forall/2` |

**Uso:**
```prolog
% Proyectar población de Aedes 30 días hacia adelante
?- project_population(aedes_aegypti, 0, 30, Projection).
```

---

### 2.2 `agent_decisions.pl`

**Propósito:** Arquitectura de agentes racionales basada en AIMA (Russell & Norvig, Cap. 1-2).

#### A. Estado de Agentes

| Predicado Dinámico | Descripción | Formato |
|--------------------|-------------|---------|
| `agent_state/5` | Estado interno | `agent_state(ID, Stage, Age, Energy, Reproduced)` |
| `agent_species/2` | Especie del agente | `agent_species(agent1, aedes_aegypti)` |
| `current_temperature/1` | Temp. ambiental | `current_temperature(27)` |
| `current_humidity/1` | Humedad ambiental | `current_humidity(75)` |
| `current_population/2` | Población actual | `current_population(aedes_aegypti, 800)` |
| `suitable_oviposition_site_available/0` | Sitio disponible | Hecho dinámico |

#### B. Percepciones del Entorno

| Predicado | Descripción | Ejemplo |
|-----------|-------------|---------|
| `perceive/2` | Obtiene percepción | `perceive(agent1, temperature(T))` |

**Tipos de percepciones:**
- `temperature(T)`: Temperatura actual
- `humidity(H)`: Humedad relativa
- `population_density(Species, D)`: Densidad poblacional
- `prey_available(N)`: Disponibilidad de presas (depredadores)

#### C. Reglas de Decisión

##### Aedes aegypti (Hembra Adulta)

| Acción | Condiciones | Prioridad |
|--------|-------------|-----------|
| `oviposit` | Edad > 3 días, Energía > 50, Humedad > 70%, Sitio disponible, NotReproduced = true | Alta (fitness: 100) |
| `feed` | Energía < 40 | Media (fitness: 50) |
| `rest` | Energía ≥ 40, no cumple condiciones para ovipositar ni alimentarse | Baja (fitness: 5) |

##### Toxorhynchites (Larva Depredadora)

| Acción | Condiciones | Prioridad |
|--------|-------------|-----------|
| `hunt` | Estadio L3/L4, Energía < 70, Presas disponibles | Alta (fitness: 80) |
| `grow` | Estadio acuático, Energía ≥ 70 | Media (fitness: 40) |
| `rest` | No cumple condiciones para cazar ni crecer | Baja (fitness: 5) |

#### D. Función de Utilidad

| Predicado | Descripción | Fórmula |
|-----------|-------------|---------|
| `utility/3` | Calcula utilidad de acción | `U(a) = Benefit - Cost + 0.1*Energy` |
| `action_energy_cost/2` | Costo energético | Ver tabla abajo |
| `action_benefit/3` | Beneficio esperado | Depende de contexto |

**Costos energéticos:**
- `oviposit`: 20 unidades
- `feed`: 10 unidades
- `hunt`: 15 unidades
- `grow`: 5 unidades
- `rest`: 1 unidad

#### E. Selección Racional

| Predicado | Descripción | Método |
|-----------|-------------|--------|
| `best_action/2` | Selecciona acción óptima | Maximización de utilidad con `findall` + `sort` |
| `possible_action/2` | Lista acciones disponibles | Filtra por género/especie |

**Algoritmo de decisión:**
1. Generar todas las acciones posibles (`possible_action/2`)
2. Calcular utilidad de cada acción (`utility/3`)
3. Ordenar por utilidad (descendente)
4. Seleccionar la de mayor utilidad (agente racional)

**Nota importante:** Las condiciones para `rest` se evalúan directamente sin recursión, verificando que no se cumplan las condiciones de otras acciones.

#### F. Gestión de Agentes

| Predicado | Propósito | Uso |
|-----------|-----------|-----|
| `initialize_agent/5` | Crea nuevo agente | `initialize_agent(a1, aedes_aegypti, adult_female, 5, 80)` |
| `update_agent_state/5` | Actualiza estado | Modifica edad, energía, estadio, etc. |
| `remove_agent/1` | Elimina agente (muerte) | `remove_agent(a1)` |

---

## 3. Consultas Definidas (`queries/`)

**Estado:** En desarrollo

**Propósito:** Consultas de alto nivel para facilitar el uso del sistema desde Python o interfaz de usuario.

**Planificado:**
- `population_queries.pl`: Consultas sobre estado poblacional
- `simulation_queries.pl`: Consultas sobre ejecución de simulación

---

## 4. Integración con Python

### 4.1 Flujo de Datos

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  config/*.json  │────►│ Python           │────►│ Prolog          │
│  (parámetros)   │     │ ConfigManager    │     │ (hechos         │
│                 │     │ carga JSON       │     │  dinámicos)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Inferencia y    │
                                                  │ Razonamiento    │
                                                  └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Resultados →    │
                                                  │ Python          │
                                                  └─────────────────┘
```

### 4.2 Ejemplo de Uso

```python
from pyswip import Prolog

# Inicializar motor Prolog
prolog = Prolog()

# Cargar base de conocimiento
prolog.consult("src/prolog/knowledge_base/species_ontology.pl")
prolog.consult("src/prolog/knowledge_base/biological_facts.pl")
prolog.consult("src/prolog/knowledge_base/ecological_rules.pl")
prolog.consult("src/prolog/inference/population_dynamics.pl")

# Cargar parámetros desde JSON (a través de ConfigManager)
# config_manager.load_to_prolog(prolog, "config/species/aedes_aegypti.json")

# Inicializar población
list(prolog.query("initialize_population(aedes_aegypti, egg, 200, 0)"))
list(prolog.query("initialize_population(aedes_aegypti, larva_l1, 150, 0)"))

# Establecer condiciones ambientales
list(prolog.query("assertz(environmental_state(0, 27, 75))"))

# Proyectar 10 días
results = list(prolog.query("project_population(aedes_aegypti, 0, 10, Projection)"))

# Consultar tendencia
trend = list(prolog.query("population_trend(aedes_aegypti, 10, Trend)"))
print(f"Tendencia: {trend[0]['Trend']}")

# Evaluar biocontrol
assessment = list(prolog.query("biocontrol_viable(10, Assessment)"))
print(f"Biocontrol: {assessment[0]['Assessment']}")
```

---

## 5. Fundamentos Teóricos

### 5.1 Programación Lógica

El sistema implementa programación lógica declarativa con:
- **Hechos**: Conocimiento factual (taxonomía, parámetros)
- **Reglas**: Conocimiento inferencial (depredación, supervivencia)
- **Consultas**: Preguntas al sistema
- **Unificación**: Mecanismo de pattern matching
- **Backtracking**: Búsqueda de soluciones

### 5.2 Modelos Matemáticos

#### Matriz de Leslie
Proyección poblacional estructurada por edad:
$$\mathbf{n}(t+1) = \mathbf{L} \cdot \mathbf{n}(t)$$

#### Respuesta Funcional (Holling II)
Depredación con saturación:
$$C = \frac{a \cdot N}{1 + a \cdot T_h \cdot N}$$

#### Modelo Lotka-Volterra (implícito)
Dinámica depredador-presa con equilibrios y ciclos.

### 5.3 Inteligencia Artificial (AIMA)

**Agentes Racionales:**
- **Percepciones**: `perceive/2`
- **Estado interno**: `agent_state/5`
- **Acciones**: `decide_action/2`
- **Función de utilidad**: `utility/3`
- **Racionalidad**: `best_action/2` (maximización)

---

## 6. Mantenimiento y Extensión

### 6.1 Agregar Nueva Especie

1. **Ontología**: Agregar en `species_ontology.pl`
   ```prolog
   species(nueva_especie, nuevo_genero).
   ecological_role(nueva_especie, rol).
   ```

2. **Parámetros**: Crear JSON en `config/species/nueva_especie.json`

3. **Transiciones**: Definir en `population_dynamics.pl`
   ```prolog
   stage_transition(nueva_especie, egg, larva_l1).
   % ... etc
   ```

### 6.2 Agregar Nueva Regla Ecológica

En `ecological_rules.pl`:
```prolog
%% nueva_regla/N: Descripción.
%% @param Parametro1: Descripción
nueva_regla(Param1, ..., Resultado) :-
    condicion1,
    condicion2,
    Resultado is calculo.
```

### 6.3 Debugging

**Trazar ejecución:**
```prolog
?- trace.
?- predicado_a_debuggear(Argumentos).
```

**Listar hechos dinámicos:**
```prolog
?- listing(population_state/4).
?- findall(X, population_state(aedes_aegypti, _, _, X), Days).
```

---

## 7. Referencias

### Bibliografía Científica

1. **Leslie, P. H.** (1945). On the use of matrices in certain population mathematics. *Biometrika*, 33(3), 183-212.

2. **Holling, C. S.** (1959). The components of predation as revealed by a study of small-mammal predation of the European pine sawfly. *The Canadian Entomologist*, 91(5), 293-320.

3. **Russell, S., & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. [Capítulos 1-2]

4. **Collins, L. E., & Blackwell, A.** (2000). The biology of Toxorhynchites mosquitoes and their potential as biocontrol agents. *Biocontrol News and Information*, 21(4), 105N-116N.

### Documentación Técnica

- **SWI-Prolog Documentation**: https://www.swi-prolog.org/pldoc/
- **PySwip Documentation**: https://github.com/yuce/pyswip

---

## 8. Glosario

| Término | Definición |
|---------|------------|
| **Predicado** | Relación lógica en Prolog (equivalente a función) |
| **Hecho** | Predicado sin cuerpo (conocimiento factual) |
| **Regla** | Predicado con cuerpo (conocimiento inferencial) |
| **Aridad** | Número de argumentos de un predicado |
| **Unificación** | Proceso de matching de patrones en Prolog |
| **Backtracking** | Búsqueda exhaustiva de soluciones |
| **Predicado dinámico** | Predicado que puede modificarse en runtime (assertz/retract) |
| **MVP** | Minimum Viable Population (población mínima viable) |
| **Biocontrol** | Control biológico mediante depredadores naturales |

---

**Fin del documento**

*Para consultas o contribuciones, referirse al README principal del proyecto.*
