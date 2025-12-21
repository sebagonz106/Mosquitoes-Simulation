# Análisis de Simulación Basada en Agentes (ABM) - Ciclo de Vida Completo

**Fecha**: 11 de enero de 2026  
**Objetivo**: Implementar simulación realista con agentes que pasen por todas las etapas del ciclo de vida (huevo → larva → pupa → adulto)

---

## 1. SITUACIÓN ACTUAL

### 1.1 Implementación Existente

#### **VectorAgent (Aedes aegypti)**
```python
# src/domain/agents/vector_agent.py - línea 52-58
super().__init__(
    agent_id=agent_id,
    species='aedes_aegypti',
    stage='adult_female',  # ❌ SIEMPRE ADULTO
    age=age,
    energy=energy,
    prolog_bridge=prolog_bridge
)
```

**Problema**: Los agentes vectores se crean directamente como adultos. No pasan por:
- Huevo (2-7 días)
- Larva L1-L4 (6-10 días total)
- Pupa (1-3 días)

**Implicaciones**:
- Ignora ~10-20 días de desarrollo pre-adulto
- No simula mortalidad en etapas inmaduras (mayor que en adultos)
- No permite modelar intervenciones larvicidas
- No refleja depredación de larvas por Toxorhynchites

#### **PredatorAgent (Toxorhynchites)**
```python
# src/domain/agents/predator_agent.py - línea 160-170
def _execute_grow(self) -> Dict[str, Any]:
    old_stage = self.state.stage
    self.growth_stage += 1
    
    if self.growth_stage >= 3:
        self.state.stage = 'pupa'  # ✅ Puede metamorfosear
```

**Observación**: Los depredadores SÍ pueden transicionar entre etapas, pero solo larva→pupa.

### 1.2 Arquitectura de Configuración

#### **SimulationConfig (dtos.py)**
```python
@dataclass
class SimulationConfig:
    species_id: str
    initial_eggs: int
    initial_larvae: int
    initial_pupae: int
    initial_adults: int
    # ❌ NO HAY: num_vectors, num_predators
```

**Problema**: El DTO está diseñado para poblaciones, no para agentes individuales con ciclo de vida.

#### **AgentService (agent_service.py)**
```python
# Línea 85-90
num_vectors_initial = config.initial_adults  # ❌ Ignora huevos/larvas/pupas

for i in range(num_vectors_initial):
    agent = VectorAgent(...)  # Crea solo adultos
```

**Problema**: Aunque el usuario especifique 1000 huevos, estos NO se convierten en agentes huevo, solo se leen los adultos.

### 1.3 Interfaz Gráfica

```python
# simulation_view.py - línea 148
self._create_dropdown(basic_section, "Tipo de Simulación:", 
    self.sim_type_var, sim_type_options, None, 'sim_type')
    #                                    ^^^^ NO HAY CALLBACK
```

**Problema**: No detecta cuando el usuario selecciona ABM para mostrar campos específicos.

---

## 2. PROBLEMÁTICA IDENTIFICADA

### 2.1 Problema Biológico: Ciclo de Vida Incompleto

**Realidad Biológica de Aedes aegypti**:
```
Huevo (2-7 días) → Larva L1 (1-2 d) → L2 (1-2 d) → L3 (2-3 d) → L4 (2-4 d) 
                → Pupa (1-3 días) → Adulto (14-30 días)
Total: ~12-49 días desde huevo hasta adulto
```

**Simulación Actual**:
```
[NADA] → Adulto (aparece instantáneamente a día 0)
```

**Consecuencias**:
1. **Mortalidad subestimada**: Las etapas inmaduras tienen supervivencia ~80-90%, pero la simulación asume supervivencia adulta 95% para todo
2. **Tiempo de generación incorrecto**: Un mosquito tarda ~15 días en completar desarrollo, no 0 días
3. **Depredación imposible**: Toxorhynchites depredador NO puede cazar adultos, solo larvas
4. **Intervenciones irreales**: No se puede simular larvicidas, destrucción de criaderos, etc.

### 2.2 Problema Arquitectural: Configuración Rígida

**Flujo Actual**:
```
Usuario → GUI (huevos=1000, adultos=50)
         ↓
    SimulationConfig (almacena valores)
         ↓
    AgentService (IGNORA huevos, usa solo adultos)
         ↓
    Resultado: 50 agentes adultos
```

**Lo esperado**:
```
Usuario → GUI (huevos=1000, larvas=500)
         ↓
    SimulationConfig (num_agents_by_stage)
         ↓
    AgentService (crea 1000 huevos, 500 larvas como agentes)
         ↓
    Resultado: 1500 agentes en diferentes etapas
```

### 2.3 Problema de Usabilidad: GUI No Adaptativa

Al seleccionar "Basada en Agentes", la GUI debería:
- ✅ Ocultar el selector de especie única
- ✅ Mostrar campos para "Vectores" y "Depredadores" separados
- ✅ Permitir especificar cantidades por etapa

**Actualmente**: Usa los mismos campos que simulación poblacional.

---

## 3. SOLUCIÓN PROPUESTA: CICLO DE VIDA COMPLETO

### 3.1 Objetivo

Implementar agentes que:
1. **Nazcan como huevos** y progresen naturalmente
2. **Transicionen entre etapas** (huevo→L1→L2→L3→L4→pupa→adulto)
3. **Tengan mortalidad específica** por etapa
4. **Metamorfoseen basados en edad y energía**
5. **Interactúen según su etapa** (larvas son depredadas, adultos ovipositan)

### 3.2 Arquitectura de Solución

#### **Fase 1: Modelo de Dominio - Agente con Ciclo de Vida**

**Crear**: `src/domain/agents/lifecycle_agent.py`

```python
class LifeCycleAgent(BaseAgent):
    """
    Agente con ciclo de vida completo: huevo → larva → pupa → adulto
    """
    
    STAGE_SEQUENCE = [
        'egg',
        'larva_L1', 'larva_L2', 'larva_L3', 'larva_L4',
        'pupa',
        'adult'
    ]
    
    STAGE_DURATIONS = {
        'egg': (2, 7),        # días mínimo-máximo
        'larva_L1': (1, 2),
        'larva_L2': (1, 2),
        'larva_L3': (2, 3),
        'larva_L4': (2, 4),
        'pupa': (1, 3),
        'adult': (14, 30)
    }
    
    STAGE_SURVIVAL = {
        'egg': 0.80,
        'larva_L1': 0.85,
        'larva_L2': 0.85,
        'larva_L3': 0.80,
        'larva_L4': 0.80,
        'pupa': 0.90,
        'adult': 0.95  # supervivencia diaria
    }
    
    def __init__(self, agent_id, species, initial_stage='egg', ...):
        super().__init__(...)
        self.days_in_stage = 0
        self.stage_duration = self._get_stage_duration(initial_stage)
    
    def age_one_day(self):
        """Envejecer y verificar metamorfosis."""
        self.state.age += 1
        self.days_in_stage += 1
        
        # Pérdida energética según etapa
        energy_loss = self._get_daily_energy_loss()
        self.state.energy = max(0, self.state.energy - energy_loss)
        
        # Mortalidad por energía
        if self.state.energy <= 0:
            self.die("energy_depletion")
            return
        
        # Mortalidad estocástica por etapa
        survival_rate = self.STAGE_SURVIVAL[self.state.stage]
        if random.random() > survival_rate:
            self.die("natural_mortality")
            return
        
        # Verificar metamorfosis
        if self.days_in_stage >= self.stage_duration:
            self._metamorphose()
    
    def _metamorphose(self):
        """Transicionar a la siguiente etapa del ciclo."""
        current_idx = self.STAGE_SEQUENCE.index(self.state.stage)
        
        if current_idx < len(self.STAGE_SEQUENCE) - 1:
            next_stage = self.STAGE_SEQUENCE[current_idx + 1]
            self.state.stage = next_stage
            self.days_in_stage = 0
            self.stage_duration = self._get_stage_duration(next_stage)
            
            # Costo energético de metamorfosis
            self.state.energy = max(0, self.state.energy - 15)
            
            # Sincronizar con Prolog
            self._sync_state_to_prolog()
    
    def can_reproduce(self) -> bool:
        """Solo adultos pueden reproducir."""
        return self.state.stage == 'adult' and self.alive
    
    def is_vulnerable_to_predation(self) -> bool:
        """Larvas son vulnerables a depredación."""
        return 'larva' in self.state.stage and self.alive
```

**Justificación**:
- **Realismo biológico**: Cada agente pasa ~15 días desarrollándose antes de reproducir
- **Mortalidad diferencial**: Huevos/larvas mueren más que adultos (80-85% vs 95%)
- **Depredación posible**: Depredadores solo atacan larvas, que ahora existen como agentes
- **Intervenciones modelables**: Se pueden aplicar larvicidas en días específicos

---

#### **Fase 2: Configuración Extendida para ABM**

**Modificar**: `src/application/dtos.py`

```python
@dataclass
class SimulationConfig:
    # Campos existentes para simulación poblacional
    species_id: str
    duration_days: int
    initial_eggs: int
    initial_larvae: Union[List[int], int]
    initial_pupae: int
    initial_adults: int
    
    # NUEVOS: Configuración específica para ABM
    simulation_type: str = 'population'  # 'population', 'agent', 'hybrid'
    
    # Para ABM: distribución de agentes por etapa
    agent_distribution: Optional[Dict[str, int]] = None
    # Ejemplo: {'egg': 1000, 'larva_L1': 200, 'larva_L4': 50, 'adult': 10}
    
    # Para ABM con depredadores
    num_predators: int = 0
    predator_species: str = 'toxorhynchites'
    predator_distribution: Optional[Dict[str, int]] = None
    
    # Configuración avanzada
    enable_full_lifecycle: bool = True  # Si False, usa comportamiento antiguo
    
    def get_agent_counts_by_stage(self) -> Dict[str, int]:
        """
        Convertir configuración poblacional a distribución de agentes.
        
        Si agent_distribution está definida, usarla.
        Si no, inferir de initial_eggs, initial_larvae, etc.
        """
        if self.agent_distribution:
            return self.agent_distribution
        
        # Distribución por defecto desde campos poblacionales
        return {
            'egg': self.initial_eggs,
            'larva_L1': self.initial_larvae // 4 if isinstance(self.initial_larvae, int) else self.initial_larvae[0],
            'larva_L2': self.initial_larvae // 4 if isinstance(self.initial_larvae, int) else self.initial_larvae[1],
            'larva_L3': self.initial_larvae // 4 if isinstance(self.initial_larvae, int) else self.initial_larvae[2],
            'larva_L4': self.initial_larvae // 4 if isinstance(self.initial_larvae, int) else self.initial_larvae[3],
            'pupa': self.initial_pupae,
            'adult': self.initial_adults
        }
```

**Ventajas**:
- **Retrocompatible**: Campos antiguos siguen funcionando
- **Flexible**: Permite especificar distribución exacta o inferirla
- **Extensible**: Fácil agregar más parámetros ABM sin romper código existente

---

#### **Fase 3: Servicio de Agentes con Ciclo de Vida**

**Modificar**: `src/application/services/agent_service.py`

```python
@staticmethod
def simulate_agents(
    config: SimulationConfig,
    num_predators: int = None,
    predator_species: str = 'toxorhynchites'
) -> AgentResult:
    """
    Simulación ABM con ciclo de vida completo.
    """
    # Obtener distribución de agentes por etapa
    agent_counts = config.get_agent_counts_by_stage()
    num_predators = num_predators or config.num_predators
    
    # Inicializar Prolog
    config_manager = get_config_manager()
    prolog_bridge = PrologBridge(config_manager=config_manager)
    prolog_bridge.inject_parameters()
    
    # Crear agentes vectores en TODAS las etapas
    vector_agents = []
    agent_id_counter = 0
    
    for stage, count in agent_counts.items():
        for i in range(count):
            # Usar LifeCycleAgent si full_lifecycle=True
            if config.enable_full_lifecycle:
                agent = LifeCycleAgent(
                    agent_id=f"vector_{agent_id_counter}",
                    species=config.species_id,
                    initial_stage=stage,
                    age=0 if stage == 'egg' else random.randint(1, 5),
                    energy=random.uniform(60, 100),
                    prolog_bridge=prolog_bridge
                )
            else:
                # Comportamiento antiguo: solo adultos
                agent = VectorAgent(...)
            
            vector_agents.append(agent)
            agent_id_counter += 1
    
    # Crear agentes depredadores
    predator_agents = []
    for i in range(num_predators):
        agent = PredatorAgent(
            agent_id=f"predator_{i}",
            stage='larva_L4',
            age=random.randint(5, 15),
            energy=random.uniform(70, 100),
            prolog_bridge=prolog_bridge
        )
        predator_agents.append(agent)
    
    # SIMULACIÓN DÍA A DÍA
    daily_stats = []
    total_eggs_laid = 0
    total_prey_consumed = 0
    total_metamorphoses = 0
    
    for day in range(config.duration_days + 1):
        # Estadísticas diarias por etapa
        stage_counts = {}
        for stage in LifeCycleAgent.STAGE_SEQUENCE:
            stage_counts[stage] = len([a for a in vector_agents 
                                       if a.alive and a.state.stage == stage])
        
        daily_stat = {
            'day': day,
            'stage_distribution': stage_counts,
            'num_vectors_alive': len([a for a in vector_agents if a.alive]),
            'num_predators_alive': len([a for a in predator_agents if a.alive]),
            'eggs_laid_today': 0,
            'prey_consumed_today': 0,
            'metamorphoses_today': 0
        }
        
        if day > 0:
            # 1. ENVEJECIMIENTO Y METAMORFOSIS
            for agent in vector_agents:
                if agent.alive:
                    old_stage = agent.state.stage
                    agent.age_one_day()  # Puede metamorfosear aquí
                    if agent.alive and agent.state.stage != old_stage:
                        total_metamorphoses += 1
                        daily_stat['metamorphoses_today'] += 1
            
            # 2. ACCIONES DE VECTORES (solo adultos pueden actuar)
            for agent in vector_agents:
                if not agent.alive or agent.state.stage != 'adult':
                    continue
                
                # Percepción y decisión
                perception = Perception(...)
                agent.perceive(perception)
                action = agent.decide_action()
                result = agent.execute_action(action)
                
                # Huevos puestos generan NUEVOS agentes huevo
                if result.get('success') and result.get('action') == 'oviposit':
                    eggs_laid = result.get('eggs_laid', 0)
                    total_eggs_laid += eggs_laid
                    daily_stat['eggs_laid_today'] += eggs_laid
                    
                    # CREAR NUEVOS AGENTES HUEVO
                    for j in range(eggs_laid):
                        new_egg = LifeCycleAgent(
                            agent_id=f"vector_{agent_id_counter}",
                            species=config.species_id,
                            initial_stage='egg',
                            age=0,
                            energy=80.0,
                            prolog_bridge=prolog_bridge
                        )
                        vector_agents.append(new_egg)
                        agent_id_counter += 1
            
            # 3. ACCIONES DE DEPREDADORES (cazan larvas)
            for predator in predator_agents:
                if not predator.alive:
                    continue
                
                # Decidir cazar
                perception = Perception(
                    prey_available=stage_counts.get('larva_L1', 0) + 
                                   stage_counts.get('larva_L2', 0) +
                                   stage_counts.get('larva_L3', 0) +
                                   stage_counts.get('larva_L4', 0),
                    ...
                )
                predator.perceive(perception)
                action = predator.decide_action()
                result = predator.execute_action(action)
                
                # Consumir presas (matar larvas)
                if result.get('success') and result.get('action') == 'hunt':
                    prey_count = result.get('prey_consumed', 0)
                    prey_consumed_today += prey_count
                    
                    # Seleccionar víctimas aleatorias entre larvas vivas
                    larvae = [a for a in vector_agents 
                              if a.alive and a.is_vulnerable_to_predation()]
                    
                    for _ in range(min(prey_count, len(larvae))):
                        if larvae:
                            victim = random.choice(larvae)
                            victim.die("predated")
                            larvae.remove(victim)
                
                predator.age_one_day()
        
        daily_stats.append(daily_stat)
    
    # RESULTADO FINAL
    result = AgentResult(
        num_vectors_initial=sum(agent_counts.values()),
        num_predators_initial=num_predators,
        num_vectors_final=len([a for a in vector_agents if a.alive]),
        num_predators_final=len([a for a in predator_agents if a.alive]),
        total_eggs_laid=total_eggs_laid,
        total_prey_consumed=total_prey_consumed,
        daily_stats=daily_stats,
        # NUEVO: estadísticas adicionales
        total_metamorphoses=total_metamorphoses,
        final_stage_distribution=stage_counts
    )
    
    return result
```

**Características clave**:
1. **Creación por etapas**: Genera agentes en huevo, L1, L2, L3, L4, pupa, adulto según configuración
2. **Metamorfosis automática**: Agentes envejecen y transicionan naturalmente
3. **Reproducción dinámica**: Adultos que ovipositan crean NUEVOS agentes huevo
4. **Depredación realista**: Depredadores solo pueden matar larvas
5. **Estadísticas detalladas**: Distribuci

ón por etapa en cada día

---

#### **Fase 4: GUI Adaptativa para ABM**

**Modificar**: `src/presentation/views/simulation_view.py`

```python
def __init__(self, ...):
    # Variables existentes
    self.species_var = tk.StringVar(value='aedes_aegypti')
    self.sim_type_var = tk.StringVar(value='population')
    
    # NUEVAS variables para ABM
    self.num_vectors_var = tk.StringVar(value='100')
    self.num_predators_var = tk.StringVar(value='10')
    
    # Distribución por etapas (avanzado)
    self.egg_agents_var = tk.StringVar(value='1000')
    self.larva_agents_var = tk.StringVar(value='500')
    self.pupa_agents_var = tk.StringVar(value='100')
    self.adult_agents_var = tk.StringVar(value='50')
    
    self._setup_ui()

def _create_form(self, parent):
    # ... código existente ...
    
    # Registrar callback para cambio de tipo de simulación
    self.sim_type_var.trace_add('write', lambda *args: self._on_sim_type_changed())
    
    # Crear secciones dinámicas (ocultas inicialmente)
    self._create_abm_sections(form)

def _create_abm_sections(self, parent):
    """Crear secciones específicas para ABM (ocultas por defecto)."""
    
    # Marco para vectores
    self.vectors_section = self._create_section(parent, "Agentes Vectores (Aedes)")
    self._create_input(self.vectors_section, "Huevos iniciales:", self.egg_agents_var, "int")
    self._create_input(self.vectors_section, "Larvas iniciales:", self.larva_agents_var, "int")
    self._create_input(self.vectors_section, "Pupas iniciales:", self.pupa_agents_var, "int")
    self._create_input(self.vectors_section, "Adultos iniciales:", self.adult_agents_var, "int")
    
    # Marco para depredadores
    self.predators_section = self._create_section(parent, "Agentes Depredadores (Toxorhynchites)")
    self._create_input(self.predators_section, "Depredadores L4:", self.num_predators_var, "int")
    
    # Ocultar por defecto
    self.vectors_section.pack_forget()
    self.predators_section.pack_forget()

def _on_sim_type_changed(self):
    """Responder a cambio de tipo de simulación."""
    sim_type_display = self.sim_type_var.get()
    sim_type = self.sim_type_map.get(sim_type_display, 'population')
    
    if sim_type == 'agent':
        # MODO ABM: Mostrar campos específicos
        self.species_dropdown_frame.pack_forget()
        self.population_section.pack_forget()
        
        self.vectors_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        self.predators_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        if self.on_log:
            self.on_log("Modo ABM: Configure agentes por etapa", "info")
    
    elif sim_type == 'population':
        # MODO POBLACIONAL: Campos tradicionales
        self.species_dropdown_frame.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        self.population_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        self.vectors_section.pack_forget()
        self.predators_section.pack_forget()
    
    elif sim_type == 'hybrid':
        # MODO HÍBRIDO: Mostrar ambos
        self.species_dropdown_frame.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        self.population_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        self.vectors_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        self.predators_section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))

def _run_simulation(self):
    """Ejecutar simulación con configuración apropiada."""
    sim_type_display = self.sim_type_var.get()
    sim_type = self.sim_type_map.get(sim_type_display, 'population')
    
    if sim_type == 'agent':
        # Construir config para ABM con distribución de agentes
        config = SimulationConfig(
            species_id='aedes_aegypti',  # Fijo para vectores
            simulation_type='agent',
            duration_days=int(self.duration_var.get()),
            
            # Distribución de agentes por etapa
            agent_distribution={
                'egg': int(self.egg_agents_var.get()),
                'larva_L1': int(self.larva_agents_var.get()) // 4,
                'larva_L2': int(self.larva_agents_var.get()) // 4,
                'larva_L3': int(self.larva_agents_var.get()) // 4,
                'larva_L4': int(self.larva_agents_var.get()) // 4,
                'pupa': int(self.pupa_agents_var.get()),
                'adult': int(self.adult_agents_var.get())
            },
            
            # Depredadores
            num_predators=int(self.num_predators_var.get()),
            predator_species='toxorhynchites',
            
            # Parámetros ambientales
            temperature=float(self.temp_var.get()),
            humidity=float(self.humidity_var.get()),
            water_availability=float(self.water_var.get()),
            
            # Habilitar ciclo de vida completo
            enable_full_lifecycle=True
        )
    else:
        # Config tradicional para poblacional
        config = SimulationConfig(...)
    
    # Ejecutar según tipo
    if sim_type == 'agent':
        result = self.controller.run_agent_simulation(config)
    # ... resto del código ...
```

**Mejoras de usabilidad**:
- ✅ Detección automática de tipo de simulación
- ✅ Campos contextuales (solo muestra lo necesario)
- ✅ Configuración granular por etapa
- ✅ Validación específica por modo

---

#### **Fase 5: Visualización de Resultados con Ciclo de Vida**

**Modificar**: `src/application/visualization.py`

```python
def plot_agent_stage_distribution(
    result: AgentResult,
    show: bool = True,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 8)
) -> matplotlib.figure.Figure:
    """
    Visualizar distribución de agentes por etapa del ciclo de vida.
    
    Gráfico de área apilada mostrando:
    - Huevos
    - Larvas L1-L4
    - Pupas
    - Adultos
    
    a lo largo del tiempo.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    days = [stat['day'] for stat in result.daily_stats]
    
    # Extraer datos por etapa
    stages = ['egg', 'larva_L1', 'larva_L2', 'larva_L3', 'larva_L4', 'pupa', 'adult']
    stage_data = {stage: [] for stage in stages}
    
    for stat in result.daily_stats:
        dist = stat.get('stage_distribution', {})
        for stage in stages:
            stage_data[stage].append(dist.get(stage, 0))
    
    # Gráfico de área apilada
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0', '#ffb3e6']
    labels = ['Huevos', 'Larva L1', 'Larva L2', 'Larva L3', 'Larva L4', 'Pupas', 'Adultos']
    
    ax.stackplot(days, 
                 *[stage_data[stage] for stage in stages],
                 labels=labels,
                 colors=colors,
                 alpha=0.8)
    
    ax.set_xlabel('Días', fontsize=12)
    ax.set_ylabel('Número de Agentes', fontsize=12)
    ax.set_title('Distribución de Agentes por Etapa del Ciclo de Vida', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig

def plot_metamorphosis_events(result: AgentResult, ...) -> matplotlib.figure.Figure:
    """
    Visualizar eventos de metamorfosis a lo largo del tiempo.
    """
    # Gráfico de barras de metamorfosis diarias
    # Útil para ver "olas" de desarrollo
    pass
```

**Nuevas visualizaciones**:
- Distribución por etapa (área apilada)
- Eventos de metamorfosis
- Tasa de depredación por etapa
- Cohortes de edad

---

## 4. ARCHIVOS A MODIFICAR

### 4.1 Nuevos Archivos

| Archivo | Propósito | Prioridad |
|---------|-----------|-----------|
| `src/domain/agents/lifecycle_agent.py` | Agente con ciclo de vida completo | **ALTA** |
| `tests/test_lifecycle_agent.py` | Tests unitarios del ciclo | Media |
| `docs/lifecycle_design.md` | Diseño detallado del ciclo | Baja |

### 4.2 Archivos a Modificar

| Archivo | Cambios Requeridos | Complejidad |
|---------|-------------------|-------------|
| `src/application/dtos.py` | Extender SimulationConfig con campos ABM | **Media** |
| `src/application/services/agent_service.py` | Crear agentes por etapa, reproducción dinámica | **Alta** |
| `src/presentation/views/simulation_view.py` | GUI adaptativa para ABM | **Alta** |
| `src/presentation/controllers/simulation_controller.py` | Pasar configuración ABM correctamente | Baja |
| `src/application/visualization.py` | Gráficos de distribución por etapa | Media |
| `src/presentation/views/results_view.py` | Mostrar resultados ABM con etapas | Media |
| `src/prolog/inference/agent_decisions.pl` | Reglas de decisión por etapa | Baja |

### 4.3 Archivos No Modificar (Retrocompatibilidad)

- `src/domain/agents/vector_agent.py` - Mantener para modo legacy
- `src/domain/agents/predator_agent.py` - Ya tiene metamorfosis básica
- `src/application/services/population_service.py` - No afectado

---

## 5. IDEAS Y CONSIDERACIONES CLAVE

### 5.1 Realismo Biológico

#### **Duración de Etapas**
```python
# Valores promedio para Aedes aegypti a 25°C
DURATIONS = {
    'egg': 4.5 días,
    'larva_L1-L4': 2.5 días cada una (10 total),
    'pupa': 2.0 días,
    'adult': 22 días
}
```

#### **Mortalidad por Etapa**
```python
# Supervivencia diaria (compuesto de supervivencia por etapa)
SURVIVAL_DAILY = {
    'egg': 0.80^(1/4.5) = 0.952/día,
    'larva': 0.83^(1/2.5) = 0.926/día,
    'pupa': 0.90^(1/2.0) = 0.949/día,
    'adult': 0.95/día
}
```

#### **Depredación**
- **Toxorhynchites L3**: Consume 5-10 larvas/día
- **Toxorhynchites L4**: Consume 10-20 larvas/día
- **Preferencia**: L1 > L2 > L3 (presas más pequeñas)

### 5.2 Consideraciones de Rendimiento

#### **Número de Agentes**
- **Población inicial**: 1000 huevos + 500 larvas = 1500 agentes
- **Reproducción**: 50 adultos × 100 huevos/adulto = 5000 huevos nuevos
- **Pico**: ~10,000-20,000 agentes simultáneos

#### **Optimizaciones Necesarias**:
1. **Batch processing**: Procesar agentes en lotes de 100
2. **Spatial indexing**: Si se agregan coordenadas, usar quadtree
3. **Lazy evaluation**: Solo calcular decisiones para agentes que actúan
4. **Prolog caching**: Cachear consultas repetidas

```python
# Ejemplo de optimización
def age_agents_batch(agents, batch_size=100):
    """Procesar envejecimiento en lotes para mejor performance."""
    for i in range(0, len(agents), batch_size):
        batch = agents[i:i+batch_size]
        for agent in batch:
            if agent.alive:
                agent.age_one_day()
```

### 5.3 Integración con Prolog

#### **Predicados Nuevos Necesarios**
```prolog
% agent_decisions.pl

% Determinar si un agente debe metamorfosear
should_metamorphose(AgentID, CurrentStage) :-
    agent_state(AgentID, CurrentStage, Age, Energy, _),
    stage_duration(CurrentStage, MinDays, MaxDays),
    Age >= MinDays,
    Energy > 30.  % Suficiente energía para transformación

% Estadio siguiente en el ciclo
next_stage(egg, larva_L1).
next_stage(larva_L1, larva_L2).
next_stage(larva_L2, larva_L3).
next_stage(larva_L3, larva_L4).
next_stage(larva_L4, pupa).
next_stage(pupa, adult).

% Costo energético de metamorfosis
metamorphosis_cost(egg, larva_L1, 5).
metamorphosis_cost(larva_L1, larva_L2, 3).
metamorphosis_cost(larva_L2, larva_L3, 3).
metamorphosis_cost(larva_L3, larva_L4, 3).
metamorphosis_cost(larva_L4, pupa, 10).
metamorphosis_cost(pupa, adult, 15).
```

### 5.4 Pruebas y Validación

#### **Tests Unitarios**
```python
# tests/test_lifecycle_agent.py

def test_egg_to_larva_L1_transition():
    """Verificar que huevo transiciona a L1 después del tiempo esperado."""
    agent = LifeCycleAgent(initial_stage='egg', age=0, energy=80)
    
    # Simular 5 días (duración promedio de huevo)
    for _ in range(5):
        agent.age_one_day()
    
    assert agent.state.stage == 'larva_L1'
    assert agent.days_in_stage == 0  # Reiniciado en nueva etapa

def test_mortality_increases_in_early_stages():
    """Verificar que huevos/larvas mueren más que adultos."""
    eggs = [LifeCycleAgent(initial_stage='egg', ...) for _ in range(1000)]
    adults = [LifeCycleAgent(initial_stage='adult', ...) for _ in range(1000)]
    
    # Simular 10 días
    for _ in range(10):
        for agent in eggs + adults:
            agent.age_one_day()
    
    eggs_alive = len([a for a in eggs if a.alive])
    adults_alive = len([a for a in adults if a.alive])
    
    assert eggs_alive < adults_alive  # Huevos mueren más
```

#### **Validación Biológica**
```python
def validate_generation_time():
    """
    Verificar que el tiempo generacional simulado coincide con datos reales.
    
    Tiempo generacional = tiempo promedio de huevo a adulto reproductor
    Esperado: ~15 días a 25°C
    """
    agents = [LifeCycleAgent(initial_stage='egg', ...) for _ in range(100)]
    
    days_to_adult = []
    for agent in agents:
        day = 0
        while agent.alive and agent.state.stage != 'adult':
            agent.age_one_day()
            day += 1
            if day > 50:  # Timeout
                break
        
        if agent.state.stage == 'adult':
            days_to_adult.append(day)
    
    avg_generation_time = np.mean(days_to_adult)
    assert 12 <= avg_generation_time <= 18  # Rango realista
```

---

## 6. PLAN DE IMPLEMENTACIÓN

### Fase 1: Fundamentos (1-2 días)
- ✅ Crear `LifeCycleAgent` con metamorfosis básica
- ✅ Extender `SimulationConfig` con campos ABM
- ✅ Tests unitarios de transición de etapas

### Fase 2: Servicio de Agentes (2-3 días)
- ✅ Modificar `AgentService` para crear agentes por etapa
- ✅ Implementar reproducción dinámica (adultos crean huevos)
- ✅ Depredación dirigida a larvas
- ✅ Tests de integración

### Fase 3: GUI Adaptativa (2-3 días)
- ✅ Callback `_on_sim_type_changed` en `SimulationView`
- ✅ Paneles dinámicos para vectores/depredadores
- ✅ Validación específica por modo
- ✅ Tests de UI (manual)

### Fase 4: Visualización (1-2 días)
- ✅ Gráficos de distribución por etapa
- ✅ Eventos de metamorfosis
- ✅ Integración en `ResultsView`

### Fase 5: Optimización y Documentación (1-2 días)
- ✅ Batch processing para rendimiento
- ✅ Actualizar documentación
- ✅ Guía de usuario para ABM

**Total estimado**: 7-12 días de trabajo

---

## 7. MÉTRICAS DE ÉXITO

### 7.1 Funcionalidad
- ✅ Agentes transicionan automáticamente por todas las etapas
- ✅ Reproducción genera nuevos agentes huevo
- ✅ Depredación solo afecta larvas
- ✅ Mortalidad diferencial por etapa

### 7.2 Realismo
- ✅ Tiempo generacional: 12-18 días (vs. real 15 días)
- ✅ Supervivencia general: 5-10% huevo→adulto (vs. real 8%)
- ✅ Tasa de depredación: 10-20 larvas/depredador/día

### 7.3 Usabilidad
- ✅ GUI cambia automáticamente según tipo de simulación
- ✅ Usuario puede especificar distribución inicial por etapa
- ✅ Visualizaciones muestran ciclo de vida claramente

### 7.4 Rendimiento
- ✅ Simula 10,000 agentes en 90 días en <5 minutos
- ✅ Uso de memoria <2 GB con 20,000 agentes
- ✅ GUI responde en <200ms al cambiar tipo

---

## 8. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Explosión poblacional (millones de agentes) | Alta | Alto | Implementar capacidad de carga con eliminación aleatoria |
| Performance pobre con >10,000 agentes | Media | Medio | Batch processing + optimización Prolog |
| Complejidad excesiva en GUI | Baja | Medio | Mantener modo "simple" (legacy) disponible |
| Bugs en metamorfosis | Media | Alto | Tests exhaustivos de transiciones |
| Integración Prolog fallida | Baja | Medio | Fallbacks a reglas Python si Prolog no disponible |

---

## 9. CONCLUSIÓN

### Estado Actual
- ❌ Agentes solo como adultos
- ❌ Sin ciclo de vida realista
- ❌ GUI no adaptativa
- ❌ Depredación imposible

### Estado Propuesto
- ✅ Agentes con ciclo completo (huevo→adulto)
- ✅ Metamorfosis automática basada en edad
- ✅ Reproducción dinámica con población emergente
- ✅ Depredación realista de larvas
- ✅ GUI contextual para ABM
- ✅ Visualizaciones de distribución por etapa

### Beneficios
1. **Realismo científico**: Modela biología de mosquitos con precisión
2. **Intervenciones modelables**: Larvicidas, destrucción de criaderos, depredadores
3. **Investigación**: Permite estudiar efectos de control en diferentes etapas
4. **Educación**: Visualiza claramente el ciclo de vida completo

**Esta solución transforma la simulación ABM de un prototipo simplificado a una herramienta científicamente válida para investigación en control de vectores.**

---

**Documento elaborado**: 11 de enero de 2026  
**Autor**: Sistema de Análisis de Simulación de Mosquitos  
**Versión**: 1.0
