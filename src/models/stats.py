"""Life dimension stats for the character system."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math


class StatType(Enum):
    """The six core life dimensions."""
    INTELLECT = "intellect"
    VITALITY = "vitality"
    SPIRIT = "spirit"
    BONDS = "bonds"
    PROSPERITY = "prosperity"
    MASTERY = "mastery"


@dataclass
class StatDefinition:
    """Definition of a stat type with metadata."""
    type: StatType
    name: str
    icon: str
    color: str
    description: str


# Define all stats with their visual properties
STAT_DEFINITIONS: dict[StatType, StatDefinition] = {
    StatType.INTELLECT: StatDefinition(
        type=StatType.INTELLECT,
        name="Intellect",
        icon="📚",
        color="#6366f1",  # Indigo
        description="Knowledge, learning, creativity, problem-solving"
    ),
    StatType.VITALITY: StatDefinition(
        type=StatType.VITALITY,
        name="Vitality",
        icon="💪",
        color="#ef4444",  # Red
        description="Physical health, fitness, energy, nutrition"
    ),
    StatType.SPIRIT: StatDefinition(
        type=StatType.SPIRIT,
        name="Spirit",
        icon="🧘",
        color="#a855f7",  # Purple
        description="Emotional wellbeing, mindfulness, resilience"
    ),
    StatType.BONDS: StatDefinition(
        type=StatType.BONDS,
        name="Bonds",
        icon="💝",
        color="#ec4899",  # Pink
        description="Relationships, social connections, communication"
    ),
    StatType.PROSPERITY: StatDefinition(
        type=StatType.PROSPERITY,
        name="Prosperity",
        icon="💰",
        color="#f59e0b",  # Amber
        description="Career, finances, professional growth"
    ),
    StatType.MASTERY: StatDefinition(
        type=StatType.MASTERY,
        name="Mastery",
        icon="🎯",
        color="#10b981",  # Emerald
        description="Skills, hobbies, personal projects"
    ),
}


@dataclass
class Stat:
    """A character stat representing a life dimension."""
    type: StatType
    current_xp: int = 0
    target_level: int = 10  # Desired level from assessment
    
    @property
    def definition(self) -> StatDefinition:
        """Get the stat definition."""
        return STAT_DEFINITIONS[self.type]
    
    @property
    def level(self) -> int:
        """Calculate level from XP. Each level requires more XP than the last."""
        # Level formula: XP needed = 100 * level^1.5
        # Inverse: level = (XP / 100)^(1/1.5)
        if self.current_xp <= 0:
            return 1
        level = int((self.current_xp / 100) ** (1/1.5)) + 1
        return max(1, min(level, 99))  # Cap at 99
    
    @property
    def xp_for_current_level(self) -> int:
        """XP required to reach current level."""
        if self.level <= 1:
            return 0
        return int(100 * ((self.level - 1) ** 1.5))
    
    @property
    def xp_for_next_level(self) -> int:
        """XP required to reach next level."""
        return int(100 * (self.level ** 1.5))
    
    @property
    def xp_progress(self) -> float:
        """Progress to next level as 0-1 float."""
        current = self.current_xp - self.xp_for_current_level
        needed = self.xp_for_next_level - self.xp_for_current_level
        if needed <= 0:
            return 1.0
        return min(1.0, max(0.0, current / needed))
    
    @property
    def xp_remaining(self) -> int:
        """XP remaining until next level."""
        return max(0, self.xp_for_next_level - self.current_xp)
    
    def add_xp(self, amount: int) -> tuple[int, bool]:
        """
        Add XP to this stat.
        Returns (new_total_xp, leveled_up).
        """
        old_level = self.level
        self.current_xp += amount
        new_level = self.level
        return self.current_xp, new_level > old_level
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.type.value,
            "current_xp": self.current_xp,
            "target_level": self.target_level,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Stat":
        """Deserialize from dictionary."""
        return cls(
            type=StatType(data["type"]),
            current_xp=data.get("current_xp", 0),
            target_level=data.get("target_level", 10),
        )

