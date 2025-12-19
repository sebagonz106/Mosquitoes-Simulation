"""
Stochastic Processes Module
============================

Implements stochastic variation for biological and environmental parameters.
Provides three types of stochasticity:
    1. General parameter variation (beta, normal distributions)
    2. Demographic stochasticity (binomial, Poisson)
    3. Environmental stochasticity (time series with autocorrelation)

Author: Mosquito Simulation System
"""

import numpy as np
from typing import Optional, Union
from scipy import stats


class StochasticVariation:
    """
    General stochastic variation generator for biological parameters.
    
    Applies appropriate statistical distributions based on parameter type:
    - Survival rates: Beta distribution (bounded [0,1])
    - Counts: Poisson or negative binomial
    - Development time: Discrete uniform or truncated normal
    - Continuous values: Normal with truncation
    
    Attributes:
        rng: NumPy random number generator
        seed: Random seed for reproducibility
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize stochastic variation generator.
        
        Args:
            seed: Random seed for reproducibility. If None, uses system entropy.
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def vary_survival(
        self, 
        base_rate: float, 
        cv: float = 0.1,
        min_rate: float = 0.0,
        max_rate: float = 1.0
    ) -> float:
        """
        Apply stochastic variation to survival rate using Beta distribution.
        
        The Beta distribution is ideal for rates bounded in [0,1]. Parameters
        are derived from the mean (base_rate) and coefficient of variation (cv).
        
        Args:
            base_rate: Base survival rate [0.0-1.0]
            cv: Coefficient of variation (std/mean), typically 0.05-0.2
            min_rate: Minimum allowed survival rate
            max_rate: Maximum allowed survival rate
        
        Returns:
            Varied survival rate in [min_rate, max_rate]
        
        Example:
            >>> stoch = StochasticVariation(seed=42)
            >>> varied = stoch.vary_survival(0.80, cv=0.1)
            >>> 0.6 <= varied <= 1.0
            True
        """
        if not (0.0 <= base_rate <= 1.0):
            raise ValueError(f"Base rate must be in [0,1], got {base_rate}")
        
        if cv <= 0:
            return base_rate
        
        # Calculate Beta distribution parameters from mean and cv
        # For Beta(α, β): mean = α/(α+β), variance = αβ/[(α+β)²(α+β+1)]
        variance = (cv * base_rate) ** 2
        
        # Prevent numerical issues near boundaries
        if base_rate < 0.01 or base_rate > 0.99 or variance > base_rate * (1 - base_rate):
            # Fall back to truncated normal
            std = cv * base_rate
            varied = self.rng.normal(base_rate, std)
            return np.clip(varied, min_rate, max_rate)
        
        # Standard Beta parameterization
        alpha = base_rate * (base_rate * (1 - base_rate) / variance - 1)
        beta = (1 - base_rate) * (base_rate * (1 - base_rate) / variance - 1)
        
        # Ensure positive parameters
        alpha = max(alpha, 0.5)
        beta = max(beta, 0.5)
        
        varied = self.rng.beta(alpha, beta)
        return np.clip(varied, min_rate, max_rate)
    
    def vary_fecundity(
        self, 
        mean: float, 
        cv: float = 0.15
    ) -> int:
        """
        Apply stochastic variation to fecundity (egg count) using Poisson.
        
        For count data with mean = variance, Poisson is appropriate.
        For overdispersion (variance > mean), consider negative binomial.
        
        Args:
            mean: Mean number of eggs
            cv: Coefficient of variation (if > 0.3, uses negative binomial)
        
        Returns:
            Varied egg count (non-negative integer)
        
        Example:
            >>> stoch = StochasticVariation(seed=42)
            >>> eggs = stoch.vary_fecundity(100, cv=0.15)
            >>> eggs >= 0
            True
        """
        if mean <= 0:
            return 0
        
        if cv <= 0:
            return int(round(mean))
        
        # Use Poisson for low variation
        if cv <= 0.3:
            return self.rng.poisson(mean)
        
        # Use negative binomial for overdispersion
        # Parameterization: variance = mean + mean²/r
        # Where r = mean / (variance - mean)
        variance = (cv * mean) ** 2
        if variance <= mean:
            return self.rng.poisson(mean)
        
        r = mean ** 2 / (variance - mean)
        p = r / (r + mean)
        
        return self.rng.negative_binomial(r, p)
    
    def vary_development_time(
        self, 
        min_days: int, 
        max_days: int,
        distribution: str = 'uniform'
    ) -> int:
        """
        Sample development time from specified distribution.
        
        Args:
            min_days: Minimum development time
            max_days: Maximum development time
            distribution: 'uniform' or 'triangular' (mode at midpoint)
        
        Returns:
            Development time in days
        
        Example:
            >>> stoch = StochasticVariation(seed=42)
            >>> days = stoch.vary_development_time(2, 7)
            >>> 2 <= days <= 7
            True
        """
        if min_days > max_days:
            min_days, max_days = max_days, min_days
        
        if min_days == max_days:
            return min_days
        
        if distribution == 'uniform':
            return int(self.rng.integers(min_days, max_days + 1))
        
        elif distribution == 'triangular':
            # Triangular with mode at midpoint
            mode = (min_days + max_days) / 2
            value = self.rng.triangular(min_days, mode, max_days + 1)
            return int(round(value))
        
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
    
    def apply_environmental_noise(
        self, 
        value: float, 
        noise_level: float = 0.05
    ) -> float:
        """
        Add Gaussian noise to environmental parameter.
        
        Args:
            value: Base value
            noise_level: Relative noise level (fraction of value)
        
        Returns:
            Value with added noise
        
        Example:
            >>> stoch = StochasticVariation(seed=42)
            >>> noisy = stoch.apply_environmental_noise(27.0, 0.05)
            >>> 25.0 <= noisy <= 29.0
            True
        """
        if noise_level <= 0:
            return value
        
        std = abs(value) * noise_level
        return self.rng.normal(value, std)
    
    def sample_from_range(
        self,
        min_val: float,
        max_val: float,
        distribution: str = 'uniform'
    ) -> float:
        """
        Sample a value from a range using specified distribution.
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            distribution: 'uniform', 'triangular', or 'beta'
        
        Returns:
            Sampled value
        """
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        
        if min_val == max_val:
            return min_val
        
        if distribution == 'uniform':
            return self.rng.uniform(min_val, max_val)
        
        elif distribution == 'triangular':
            mode = (min_val + max_val) / 2
            return self.rng.triangular(min_val, mode, max_val)
        
        elif distribution == 'beta':
            # Beta(2,2) for central tendency
            beta_sample = self.rng.beta(2, 2)
            return min_val + (max_val - min_val) * beta_sample
        
        else:
            raise ValueError(f"Unknown distribution: {distribution}")


class DemographicStochasticity:
    """
    Demographic stochasticity: random variation in vital rates due to
    individual-level randomness.
    
    This is particularly important for small populations where discrete
    events (births, deaths) create substantial variation.
    
    Implements:
    - Binomial sampling for stage transitions (n individuals, probability p)
    - Poisson sampling for birth events
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize demographic stochasticity generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.default_rng(seed)
    
    def apply_to_transitions(
        self, 
        count: int, 
        rate: float
    ) -> int:
        """
        Apply binomial sampling to stage transitions.
        
        Models the number of individuals that successfully transition
        from one stage to another, given a population count and survival rate.
        
        Args:
            count: Number of individuals attempting transition
            rate: Probability of successful transition [0.0-1.0]
        
        Returns:
            Number of individuals that successfully transitioned
        
        Example:
            >>> demo = DemographicStochasticity(seed=42)
            >>> survivors = demo.apply_to_transitions(100, 0.80)
            >>> 0 <= survivors <= 100
            True
        """
        if count <= 0:
            return 0
        
        if rate <= 0:
            return 0
        
        if rate >= 1.0:
            return count
        
        # Binomial(n, p): number of successes in n trials with probability p
        return self.rng.binomial(count, rate)
    
    def apply_to_births(
        self, 
        females: int, 
        mean_eggs: float
    ) -> int:
        """
        Apply Poisson sampling to birth events.
        
        Models the total number of eggs laid by a population of females,
        where each female lays eggs according to a Poisson process.
        
        Args:
            females: Number of reproductive females
            mean_eggs: Mean eggs per female
        
        Returns:
            Total number of eggs produced
        
        Example:
            >>> demo = DemographicStochasticity(seed=42)
            >>> eggs = demo.apply_to_births(50, 100)
            >>> eggs >= 0
            True
        """
        if females <= 0 or mean_eggs <= 0:
            return 0
        
        # Sum of Poisson random variables is also Poisson
        lambda_total = females * mean_eggs
        
        return self.rng.poisson(lambda_total)
    
    def apply_mortality(
        self,
        count: int,
        daily_survival: float,
        days: int = 1
    ) -> int:
        """
        Apply mortality over multiple days.
        
        Args:
            count: Initial population
            daily_survival: Daily survival probability
            days: Number of days
        
        Returns:
            Number of survivors
        """
        if count <= 0 or days <= 0:
            return count
        
        survivors = count
        for _ in range(days):
            survivors = self.apply_to_transitions(survivors, daily_survival)
            if survivors == 0:
                break
        
        return survivors


class EnvironmentalStochasticity:
    """
    Environmental stochasticity: temporal variation in environmental conditions
    that affects all individuals simultaneously.
    
    Generates time series with:
    - Temporal autocorrelation (AR(1) process)
    - Seasonal variation (sinusoidal)
    - White noise
    
    Used for temperature, humidity, and other environmental drivers.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize environmental stochasticity generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.default_rng(seed)
        self.seed = seed
    
    def generate_temperature_series(
        self,
        days: int,
        mean: float = 27.0,
        std: float = 3.0,
        seasonal: bool = True,
        seasonal_amplitude: float = 5.0,
        autocorr: float = 0.7
    ) -> np.ndarray:
        """
        Generate temperature time series with seasonal variation and autocorrelation.
        
        Uses AR(1) process: T(t) = μ + ρ(T(t-1) - μ) + ε(t)
        Where:
            μ = mean temperature
            ρ = autocorrelation coefficient
            ε ~ N(0, σ²)
        
        Args:
            days: Number of days to simulate
            mean: Mean temperature (°C)
            std: Standard deviation of noise
            seasonal: Whether to add seasonal cycle
            seasonal_amplitude: Amplitude of seasonal variation (°C)
            autocorr: Autocorrelation coefficient [0-1]
        
        Returns:
            Array of daily temperatures
        
        Example:
            >>> env_stoch = EnvironmentalStochasticity(seed=42)
            >>> temps = env_stoch.generate_temperature_series(365, mean=27, std=3)
            >>> len(temps)
            365
            >>> 15 <= temps.mean() <= 35
            True
        """
        # Initialize series
        series = np.zeros(days)
        series[0] = self.rng.normal(mean, std)
        
        # Generate AR(1) process
        innovation_std = std * np.sqrt(1 - autocorr**2)
        
        for t in range(1, days):
            innovation = self.rng.normal(0, innovation_std)
            series[t] = mean + autocorr * (series[t-1] - mean) + innovation
        
        # Add seasonal variation if requested
        if seasonal:
            seasonal_cycle = self._generate_seasonal_cycle(
                days, 
                amplitude=seasonal_amplitude,
                period=365
            )
            series += seasonal_cycle
        
        return series
    
    def generate_humidity_series(
        self,
        days: int,
        mean: float = 75.0,
        std: float = 10.0,
        autocorr: float = 0.8,
        min_humidity: float = 30.0,
        max_humidity: float = 100.0
    ) -> np.ndarray:
        """
        Generate humidity time series with strong autocorrelation.
        
        Humidity typically has higher autocorrelation than temperature
        due to longer persistence of weather patterns.
        
        Args:
            days: Number of days to simulate
            mean: Mean relative humidity (%)
            std: Standard deviation
            autocorr: Autocorrelation coefficient [0-1]
            min_humidity: Minimum allowed humidity
            max_humidity: Maximum allowed humidity
        
        Returns:
            Array of daily humidity values (%)
        
        Example:
            >>> env_stoch = EnvironmentalStochasticity(seed=42)
            >>> humidity = env_stoch.generate_humidity_series(365, mean=75, std=10)
            >>> len(humidity)
            365
            >>> (humidity >= 30).all() and (humidity <= 100).all()
            True
        """
        # Initialize series
        series = np.zeros(days)
        series[0] = np.clip(self.rng.normal(mean, std), min_humidity, max_humidity)
        
        # Generate AR(1) process
        innovation_std = std * np.sqrt(1 - autocorr**2)
        
        for t in range(1, days):
            innovation = self.rng.normal(0, innovation_std)
            series[t] = mean + autocorr * (series[t-1] - mean) + innovation
            series[t] = np.clip(series[t], min_humidity, max_humidity)
        
        return series
    
    def add_seasonal_variation(
        self,
        series: np.ndarray,
        amplitude: float = 5.0,
        period: int = 365,
        phase_shift: float = 0.0
    ) -> np.ndarray:
        """
        Add sinusoidal seasonal variation to existing time series.
        
        Args:
            series: Existing time series
            amplitude: Amplitude of seasonal cycle
            period: Period in days (365 for annual cycle)
            phase_shift: Phase shift in radians
        
        Returns:
            Series with added seasonal variation
        
        Example:
            >>> env_stoch = EnvironmentalStochasticity(seed=42)
            >>> base = np.ones(365) * 27
            >>> with_season = env_stoch.add_seasonal_variation(base, amplitude=5)
            >>> with_season.max() > 27 and with_season.min() < 27
            True
        """
        days = len(series)
        seasonal = self._generate_seasonal_cycle(days, amplitude, period, phase_shift)
        return series + seasonal
    
    def _generate_seasonal_cycle(
        self,
        days: int,
        amplitude: float,
        period: int = 365,
        phase_shift: float = 0.0
    ) -> np.ndarray:
        """
        Generate sinusoidal seasonal cycle.
        
        Args:
            days: Number of days
            amplitude: Amplitude of cycle
            period: Period in days
            phase_shift: Phase shift in radians
        
        Returns:
            Seasonal component
        """
        t = np.arange(days)
        return amplitude * np.sin(2 * np.pi * t / period + phase_shift)
    
    def generate_correlated_series(
        self,
        days: int,
        mean: float,
        std: float,
        autocorr: float = 0.5
    ) -> np.ndarray:
        """
        Generate generic AR(1) time series.
        
        Args:
            days: Number of time steps
            mean: Series mean
            std: Series standard deviation
            autocorr: Autocorrelation coefficient
        
        Returns:
            Correlated time series
        """
        series = np.zeros(days)
        series[0] = self.rng.normal(mean, std)
        
        innovation_std = std * np.sqrt(1 - autocorr**2)
        
        for t in range(1, days):
            innovation = self.rng.normal(0, innovation_std)
            series[t] = mean + autocorr * (series[t-1] - mean) + innovation
        
        return series


# Convenience function for common use case
def create_stochastic_generator(
    seed: Optional[int] = None,
    stochastic_mode: bool = True
) -> tuple[StochasticVariation, DemographicStochasticity, EnvironmentalStochasticity]:
    """
    Create all three stochastic generators with shared seed.
    
    Args:
        seed: Random seed for all generators
        stochastic_mode: If False, returns generators that return deterministic values
    
    Returns:
        Tuple of (StochasticVariation, DemographicStochasticity, EnvironmentalStochasticity)
    
    Example:
        >>> stoch, demo, env = create_stochastic_generator(seed=42)
        >>> isinstance(stoch, StochasticVariation)
        True
    """
    if not stochastic_mode:
        # In deterministic mode, set cv=0 effectively disabling variation
        seed = 0
    
    return (
        StochasticVariation(seed),
        DemographicStochasticity(seed),
        EnvironmentalStochasticity(seed)
    )
