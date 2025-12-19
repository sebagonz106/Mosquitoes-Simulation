"""
Domain Models Module
====================

Mathematical models for population dynamics simulation.

Modules:
    - stochastic_processes: Stochastic variation generators
    - leslie_matrix: Leslie matrix implementation for demographic projection
    - environment_model: Environmental conditions time series
    - population_model: Integrated population dynamics model
"""

from .stochastic_processes import (
    StochasticVariation,
    DemographicStochasticity,
    EnvironmentalStochasticity
)

from .leslie_matrix import (
    LeslieMatrix,
    create_leslie_matrix_from_config
)

from .environment_model import (
    EnvironmentModel,
    TemperatureSeries,
    HumiditySeries
)

from .population_model import (
    PopulationModel
)

__all__ = [
    # Stochastic processes
    'StochasticVariation',
    'DemographicStochasticity',
    'EnvironmentalStochasticity',
    
    # Leslie matrix
    'LeslieMatrix',
    'create_leslie_matrix_from_config',
    
    # Environment
    'EnvironmentModel',
    'TemperatureSeries',
    'HumiditySeries',
    
    # Population model
    'PopulationModel'
]
