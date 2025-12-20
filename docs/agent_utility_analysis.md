# Análisis Crítico: Sistema de Utilidad de Agentes

**Fecha:** 9 de enero de 2026  
**Componente:** `agent_decisions.pl` - Función de utilidad y beneficios  
**Estado:** Requiere corrección urgente

---

## 🔴 Problema Actual

### Descripción del Bug

El sistema actual calcula **utilidades negativas** para acciones que no cumplen precondiciones, debido a que `action_benefit/3` contiene condiciones que pueden fallar:

```prolog
% Líneas 204-215 (CÓDIGO ACTUAL - PROBLEMÁTICO)
action_benefit(Agent, feed, 50) :-
    agent_state(Agent, _, _, Energy, _),
    Energy < 40.  % ← Si Energy >= 40, esta cláusula FALLA

action_benefit(Agent, oviposit, 100) :-
    agent_state(Agent, adult_female, _, _, false).  % ← Si ya reprodujo (true), FALLA

action_benefit(Agent, hunt, 80) :-
    perceive(Agent, prey_available(N)),
    N > 0.  % ← Si no hay presas, FALLA

action_benefit(_, _, 0).  % ← CAE AQUÍ cuando las condiciones fallan
```

### Ejemplo del Bug

**Escenario:** Agente con Energy=50, Reproduced=true

Al calcular `utility(agent, oviposit, U)`:
1. Busca `action_benefit(agent, oviposit, B)`
2. Intenta `agent_state(..., false)` pero encuentra `true` → **FALLA**
3. Cae en `action_benefit(_, _, 0)` → Benefit = 0
4. Calcula: `Utility = 0 - 20 + 5 = -15` ❌

**Resultado del Test 5:**
```
oviposit: utility = -14.00  ❌
feed: utility = -4.00       ❌
rest: utility = 10.00       ✓
```

---

## ⚠️ Consecuencias de Mantener el Código Actual

### 1. **Decisiones Irracionales en Casos Extremos**

Si un agente tiene múltiples acciones con utilidad negativa, puede elegir arbitrariamente entre ellas:

```prolog
best_action(Agent, BestAction) :-
    findall(U-A, (decide_action(Agent, A), utility(Agent, A, U)), Actions),
    sort(Actions, Sorted),
    reverse(Sorted, [_-BestAction|_]).
```

- Si `Actions = [(-15)-oviposit, (-4)-feed]`, elegirá `feed` (menos negativo)
- Pero esto **no refleja la realidad biológica**: alimentarse con Energy=50 es menos urgente

### 2. **Inconsistencia Lógica**

El sistema actual tiene **dos sistemas de precondiciones**:
- `decide_action/2`: Define si una acción es **válida**
- `action_benefit/3` con condiciones: Define si una acción tiene **valor**

**Esto rompe el principio de separación de responsabilidades:**
- Las precondiciones deben estar **solo en `decide_action/2`**
- Los beneficios deben ser **propiedades intrínsecas** de las acciones

### 3. **Dificultad para Debugging**

Cuando un agente toma una decisión extraña:
- ¿Es un problema de precondiciones en `decide_action`?
- ¿O un problema de beneficios en `action_benefit`?
- El desarrollador debe revisar **dos lugares** con lógica superpuesta

### 4. **Valores Arbitrarios Sin Fundamento**

Los beneficios actuales son números fijos sin justificación biológica:
```prolog
action_benefit(Agent, oviposit, 100).  % ¿Por qué 100?
action_benefit(Agent, feed, 50).       % ¿Por qué 50?
action_benefit(Agent, rest, 5).        % ¿Por qué 5?
```

**Problema:** Si se ajusta la configuración biológica (ej: eggs_per_batch), los beneficios permanecen desincronizados.

### 5. **Escalas Incomparables**

¿Cómo comparar?
- **100** huevos puestos (fitness reproductivo)
- **50** energía ganada (recurso inmediato)
- **5** recuperación (pequeño beneficio)

No hay **fundamento teórico** para estas escalas relativas.

---

## ✅ Solución Propuesta: Beneficios Basados en Biología

### Arquitectura Mejorada

```prolog
%% ══════════════════════════════════════════════════════════════════
%% BENEFICIOS BASADOS EN PARÁMETROS BIOLÓGICOS
%% ══════════════════════════════════════════════════════════════════

%% Beneficio de ovipositar = Fitness reproductivo real
action_benefit(Agent, oviposit, Benefit) :-
    agent_species(Agent, Species),
    eggs_per_batch_range(Species, Min, Max),
    AvgEggs is (Min + Max) / 2,
    Benefit is AvgEggs * 1.0.  % Cada huevo = 1 unidad de fitness

%% Beneficio de alimentarse = Energía ganada real
action_benefit(Agent, feed, Benefit) :-
    agent_species(Agent, Species),
    blood_meal_energy_gain(Species, EnergyGain),
    Benefit is EnergyGain.

%% Beneficio de cazar = Energía por presa * Tasa de predación
action_benefit(Agent, hunt, Benefit) :-
    agent_species(Agent, Species),
    predation_rate_range(Species, MinRate, MaxRate),
    AvgRate is (MinRate + MaxRate) / 2,
    prey_energy_value(EnergyPerPrey),
    Benefit is AvgRate * EnergyPerPrey.

%% Beneficio de crecer = Fitness de avanzar en metamorfosis
action_benefit(Agent, grow, Benefit) :-
    agent_state(Agent, Stage, _, _, _),
    next_stage(Stage, NextStage),
    stage_fitness_value(NextStage, Benefit).

%% Beneficio de descansar = Energía recuperada
action_benefit(Agent, rest, Benefit) :-
    rest_energy_recovery(Recovery),
    Benefit is Recovery.
```

### Parámetros Biológicos Requeridos

Agregar a `biological_facts.pl` o configuración:

```prolog
%% Parámetros energéticos
blood_meal_energy_gain(aedes_aegypti, 40).
blood_meal_energy_gain(toxorhynchites, 0).  % No se alimentan de sangre
prey_energy_value(15).  % Energía por larva de Aedes consumida
rest_energy_recovery(3).

%% Fitness por estadio (refleja valor adaptativo de cada etapa)
stage_fitness_value(larva_l1, 10).
stage_fitness_value(larva_l2, 20).
stage_fitness_value(larva_l3, 35).
stage_fitness_value(larva_l4, 50).
stage_fitness_value(pupa, 70).
stage_fitness_value(adult_female, 100).
stage_fitness_value(adult_male, 50).  % Menor fitness reproductivo directo
```

### Valores Resultantes (Ejemplo Real)

Con `eggs_per_batch_range(aedes_aegypti, 80, 150)`:

| Acción | Cálculo | Beneficio | Costo | Utilidad (Energy=80) |
|--------|---------|-----------|-------|----------------------|
| oviposit | (80+150)/2 = 115 | 115 | 20 | 115 - 20 + 8 = **103** ✅ |
| feed | 40 | 40 | 10 | 40 - 10 + 8 = **38** ✅ |
| rest | 3 | 3 | 1 | 3 - 1 + 8 = **10** ✅ |

**Todos los valores son positivos y proporcionales a su valor biológico real.**

---

## 📊 Comparación de Enfoques

| Aspecto | Sistema Actual | Sistema Mejorado |
|---------|----------------|------------------|
| **Fundamento** | Números arbitrarios | Parámetros biológicos reales |
| **Mantenibilidad** | Difícil (valores hardcodeados) | Fácil (basado en config) |
| **Escalas** | Incomparables | Comparables (fitness o energía) |
| **Valores negativos** | Sí (bug) | No (solo para acciones válidas) |
| **Sincronización** | Manual | Automática con parámetros |
| **Interpretabilidad** | Baja | Alta (refleja biología) |
| **Validación científica** | Imposible | Posible (citar fuentes) |

---

## 🎯 Recomendación

**Implementar la solución basada en biología** por las siguientes razones:

1. **Corrección del bug:** Elimina utilidades negativas espurias
2. **Fundamento científico:** Valores justificables con literatura
3. **Mantenibilidad:** Cambiar un parámetro actualiza todo el sistema
4. **Escalabilidad:** Fácil agregar nuevas especies o acciones
5. **Trazabilidad:** Cada valor tiene origen claro

---

## 📚 Referencias Sugeridas

Para justificar los valores de parámetros biológicos:

1. **Fitness reproductivo:**
   - Hoffmann AA, Turelli M. (1997). *Cytoplasmic incompatibility in insects*
   - Eggs per batch: directamente del paper de Scott et al. (2000)

2. **Costos energéticos:**
   - Briegel H. (1990). *Metabolic relationship between female body size, reserves, and fecundity of Aedes aegypti*

3. **Tasa de predación de Toxorhynchites:**
   - Focks DA, et al. (1985). *Larval competition and adult fitness in Aedes aegypti*

4. **Teoría de fitness:**
   - Russell & Norvig (2020). *AI: A Modern Approach*, Cap. 2 - Rational Agents

---

## 🔧 Plan de Implementación

1. **Fase 1:** Agregar parámetros biológicos a `biological_facts.pl`
2. **Fase 2:** Reescribir `action_benefit/3` en `agent_decisions.pl`
3. **Fase 3:** Actualizar tests con valores esperados reales
4. **Fase 4:** Validar que `best_action` funciona correctamente
5. **Fase 5:** Documentar fuentes de cada parámetro

**Tiempo estimado:** 2-3 horas  
**Riesgo:** Bajo (los tests detectarán cualquier regresión)

---

## 💡 Conclusión

El sistema actual **funciona para casos básicos** pero tiene **defectos arquitectónicos** que pueden causar comportamientos anómalos en escenarios complejos. La solución propuesta no solo corrige el bug, sino que establece una **arquitectura más robusta y científicamente fundamentada** para el largo plazo.

**Si se deja como está:**
- Los agentes tomarán decisiones **técnicamente correctas** (gracias a que `best_action` usa `decide_action`)
- Pero los valores de utilidad serán **engañosos** y dificultarán debugging
- Cualquier análisis de "por qué el agente eligió X" será **ininterpretable**
- Extender el sistema (nuevas especies, nuevas acciones) será **complejo y propenso a errores**

**Si se implementa la mejora:**
- Decisiones **transparentes** y **justificables biológicamente**
- Sistema **escalable** y **mantenible**
- Base sólida para **publicaciones científicas** sobre el modelo
