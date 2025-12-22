"""
Leslie Matrix Module
====================

Implements Leslie matrix models for age-structured population dynamics.

The Leslie matrix is a discrete-time age-structured population model:
    n(t+1) = L * n(t)

Where:
    - n(t) is the population vector (ages or stages)
    - L is the Leslie matrix with:
        * First row: fecundity (F_i)
        * Subdiagonal: survival rates (P_i)

Eigenanalysis provides:
    - λ₁: dominant eigenvalue (population growth rate)
    - w: stable age distribution
    - v: reproductive value vector

Author: Mosquito Simulation System
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from scipy.linalg import eig
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from infrastructure.config import SpeciesConfig


@dataclass
class LeslieMatrixResult:
    """
    Results from Leslie matrix eigenanalysis.
    
    Attributes:
        lambda_1: Dominant eigenvalue (population growth rate)
        stable_age_dist: Stable age distribution (right eigenvector)
        reproductive_value: Reproductive value distribution (left eigenvector)
        generation_time: Mean generation time
        r: Intrinsic rate of increase (ln(λ₁))
        doubling_time: Population doubling time (ln(2)/r), if r > 0
    """
    lambda_1: float
    stable_age_dist: np.ndarray
    reproductive_value: np.ndarray
    generation_time: float
    r: float
    doubling_time: Optional[float]


class LeslieMatrix:
    """
    Leslie matrix model for age-structured population dynamics.
    
    This class constructs and analyzes Leslie matrices for mosquito populations
    with discrete life stages (egg, larva, pupa, adult).
    
    The matrix structure for 4 stages:
        [F₁  F₂  F₃  F₄]     [eggs_from_eggs    eggs_from_larvae  ...]
        [P₁  0   0   0 ]  =  [larvae_survival   0                 ...]
        [0   P₂  0   0 ]     [0                 pupae_survival    ...]
        [0   0   P₃  0 ]     [0                 0                 ...]
    
    Attributes:
        matrix: NumPy array representing the Leslie matrix
        n_stages: Number of life stages
        stage_names: Names of life stages
    """
    
    def __init__(
        self,
        fecundity: List[float],
        survival: List[float],
        stage_names: Optional[List[str]] = None,
        adult_survival: float = 0.0
    ):
        """
        Initialize Leslie matrix with fecundity and survival rates.
        
        Args:
            fecundity: Fecundity rates for each stage [F₁, F₂, ..., Fₙ]
                      Typically only adults reproduce, so F₁=F₂=F₃=0, F₄>0
            survival: Survival rates for transition to next stage [P₁, P₂, ..., Pₙ₋₁]
                     Length should be n_stages - 1
            stage_names: Optional names for stages (e.g., ['egg', 'larva', 'pupa', 'adult'])
            adult_survival: Daily survival rate for adults (stays in adult stage).
                           This is placed on the diagonal of the last row.
                           For mosquitoes, typically 0.90-0.95.
        
        Raises:
            ValueError: If dimensions are inconsistent
        
        Example:
            >>> fecundity = [0, 0, 0, 100]  # Only adults reproduce
            >>> survival = [0.7, 0.8, 0.9]  # Egg->larva, larva->pupa, pupa->adult
            >>> L = LeslieMatrix(fecundity, survival, adult_survival=0.95)
            >>> L.matrix.shape
            (4, 4)
        """
        self.n_stages = len(fecundity)
        
        if len(survival) != self.n_stages - 1:
            raise ValueError(
                f"Survival rates length ({len(survival)}) must be "
                f"n_stages - 1 ({self.n_stages - 1})"
            )
        
        self.stage_names = stage_names or [f"Stage_{i}" for i in range(self.n_stages)]
        self.adult_survival = adult_survival
        
        if len(self.stage_names) != self.n_stages:
            raise ValueError(
                f"Stage names length ({len(self.stage_names)}) must match "
                f"n_stages ({self.n_stages})"
            )
        
        # Construct Leslie matrix
        self.matrix = np.zeros((self.n_stages, self.n_stages))
        
        # First row: fecundity
        self.matrix[0, :] = fecundity
        
        # Subdiagonal: survival rates (transition to next stage)
        for i in range(self.n_stages - 1):
            self.matrix[i + 1, i] = survival[i]
        
        # Diagonal element for adult survival (adults that survive stay as adults)
        # This is crucial for realistic population dynamics!
        # Without this, adults die immediately after reproducing once.
        if adult_survival > 0:
            self.matrix[self.n_stages - 1, self.n_stages - 1] = adult_survival
    
    def update_survival_rates(self, survival: List[float]) -> None:
        """
        Update survival rates in the Leslie matrix dynamically.
        
        Modifies the subdiagonal of the matrix to reflect changing environmental
        conditions such as temperature and humidity effects on survival.
        
        Args:
            survival: Updated survival rates [P₁, P₂, ..., Pₙ₋₁]
                     Must be in range [0, 1]
        
        Raises:
            ValueError: If dimensions mismatch or values out of range
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> L.update_survival_rates([0.75, 0.85, 0.92])
            >>> L.matrix[1, 0]
            0.75
        """
        if len(survival) != self.n_stages - 1:
            raise ValueError(
                f"Survival rates length ({len(survival)}) must be "
                f"n_stages - 1 ({self.n_stages - 1})"
            )
        
        # Validar que estén en rango [0, 1]
        for i, rate in enumerate(survival):
            if not (0 <= rate <= 1):
                raise ValueError(
                    f"Survival rate {i} is out of range [0, 1]: {rate}"
                )
        
        # Actualizar subdiagonal
        for i in range(self.n_stages - 1):
            self.matrix[i + 1, i] = survival[i]
    
    def update_fecundity(self, fecundity: List[float]) -> None:
        """
        Update fecundity rates in the Leslie matrix dynamically.
        
        Modifies the first row of the matrix to reflect changes in reproductive
        capacity due to factors such as density dependence, nutrition, or adult age.
        
        Args:
            fecundity: Updated fecundity rates [F₁, F₂, ..., Fₙ]
                      Must be >= 0
        
        Raises:
            ValueError: If dimensions mismatch or negative values provided
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> L.update_fecundity([0, 0, 0, 70])
            >>> L.matrix[0, 3]
            70.0
        """
        if len(fecundity) != self.n_stages:
            raise ValueError(
                f"Fecundity length ({len(fecundity)}) must match "
                f"n_stages ({self.n_stages})"
            )
        
        # Validar que sean no negativos
        for i, rate in enumerate(fecundity):
            if rate < 0:
                raise ValueError(
                    f"Fecundity rate {i} must be non-negative: {rate}"
                )
        
        # Actualizar primera fila
        self.matrix[0, :] = fecundity
    
    def get_survival_rates(self) -> List[float]:
        """
        Retrieve current survival rates from the matrix.
        
        Returns:
            List of survival rates [P₁, P₂, ..., Pₙ₋₁]
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> L.get_survival_rates()
            [0.7, 0.8, 0.9]
        """
        return [self.matrix[i + 1, i] for i in range(self.n_stages - 1)]
    
    def get_fecundity_rates(self) -> List[float]:
        """
        Retrieve current fecundity rates from the matrix.
        
        Returns:
            List of fecundity rates [F₁, F₂, ..., Fₙ]
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> L.get_fecundity_rates()
            [0, 0, 0, 100]
        """
        return list(self.matrix[0, :])
    
    def project(
        self,
        initial_population: np.ndarray,
        timesteps: int
    ) -> np.ndarray:
        """
        Project population forward in time.
        
        Args:
            initial_population: Initial population vector [n₁, n₂, ..., nₖ]
            timesteps: Number of time steps to project
        
        Returns:
            Array of shape (timesteps + 1, n_stages) with population trajectories
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> initial = np.array([1000, 500, 200, 100])
            >>> trajectory = L.project(initial, timesteps=10)
            >>> trajectory.shape
            (11, 4)
        """
        if len(initial_population) != self.n_stages:
            raise ValueError(
                f"Initial population length ({len(initial_population)}) must match "
                f"n_stages ({self.n_stages})"
            )
        
        # Initialize trajectory array
        trajectory = np.zeros((timesteps + 1, self.n_stages))
        trajectory[0] = initial_population
        
        # Project forward
        for t in range(timesteps):
            trajectory[t + 1] = self.matrix @ trajectory[t]
        
        return trajectory
    
    def eigenanalysis(self) -> LeslieMatrixResult:
        """
        Perform eigenanalysis of the Leslie matrix.
        
        Computes:
        - Dominant eigenvalue λ₁ (population growth rate)
        - Right eigenvector w (stable age distribution)
        - Left eigenvector v (reproductive value)
        - Generation time T
        - Intrinsic rate of increase r = ln(λ₁)
        
        Returns:
            LeslieMatrixResult with all demographic parameters
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> result = L.eigenanalysis()
            >>> result.lambda_1 > 0
            True
            >>> result.r == np.log(result.lambda_1)
            True
        """
        # Compute eigenvalues and eigenvectors
        eig_result = eig(self.matrix)
        eigenvalues: np.ndarray = eig_result[0]  # type: ignore
        eigenvectors: np.ndarray = eig_result[1]  # type: ignore
        
        # Find dominant eigenvalue (largest magnitude)
        idx = np.argmax(np.abs(eigenvalues))
        lambda_1 = np.real(eigenvalues[idx])
        
        # Right eigenvector (stable age distribution)
        w = np.real(eigenvectors[:, idx])
        w = w / w.sum()  # Normalize to sum to 1
        
        # Left eigenvector (reproductive value)
        # L^T * v = λ * v
        eig_left_result = eig(self.matrix.T)
        eigenvalues_left: np.ndarray = eig_left_result[0]  # type: ignore
        eigenvectors_left: np.ndarray = eig_left_result[1]  # type: ignore
        idx_left = np.argmax(np.abs(eigenvalues_left))
        v = np.real(eigenvectors_left[:, idx_left])
        v = v / v[0]  # Normalize so that v[0] = 1
        
        # Generation time (weighted mean age of reproduction)
        T = self._compute_generation_time(w)
        
        # Intrinsic rate of increase
        r = np.log(lambda_1) if lambda_1 > 0 else -np.inf
        
        # Doubling time
        doubling_time = np.log(2) / r if r > 0 else None
        
        return LeslieMatrixResult(
            lambda_1=lambda_1,
            stable_age_dist=w,
            reproductive_value=v,
            generation_time=T,
            r=r,
            doubling_time=doubling_time
        )
    
    def _compute_generation_time(self, stable_age_dist: np.ndarray) -> float:
        """
        Compute mean generation time.
        
        T = Σ(x * l(x) * m(x)) / Σ(l(x) * m(x))
        
        Where:
            x: age class
            l(x): survivorship to age x
            m(x): fecundity at age x
        
        Args:
            stable_age_dist: Stable age distribution
        
        Returns:
            Mean generation time
        """
        fecundity = self.matrix[0, :]
        
        # Compute survivorship l(x)
        survivorship = np.ones(self.n_stages)
        for i in range(1, self.n_stages):
            # Cumulative product of survival rates
            survivorship[i] = survivorship[i-1] * self.matrix[i, i-1]
        
        # Weighted mean
        numerator = np.sum(np.arange(self.n_stages) * survivorship * fecundity)
        denominator = np.sum(survivorship * fecundity)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def net_reproductive_rate(self) -> float:
        """
        Compute net reproductive rate R₀.
        
        R₀ = Σ l(x) * m(x)
        
        This is the expected number of offspring produced by an individual
        over its lifetime in the absence of density dependence.
        
        Returns:
            Net reproductive rate R₀
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> R0 = L.net_reproductive_rate()
            >>> R0 > 0
            True
        """
        fecundity = self.matrix[0, :]
        
        # Compute survivorship
        survivorship = np.ones(self.n_stages)
        for i in range(1, self.n_stages):
            survivorship[i] = survivorship[i-1] * self.matrix[i, i-1]
        
        R0 = np.sum(survivorship * fecundity)
        return R0
    
    def sensitivity_analysis(self) -> Dict[str, np.ndarray]:
        """
        Compute sensitivity of λ₁ to changes in matrix elements.
        
        Sensitivity: s_ij = (∂λ₁/∂a_ij)
        
        Formula: s_ij = (v_i * w_j) / <v, w>
        Where v and w are left and right eigenvectors.
        
        Returns:
            Dictionary with:
                - 'sensitivity': Sensitivity matrix
                - 'elasticity': Elasticity matrix (proportional sensitivity)
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> sens = L.sensitivity_analysis()
            >>> 'sensitivity' in sens and 'elasticity' in sens
            True
        """
        result = self.eigenanalysis()
        lambda_1 = result.lambda_1
        w = result.stable_age_dist
        v = result.reproductive_value
        
        # Sensitivity matrix: s_ij = v_i * w_j / <v,w>
        scalar_product = np.dot(v, w)
        sensitivity = np.outer(v, w) / scalar_product
        
        # Elasticity matrix: e_ij = (a_ij / λ₁) * s_ij
        elasticity = (self.matrix / lambda_1) * sensitivity
        
        return {
            'sensitivity': sensitivity,
            'elasticity': elasticity
        }
    
    def is_viable(self) -> bool:
        """
        Check if population is viable (λ₁ > 1).
        
        Returns:
            True if population is growing or stable (λ₁ >= 1)
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
            >>> L.is_viable()
            True
        """
        result = self.eigenanalysis()
        return result.lambda_1 >= 1.0
    
    def get_stable_distribution(self) -> Dict[str, float]:
        """
        Get stable age distribution as dictionary.
        
        Returns:
            Dictionary mapping stage names to proportions
        
        Example:
            >>> L = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9],
            ...                  stage_names=['egg', 'larva', 'pupa', 'adult'])
            >>> dist = L.get_stable_distribution()
            >>> 'adult' in dist
            True
        """
        result = self.eigenanalysis()
        return dict(zip(self.stage_names, result.stable_age_dist))
    
    def __repr__(self) -> str:
        """String representation of the Leslie matrix."""
        return (
            f"LeslieMatrix(n_stages={self.n_stages}, "
            f"stages={self.stage_names}, "
            f"λ₁={self.eigenanalysis().lambda_1:.3f})"
        )
    
    def to_dict(self) -> Dict:
        """
        Convert Leslie matrix and analysis results to dictionary.
        
        Returns:
            Dictionary with matrix, eigenanalysis, and vital rates
        """
        result = self.eigenanalysis()
        
        return {
            'matrix': self.matrix.tolist(),
            'stages': self.stage_names,
            'n_stages': self.n_stages,
            'lambda_1': float(result.lambda_1),
            'r': float(result.r),
            'generation_time': float(result.generation_time),
            'net_reproductive_rate': float(self.net_reproductive_rate()),
            'stable_age_distribution': dict(zip(self.stage_names, result.stable_age_dist)),
            'reproductive_value': dict(zip(self.stage_names, result.reproductive_value)),
            'is_viable': self.is_viable()
        }


def create_leslie_matrix_from_config(
    species_config: SpeciesConfig,
    temperature: float = 27.0
) -> LeslieMatrix:
    """
    Create Leslie matrix from species configuration.
    
    This function translates mosquito life history parameters from the
    configuration into Leslie matrix format. It accounts for:
    - Stage-specific survival rates
    - Adult fecundity (eggs per female per day)
    - Development times (converted to daily transition rates)
    
    Args:
        species_config: Species configuration from ConfigManager
        temperature: Current temperature (°C) for temperature-dependent rates
    
    Returns:
        Configured LeslieMatrix instance
    
    Example:
        >>> from infrastructure.config import load_default_config
        >>> config = load_default_config()
        >>> aegypti_config = config.get_species('aedes_aegypti')
        >>> L = create_leslie_matrix_from_config(aegypti_config)
        >>> L.n_stages
        4
    """
    # Extract life stage parameters
    life_stages = species_config.life_stages
    reproduction = species_config.reproduction
    
    # Define stage names
    stage_names = ['egg', 'larva', 'pupa', 'adult']
    
    # Extract specific stages from configuration
    egg_stage = life_stages.get('egg')
    pupa_stage = life_stages.get('pupa')
    
    # Aggregate larval stages (L1, L2, L3, L4)
    larval_stages = [stage for key, stage in life_stages.items() if 'larva' in key.lower()]
    
    if not egg_stage or not pupa_stage or not larval_stages:
        raise ValueError("Missing required life stages in configuration")
    
    # Compute daily survival rates for each stage
    # Use survival_to_next if available, otherwise survival_daily
    egg_survival = egg_stage.survival_to_next if egg_stage.survival_to_next else 0.8
    
    # Average larval stages
    larva_survival = np.mean([
        stage.survival_to_next if stage.survival_to_next else 0.8
        for stage in larval_stages
    ])
    # Total larval development days (sum of all larval stages, not average)
    larva_dev_days_total = sum([
        (stage.duration_min + stage.duration_max) / 2
        for stage in larval_stages
    ])
    
    pupa_survival = pupa_stage.survival_to_next if pupa_stage.survival_to_next else 0.9
    
    # Development days
    egg_dev_days = (egg_stage.duration_min + egg_stage.duration_max) / 2
    pupa_dev_days = (pupa_stage.duration_min + pupa_stage.duration_max) / 2
    
    # Daily transition probability calculation:
    # For a Leslie matrix, P_i represents the fraction that transitions to next stage each day.
    # 
    # Mathematical interpretation:
    # - survival_to_next = probability of surviving the ENTIRE stage
    # - dev_days = expected duration of stage
    # 
    # If survival_to_next = 0.80 over 4 days, the daily survival is 0.80^(1/4) = 0.946
    # But we need the transition probability which combines:
    # 1. Daily survival: S_daily = survival_to_next^(1/dev_days)
    # 2. Daily transition rate: ~1/dev_days
    # 
    # The effective daily transition probability is:
    # P = S_daily * (1/dev_days) ≈ survival_to_next^(1/dev_days) / dev_days
    #
    # However, for stable populations, we need to use the simpler formula that ensures
    # biological plausibility: the survival_to_next is the probability of making it through.
    # 
    # CORRECTED FORMULA: Use the total stage survival raised to 1/days power to get 
    # daily survival, then multiply by transition probability (1/days).
    # This gives approximately the same flow but handles longer stages better.
    
    def compute_daily_transition(survival_to_next: float, dev_days: float) -> float:
        """
        Compute daily transition probability for Leslie matrix.
        
        For biological realism, we interpret this as:
        - An individual spends on average 'dev_days' in the stage
        - Each day has survival probability S_daily = survival^(1/dev_days)
        - Transition probability = S_daily * (1/dev_days)
        
        This ensures longer-lived stages don't penalize growth rate excessively.
        """
        # Daily survival within the stage
        daily_survival = survival_to_next ** (1.0 / dev_days)
        # Probability of transitioning on any given day
        transition_prob = 1.0 / dev_days
        # Combined: survive AND transition
        return daily_survival * transition_prob
    
    P_egg = compute_daily_transition(egg_survival, egg_dev_days)
    P_larva = compute_daily_transition(larva_survival, larva_dev_days_total)
    P_pupa = compute_daily_transition(pupa_survival, pupa_dev_days)
    
    survival = [P_egg, P_larva, P_pupa]
    
    # Get adult survival (daily)
    adult_stages = [stage for key, stage in life_stages.items() if 'adult' in key.lower()]
    if adult_stages:
        adult_survival_daily = adult_stages[0].survival_daily if adult_stages[0].survival_daily else 0.95
    else:
        adult_survival_daily = 0.95
    
    # Compute fecundity (only adults reproduce)
    # Assume 50% of adults are female
    female_ratio = 0.5
    eggs_per_batch = (reproduction.eggs_per_batch_min + reproduction.eggs_per_batch_max) / 2
    
    # Daily fecundity = eggs_per_batch * oviposition_events * female_ratio * adult_survival
    # Distributed over adult lifespan (use average adult duration)
    if adult_stages:
        adult_lifespan = (adult_stages[0].duration_min + adult_stages[0].duration_max) / 2
    else:
        adult_lifespan = 22.0  # Default average lifespan
    
    total_eggs = eggs_per_batch * reproduction.oviposition_events
    daily_fecundity = (total_eggs * female_ratio * adult_survival_daily) / adult_lifespan
    
    # Only adults reproduce (last stage)
    fecundity = [0.0, 0.0, 0.0, daily_fecundity]
    
    return LeslieMatrix(
        fecundity=fecundity,
        survival=survival,
        stage_names=stage_names,
        adult_survival=adult_survival_daily  # CRITICAL: Include adult daily survival!
    )


def compare_leslie_matrices(
    matrix1: LeslieMatrix,
    matrix2: LeslieMatrix,
    name1: str = "Matrix 1",
    name2: str = "Matrix 2"
) -> Dict[str, Any]:
    """
    Compare two Leslie matrices and their demographic properties.
    
    Args:
        matrix1: First Leslie matrix
        matrix2: Second Leslie matrix
        name1: Name for first matrix
        name2: Name for second matrix
    
    Returns:
        Dictionary with comparison results
    
    Example:
        >>> L1 = LeslieMatrix([0, 0, 0, 100], [0.7, 0.8, 0.9])
        >>> L2 = LeslieMatrix([0, 0, 0, 80], [0.6, 0.7, 0.8])
        >>> comparison = compare_leslie_matrices(L1, L2, "Species A", "Species B")
        >>> 'lambda_ratio' in comparison
        True
    """
    result1 = matrix1.eigenanalysis()
    result2 = matrix2.eigenanalysis()
    
    return {
        'names': (name1, name2),
        'lambda_1': (result1.lambda_1, result2.lambda_1),
        'lambda_ratio': result1.lambda_1 / result2.lambda_1 if result2.lambda_1 != 0 else np.inf,
        'r': (result1.r, result2.r),
        'r_difference': result1.r - result2.r,
        'generation_time': (result1.generation_time, result2.generation_time),
        'net_reproductive_rate': (matrix1.net_reproductive_rate(), matrix2.net_reproductive_rate()),
        'viability': (matrix1.is_viable(), matrix2.is_viable())
    }
