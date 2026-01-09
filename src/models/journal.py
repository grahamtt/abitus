"""Journal model for reflective writing entries."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class JournalEntryType(Enum):
    """Types of journal entries."""
    FREE_FORM = "free_form"        # Open-ended writing
    GRATITUDE = "gratitude"        # Gratitude list/reflection
    REFLECTION = "reflection"      # Daily/weekly reflection
    EMOTION = "emotion"            # Emotional check-in
    GOAL = "goal"                  # Goal setting/tracking
    LESSON = "lesson"              # Lessons learned


# Medieval-themed prompts for each entry type
ENTRY_PROMPTS: dict[JournalEntryType, list[str]] = {
    JournalEntryType.FREE_FORM: [
        "Let your quill flow freely upon this parchment...",
        "What weighs upon your mind this day?",
        "Chronicle the thoughts that swirl within your keep...",
    ],
    JournalEntryType.GRATITUDE: [
        "Name three blessings that have graced your path today...",
        "For what gifts of fortune do you give thanks?",
        "What kindnesses have the fates bestowed upon you?",
    ],
    JournalEntryType.REFLECTION: [
        "As the day draws to a close, what wisdom have you gathered?",
        "Reflect upon your deeds—what would you have done differently?",
        "What lessons has this chapter of your journey revealed?",
    ],
    JournalEntryType.EMOTION: [
        "How fares your heart and spirit at this hour?",
        "What tempests or calms stir within your soul?",
        "Name the feelings that dwell within your castle walls...",
    ],
    JournalEntryType.GOAL: [
        "What quest do you set before yourself?",
        "Declare your intentions for the days ahead...",
        "What mountain do you aim to conquer next?",
    ],
    JournalEntryType.LESSON: [
        "What hard-won wisdom have you claimed today?",
        "What truth has experience etched upon your soul?",
        "Record the knowledge gained through trial and triumph...",
    ],
}


@dataclass
class JournalEntry:
    """A single journal entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Content
    content: str = ""
    entry_type: JournalEntryType = JournalEntryType.FREE_FORM
    prompt_used: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Mood tracking (1-5 scale, optional)
    mood_before: Optional[int] = None  # How you felt before writing
    mood_after: Optional[int] = None   # How you felt after writing
    
    # Tags for organization
    tags: list[str] = field(default_factory=list)
    
    # Quest integration
    satisfied_quest_id: Optional[str] = None  # Quest this entry completed
    
    @property
    def word_count(self) -> int:
        """Count words in the entry."""
        return len(self.content.split())
    
    @property
    def is_substantial(self) -> bool:
        """Check if entry has meaningful content (at least 10 words)."""
        return self.word_count >= 10
    
    @property
    def mood_change(self) -> Optional[int]:
        """Calculate mood change from writing (positive = improved)."""
        if self.mood_before is not None and self.mood_after is not None:
            return self.mood_after - self.mood_before
        return None
    
    @property
    def type_icon(self) -> str:
        """Icon for the entry type."""
        icons = {
            JournalEntryType.FREE_FORM: "📝",
            JournalEntryType.GRATITUDE: "🙏",
            JournalEntryType.REFLECTION: "🪞",
            JournalEntryType.EMOTION: "💭",
            JournalEntryType.GOAL: "🎯",
            JournalEntryType.LESSON: "📖",
        }
        return icons.get(self.entry_type, "📝")
    
    @property
    def type_name(self) -> str:
        """Human-readable type name."""
        names = {
            JournalEntryType.FREE_FORM: "Free Writing",
            JournalEntryType.GRATITUDE: "Gratitude",
            JournalEntryType.REFLECTION: "Reflection",
            JournalEntryType.EMOTION: "Emotional Check-in",
            JournalEntryType.GOAL: "Goal Setting",
            JournalEntryType.LESSON: "Lesson Learned",
        }
        return names.get(self.entry_type, "Entry")
    
    def update_content(self, new_content: str) -> None:
        """Update the entry content."""
        self.content = new_content
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "entry_type": self.entry_type.value,
            "prompt_used": self.prompt_used,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "mood_before": self.mood_before,
            "mood_after": self.mood_after,
            "tags": self.tags,
            "satisfied_quest_id": self.satisfied_quest_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "JournalEntry":
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", ""),
            entry_type=JournalEntryType(data.get("entry_type", "free_form")),
            prompt_used=data.get("prompt_used"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            mood_before=data.get("mood_before"),
            mood_after=data.get("mood_after"),
            tags=data.get("tags", []),
            satisfied_quest_id=data.get("satisfied_quest_id"),
        )


def get_random_prompt(entry_type: JournalEntryType) -> str:
    """Get a random prompt for the given entry type."""
    import random
    prompts = ENTRY_PROMPTS.get(entry_type, ENTRY_PROMPTS[JournalEntryType.FREE_FORM])
    return random.choice(prompts)

