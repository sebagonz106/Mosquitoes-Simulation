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
%% Autor: Sistema de Simulación de Mosquitos
%% Fecha: Enero 2026
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

%% humidity_adjustment/2: Calcula factor de ajuste por humedad.
%% @param Humedad: Humedad relativa en porcentaje
%% @param Factor: Factor de ajuste [0.3-1.0]
%% La humedad óptima es >60%, crítica <60%.
humidity_adjustment(Humidity, Factor) :-
    Humidity >= 60,
    Factor is min(1.0, 0.7 + (Humidity - 60) * 0.0075).
humidity_adjustment(Humidity, Factor) :-
    Humidity < 60,
    Factor is max(0.3, Humidity / 100).

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