"""
Mosquito Entity Module
======================

Represents individual mosquitoes in the simulation.

Author: Mosquito Simulation System
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class LifeStage(Enum):
    """Enumeration of mosquito life stages."""
    EGG = "egg"
    LARVA_L1 = "larva_L1"
    LARVA_L2 = "larva_L2"
    LARVA_L3 = "larva_L3"
    LARVA_L4 = "larva_L4"
    PUPA = "pupa"
    ADULT = "adult"
    DEAD = "dead"
    
    def is_aquatic(self) -> bool:
        """Check if stage is aquatic."""
        return self in {
            LifeStage.EGG,
            LifeStage.LARVA_L1,
            LifeStage.LARVA_L2,
            LifeStage.LARVA_L3,
            LifeStage.LARVA_L4,
            LifeStage.PUPA
        }
    
    def is_larval(self) -> bool:
        """Check if stage is larval."""
        return self in {
            LifeStage.LARVA_L1,
            LifeStage.LARVA_L2,
            LifeStage.LARVA_L3,
            LifeStage.LARVA_L4
        }
    
    def is_adult(self) -> bool:
        """Check if stage is adult."""
        return self == LifeStage.ADULT
    
    def next_stage(self) -> Optional['LifeStage']:
        """Get the next developmental stage."""
        stage_order = [
            LifeStage.EGG,
            LifeStage.LARVA_L1,
            LifeStage.LARVA_L2,
            LifeStage.LARVA_L3,
            LifeStage.LARVA_L4,
            LifeStage.PUPA,
            LifeStage.ADULT,
            LifeStage.DEAD
        ]
        
        try:
            current_idx = stage_order.index(self)
            if current_idx < len(stage_order) - 1:
                return stage_order[current_idx + 1]
        except ValueError:
            pass
        
        return None


@dataclass
class Mosquito:
    """
    Represents an individual mosquito.
    
    For population-level simulations, this entity may not be instantiated
    frequently. However, it provides a clear domain representation for
    individual-based scenarios or tracking specific mosquitoes.
    
    Attributes:
        mosquito_id: Unique identifier
        species_id: Species this mosquito belongs to
        life_stage: Current life stage
        age_days: Age in days
        age_in_stage: Days spent in current stage
        is_alive: Whether mosquito is alive
        birth_day: Simulation day when born
        death_day: Simulation day when died (if applicable)
    """
    
    mosquito_id: str
    species_id: str
    life_stage: LifeStage
    age_days: int = 0
    age_in_stage: int = 0
    is_alive: bool = True
    birth_day: int = 0
    death_day: Optional[int] = None
    
    def advance_age(self, days: int = 1) -> None:
        """
        Advance age by specified days.
        
        Args:
            days: Number of days to advance
        """
        if self.is_alive:
            self.age_days += days
            self.age_in_stage += days
    
    def transition_to_stage(self, new_stage: LifeStage) -> None:
        """
        Transition to a new life stage.
        
        Args:
            new_stage: New life stage to transition to
        """
        if self.is_alive:
            self.life_stage = new_stage
            self.age_in_stage = 0
            
            if new_stage == LifeStage.DEAD:
                self.is_alive = False
    
    def die(self, current_day: int) -> None:
        """
        Mark mosquito as dead.
        
        Args:
            current_day: Current simulation day
        """
        self.is_alive = False
        self.life_stage = LifeStage.DEAD
        self.death_day = current_day
    
    def is_aquatic_stage(self) -> bool:
        """Check if in aquatic life stage."""
        return self.life_stage.is_aquatic()
    
    def is_larval_stage(self) -> bool:
        """Check if in larval stage."""
        return self.life_stage.is_larval()
    
    def is_adult_stage(self) -> bool:
        """Check if in adult stage."""
        return self.life_stage.is_adult()
    
    def can_reproduce(self, min_reproductive_age: int) -> bool:
        """
        Check if mosquito can reproduce.
        
        Args:
            min_reproductive_age: Minimum age for reproduction
        
        Returns:
            True if can reproduce
        """
        return (
            self.is_alive and
            self.is_adult_stage() and
            self.age_days >= min_reproductive_age
        )
    
    def lifespan_days(self) -> int:
        """
        Get total lifespan in days.
        
        Returns:
            Days lived (current age if alive, or age at death)
        """
        if self.is_alive:
            return self.age_days
        else:
            return self.age_days if self.death_day is None else (self.death_day - self.birth_day)
    
    def __repr__(self) -> str:
        """String representation."""
        status = "alive" if self.is_alive else "dead"
        return (
            f"Mosquito(id='{self.mosquito_id}', species='{self.species_id}', "
            f"stage={self.life_stage.value}, age={self.age_days}d, {status})"
        )
    
    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.species_id} mosquito (age {self.age_days}d, {self.life_stage.value})"
