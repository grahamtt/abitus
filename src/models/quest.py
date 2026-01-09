"""Quest model for the gamified task system."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid

from .stats import StatType, SubFacetType


class QuestType(Enum):
    """Types of quests with different time commitments."""
    DAILY = "daily"           # 5-15 min, repeatable
    WEEKLY = "weekly"         # Medium commitment
    EPIC = "epic"             # Multi-week pursuit
    RANDOM = "random"         # Surprise encounters
    PARTY = "party"           # Collaborative goals


class QuestStatus(Enum):
    """Quest completion status."""
    AVAILABLE = "available"   # Can be accepted
    ACTIVE = "active"         # Currently in progress
    COMPLETED = "completed"   # Successfully finished
    FAILED = "failed"         # Expired or abandoned
    LOCKED = "locked"         # Not yet unlocked


class SatisfactionType(Enum):
    """How a quest can be satisfied/completed."""
    MANUAL = "manual"                      # User marks complete manually
    
    # Journal-based satisfaction
    JOURNAL_ANY = "journal_any"            # Any journal entry
    JOURNAL_GRATITUDE = "journal_gratitude"  # Gratitude entry
    JOURNAL_REFLECTION = "journal_reflection"  # Reflection entry
    JOURNAL_EMOTION = "journal_emotion"    # Emotional check-in entry
    JOURNAL_GOAL = "journal_goal"          # Goal setting entry
    JOURNAL_LESSON = "journal_lesson"      # Lesson learned entry
    
    # Future app integrations
    APP_DUOLINGO = "app_duolingo"          # Duolingo lesson completion
    APP_STRAVA = "app_strava"              # Strava activity
    APP_FITBIT = "app_fitbit"              # Fitbit activity
    APP_HEADSPACE = "app_headspace"        # Headspace meditation
    APP_CUSTOM = "app_custom"              # Custom webhook/API


# Mapping of journal entry types to satisfaction types
JOURNAL_SATISFACTION_MAP = {
    "free_form": SatisfactionType.JOURNAL_ANY,
    "gratitude": SatisfactionType.JOURNAL_GRATITUDE,
    "reflection": SatisfactionType.JOURNAL_REFLECTION,
    "emotion": SatisfactionType.JOURNAL_EMOTION,
    "goal": SatisfactionType.JOURNAL_GOAL,
    "lesson": SatisfactionType.JOURNAL_LESSON,
}


@dataclass
class Quest:
    """A quest that rewards XP for completion."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Quest identity
    title: str = "Untitled Quest"
    description: str = ""
    icon: str = "⚔️"
    
    # Quest type and status
    quest_type: QuestType = QuestType.DAILY
    status: QuestStatus = QuestStatus.AVAILABLE
    
    # Rewards
    primary_stat: StatType = StatType.INTELLECT
    xp_reward: int = 10
    secondary_rewards: dict[StatType, int] = field(default_factory=dict)
    target_subfacets: list[SubFacetType] = field(default_factory=list)  # Which subfacets get XP
    
    # Requirements
    duration_minutes: int = 15
    difficulty: int = 1  # 1-5 scale
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Recurrence for daily quests
    is_recurring: bool = False
    last_completed: Optional[datetime] = None
    times_completed: int = 0
    
    # Quest chain support
    chain_id: Optional[str] = None
    chain_order: int = 0
    prerequisite_quest_id: Optional[str] = None
    
    # Satisfaction/auto-completion
    satisfied_by: SatisfactionType = SatisfactionType.MANUAL
    satisfaction_config: dict = field(default_factory=dict)  # e.g., {"min_words": 50}
    
    @property
    def is_expired(self) -> bool:
        """Check if quest has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    @property
    def can_accept(self) -> bool:
        """Check if quest can be accepted."""
        return (
            self.status == QuestStatus.AVAILABLE and
            not self.is_expired
        )
    
    @property
    def can_complete(self) -> bool:
        """Check if quest can be completed."""
        return self.status == QuestStatus.ACTIVE
    
    @property
    def total_xp(self) -> int:
        """Total XP from all rewards."""
        return self.xp_reward + sum(self.secondary_rewards.values())
    
    @property
    def type_icon(self) -> str:
        """Icon representing quest type."""
        icons = {
            QuestType.DAILY: "🗡️",
            QuestType.WEEKLY: "🛡️",
            QuestType.EPIC: "🏰",
            QuestType.RANDOM: "🎲",
            QuestType.PARTY: "👥",
        }
        return icons.get(self.quest_type, "⚔️")
    
    @property
    def difficulty_stars(self) -> str:
        """Visual difficulty representation."""
        return "★" * self.difficulty + "☆" * (5 - self.difficulty)
    
    @property
    def is_auto_completable(self) -> bool:
        """Check if this quest can be auto-completed by some action."""
        return self.satisfied_by != SatisfactionType.MANUAL
    
    @property
    def requires_journal(self) -> bool:
        """Check if this quest is satisfied by a journal entry."""
        return self.satisfied_by.value.startswith("journal_")
    
    @property
    def satisfaction_description(self) -> str:
        """Human-readable description of how to satisfy this quest."""
        descriptions = {
            SatisfactionType.MANUAL: "Mark as complete when done",
            SatisfactionType.JOURNAL_ANY: "Write a journal entry",
            SatisfactionType.JOURNAL_GRATITUDE: "Write a gratitude entry",
            SatisfactionType.JOURNAL_REFLECTION: "Write a reflection",
            SatisfactionType.JOURNAL_EMOTION: "Write an emotional check-in",
            SatisfactionType.JOURNAL_GOAL: "Set a goal in your journal",
            SatisfactionType.JOURNAL_LESSON: "Record a lesson learned",
            SatisfactionType.APP_DUOLINGO: "Complete a Duolingo lesson",
            SatisfactionType.APP_STRAVA: "Log a Strava activity",
            SatisfactionType.APP_FITBIT: "Log Fitbit activity",
            SatisfactionType.APP_HEADSPACE: "Complete a Headspace session",
            SatisfactionType.APP_CUSTOM: "Via connected app",
        }
        desc = descriptions.get(self.satisfied_by, "Complete the task")
        
        # Add config requirements if any
        if min_words := self.satisfaction_config.get("min_words"):
            desc += f" (min {min_words} words)"
        if min_items := self.satisfaction_config.get("min_items"):
            desc += f" (at least {min_items} items)"
        
        return desc
    
    def can_be_satisfied_by_journal(self, entry_type: str) -> bool:
        """Check if a journal entry of the given type would satisfy this quest."""
        if self.satisfied_by == SatisfactionType.MANUAL:
            return False
        
        # JOURNAL_ANY accepts any journal entry
        if self.satisfied_by == SatisfactionType.JOURNAL_ANY:
            return True
        
        # Check specific type match
        expected_type = JOURNAL_SATISFACTION_MAP.get(entry_type)
        return expected_type == self.satisfied_by
    
    def accept(self) -> bool:
        """Accept the quest."""
        if not self.can_accept:
            return False
        self.status = QuestStatus.ACTIVE
        self.accepted_at = datetime.now()
        return True
    
    def complete(self) -> dict[StatType, int]:
        """
        Complete the quest and return XP rewards.
        Returns dict of stat_type -> xp_amount.
        """
        if not self.can_complete:
            return {}
        
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.now()
        self.times_completed += 1
        self.last_completed = self.completed_at
        
        # Collect all rewards
        rewards = {self.primary_stat: self.xp_reward}
        for stat, xp in self.secondary_rewards.items():
            rewards[stat] = rewards.get(stat, 0) + xp
        
        return rewards
    
    def abandon(self):
        """Abandon an active quest."""
        if self.status == QuestStatus.ACTIVE:
            self.status = QuestStatus.AVAILABLE
            self.accepted_at = None
    
    def reset_for_recurrence(self):
        """Reset a recurring quest for the next day."""
        if self.is_recurring and self.status == QuestStatus.COMPLETED:
            self.status = QuestStatus.AVAILABLE
            self.accepted_at = None
            self.completed_at = None
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "quest_type": self.quest_type.value,
            "status": self.status.value,
            "primary_stat": self.primary_stat.value,
            "xp_reward": self.xp_reward,
            "secondary_rewards": {k.value: v for k, v in self.secondary_rewards.items()},
            "target_subfacets": [sf.value for sf in self.target_subfacets],
            "duration_minutes": self.duration_minutes,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat(),
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_recurring": self.is_recurring,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None,
            "times_completed": self.times_completed,
            "chain_id": self.chain_id,
            "chain_order": self.chain_order,
            "prerequisite_quest_id": self.prerequisite_quest_id,
            "satisfied_by": self.satisfied_by.value,
            "satisfaction_config": self.satisfaction_config,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Quest":
        """Deserialize from dictionary."""
        secondary = {}
        for k, v in data.get("secondary_rewards", {}).items():
            secondary[StatType(k)] = v
        
        # Parse target subfacets
        subfacets = []
        for sf_value in data.get("target_subfacets", []):
            try:
                subfacets.append(SubFacetType(sf_value))
            except ValueError:
                pass  # Skip invalid subfacet values
        
        # Parse satisfaction type
        try:
            satisfied_by = SatisfactionType(data.get("satisfied_by", "manual"))
        except ValueError:
            satisfied_by = SatisfactionType.MANUAL
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", "Untitled Quest"),
            description=data.get("description", ""),
            icon=data.get("icon", "⚔️"),
            quest_type=QuestType(data.get("quest_type", "daily")),
            status=QuestStatus(data.get("status", "available")),
            primary_stat=StatType(data.get("primary_stat", "intellect")),
            xp_reward=data.get("xp_reward", 10),
            secondary_rewards=secondary,
            target_subfacets=subfacets,
            duration_minutes=data.get("duration_minutes", 15),
            difficulty=data.get("difficulty", 1),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            accepted_at=datetime.fromisoformat(data["accepted_at"]) if data.get("accepted_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            is_recurring=data.get("is_recurring", False),
            last_completed=datetime.fromisoformat(data["last_completed"]) if data.get("last_completed") else None,
            times_completed=data.get("times_completed", 0),
            chain_id=data.get("chain_id"),
            chain_order=data.get("chain_order", 0),
            prerequisite_quest_id=data.get("prerequisite_quest_id"),
            satisfied_by=satisfied_by,
            satisfaction_config=data.get("satisfaction_config", {}),
        )

