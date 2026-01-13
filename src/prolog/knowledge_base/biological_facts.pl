%% ══════════════════════════════════════════════════════════════════
%% HECHOS BIOLÓGICOS - Cargados Dinámicamente desde Configuración
%% ══════════════════════════════════════════════════════════════════
%%
%% Este archivo define predicados dinámicos para parámetros biológicos
%% que son cargados desde archivos JSON de configuración en tiempo de
%% ejecución. NO contiene valores hardcodeados.
%%
%% Flujo: JSON → Python (ConfigManager) → PySwip → assertz() → Prolog
%%
%% ══════════════════════════════════════════════════════════════════

%% ══════════════════════════════════════════════════════════════════
%% DECLARACIÓN DE PREDICADOS DINÁMICOS
%% ══════════════════════════════════════════════════════════════════

%% stage_duration/4: Duración de cada estadio de desarrollo.
%% @param Especie: Nombre de la especie
%% @param Estadio: Estadio del ciclo de vida
%% @param MinDias: Duración minima en días
%% @param MaxDias: Duración mixima en días
:- dynamic stage_duration/4.

%% survival_rate/4: Tasa de supervivencia entre estadios.
%% @param Especie: Nombre de la especie
%% @param EstadioOrigen: Estadio de origen
%% @param EstadioDestino: Estadio de destino
%% @param Tasa: Tasa de supervivencia [0.0-1.0]
:- dynamic survival_rate/4.

%% fecundity/4: Fecundidad de hembras adultas.
%% @param Especie: Nombre de la especie
%% @param MinHuevos: Mínimo de huevos por evento
%% @param MaxHuevos: Máximo de huevos por evento
%% @param EventosOviposicion: Número de eventos en vida
:- dynamic fecundity/4.

%% predation_rate/3: Tasa de depredación por estadio.
%% @param Depredador: Especie depredadora
%% @param EstadioPresam: Estadio de la presa
%% @param TasaDiaria: Número de presas consumidas por día
:- dynamic predation_rate/3.

%% functional_response/3: Parámetros de respuesta funcional tipo II.
%% @param Depredador: Especie depredadora
%% @param TasaAtaque: Tasa de ataque (a)
%% @param TiempoManipulacion: Tiempo de manipulación (Th)
:- dynamic functional_response/3.

%% environmental_param/2: Parámetros ambientales generales.
%% @param Nombre: Nombre del parámetro
%% @param Valor: Valor del parámetro
:- dynamic environmental_param/2.

%% ══════════════════════════════════════════════════════════════════
%% PREDICADOS DE CARGA - Llamados desde Python vía PySwip
%% ══════════════════════════════════════════════════════════════════

%% clear_all_parameters/0: Elimina todos los parámetros cargados.
%% Útil para reiniciar la simulación o cargar nueva configuración.
clear_all_parameters :-
    retractall(stage_duration(_, _, _, _)),
    retractall(survival_rate(_, _, _, _)),
    retractall(fecundity(_, _, _, _)),
    retractall(predation_rate(_, _, _)),
    retractall(functional_response(_, _, _)),
    retractall(environmental_param(_, _)).

%% load_stage_duration/4: Carga duración de un estadio.
%% @param Especie: Identificador de especie
%% @param Estadio: Estadio del ciclo de vida
%% @param Min: Duración minima en días
%% @param Max: Duración maxima en días
load_stage_duration(Species, Stage, Min, Max) :-
    assertz(stage_duration(Species, Stage, Min, Max)).

%% load_survival_rate/4: Carga tasa de supervivencia.
%% @param Especie: Identificador de especie
%% @param Desde: Estadio origen
%% @param Hasta: Estadio destino
%% @param Tasa: Tasa de supervivencia [0.0-1.0]
load_survival_rate(Species, From, To, Rate) :-
    assertz(survival_rate(Species, From, To, Rate)).

%% load_fecundity/4: Carga parámetros de fecundidad.
%% @param Especie: Identificador de especie
%% @param Min: Mínimo de huevos por evento
%% @param Max: Máximo de huevos por evento
%% @param Eventos: Número de eventos de oviposición
load_fecundity(Species, Min, Max, Events) :-
    assertz(fecundity(Species, Min, Max, Events)).

%% load_predation_rate/3: Carga tasa de depredación.
%% @param Depredador: Especie depredadora
%% @param EstadioPresam: Estadio de la presa
%% @param Tasa: Número de presas por día
load_predation_rate(Predator, PreyStage, Rate) :-
    assertz(predation_rate(Predator, PreyStage, Rate)).

%% load_functional_response/3: Carga parámetros de respuesta funcional.
%% @param Depredador: Especie depredadora
%% @param TasaAtaque: Parámetro 'a' de la ecuación de Holling
%% @param TiempoManipulacion: Parámetro 'Th' de la ecuación de Holling
load_functional_response(Predator, AttackRate, HandlingTime) :-
    assertz(functional_response(Predator, AttackRate, HandlingTime)).

%% load_environmental_param/2: Carga parámetro ambiental general.
%% @param Nombre: Nombre del parámetro (e.g., carrying_capacity, temperature)
%% @param Valor: Valor del parámetro
load_environmental_param(Name, Value) :-
    assertz(environmental_param(Name, Value)).

%% ══════════════════════════════════════════════════════════════════
%% CONSULTAS DE VALIDACIÓN Y DIAGNÓSTICO
%% ══════════════════════════════════════════════════════════════════

%% parameters_loaded/1: Verifica que parámetros esenciales estén cargados.
%% @param Especie: Especie a verificar
%% Retorna true si los parámetros minimos necesarios están presentes.
parameters_loaded(Species) :-
    stage_duration(Species, egg, _, _),
    stage_duration(Species, larva_l1, _, _),
    survival_rate(Species, egg, larva_l1, _),
    fecundity(Species, _, _, _).

%% list_species_params/2: Lista todos los parámetros de una especie.
%% @param Especie: Especie a consultar
%% @param Parametros: Lista de parámetros en formato param(Tipo, Datos)
%% Útil para debugging y verificación de configuración cargada.
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

%% count_loaded_params/2: Cuenta parámetros cargados por tipo.
%% @param Tipo: Tipo de parámetro (duration, survival, fecundity, etc.)
%% @param Cantidad: Número de parámetros de ese tipo
count_loaded_params(duration, Count) :-
    findall(1, stage_duration(_, _, _, _), List),
    length(List, Count).
count_loaded_params(survival, Count) :-
    findall(1, survival_rate(_, _, _, _), List),
    length(List, Count).
count_loaded_params(fecundity, Count) :-
    findall(1, fecundity(_, _, _, _), List),
    length(List, Count).
count_loaded_params(predation, Count) :-
    findall(1, predation_rate(_, _, _), List),
    length(List, Count).
count_loaded_params(environmental, Count) :-
    findall(1, environmental_param(_, _), List),
    length(List, Count).