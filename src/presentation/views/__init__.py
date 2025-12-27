"""
Presentation Layer - Views Package
==================================

View components for different screens.
"""

from .home_view import HomeView
from .simulation_view import SimulationView
from .predator_prey_view import PredatorPreyView
from .results_view import ResultsView
from .results_predator_prey_view import PredatorPreyResultsView
from .compare_view import CompareView
from .checkpoints_view import CheckpointsView
from .species_view import SpeciesView

__all__ = [
    'HomeView',
    'SimulationView',
    'PredatorPreyView',
    'ResultsView',
    'PredatorPreyResultsView',
    'CompareView',
    'CheckpointsView',
    'SpeciesView'
]
