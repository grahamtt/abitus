"""Player character model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
import uuid

from .stats import (
    Stat, StatType, SubFacetType, STAT_DEFINITIONS,
    SUBFACET_TO_DIMENSION, parse_score_key
)


@dataclass
class Character:
    """The player's character with stats and progression."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Adventurer"
    title: str = "Novice"
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Stats - one for each life dimension
    stats: dict[StatType, Stat] = field(default_factory=dict)
    
    # Progression
    total_quests_completed: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_quest_date: Optional[datetime] = None
    
    # Assessment completed flag
    assessment_completed: bool = False
    
    # User preferences from assessment
    available_time_minutes: int = 30  # Daily time available
    challenge_level: int = 2  # 1-4 scale
    
    # Interview data - stores answers for potential re-analysis
    interview_responses: dict[str, Any] = field(default_factory=dict)
    
    # Priority focus area (set during interview)
    priority_dimension: Optional[StatType] = None
    
    def __post_init__(self):
        """Initialize stats if not provided."""
        if not self.stats:
            self.stats = {
                stat_type: Stat(type=stat_type)
                for stat_type in StatType
            }
    
    @property
    def total_level(self) -> int:
        """Sum of all stat levels."""
        return sum(stat.level for stat in self.stats.values())
    
    @property
    def average_level(self) -> float:
        """Average level across all stats."""
        return self.total_level / len(self.stats)
    
    @property
    def total_xp(self) -> int:
        """Total XP across all stats."""
        return sum(stat.current_xp for stat in self.stats.values())
    
    @property
    def highest_stat(self) -> Stat:
        """The stat with the highest level."""
        return max(self.stats.values(), key=lambda s: (s.level, s.current_xp))
    
    @property
    def lowest_stat(self) -> Stat:
        """The stat with the lowest level."""
        return min(self.stats.values(), key=lambda s: (s.level, s.current_xp))
    
    def get_title(self) -> str:
        """Generate a title based on highest stat and sub-facet strengths."""
        highest = self.highest_stat
        avg_level = self.average_level
        
        # Title prefixes based on average level
        if avg_level < 3:
            prefix = "Novice"
        elif avg_level < 5:
            prefix = "Apprentice"
        elif avg_level < 8:
            prefix = "Journeyman"
        elif avg_level < 12:
            prefix = "Expert"
        elif avg_level < 16:
            prefix = "Master"
        else:
            prefix = "Legendary"
        
        # Title suffixes based on highest stat
        suffixes = {
            StatType.INTELLECT: "Scholar",
            StatType.VITALITY: "Warrior",
            StatType.SPIRIT: "Sage",
            StatType.BONDS: "Diplomat",
            StatType.PROSPERITY: "Merchant",
            StatType.MASTERY: "Artisan",
        }
        
        return f"{prefix} {suffixes[highest.type]}"
    
    def apply_interview_scores(self, scores: dict[str, int]) -> None:
        """
        Apply scores from interview answers to sub-facets.
        
        Args:
            scores: Dict mapping "dimension.subfacet" keys to score values
                   e.g., {"vitality.energy": 4, "mastery.discipline": 3}
        """
        for key, value in scores.items():
            try:
                stat_type, facet_type = parse_score_key(key)
                if stat_type in self.stats:
                    self.stats[stat_type].add_subfacet_score(facet_type, value)
            except (ValueError, KeyError) as e:
                # Log but don't fail on invalid keys
                print(f"Warning: Could not apply score for {key}: {e}")
    
    def set_priority(self, dimension: StatType) -> None:
        """Set the priority focus dimension."""
        self.priority_dimension = dimension
    
    def add_xp(self, stat_type: StatType, amount: int) -> tuple[int, bool]:
        """Add XP to a specific stat (distributed across sub-facets)."""
        if stat_type not in self.stats:
            self.stats[stat_type] = Stat(type=stat_type)
        return self.stats[stat_type].add_xp(amount)
    
    def add_subfacet_xp(
        self, 
        facet_type: SubFacetType, 
        amount: int
    ) -> tuple[int, bool]:
        """Add XP to a specific sub-facet."""
        stat_type = SUBFACET_TO_DIMENSION.get(facet_type)
        if stat_type and stat_type in self.stats:
            return self.stats[stat_type].add_subfacet_xp(facet_type, amount)
        return 0, False
    
    def get_strongest_subfacets(self, n: int = 5) -> list[tuple[Stat, 'SubFacet']]:
        """Get the n strongest sub-facets across all dimensions."""
        all_facets = []
        for stat in self.stats.values():
            for facet in stat.sub_facets.values():
                all_facets.append((stat, facet))
        
        sorted_facets = sorted(
            all_facets,
            key=lambda x: x[1].total_score,
            reverse=True
        )
        return sorted_facets[:n]
    
    def get_weakest_subfacets(self, n: int = 5) -> list[tuple[Stat, 'SubFacet']]:
        """Get the n weakest sub-facets across all dimensions."""
        all_facets = []
        for stat in self.stats.values():
            for facet in stat.sub_facets.values():
                all_facets.append((stat, facet))
        
        sorted_facets = sorted(
            all_facets,
            key=lambda x: x[1].total_score
        )
        return sorted_facets[:n]
    
    def get_improvement_suggestions(self) -> list[SubFacetType]:
        """
        Get sub-facets that would benefit most from improvement.
        Considers priority dimension and weakness balance.
        """
        suggestions = []
        
        # Start with weakest overall
        weakest = self.get_weakest_subfacets(3)
        for stat, facet in weakest:
            suggestions.append(facet.type)
        
        # Add priority dimension facets if set
        if self.priority_dimension and self.priority_dimension in self.stats:
            priority_stat = self.stats[self.priority_dimension]
            for facet in priority_stat.get_weakest_facets(2):
                if facet.type not in suggestions:
                    suggestions.append(facet.type)
        
        return suggestions[:5]
    
    def complete_quest(self):
        """Record quest completion for streak tracking."""
        now = datetime.now()
        
        if self.last_quest_date:
            days_since = (now.date() - self.last_quest_date.date()).days
            if days_since == 1:
                self.current_streak += 1
            elif days_since > 1:
                self.current_streak = 1
            # Same day doesn't change streak
        else:
            self.current_streak = 1
        
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_quest_date = now
        self.last_active = now
        self.total_quests_completed += 1
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "stats": {k.value: v.to_dict() for k, v in self.stats.items()},
            "total_quests_completed": self.total_quests_completed,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_quest_date": self.last_quest_date.isoformat() if self.last_quest_date else None,
            "assessment_completed": self.assessment_completed,
            "available_time_minutes": self.available_time_minutes,
            "challenge_level": self.challenge_level,
            "interview_responses": self.interview_responses,
            "priority_dimension": self.priority_dimension.value if self.priority_dimension else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        """Deserialize from dictionary."""
        stats = {}
        for stat_type in StatType:
            if stat_type.value in data.get("stats", {}):
                stats[stat_type] = Stat.from_dict(data["stats"][stat_type.value])
            else:
                stats[stat_type] = Stat(type=stat_type)
        
        priority_dim = None
        if data.get("priority_dimension"):
            try:
                priority_dim = StatType(data["priority_dimension"])
            except ValueError:
                pass
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Adventurer"),
            title=data.get("title", "Novice"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_active=datetime.fromisoformat(data["last_active"]) if "last_active" in data else datetime.now(),
            stats=stats,
            total_quests_completed=data.get("total_quests_completed", 0),
            current_streak=data.get("current_streak", 0),
            longest_streak=data.get("longest_streak", 0),
            last_quest_date=datetime.fromisoformat(data["last_quest_date"]) if data.get("last_quest_date") else None,
            assessment_completed=data.get("assessment_completed", False),
            available_time_minutes=data.get("available_time_minutes", 30),
            challenge_level=data.get("challenge_level", 2),
            interview_responses=data.get("interview_responses", {}),
            priority_dimension=priority_dim,
        )
