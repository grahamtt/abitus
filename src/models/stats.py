"""Life dimension stats with multi-faceted sub-scores."""

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


class SubFacetType(Enum):
    """All sub-facets across all dimensions."""
    # Intellect sub-facets
    LEARNING = "learning"
    CREATIVITY = "creativity"
    CURIOSITY = "curiosity"
    PROBLEM_SOLVING = "problem_solving"
    KNOWLEDGE = "knowledge"
    
    # Vitality sub-facets
    EXERCISE = "exercise"
    NUTRITION = "nutrition"
    SLEEP = "sleep"
    ENERGY = "energy"
    ENDURANCE = "endurance"
    
    # Spirit sub-facets
    MINDFULNESS = "mindfulness"
    EMOTIONAL_AWARENESS = "emotional_awareness"
    RESILIENCE = "resilience"
    GRATITUDE = "gratitude"
    INNER_PEACE = "inner_peace"
    
    # Bonds sub-facets
    FAMILY = "family"
    FRIENDSHIP = "friendship"
    ROMANCE = "romance"
    COMMUNITY = "community"
    COMMUNICATION = "communication"
    
    # Prosperity sub-facets
    CAREER = "career"
    FINANCES = "finances"
    AMBITION = "ambition"
    STABILITY = "stability"
    GROWTH = "growth"
    
    # Mastery sub-facets
    HOBBIES = "hobbies"
    SKILLS = "skills"
    DISCIPLINE = "discipline"
    CRAFTSMANSHIP = "craftsmanship"
    DEDICATION = "dedication"


# Mapping of dimensions to their sub-facets
DIMENSION_SUBFACETS: dict[StatType, list[SubFacetType]] = {
    StatType.INTELLECT: [
        SubFacetType.LEARNING,
        SubFacetType.CREATIVITY,
        SubFacetType.CURIOSITY,
        SubFacetType.PROBLEM_SOLVING,
        SubFacetType.KNOWLEDGE,
    ],
    StatType.VITALITY: [
        SubFacetType.EXERCISE,
        SubFacetType.NUTRITION,
        SubFacetType.SLEEP,
        SubFacetType.ENERGY,
        SubFacetType.ENDURANCE,
    ],
    StatType.SPIRIT: [
        SubFacetType.MINDFULNESS,
        SubFacetType.EMOTIONAL_AWARENESS,
        SubFacetType.RESILIENCE,
        SubFacetType.GRATITUDE,
        SubFacetType.INNER_PEACE,
    ],
    StatType.BONDS: [
        SubFacetType.FAMILY,
        SubFacetType.FRIENDSHIP,
        SubFacetType.ROMANCE,
        SubFacetType.COMMUNITY,
        SubFacetType.COMMUNICATION,
    ],
    StatType.PROSPERITY: [
        SubFacetType.CAREER,
        SubFacetType.FINANCES,
        SubFacetType.AMBITION,
        SubFacetType.STABILITY,
        SubFacetType.GROWTH,
    ],
    StatType.MASTERY: [
        SubFacetType.HOBBIES,
        SubFacetType.SKILLS,
        SubFacetType.DISCIPLINE,
        SubFacetType.CRAFTSMANSHIP,
        SubFacetType.DEDICATION,
    ],
}

# Reverse mapping: sub-facet -> parent dimension
SUBFACET_TO_DIMENSION: dict[SubFacetType, StatType] = {}
for dim, facets in DIMENSION_SUBFACETS.items():
    for facet in facets:
        SUBFACET_TO_DIMENSION[facet] = dim


@dataclass
class SubFacetDefinition:
    """Definition of a sub-facet with metadata."""
    type: SubFacetType
    name: str
    description: str
    icon: str = ""  # Optional specific icon


# Sub-facet definitions with descriptions
SUBFACET_DEFINITIONS: dict[SubFacetType, SubFacetDefinition] = {
    # Intellect
    SubFacetType.LEARNING: SubFacetDefinition(
        type=SubFacetType.LEARNING,
        name="Learning",
        description="Active pursuit of new knowledge and education",
        icon="📖"
    ),
    SubFacetType.CREATIVITY: SubFacetDefinition(
        type=SubFacetType.CREATIVITY,
        name="Creativity",
        description="Imagination, innovation, and original thinking",
        icon="🎨"
    ),
    SubFacetType.CURIOSITY: SubFacetDefinition(
        type=SubFacetType.CURIOSITY,
        name="Curiosity",
        description="Drive to explore, question, and discover",
        icon="🔍"
    ),
    SubFacetType.PROBLEM_SOLVING: SubFacetDefinition(
        type=SubFacetType.PROBLEM_SOLVING,
        name="Problem Solving",
        description="Analytical thinking and finding solutions",
        icon="🧩"
    ),
    SubFacetType.KNOWLEDGE: SubFacetDefinition(
        type=SubFacetType.KNOWLEDGE,
        name="Knowledge",
        description="Accumulated wisdom and understanding",
        icon="🎓"
    ),
    
    # Vitality
    SubFacetType.EXERCISE: SubFacetDefinition(
        type=SubFacetType.EXERCISE,
        name="Exercise",
        description="Regular physical activity and training",
        icon="🏃"
    ),
    SubFacetType.NUTRITION: SubFacetDefinition(
        type=SubFacetType.NUTRITION,
        name="Nutrition",
        description="Quality of diet and eating habits",
        icon="🥗"
    ),
    SubFacetType.SLEEP: SubFacetDefinition(
        type=SubFacetType.SLEEP,
        name="Sleep",
        description="Rest quality and recovery",
        icon="😴"
    ),
    SubFacetType.ENERGY: SubFacetDefinition(
        type=SubFacetType.ENERGY,
        name="Energy",
        description="Daily vitality and alertness",
        icon="⚡"
    ),
    SubFacetType.ENDURANCE: SubFacetDefinition(
        type=SubFacetType.ENDURANCE,
        name="Endurance",
        description="Stamina and physical resilience",
        icon="🏔️"
    ),
    
    # Spirit
    SubFacetType.MINDFULNESS: SubFacetDefinition(
        type=SubFacetType.MINDFULNESS,
        name="Mindfulness",
        description="Present-moment awareness and meditation",
        icon="🧘"
    ),
    SubFacetType.EMOTIONAL_AWARENESS: SubFacetDefinition(
        type=SubFacetType.EMOTIONAL_AWARENESS,
        name="Emotional Awareness",
        description="Understanding and processing feelings",
        icon="💭"
    ),
    SubFacetType.RESILIENCE: SubFacetDefinition(
        type=SubFacetType.RESILIENCE,
        name="Resilience",
        description="Ability to recover from setbacks",
        icon="🛡️"
    ),
    SubFacetType.GRATITUDE: SubFacetDefinition(
        type=SubFacetType.GRATITUDE,
        name="Gratitude",
        description="Appreciation for what you have",
        icon="🙏"
    ),
    SubFacetType.INNER_PEACE: SubFacetDefinition(
        type=SubFacetType.INNER_PEACE,
        name="Inner Peace",
        description="Calm, contentment, and acceptance",
        icon="☮️"
    ),
    
    # Bonds
    SubFacetType.FAMILY: SubFacetDefinition(
        type=SubFacetType.FAMILY,
        name="Family",
        description="Connections with kin and household",
        icon="👨‍👩‍👧‍👦"
    ),
    SubFacetType.FRIENDSHIP: SubFacetDefinition(
        type=SubFacetType.FRIENDSHIP,
        name="Friendship",
        description="Bonds with friends and companions",
        icon="🤝"
    ),
    SubFacetType.ROMANCE: SubFacetDefinition(
        type=SubFacetType.ROMANCE,
        name="Romance",
        description="Romantic partnerships and intimacy",
        icon="💕"
    ),
    SubFacetType.COMMUNITY: SubFacetDefinition(
        type=SubFacetType.COMMUNITY,
        name="Community",
        description="Connection to broader social groups",
        icon="🏘️"
    ),
    SubFacetType.COMMUNICATION: SubFacetDefinition(
        type=SubFacetType.COMMUNICATION,
        name="Communication",
        description="Expressing and understanding others",
        icon="💬"
    ),
    
    # Prosperity
    SubFacetType.CAREER: SubFacetDefinition(
        type=SubFacetType.CAREER,
        name="Career",
        description="Professional path and work satisfaction",
        icon="💼"
    ),
    SubFacetType.FINANCES: SubFacetDefinition(
        type=SubFacetType.FINANCES,
        name="Finances",
        description="Money management and security",
        icon="🏦"
    ),
    SubFacetType.AMBITION: SubFacetDefinition(
        type=SubFacetType.AMBITION,
        name="Ambition",
        description="Drive for achievement and success",
        icon="🚀"
    ),
    SubFacetType.STABILITY: SubFacetDefinition(
        type=SubFacetType.STABILITY,
        name="Stability",
        description="Work-life balance and security",
        icon="⚖️"
    ),
    SubFacetType.GROWTH: SubFacetDefinition(
        type=SubFacetType.GROWTH,
        name="Growth",
        description="Professional development and advancement",
        icon="📈"
    ),
    
    # Mastery
    SubFacetType.HOBBIES: SubFacetDefinition(
        type=SubFacetType.HOBBIES,
        name="Hobbies",
        description="Personal interests and pastimes",
        icon="🎮"
    ),
    SubFacetType.SKILLS: SubFacetDefinition(
        type=SubFacetType.SKILLS,
        name="Skills",
        description="Practical abilities and techniques",
        icon="🔧"
    ),
    SubFacetType.DISCIPLINE: SubFacetDefinition(
        type=SubFacetType.DISCIPLINE,
        name="Discipline",
        description="Self-control and consistent practice",
        icon="⏰"
    ),
    SubFacetType.CRAFTSMANSHIP: SubFacetDefinition(
        type=SubFacetType.CRAFTSMANSHIP,
        name="Craftsmanship",
        description="Quality and pride in one's work",
        icon="⚒️"
    ),
    SubFacetType.DEDICATION: SubFacetDefinition(
        type=SubFacetType.DEDICATION,
        name="Dedication",
        description="Commitment to seeing things through",
        icon="🎯"
    ),
}


@dataclass
class SubFacet:
    """A sub-facet score within a dimension."""
    type: SubFacetType
    score: int = 0  # Raw score from interview (0-25 typical range)
    xp_bonus: int = 0  # Additional XP earned through quests
    
    @property
    def definition(self) -> SubFacetDefinition:
        """Get the sub-facet definition."""
        return SUBFACET_DEFINITIONS[self.type]
    
    @property
    def parent_dimension(self) -> StatType:
        """Get the parent dimension type."""
        return SUBFACET_TO_DIMENSION[self.type]
    
    @property
    def total_score(self) -> int:
        """Combined score from interview + quest XP."""
        # XP bonus converts at 10 XP = 1 score point
        return self.score + (self.xp_bonus // 10)
    
    @property
    def level(self) -> int:
        """Calculate level from total score (1-20 scale)."""
        # Score of 0-5 = level 1, 6-10 = level 2, etc.
        # Max practical score ~100 = level 20
        return max(1, min(20, (self.total_score // 5) + 1))
    
    def add_score(self, amount: int) -> None:
        """Add to the base score (from interview)."""
        self.score = max(0, self.score + amount)
    
    def add_xp(self, amount: int) -> None:
        """Add XP bonus (from quests)."""
        self.xp_bonus = max(0, self.xp_bonus + amount)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.type.value,
            "score": self.score,
            "xp_bonus": self.xp_bonus,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SubFacet":
        """Deserialize from dictionary."""
        return cls(
            type=SubFacetType(data["type"]),
            score=data.get("score", 0),
            xp_bonus=data.get("xp_bonus", 0),
        )


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
    """A character stat representing a life dimension with sub-facets."""
    type: StatType
    sub_facets: dict[SubFacetType, SubFacet] = field(default_factory=dict)
    target_level: int = 10  # Desired level from assessment
    
    def __post_init__(self):
        """Initialize sub-facets if not provided."""
        if not self.sub_facets:
            for facet_type in DIMENSION_SUBFACETS[self.type]:
                self.sub_facets[facet_type] = SubFacet(type=facet_type)
    
    @property
    def definition(self) -> StatDefinition:
        """Get the stat definition."""
        return STAT_DEFINITIONS[self.type]
    
    @property
    def total_score(self) -> int:
        """Sum of all sub-facet total scores."""
        return sum(sf.total_score for sf in self.sub_facets.values())
    
    @property
    def average_score(self) -> float:
        """Average score across sub-facets."""
        if not self.sub_facets:
            return 0.0
        return self.total_score / len(self.sub_facets)
    
    @property
    def level(self) -> int:
        """
        Calculate aggregate level from sub-facet scores.
        Uses average of sub-facet levels, weighted slightly toward the highest.
        """
        if not self.sub_facets:
            return 1
        
        levels = [sf.level for sf in self.sub_facets.values()]
        avg_level = sum(levels) / len(levels)
        max_level = max(levels)
        
        # Weighted: 80% average, 20% max (rewards specialization slightly)
        weighted_level = (avg_level * 0.8) + (max_level * 0.2)
        return max(1, min(20, int(weighted_level)))
    
    @property
    def current_xp(self) -> int:
        """
        Calculate equivalent XP from sub-facet scores.
        Used for backward compatibility with existing UI.
        """
        # Convert level to XP using the original formula
        level = self.level
        if level <= 1:
            return 0
        return int(100 * ((level - 1) ** 1.5))
    
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
        """
        Progress to next level as 0-1 float.
        Based on average sub-facet progress within current level bracket.
        """
        levels = [sf.level for sf in self.sub_facets.values()]
        current_level = self.level
        
        # Calculate how close sub-facets are to the next level
        # Count sub-facets at or above current level
        at_or_above = sum(1 for l in levels if l >= current_level)
        above = sum(1 for l in levels if l > current_level)
        
        # Progress based on how many sub-facets have reached the next level
        return min(1.0, above / len(levels))
    
    @property
    def xp_remaining(self) -> int:
        """XP remaining until next level (estimated)."""
        return max(0, self.xp_for_next_level - self.current_xp)
    
    def get_subfacet(self, facet_type: SubFacetType) -> SubFacet:
        """Get a specific sub-facet."""
        return self.sub_facets.get(facet_type)
    
    def add_subfacet_score(self, facet_type: SubFacetType, amount: int) -> None:
        """Add score to a specific sub-facet."""
        if facet_type in self.sub_facets:
            self.sub_facets[facet_type].add_score(amount)
    
    def add_subfacet_xp(self, facet_type: SubFacetType, amount: int) -> tuple[int, bool]:
        """
        Add XP to a specific sub-facet.
        Returns (new_total_xp, leveled_up).
        """
        if facet_type not in self.sub_facets:
            return 0, False
        
        old_level = self.level
        self.sub_facets[facet_type].add_xp(amount)
        new_level = self.level
        
        return self.current_xp, new_level > old_level
    
    def add_xp(self, amount: int) -> tuple[int, bool]:
        """
        Add XP distributed across all sub-facets.
        For backward compatibility - distributes evenly.
        Returns (new_total_xp, leveled_up).
        """
        old_level = self.level
        per_facet = amount // len(self.sub_facets)
        remainder = amount % len(self.sub_facets)
        
        for i, sf in enumerate(self.sub_facets.values()):
            # Distribute evenly, with remainder going to first facets
            sf.add_xp(per_facet + (1 if i < remainder else 0))
        
        new_level = self.level
        return self.current_xp, new_level > old_level
    
    def get_strongest_facets(self, n: int = 2) -> list[SubFacet]:
        """Get the n strongest sub-facets."""
        sorted_facets = sorted(
            self.sub_facets.values(),
            key=lambda sf: sf.total_score,
            reverse=True
        )
        return sorted_facets[:n]
    
    def get_weakest_facets(self, n: int = 2) -> list[SubFacet]:
        """Get the n weakest sub-facets."""
        sorted_facets = sorted(
            self.sub_facets.values(),
            key=lambda sf: sf.total_score
        )
        return sorted_facets[:n]
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "type": self.type.value,
            "sub_facets": {
                k.value: v.to_dict() for k, v in self.sub_facets.items()
            },
            "target_level": self.target_level,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Stat":
        """Deserialize from dictionary."""
        stat = cls(
            type=StatType(data["type"]),
            target_level=data.get("target_level", 10),
        )
        
        # Load sub-facets if present
        if "sub_facets" in data:
            for facet_key, facet_data in data["sub_facets"].items():
                facet_type = SubFacetType(facet_key)
                if facet_type in stat.sub_facets:
                    stat.sub_facets[facet_type] = SubFacet.from_dict(facet_data)
        
        # Backward compatibility: convert old current_xp to sub-facet scores
        elif "current_xp" in data:
            old_xp = data.get("current_xp", 0)
            # Distribute old XP evenly across sub-facets
            per_facet = old_xp // len(stat.sub_facets)
            for sf in stat.sub_facets.values():
                sf.xp_bonus = per_facet
        
        return stat


def parse_score_key(key: str) -> tuple[StatType, SubFacetType]:
    """
    Parse a score key like 'vitality.energy' into (StatType, SubFacetType).
    Used when processing interview answers.
    """
    parts = key.split(".")
    if len(parts) != 2:
        raise ValueError(f"Invalid score key format: {key}")
    
    dimension_str, facet_str = parts
    
    # Find the StatType
    stat_type = StatType(dimension_str)
    
    # Find the SubFacetType
    facet_type = SubFacetType(facet_str)
    
    # Validate the facet belongs to this dimension
    if facet_type not in DIMENSION_SUBFACETS[stat_type]:
        raise ValueError(f"Sub-facet {facet_str} does not belong to {dimension_str}")
    
    return stat_type, facet_type
