%% ══════════════════════════════════════════════════════════════════
%% DINÁMICA POBLACIONAL - Razonamiento Declarativo sobre Poblaciones
%% ══════════════════════════════════════════════════════════════════
%%
%% Este archivo implementa el núcleo del motor de simulación poblacional
%% usando programación lógica declarativa. Incluye:
%%
%% - Representación de estados poblacionales dinámicos
%% - Inferencia de transiciones entre estadios
%% - Cálculo de mortalidad por depredación
%% - Consultas analíticas sobre tendencias y viabilidad
%% - Proyección temporal recursiva
%%
%% Basado en:
%% - Matrices de Leslie para dinámica estructurada por edad
%% - Respuesta funcional tipo II (Holling) para depredación
%% - Agentes racionales (AIMA Cap. 1)
%%
%% ══════════════════════════════════════════════════════════════════

%% ============== REPRESENTACIÓN DEL ESTADO POBLACIONAL ==============

%% population_state/4: Estado poblacional de una especie en un día.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio del ciclo de vida
%% @param Cantidad: Número de individuos
%% @param Dia: Día de la simulación
:- dynamic population_state/4.

%% environmental_state/3: Condiciones ambientales en un día.
%% @param Dia: Día de la simulación
%% @param Temperatura: Temperatura en °C
%% @param Humedad: Humedad relativa en %
:- dynamic environmental_state/3.

%% initialize_population/4: Inicializa población para un estadio.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio a inicializar
%% @param Cantidad: Número inicial de individuos
%% @param Dia: Día inicial (usualmente 0)
%% NOTA: Elimina estados previos del mismo estadio antes de insertar.
initialize_population(Species, Stage, Count, Day) :-
    retractall(population_state(Species, Stage, _, Day)),
    assertz(population_state(Species, Stage, Count, Day)).

%% ============== INFERENCIA DE TRANSICIONES POBLACIONALES ==============

%% next_generation/4: Calcula población del próximo paso temporal.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio a calcular
%% @param Dia: Día actual
%% @param NuevaCantidad: Población calculada para siguiente día
%% Integra: entrada desde estadios previos, mortalidad y salida a siguientes.
next_generation(Species, Stage, Day, NewCount) :-
    population_state(Species, Stage, CurrentCount, Day),
    environmental_state(Day, Temp, Humidity),
    findall(PrevStage, 
            stage_transition(Species, PrevStage, Stage), 
            PrevStages),
    calculate_incoming(Species, PrevStages, Stage, Day, Temp, Humidity, Incoming),
    calculate_mortality(Species, Stage, CurrentCount, Temp, Humidity, Day, Deaths),
    calculate_outgoing(Species, Stage, CurrentCount, Temp, Humidity, Outgoing),
    NewCount is max(0, CurrentCount + Incoming - Deaths - Outgoing).

%% stage_transition/3: Define transiciones válidas entre estadios.
%% @param Especie: Identificador de especie
%% @param EstadioOrigen: Estadio desde el cual se transiciona
%% @param EstadioDestino: Estadio al cual se transiciona
%% Aedes aegypti
stage_transition(aedes_aegypti, egg, larva_l1).
stage_transition(aedes_aegypti, larva_l1, larva_l2).
stage_transition(aedes_aegypti, larva_l2, larva_l3).
stage_transition(aedes_aegypti, larva_l3, larva_l4).
stage_transition(aedes_aegypti, larva_l4, pupa).
stage_transition(aedes_aegypti, pupa, adult_female).
stage_transition(aedes_aegypti, pupa, adult_male).

%% Toxorhynchites (similar structure)
stage_transition(toxorhynchites, egg, larva_l1).
stage_transition(toxorhynchites, larva_l1, larva_l2).
stage_transition(toxorhynchites, larva_l2, larva_l3).
stage_transition(toxorhynchites, larva_l3, larva_l4).
stage_transition(toxorhynchites, larva_l4, pupa).
stage_transition(toxorhynchites, pupa, adult_female).
stage_transition(toxorhynchites, pupa, adult_male).

%% calculate_incoming/7: Calcula individuos entrantes desde estadios previos.
%% @param Especie: Identificador de especie
%% @param EstadiosPrevios: Lista de estadios que transicionan a este
%% @param EstadioActual: Estadio que recibe individuos
%% @param Dia: Día actual
%% @param Temperatura: Temperatura actual
%% @param Humedad: Humedad actual
%% @param TotalEntrantes: Suma de individuos que transicionan
%% Caso base: sin estadios previos
calculate_incoming(_, [], _, _, _, _, 0).
%% Caso recursivo: sumar contribuciones
calculate_incoming(Species, [PrevStage|Rest], Stage, Day, Temp, Hum, Total) :-
    (population_state(Species, PrevStage, PrevCount, Day) ->
        effective_survival(Species, PrevStage, Stage, Temp, Hum, SurvRate),
        % Probabilidad de transición basada en duración del estadio
        stage_duration(Species, PrevStage, MinDays, MaxDays),
        AvgDays is (MinDays + MaxDays) / 2,
        TransitionProb is 1 / AvgDays,
        Incoming is PrevCount * SurvRate * TransitionProb
    ;
        Incoming = 0
    ),
    calculate_incoming(Species, Rest, Stage, Day, Temp, Hum, RestIncoming),
    Total is Incoming + RestIncoming.

%% calculate_mortality/7: Calcula mortalidad natural y por depredación.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio actual
%% @param CantidadActual: Población actual
%% @param Temperatura: Temperatura actual
%% @param Humedad: Humedad actual
%% @param Dia: Día actual
%% @param Muertes: Total de muertes calculadas
%% Integra mortalidad natural (basada en supervivencia) y depredación.
calculate_mortality(Species, Stage, CurrentCount, Temp, Humidity, Day, Deaths) :-
    % Mortalidad natural (inverso de supervivencia diaria)
    stage_duration(Species, Stage, MinDays, MaxDays),
    AvgDays is (MinDays + MaxDays) / 2,
    BaseMortality is CurrentCount * (1 - (1 / AvgDays)),
    % Mortalidad por depredación
    predation_mortality(Species, Stage, Day, PredDeaths),
    % Total de muertes
    Deaths is BaseMortality + PredDeaths.

%% calculate_outgoing/6: Calcula individuos que transicionan a siguiente estadio.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio actual
%% @param CantidadActual: Población actual
%% @param Temperatura: Temperatura actual
%% @param Humedad: Humedad actual
%% @param Salientes: Individuos que transicionan
%% Basado en la duración promedio del estadio.
calculate_outgoing(Species, Stage, CurrentCount, Temp, Humidity, Outgoing) :-
    (stage_duration(Species, Stage, MinDays, MaxDays) ->
        AvgDays is (MinDays + MaxDays) / 2,
        TransitionRate is 1 / AvgDays,
        Outgoing is CurrentCount * TransitionRate
    ;
        Outgoing = 0
    ).

%% ============== INFERENCIA DE INTERACCIONES DEPREDADOR-PRESA ==============

%% predation_mortality/4: Calcula mortalidad por depredación.
%% @param EspeciePresa: Especie que es presa
%% @param EstadioPresam: Estadio de la presa
%% @param Dia: Día actual
%% @param MuertesPorDepredacion: Número de presas consumidas
%% Usa respuesta funcional tipo II y verifica vulnerabilidad del estadio.
predation_mortality(PreySpecies, PreyStage, Day, PredationDeaths) :-
    genus_of(PreySpecies, PreyGenus),
    vulnerable_stage(PreyGenus, PreyStage),
    population_state(PreySpecies, PreyStage, PreyCount, Day),
    findall(PredCount,
            (genus_of(PredSpecies, PredGenus),
             predatory_stage(PredGenus, PredStage),
             population_state(PredSpecies, PredStage, PredCount, Day)),
            PredatorCounts),
    sum_list(PredatorCounts, TotalPredators),
    (TotalPredators > 0 ->
        calculate_functional_response(TotalPredators, PreyCount, PredationDeaths)
    ;
        PredationDeaths = 0
    ).

%% Caso cuando el estadio no es vulnerable
predation_mortality(PreySpecies, PreyStage, _, 0) :-
    genus_of(PreySpecies, PreyGenus),
    \+ vulnerable_stage(PreyGenus, PreyStage).

%% calculate_functional_response/3: Implementa respuesta funcional tipo II (Holling).
%% @param Depredadores: Número total de depredadores
%% @param Presas: Número de presas disponibles
%% @param Consumidas: Número de presas consumidas
%% Fórmula: C = (P * a * N) / (1 + a * Th * N)
%% Donde P = depredadores, a = tasa de ataque, Th = tiempo de manipulación, N = presas
calculate_functional_response(Predators, Prey, Consumed) :-
    functional_response(toxorhynchites, AttackRate, HandlingTime),
    Consumed is (Predators * AttackRate * Prey) / (1 + AttackRate * HandlingTime * Prey).

%% ============== CONSULTAS ANALÍTICAS SOBRE LA POBLACIÓN ==============

%% total_population/3: Calcula población total de una especie en un día dado.
%% @param Especie: Identificador del género (aedes_aegypti o toxorhynchites)
%% @param Dia: Día de simulación
%% @param Total: Suma de todos los individuos en todos los estadios
%% Itera sobre todos los estadios de vida y suma sus poblaciones.
total_population(Species, Day, Total) :-
    findall(Count, population_state(Species, _, Count, Day), Counts),
    sum_list(Counts, Total).

%% population_trend/3: Analiza tendencia poblacional usando ventana temporal amplia.
%% @param Especie: Identificador de la especie
%% @param Dia: Día actual
%% @param Tendencia: growing (>5% aumento) | stable (variación <5%) | declining (>5% reducción)
%% - Usa ventana de 10 días (o menos si simulación es mas corta)
%% - Compara promedio de primeros 5 días vs últimos 5 días de la ventana
%% - Detecta crecimiento exponencial que antes se clasificaba como "estable"
population_trend(Species, Day, Trend) :-
    Day >= 10,
    % Obtener población actual y 10 días atrás
    total_population(Species, Day, CurrentPop),
    Day10Ago is Day - 9,
    total_population(Species, Day10Ago, Pop10DaysAgo),
    % Calcular promedio de primeros 5 días de la ventana (días -9 a -5)
    Day9Ago is Day - 9,
    Day8Ago is Day - 8,
    Day7Ago is Day - 7,
    Day6Ago is Day - 6,
    Day5Ago is Day - 5,
    total_population(Species, Day9Ago, P9),
    total_population(Species, Day8Ago, P8),
    total_population(Species, Day7Ago, P7),
    total_population(Species, Day6Ago, P6),
    total_population(Species, Day5Ago, P5),
    EarlyAvg is (P9 + P8 + P7 + P6 + P5) / 5,
    % Calcular promedio de últimos 5 días (días -4 a 0)
    Day4Ago is Day - 4,
    Day3Ago is Day - 3,
    Day2Ago is Day - 2,
    Day1Ago is Day - 1,
    total_population(Species, Day4Ago, P4),
    total_population(Species, Day3Ago, P3),
    total_population(Species, Day2Ago, P2),
    total_population(Species, Day1Ago, P1),
    total_population(Species, Day, P0),
    LateAvg is (P4 + P3 + P2 + P1 + P0) / 5,
    % Clasificar tendencia
    ( LateAvg > EarlyAvg * 1.05 -> Trend = growing
    ; LateAvg < EarlyAvg * 0.95 -> Trend = declining
    ; Trend = stable
    ).

%% Caso para simulaciones cortas (menos de 10 días): usa ventana reducida
population_trend(Species, Day, Trend) :-
    Day >= 5,
    Day < 10,
    % Comparar día actual con promedio de los 4 días anteriores
    Day1 is Day - 1,
    Day2 is Day - 2,
    Day3 is Day - 3,
    Day4 is Day - 4,
    total_population(Species, Day, CurrentPop),
    total_population(Species, Day1, P1),
    total_population(Species, Day2, P2),
    total_population(Species, Day3, P3),
    total_population(Species, Day4, P4),
    AvgPast is (P1 + P2 + P3 + P4) / 4,
    ( CurrentPop > AvgPast * 1.05 -> Trend = growing
    ; CurrentPop < AvgPast * 0.95 -> Trend = declining
    ; Trend = stable
    ).

%% Caso para días muy iniciales (menos de 5 días): comparación simple
population_trend(Species, Day, Trend) :-
    Day > 0,
    Day < 5,
    total_population(Species, Day, Pop1),
    PrevDay is Day - 1,
    (total_population(Species, PrevDay, Pop0) ->
        ( Pop1 > Pop0 * 1.05 -> Trend = growing
        ; Pop1 < Pop0 * 0.95 -> Trend = declining
        ; Trend = stable
        )
    ;
        Trend = initial
    ).

%% Caso inicial (día 0)
population_trend(_, 0, initial).

%% predator_prey_ratio/2: Calcula ratio de depredadores respecto a presas.
%% @param Dia: Día de simulación
%% @param Ratio: Proporción Toxorhynchites/Aedes (0 si no hay presas)
%% Métrica crítica para biocontrol: rango óptimo 0.1-0.3.
predator_prey_ratio(Day, Ratio) :-
    total_population(toxorhynchites, Day, PredPop),
    total_population(aedes_aegypti, Day, PreyPop),
    (PreyPop > 0 ->
        Ratio is PredPop / PreyPop
    ;
        Ratio = 0
    ).

%% biocontrol_viable/2: Evalúa viabilidad del biocontrol según criterios expertos.
%% @param Dia: Día de evaluación
%% @param Evaluacion: highly_effective | effective | promising | ineffective | requires_analysis
%% Combina ratio depredador-presa con tendencias poblacionales de ambas especies.
biocontrol_viable(Day, Assessment) :-
    predator_prey_ratio(Day, Ratio),
    population_trend(aedes_aegypti, Day, AedesTrend),
    population_trend(toxorhynchites, Day, ToxoTrend),
    assess_biocontrol(Ratio, AedesTrend, ToxoTrend, Assessment).

%% assess_biocontrol/4: Reglas expertas para clasificación de biocontrol.
%% @param Ratio: Proporción depredador/presa
%% @param TendenciaAedes: Tendencia poblacional de la presa
%% @param TendenciaToxo: Tendencia poblacional del depredador
%% @param Evaluacion: Clasificación del estatus de biocontrol
%% Implementa árbol de decisión basado en dinámica Lotka-Volterra.
assess_biocontrol(Ratio, declining, growing, highly_effective) :- Ratio > 0.05.
assess_biocontrol(Ratio, declining, stable, effective) :- Ratio > 0.03.
assess_biocontrol(Ratio, stable, growing, promising) :- Ratio > 0.02.
assess_biocontrol(_, growing, declining, ineffective).
assess_biocontrol(_, _, _, requires_analysis).

%% ============== REGLAS DE EQUILIBRIO ECOLÓGICO ==============

%% ecological_equilibrium/1: Determina si el sistema alcanzó equilibrio ecológico.
%% @param Dia: Día de evaluación
%% 
%% Detecta automáticamente el tipo de simulación (una o dos especies) y aplica
%% el criterio de equilibrio correspondiente.
%%
%% IMPLEMENTACIÓN: Prolog evaluará las reglas en orden. La primera que tenga
%% éxito será la que se use (backtracking).

%% ────────────────────────────────────────────────────────────────────────────
%% CASO 1: Sistema depredador-presa (DOS especies coexistiendo)
%% ────────────────────────────────────────────────────────────────────────────
%% Modelado según ecuaciones de Lotka-Volterra.
%% Condiciones para equilibrio ecológico:
%% 1. Ambas especies deben tener población activa (> 0)
%% 2. Ambas especies deben mostrar tendencia estable (variación < 5% diaria)
%% 3. Ratio depredador/presa debe estar en rango biológicamente viable (0.01 - 0.5)
%%
%% Este caso se usará en futuras implementaciones con depredación.
ecological_equilibrium(Day) :-
    % Verificar que ambas especies tengan población activa
    total_population(aedes_aegypti, Day, AedesPop),
    total_population(toxorhynchites, Day, ToxoPop),
    AedesPop > 0,
    ToxoPop > 0,
    % Verificar que ambas poblaciones estén estables
    population_trend(aedes_aegypti, Day, stable),
    population_trend(toxorhynchites, Day, stable),
    % Verificar que el ratio depredador-presa esté en rango válido
    predator_prey_ratio(Day, Ratio),
    Ratio > 0.01,   % Al menos 1% de depredadores respecto a presas
    Ratio < 0.5.    % No más de 50% (evita sobredepredación)

%% ────────────────────────────────────────────────────────────────────────────
%% CASO 2: Simulación de UNA sola especie (sin interacción)
%% ────────────────────────────────────────────────────────────────────────────
%% Para simulaciones poblacionales estándar (actual implementación).
%% Condiciones para equilibrio:
%% 1. Solo una especie tiene población activa
%% 2. La especie tiene tendencia estable (variación < 5% diaria)
%% 3. La población está por encima del doble del MVP (población saludable)
%%
%% Detecta automáticamente cuál especie se está simulando (Aedes o Toxorhynchites).
ecological_equilibrium(Day) :-
    % Detectar cuál especie está siendo simulada
    detect_simulated_species(Day, Species),
    % Verificar equilibrio para esa especie
    single_species_equilibrium(Species, Day).

%% detect_simulated_species/2: Detecta automáticamente qué especie se está simulando.
%% @param Dia: Día de simulación
%% @param Especie: Especie detectada (aedes_aegypti o toxorhynchites)
%% 
%% Retorna la especie que tiene población > 0 mientras la otra tiene 0 o no existe.
detect_simulated_species(Day, aedes_aegypti) :-
    total_population(aedes_aegypti, Day, AedesPop),
    AedesPop > 0,
    % Verificar que Toxo no tenga población o no exista
    (
        \+ total_population(toxorhynchites, Day, _)
    ;
        (total_population(toxorhynchites, Day, ToxoPop), ToxoPop = 0)
    ).

detect_simulated_species(Day, toxorhynchites) :-
    total_population(toxorhynchites, Day, ToxoPop),
    ToxoPop > 0,
    % Verificar que Aedes no tenga población o no exista
    (
        \+ total_population(aedes_aegypti, Day, _)
    ;
        (total_population(aedes_aegypti, Day, AedesPop), AedesPop = 0)
    ).

%% single_species_equilibrium/2: Verifica equilibrio para una sola especie.
%% @param Especie: Identificador de la especie
%% @param Dia: Día de evaluación
%%
%% Criterios:
%% - Tendencia estable (variación diaria < 5%)
%% - Población > 2 × MVP (población saludable y sostenible)
single_species_equilibrium(Species, Day) :-
    % Verificar tendencia estable
    population_trend(Species, Day, stable),
    % Verificar población saludable
    total_population(Species, Day, Pop),
    minimum_viable_population(Species, MVP),
    Pop > MVP * 2.  % Población debe ser al menos el doble del MVP

%% extinction_risk/3: Analiza riesgo de extinción según MVP (Minimum Viable Population).
%% @param Especie: Identificador de la especie
%% @param Dia: Día de evaluación
%% @param Riesgo: critical (<50% MVP) | high (<MVP) | moderate (<2×MVP) | low (≥2×MVP)
%% Compara población actual con umbrales basados en MVP ecológico (biología de la conservación).
extinction_risk(Species, Day, Risk) :-
    total_population(Species, Day, Pop),
    minimum_viable_population(Species, MVP),
    ( Pop < MVP * 0.5 -> Risk = critical
    ; Pop < MVP -> Risk = high
    ; Pop < MVP * 2 -> Risk = moderate
    ; Risk = low
    ).

%% minimum_viable_population/2: Define MVP (Minimum Viable Population) por género.
%% @param Genero: Identificador del género
%% @param MVP: Población mínima para viabilidad genética y demográfica a largo plazo
%% Valores conservadores basados en estrategia reproductiva: Aedes 50 (r-estratega con alta fecundidad),
%% Toxorhynchites 20 (K-estratega con baja fecundidad).
minimum_viable_population(aedes_aegypti, 50).
minimum_viable_population(toxorhynchites, 20).

%% ============== PROYECCIÓN TEMPORAL (RECURSIVA) ==============

%% project_population/4: Proyecta población hacia el futuro iterativamente.
%% @param Especie: Identificador de la especie a proyectar
%% @param DiaActual: Día de inicio de la proyección
%% @param DiaObjetivo: Día final de la proyección
%% @param Proyeccion: Lista de estructuras stage_pop(Estadio, Cantidad) para día objetivo
%% Recursivamente aplica transiciones diarias usando advance_all_stages/3.
%% Caso base: día actual alcanzó o superó día objetivo
project_population(Species, CurrentDay, TargetDay, Projection) :-
    CurrentDay >= TargetDay,
    !,
    findall(stage_pop(Stage, Count), 
            population_state(Species, Stage, Count, CurrentDay), 
            Projection).

%% Caso recursivo: avanzar un día y continuar proyección
project_population(Species, CurrentDay, TargetDay, Projection) :-
    CurrentDay < TargetDay,
    NextDay is CurrentDay + 1,
    advance_all_stages(Species, CurrentDay, NextDay),
    project_population(Species, NextDay, TargetDay, Projection).

%% advance_all_stages/3: Avanza todos los estadios de una especie un día.
%% @param Especie: Identificador de especie
%% @param DiaActual: Día actual
%% @param DiaSiguiente: Día siguiente (DiaActual + 1)
%% Itera sobre todos los life_stage/1, calcula next_generation/4 y aserta nuevos estados.
advance_all_stages(Species, CurrentDay, NextDay) :-
    forall(
        life_stage(Stage),
        (
            next_generation(Species, Stage, CurrentDay, NewCount),
            assertz(population_state(Species, Stage, NewCount, NextDay))
        )
    ).