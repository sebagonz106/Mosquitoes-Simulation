%% ══════════════════════════════════════════════════════════════════
%% DECISIONES DE AGENTES - Arquitectura de Agentes Racionales (AIMA Cap. 1-2)
%% ══════════════════════════════════════════════════════════════════
%%
%% Este modulo implementa la arquitectura de agentes inteligentes basada en:
%% - Percepciones del entorno
%% - Estados internos
%% - Funciones de utilidad
%% - Selección de acciones racionales
%%
%% Basado en: Russell & Norvig - "Artificial Intelligence: A Modern Approach"
%% Capítulo 2: Agentes Inteligentes
%%
%% Los agentes pueden ser:
%% - Agentes de Aedes aegypti (hembras adultas con comportamiento reproductivo)
%% - Agentes de Toxorhynchites (larvas depredadoras)
%%
%% Autor: Sistema de Simulación de Mosquitos
%% Fecha: Enero 2026
%% ══════════════════════════════════════════════════════════════════

%% ══════════════════════════════════════════════════════════════════
%% ESTADO DINÁMICO DE AGENTES
%% ══════════════════════════════════════════════════════════════════

%% agent_state/5: Estado interno de un agente individual.
%% @param AgentID: Identificador único del agente
%% @param Estadio: Estadio de vida actual
%% @param Edad: Edad en días
%% @param Energia: Nivel de energía [0-100]
%% @param Reprodujo: Booleano indicando si ya reprodujo
:- dynamic agent_state/5.

%% agent_species/2: Relaciona un agente con su especie.
%% @param AgentID: Identificador del agente
%% @param Especie: Especie del agente (aedes_aegypti o toxorhynchites)
:- dynamic agent_species/2.

%% current_temperature/1: Temperatura actual del entorno (°C).
%% @param Temperatura: Valor actual en grados Celsius
:- dynamic current_temperature/1.

%% current_humidity/1: Humedad relativa actual del entorno (%).
%% @param Humedad: Porcentaje de humedad relativa
:- dynamic current_humidity/1.

%% current_population/2: Población actual de una especie.
%% @param Especie: Identificador de especie
%% @param Poblacion: Número total de individuos
:- dynamic current_population/2.

%% suitable_oviposition_site_available/0: Indica disponibilidad de sitios de oviposición.
:- dynamic suitable_oviposition_site_available/0.

%% ══════════════════════════════════════════════════════════════════
%% PERCEPCIONES DEL ENTORNO
%% ══════════════════════════════════════════════════════════════════

%% perceive/2: Define las percepciones que un agente obtiene del entorno.
%% @param AgentID: Identificador del agente
%% @param Percepcion: Estructura perception(Tipo, Valor)
%% Los agentes son capaces de percibir:
%% - Temperatura ambiental
%% - Humedad relativa
%% - Densidad poblacional de su especie
%% - Disponibilidad de presas (para depredadores)

%% Percibir temperatura
perceive(Agent, temperature(T)) :- 
    current_temperature(T).

%% Percibir humedad
perceive(Agent, humidity(H)) :- 
    current_humidity(H).

%% Percibir densidad poblacional (relativa a capacidad de carga)
perceive(Agent, population_density(Species, D)) :- 
    agent_species(Agent, Species),
    current_population(Species, Pop),
    carrying_capacity(Cap),
    D is Pop / Cap.

%% Percibir disponibilidad de presas (solo para depredadores)
perceive(Agent, prey_available(N)) :-
    agent_species(Agent, Toxo),
    genus_of(Toxo, toxorhynchites),
    current_population(aedes_aegypti, N).

%% ══════════════════════════════════════════════════════════════════
%% REGLAS DE DECISIÓN - Aedes aegypti (Hembra Adulta)
%% ══════════════════════════════════════════════════════════════════

%% decide_action/2: Determina la mejor acción para un agente.
%% @param AgentID: Identificador del agente
%% @param Accion: Acción seleccionada (oviposit, feed, rest)

%% Decisión: Ovipositar
%% Condiciones: hembra adulta, edad suficiente, energía alta, humedad favorable
decide_action(Agent, oviposit) :-
    agent_species(Agent, Species),
    genus_of(Species, aedes),
    agent_state(Agent, adult_female, Age, Energy, NotReproduced),
    Age > 3,
    Energy > 50,
    perceive(Agent, humidity(H)), 
    H > 70,
    suitable_oviposition_site_available,
    NotReproduced = true.

%% Decisión: Alimentarse
%% Condiciones: energía baja, necesita recursos
decide_action(Agent, feed) :-
    agent_species(Agent, Species),
    genus_of(Species, aedes),
    agent_state(Agent, adult_female, _, Energy, _),
    Energy < 40.

%% Decisión: Descansar
%% Condiciones: energía suficiente, no cumple condiciones para ovipositar ni alimentarse
decide_action(Agent, rest) :-
    agent_species(Agent, Species),
    genus_of(Species, aedes),
    agent_state(Agent, Stage, Age, Energy, Reproduced),
    Energy >= 40,
    % No cumple condiciones para ovipositar
    \+ (Stage = adult_female, Age > 3, Energy > 50, Reproduced = true, suitable_oviposition_site_available),
    % No cumple condiciones para alimentarse
    \+ (Energy < 40).

%% ══════════════════════════════════════════════════════════════════
%% REGLAS DE DECISIÓN - Toxorhynchites (Larva Depredadora)
%% ══════════════════════════════════════════════════════════════════

%% Decisión: Cazar (depredación activa)
%% Condiciones: estadio depredador, energía baja, presas disponibles
decide_action(Agent, hunt) :-
    agent_species(Agent, Species),
    genus_of(Species, toxorhynchites),
    agent_state(Agent, Stage, _, Energy, _),
    predatory_stage(toxorhynchites, Stage),
    Energy < 70,
    perceive(Agent, prey_available(N)), 
    N > 0.

%% Decisión: Crecer (desarrollo metamórfico)
%% Condiciones: estadio acuático, energía suficiente
decide_action(Agent, grow) :-
    agent_species(Agent, Species),
    genus_of(Species, toxorhynchites),
    agent_state(Agent, Stage, _, Energy, _),
    aquatic_stage(Stage),
    Energy >= 70.

%% Decisión por defecto: Descansar
%% Condiciones: no cumple condiciones para cazar ni crecer
decide_action(Agent, rest) :-
    agent_species(Agent, Species),
    genus_of(Species, toxorhynchites),
    agent_state(Agent, Stage, _, Energy, _),
    % No cumple condiciones para cazar
    \+ (predatory_stage(toxorhynchites, Stage), Energy < 70),
    % No cumple condiciones para crecer
    \+ (aquatic_stage(Stage), Energy >= 70).

%% ══════════════════════════════════════════════════════════════════
%% FUNCIÓN DE UTILIDAD Y SELECCIÓN RACIONAL
%% ══════════════════════════════════════════════════════════════════

%% utility/3: Calcula la utilidad de una acción para un agente.
%% @param AgentID: Identificador del agente
%% @param Accion: Acción a evaluar
%% @param Utilidad: Valor de utilidad calculado
%% Fórmula: U(a) = Benefit(a) - Cost(a) + 0.1*Energy
utility(Agent, Action, Utility) :-
    agent_state(Agent, _, _, Energy, _),
    action_energy_cost(Action, Cost),
    action_benefit(Agent, Action, Benefit),
    Utility is Benefit - Cost + Energy * 0.1.

%% action_energy_cost/2: Costo energético de cada acción.
%% @param Accion: Tipo de acción
%% @param Costo: Unidades de energía consumidas
action_energy_cost(oviposit, 20).
action_energy_cost(feed, 10).
action_energy_cost(rest, 1).
action_energy_cost(hunt, 15).
action_energy_cost(grow, 5).

%% action_benefit/3: Beneficio esperado de una acción.
%% @param AgentID: Identificador del agente
%% @param Accion: Tipo de acción
%% @param Beneficio: Valor de beneficio (fitness)
action_benefit(Agent, feed, 50) :-
    agent_state(Agent, _, _, Energy, _),
    Energy < 40.
action_benefit(Agent, rest, 5).
action_benefit(Agent, oviposit, 100) :-
    agent_state(Agent, adult_female, _, _, false).
action_benefit(Agent, hunt, 80) :-
    perceive(Agent, prey_available(N)),
    N > 0.
action_benefit(Agent, grow, 40).
action_benefit(_, _, 0). % Beneficio por defecto

%% best_action/2: Selecciona la acción con mayor utilidad (agente racional).
%% @param AgentID: Identificador del agente
%% @param MejorAccion: Acción con utilidad maxima
%% Implementa el principio de racionalidad: maximización de utilidad esperada.
best_action(Agent, BestAction) :-
    findall(U-A, 
            (possible_action(Agent, A), utility(Agent, A, U)), 
            Actions),
    (Actions \= [] ->
        sort(Actions, Sorted),
        reverse(Sorted, [_-BestAction|_])
    ;
        BestAction = rest
    ).

%% possible_action/2: Define el conjunto de acciones posibles para un agente.
%% @param AgentID: Identificador del agente
%% @param Accion: Acción disponible
possible_action(Agent, Action) :-
    agent_species(Agent, Species),
    genus_of(Species, Genus),
    (Genus = aedes ->
        member(Action, [oviposit, feed, rest])
    ; Genus = toxorhynchites ->
        member(Action, [hunt, grow, rest])
    ; fail
    ).

%% ══════════════════════════════════════════════════════════════════
%% PREDICADOS AUXILIARES Y DE INICIALIZACIÓN
%% ══════════════════════════════════════════════════════════════════

%% initialize_agent/5: Crea un nuevo agente con estado inicial.
%% @param AgentID: Identificador único
%% @param Especie: Especie del agente
%% @param Estadio: Estadio inicial
%% @param Edad: Edad inicial
%% @param Energia: Energía inicial
initialize_agent(AgentID, Species, Stage, Age, Energy) :-
    assertz(agent_species(AgentID, Species)),
    assertz(agent_state(AgentID, Stage, Age, Energy, false)).

%% update_agent_state/5: Actualiza el estado de un agente.
%% @param AgentID: Identificador del agente
%% @param NuevoEstadio: Nuevo estadio
%% @param NuevaEdad: Nueva edad
%% @param NuevaEnergia: Nueva energía
%% @param Reprodujo: Estado reproductivo
update_agent_state(AgentID, NewStage, NewAge, NewEnergy, Reproduced) :-
    retract(agent_state(AgentID, _, _, _, _)),
    assertz(agent_state(AgentID, NewStage, NewAge, NewEnergy, Reproduced)).

%% remove_agent/1: Elimina un agente del sistema (muerte).
%% @param AgentID: Identificador del agente a eliminar
remove_agent(AgentID) :-
    retractall(agent_species(AgentID, _)),
    retractall(agent_state(AgentID, _, _, _, _)).
