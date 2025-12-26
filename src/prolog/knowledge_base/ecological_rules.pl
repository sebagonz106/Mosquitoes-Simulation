%% ══════════════════════════════════════════════════════════════════
%% REGLAS ECOLÓGICAS - Inferencia de Interacciones
%% ══════════════════════════════════════════════════════════════════
%%
%% Este archivo contiene reglas de inferencia para modelar interacciones
%% ecológicas, efectos ambientales y dinámicas poblacionales.
%%
%% Incluye:
%% - Determinación de depredación
%% - Ajustes por temperatura y humedad
%% - Cálculo de supervivencia efectiva
%% - Capacidad de carga del hábitat
%% - Evaluación de equilibrio poblacional
%%
%% ══════════════════════════════════════════════════════════════════

%% ══════════════════════════════════════════════════════════════════
%% INFERENCIA DE DEPREDACIÓN
%% ══════════════════════════════════════════════════════════════════

%% can_predate/4: Determina si puede ocurrir depredación entre especies.
%% @param Depredador: Especie depredadora
%% @param Presa: Especie presa
%% @param EstadioDepredador: Estadio del depredador
%% @param EstadioPresam: Estadio de la presa
%% Retorna true si todos los criterios para depredación se cumplen.
can_predate(Predator, Prey, PredatorStage, PreyStage) :-
    species(Predator, GenusP),
    species(Prey, GenusY),
    predatory_stage(GenusP, PredatorStage),
    vulnerable_stage(GenusY, PreyStage),
    ecological_role(Predator, predator),
    ecological_role(Prey, prey).

%% ══════════════════════════════════════════════════════════════════
%% AJUSTES AMBIENTALES
%% ══════════════════════════════════════════════════════════════════

%% temperature_adjustment/3: Calcula factor de ajuste por temperatura.
%% @param Temperatura: Temperatura actual en °C
%% @param Especie: Especie a evaluar
%% @param Factor: Factor de ajuste [0.5-1.0]
%% Implementa curva de respuesta térmica específica por especie.
%% temperature_adjustment para Aedes aegypti (óptimo 27°C, límites 10-40°C)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp >= 20, Temp =< 35,
    OptimalTemp = 27,
    Diff is abs(Temp - OptimalTemp),
    Factor is max(0.5, 1 - (Diff * 0.03)).

%% Temperatura baja (10-20°C)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp >= 10, Temp < 20,
    Factor is max(0.05, 0.3 - (20 - Temp) * 0.04).  % Decreases rapidly below 20°C

%% Temperatura muy baja (<10°C)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp < 10,
    Factor is 0.01.  % Practically extinct

%% Temperatura alta (>35°C)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp > 35, Temp =< 40,
    Factor is max(0.05, 0.6 - (Temp - 35) * 0.11).  % Lethal threshold at ~40°C

%% Temperatura letal (>40°C)
temperature_adjustment(Temp, aedes_aegypti, Factor) :-
    Temp > 40,
    Factor is 0.01.  % Practically extinct

%% temperature_adjustment para Toxorhynchites (óptimo 28°C, límites 8-42°C)
temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp >= 18, Temp =< 35,
    OptimalTemp = 28,
    Diff is abs(Temp - OptimalTemp),
    Factor is max(0.5, 1 - (Diff * 0.025)).

%% Temperatura baja (8-18°C)
temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp >= 8, Temp < 18,
    Factor is max(0.05, 0.4 - (18 - Temp) * 0.035).  % More cold-tolerant than Aedes

%% Temperatura muy baja (<8°C)
temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp < 8,
    Factor is 0.01.

%% Temperatura alta (>35°C)
temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp > 35, Temp =< 42,
    Factor is max(0.05, 0.65 - (Temp - 35) * 0.108).  % More heat-tolerant

%% Temperatura letal (>42°C)
temperature_adjustment(Temp, toxorhynchites, Factor) :-
    Temp > 42,
    Factor is 0.01.

%% humidity_adjustment/2: Calcula factor de ajuste por humedad.
%% @param Humedad: Humedad relativa en porcentaje
%% @param Factor: Factor de ajuste [0.01-1.0]
%% Óptima: >60%, tolerable 40-60%, crítica 20-40%, letal <20%
humidity_adjustment(Humidity, Factor) :-
    Humidity >= 60,
    Factor is min(1.0, 0.7 + (Humidity - 60) * 0.0075).

%% Humedad tolerable (40-60%)
humidity_adjustment(Humidity, Factor) :-
    Humidity >= 40, Humidity < 60,
    Factor is 0.5 + (Humidity - 40) * 0.01.  % Linear from 0.5 to 0.7

%% Humedad baja (20-40%)
humidity_adjustment(Humidity, Factor) :-
    Humidity >= 20, Humidity < 40,
    Factor is max(0.1, 0.35 - (40 - Humidity) * 0.0125).  % Rapid decrease

%% Humedad crítica (<20%)
humidity_adjustment(Humidity, Factor) :-
    Humidity < 20,
    Factor is 0.01.  % Nearly lethal

%% effective_survival/6: Calcula supervivencia efectiva con factores ambientales.
%% @param Especie: Especie a evaluar
%% @param EstadioOrigen: Estadio de origen
%% @param EstadioDestino: Estadio de destino
%% @param Temperatura: Temperatura actual
%% @param Humedad: Humedad relativa actual
%% @param TasaEfectiva: Tasa de supervivencia ajustada
%% Combina tasa base con factores ambientales multiplicativos.
effective_survival(Species, FromStage, ToStage, Temp, Humidity, EffRate) :-
    survival_rate(Species, FromStage, ToStage, BaseRate),
    temperature_adjustment(Temp, Species, TempFactor),
    humidity_adjustment(Humidity, HumFactor),
    EffRate is BaseRate * TempFactor * HumFactor.

%% ══════════════════════════════════════════════════════════════════
%% CAPACIDAD DE CARGA Y EQUILIBRIO
%% ══════════════════════════════════════════════════════════════════

%% carrying_capacity/1: Obtiene capacidad de carga del hábitat.
%% @param Capacidad: Número máximo de individuos sostenibles
%% Recupera el valor desde parámetros ambientales cargados dinámicamente.
carrying_capacity(Capacity) :-
    environmental_param(carrying_capacity, Capacity).

%% population_equilibrium/4: Determina estado de equilibrio poblacional.
%% @param Especie: Especie a evaluar
%% @param Poblacion: Población actual
%% @param Capacidad: Capacidad de carga del hábitat
%% @param Estado: Estado inferido (growing, declining, stable)
%% Usa umbrales del 80% y 120% de la capacidad de carga.
population_equilibrium(Species, Population, Capacity, Status) :-
    Ratio is Population / Capacity,
    (Ratio < 0.8 -> Status = growing ;
     Ratio > 1.2 -> Status = declining ;
     Status = stable).

%% ══════════════════════════════════════════════════════════════════
%% MODELADO DE DEPREDACIÓN
%% ══════════════════════════════════════════════════════════════════

%% predation_impact/4: Calcula impacto de depredación con respuesta funcional.
%% @param PoblacionDepredador: Número de depredadores
%% @param PoblacionPresam: Número de presas
%% @param EstadioPresam: Estadio de la presa
%% @param Impacto: Número de presas consumidas
%% Implementa respuesta funcional tipo II de Holling con límite por capacidad.
predation_impact(PredatorPop, PreyPop, PreyStage, Impact) :-
    predation_rate(toxorhynchites, PreyStage, RatePerPredator),
    functional_response(toxorhynchites, AttackRate, HandlingTime),
    TotalPotential is PredatorPop * RatePerPredator,
    % Aplicar respuesta funcional tipo II: C = (a*N) / (1 + a*Th*N)
    RawImpact is (AttackRate * PreyPop) / (1 + AttackRate * HandlingTime * PreyPop),
    % El impacto no puede exceder el potencial total de depredación
    Impact is min(RawImpact, TotalPotential).