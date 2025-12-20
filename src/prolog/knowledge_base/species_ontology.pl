%% ══════════════════════════════════════════════════════════════════
%% ONTOLOGÍA DE ESPECIES - Base de Conocimiento Taxonómica
%% ══════════════════════════════════════════════════════════════════
%%
%% Este archivo define la estructura taxonómica y características
%% fundamentales de las especies modeladas en el simulador.
%%
%% ══════════════════════════════════════════════════════════════════

%% ══════════════════════════════════════════════════════════════════
%% JERARQUÍA TAXONÓMICA
%% ══════════════════════════════════════════════════════════════════

%% kingdom/1: Define el reino al que pertenecen las especies.
%% @param Reino: Nombre del reino taxonómico
kingdom(animalia).

%% phylum/1: Define el filo taxonómico.
%% @param Filo: Nombre del filo
phylum(arthropoda).

%% class/1: Define la clase taxonómica.
%% @param Clase: Nombre de la clase
class(insecta).

%% order/1: Define el orden taxonómico.
%% @param Orden: Nombre del orden
order(diptera).

%% family/1: Define la familia taxonómica.
%% @param Familia: Nombre de la familia
family(culicidae).

%% ══════════════════════════════════════════════════════════════════
%% GÉNEROS Y ESPECIES
%% ══════════════════════════════════════════════════════════════════

%% genus/1: Define los géneros de mosquitos modelados.
%% @param Genero: Nombre del género
genus(aedes).
genus(toxorhynchites).

%% species/2: Relaciona una especie con su género.
%% @param Especie: Nombre científico de la especie
%% @param Genero: Género al que pertenece
species(aedes_aegypti, aedes).
species(toxorhynchites_rutilus, toxorhynchites).
species(toxorhynchites_amboinensis, toxorhynchites).

%% ══════════════════════════════════════════════════════════════════
%% ROLES ECOLÓGICOS
%% ══════════════════════════════════════════════════════════════════

%% ecological_role/2: Define el rol ecológico de cada especie o género.
%% @param Especie: Nombre de la especie o género
%% @param Rol: Rol ecológico (prey, predator, disease_vector, etc.)
ecological_role(aedes_aegypti, prey).
ecological_role(aedes_aegypti, disease_vector).
ecological_role(toxorhynchites, predator).
ecological_role(toxorhynchites_rutilus, predator).
ecological_role(toxorhynchites_amboinensis, predator).

%% ══════════════════════════════════════════════════════════════════
%% ESTADIOS DEL CICLO DE VIDA
%% ══════════════════════════════════════════════════════════════════

%% life_stage/1: Define los estadios posibles del ciclo de vida.
%% @param Estadio: Nombre del estadio de desarrollo
life_stage(egg).
life_stage(larva_l1).
life_stage(larva_l2).
life_stage(larva_l3).
life_stage(larva_l4).
life_stage(pupa).
life_stage(adult_male).
life_stage(adult_female).

%% aquatic_stage/1: Identifica los estadios acuáticos.
%% @param Estadio: Estadio que ocurre en medio acuático
aquatic_stage(egg).
aquatic_stage(larva_l1).
aquatic_stage(larva_l2).
aquatic_stage(larva_l3).
aquatic_stage(larva_l4).
aquatic_stage(pupa).

%% ══════════════════════════════════════════════════════════════════
%% INTERACCIONES DEPREDADOR-PRESA
%% ══════════════════════════════════════════════════════════════════

%% predatory_stage/2: Define qué estadios son depredadores activos.
%% @param Genero: Género del depredador
%% @param Estadio: Estadio en el que es depredador activo
predatory_stage(toxorhynchites, larva_l3).
predatory_stage(toxorhynchites, larva_l4).

%% vulnerable_stage/2: Define qué estadios son vulnerables a depredación.
%% @param Genero: Género de la presa
%% @param Estadio: Estadio vulnerable
vulnerable_stage(aedes, larva_l1).
vulnerable_stage(aedes, larva_l2).
vulnerable_stage(aedes, larva_l3).
vulnerable_stage(aedes, larva_l4).

%% ══════════════════════════════════════════════════════════════════
%% PREDICADOS DE CONSULTA AUXILIARES
%% ══════════════════════════════════════════════════════════════════

%% is_predator/1: Verifica si una especie es depredadora.
%% @param Especie: Especie a verificar
is_predator(Species) :-
    ecological_role(Species, predator).

%% is_prey/1: Verifica si una especie es presa.
%% @param Especie: Especie a verificar
is_prey(Species) :-
    ecological_role(Species, prey).

%% is_vector/1: Verifica si una especie es vector de enfermedades.
%% @param Especie: Especie a verificar
is_vector(Species) :-
    ecological_role(Species, disease_vector).

%% genus_of/2: Obtiene el género de una especie.
%% @param Especie: Nombre de la especie
%% @param Genero: Género al que pertenece
genus_of(Species, Genus) :-
    species(Species, Genus).