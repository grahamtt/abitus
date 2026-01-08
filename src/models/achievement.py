"""Achievement system for milestones and rewards."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
import uuid


class AchievementType(Enum):
    """Categories of achievements."""
    MILESTONE = "milestone"       # Level/XP milestones
    STREAK = "streak"             # Consistency achievements
    QUEST = "quest"               # Quest completion counts
    BALANCE = "balance"           # Balanced stat growth
    MASTERY = "mastery"           # Single stat excellence
    SPECIAL = "special"           # Special/hidden achievements


@dataclass
class Achievement:
    """An achievement that can be unlocked."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Achievement identity
    name: str = "Untitled Achievement"
    description: str = ""
    icon: str = "🏆"
    
    # Category
    achievement_type: AchievementType = AchievementType.MILESTONE
    
    # Unlock conditions (stored as description, checked in code)
    requirement_description: str = ""
    requirement_value: int = 0  # e.g., "Complete 10 quests" -> 10
    
    # Status
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    progress: int = 0  # Current progress toward requirement
    
    # Rarity
    rarity: int = 1  # 1=common, 2=uncommon, 3=rare, 4=epic, 5=legendary
    
    # Hidden achievements
    is_hidden: bool = False  # Don't show until unlocked
    
    @property
    def progress_percent(self) -> float:
        """Progress as percentage."""
        if self.requirement_value <= 0:
            return 100.0 if self.is_unlocked else 0.0
        return min(100.0, (self.progress / self.requirement_value) * 100)
    
    @property
    def rarity_name(self) -> str:
        """Human-readable rarity."""
        names = {
            1: "Common",
            2: "Uncommon", 
            3: "Rare",
            4: "Epic",
            5: "Legendary"
        }
        return names.get(self.rarity, "Common")
    
    @property
    def rarity_color(self) -> str:
        """Color for rarity tier."""
        colors = {
            1: "#9ca3af",  # Gray
            2: "#22c55e",  # Green
            3: "#3b82f6",  # Blue
            4: "#a855f7",  # Purple
            5: "#f59e0b",  # Gold
        }
        return colors.get(self.rarity, "#9ca3af")
    
    def update_progress(self, value: int) -> bool:
        """
        Update progress and check for unlock.
        Returns True if newly unlocked.
        """
        if self.is_unlocked:
            return False
        
        self.progress = value
        
        if self.progress >= self.requirement_value:
            self.unlock()
            return True
        return False
    
    def unlock(self):
        """Unlock this achievement."""
        if not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = datetime.now()
            self.progress = self.requirement_value
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "achievement_type": self.achievement_type.value,
            "requirement_description": self.requirement_description,
            "requirement_value": self.requirement_value,
            "is_unlocked": self.is_unlocked,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "progress": self.progress,
            "rarity": self.rarity,
            "is_hidden": self.is_hidden,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Achievement":
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled Achievement"),
            description=data.get("description", ""),
            icon=data.get("icon", "🏆"),
            achievement_type=AchievementType(data.get("achievement_type", "milestone")),
            requirement_description=data.get("requirement_description", ""),
            requirement_value=data.get("requirement_value", 0),
            is_unlocked=data.get("is_unlocked", False),
            unlocked_at=datetime.fromisoformat(data["unlocked_at"]) if data.get("unlocked_at") else None,
            progress=data.get("progress", 0),
            rarity=data.get("rarity", 1),
            is_hidden=data.get("is_hidden", False),
        )


# Pre-defined achievements
def create_default_achievements() -> list[Achievement]:
    """Create the default set of achievements."""
    return [
        # Milestone achievements
        Achievement(
            id="first_quest",
            name="First Steps",
            description="Complete your first quest",
            icon="👣",
            achievement_type=AchievementType.QUEST,
            requirement_description="Complete 1 quest",
            requirement_value=1,
            rarity=1,
        ),
        Achievement(
            id="quest_10",
            name="Quest Apprentice",
            description="Complete 10 quests",
            icon="⚔️",
            achievement_type=AchievementType.QUEST,
            requirement_description="Complete 10 quests",
            requirement_value=10,
            rarity=1,
        ),
        Achievement(
            id="quest_50",
            name="Quest Adept",
            description="Complete 50 quests",
            icon="🗡️",
            achievement_type=AchievementType.QUEST,
            requirement_description="Complete 50 quests",
            requirement_value=50,
            rarity=2,
        ),
        Achievement(
            id="quest_100",
            name="Quest Master",
            description="Complete 100 quests",
            icon="🏅",
            achievement_type=AchievementType.QUEST,
            requirement_description="Complete 100 quests",
            requirement_value=100,
            rarity=3,
        ),
        Achievement(
            id="quest_500",
            name="Legendary Adventurer",
            description="Complete 500 quests",
            icon="👑",
            achievement_type=AchievementType.QUEST,
            requirement_description="Complete 500 quests",
            requirement_value=500,
            rarity=5,
        ),
        
        # Streak achievements
        Achievement(
            id="streak_3",
            name="Consistent",
            description="Maintain a 3-day streak",
            icon="🔥",
            achievement_type=AchievementType.STREAK,
            requirement_description="3-day streak",
            requirement_value=3,
            rarity=1,
        ),
        Achievement(
            id="streak_7",
            name="Week Warrior",
            description="Maintain a 7-day streak",
            icon="📅",
            achievement_type=AchievementType.STREAK,
            requirement_description="7-day streak",
            requirement_value=7,
            rarity=2,
        ),
        Achievement(
            id="streak_30",
            name="Monthly Master",
            description="Maintain a 30-day streak",
            icon="🌟",
            achievement_type=AchievementType.STREAK,
            requirement_description="30-day streak",
            requirement_value=30,
            rarity=3,
        ),
        Achievement(
            id="streak_100",
            name="Centurion",
            description="Maintain a 100-day streak",
            icon="💎",
            achievement_type=AchievementType.STREAK,
            requirement_description="100-day streak",
            requirement_value=100,
            rarity=4,
        ),
        Achievement(
            id="streak_365",
            name="Year of Growth",
            description="Maintain a 365-day streak",
            icon="🎊",
            achievement_type=AchievementType.STREAK,
            requirement_description="365-day streak",
            requirement_value=365,
            rarity=5,
        ),
        
        # Level achievements
        Achievement(
            id="level_5",
            name="Rising Star",
            description="Reach level 5 in any stat",
            icon="⭐",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Level 5 in any stat",
            requirement_value=5,
            rarity=1,
        ),
        Achievement(
            id="level_10",
            name="Double Digits",
            description="Reach level 10 in any stat",
            icon="🌟",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Level 10 in any stat",
            requirement_value=10,
            rarity=2,
        ),
        Achievement(
            id="level_25",
            name="Quarter Century",
            description="Reach level 25 in any stat",
            icon="✨",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Level 25 in any stat",
            requirement_value=25,
            rarity=3,
        ),
        Achievement(
            id="level_50",
            name="Half-way Hero",
            description="Reach level 50 in any stat",
            icon="🌠",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Level 50 in any stat",
            requirement_value=50,
            rarity=4,
        ),
        
        # Balance achievement
        Achievement(
            id="balanced_5",
            name="Well-Rounded",
            description="Reach level 5 in all stats",
            icon="⚖️",
            achievement_type=AchievementType.BALANCE,
            requirement_description="Level 5 in all stats",
            requirement_value=5,
            rarity=2,
        ),
        Achievement(
            id="balanced_10",
            name="Renaissance Soul",
            description="Reach level 10 in all stats",
            icon="🎭",
            achievement_type=AchievementType.BALANCE,
            requirement_description="Level 10 in all stats",
            requirement_value=10,
            rarity=3,
        ),
        Achievement(
            id="balanced_25",
            name="Life Master",
            description="Reach level 25 in all stats",
            icon="🏛️",
            achievement_type=AchievementType.BALANCE,
            requirement_description="Level 25 in all stats",
            requirement_value=25,
            rarity=5,
        ),
        
        # XP milestones
        Achievement(
            id="xp_1000",
            name="First Thousand",
            description="Earn 1,000 total XP",
            icon="💫",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Earn 1,000 XP",
            requirement_value=1000,
            rarity=1,
        ),
        Achievement(
            id="xp_10000",
            name="Ten Thousand Club",
            description="Earn 10,000 total XP",
            icon="🌈",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Earn 10,000 XP",
            requirement_value=10000,
            rarity=2,
        ),
        Achievement(
            id="xp_100000",
            name="XP Millionaire",
            description="Earn 100,000 total XP",
            icon="💰",
            achievement_type=AchievementType.MILESTONE,
            requirement_description="Earn 100,000 XP",
            requirement_value=100000,
            rarity=4,
        ),
    ]

