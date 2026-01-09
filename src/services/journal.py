"""Journal service for managing entries and quest integration."""

from datetime import datetime, timedelta
from typing import Optional

from models.journal import JournalEntry, JournalEntryType, get_random_prompt
from models.quest import Quest, QuestStatus, SatisfactionType


class JournalService:
    """Manages journal entries and their integration with quests."""
    
    def __init__(self):
        self.entries: list[JournalEntry] = []
    
    def create_entry(
        self,
        entry_type: JournalEntryType = JournalEntryType.FREE_FORM,
        content: str = "",
        use_prompt: bool = True,
        mood_before: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> JournalEntry:
        """Create a new journal entry."""
        prompt = get_random_prompt(entry_type) if use_prompt else None
        
        entry = JournalEntry(
            content=content,
            entry_type=entry_type,
            prompt_used=prompt,
            mood_before=mood_before,
            tags=tags or [],
        )
        
        self.entries.append(entry)
        return entry
    
    def update_entry(
        self,
        entry_id: str,
        content: Optional[str] = None,
        mood_after: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> Optional[JournalEntry]:
        """Update an existing journal entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return None
        
        if content is not None:
            entry.update_content(content)
        if mood_after is not None:
            entry.mood_after = mood_after
        if tags is not None:
            entry.tags = tags
        
        return entry
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        entry = self.get_entry(entry_id)
        if entry:
            self.entries.remove(entry)
            return True
        return False
    
    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get a specific entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def get_entries(
        self,
        entry_type: Optional[JournalEntryType] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[JournalEntry]:
        """Get entries, optionally filtered."""
        result = self.entries.copy()
        
        # Filter by type
        if entry_type:
            result = [e for e in result if e.entry_type == entry_type]
        
        # Filter by date
        if since:
            result = [e for e in result if e.created_at >= since]
        
        # Sort by date (newest first)
        result.sort(key=lambda e: e.created_at, reverse=True)
        
        # Limit results
        if limit:
            result = result[:limit]
        
        return result
    
    def get_today_entries(self) -> list[JournalEntry]:
        """Get all entries from today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_entries(since=today_start)
    
    def get_streak(self) -> int:
        """Calculate current journaling streak (consecutive days with entries)."""
        if not self.entries:
            return 0
        
        # Get unique days with entries
        days_with_entries = set()
        for entry in self.entries:
            day = entry.created_at.date()
            days_with_entries.add(day)
        
        # Check streak starting from today
        streak = 0
        current_day = datetime.now().date()
        
        while current_day in days_with_entries:
            streak += 1
            current_day = current_day - timedelta(days=1)
        
        return streak
    
    def find_satisfiable_quests(
        self,
        entry: JournalEntry,
        active_quests: list[Quest],
    ) -> list[Quest]:
        """
        Find active quests that can be satisfied by the given journal entry.
        
        Returns list of quests that would be completed by this entry.
        """
        satisfiable = []
        
        for quest in active_quests:
            if quest.status != QuestStatus.ACTIVE:
                continue
            
            if not quest.requires_journal:
                continue
            
            # Check if entry type matches quest requirement
            if quest.can_be_satisfied_by_journal(entry.entry_type.value):
                # Check satisfaction config requirements
                if self._meets_satisfaction_requirements(entry, quest):
                    satisfiable.append(quest)
        
        return satisfiable
    
    def _meets_satisfaction_requirements(self, entry: JournalEntry, quest: Quest) -> bool:
        """Check if entry meets the quest's satisfaction requirements."""
        config = quest.satisfaction_config
        
        # Check minimum word count
        if min_words := config.get("min_words"):
            if entry.word_count < min_words:
                return False
        
        # Check minimum items (for gratitude lists, etc.)
        if min_items := config.get("min_items"):
            # Count newlines or bullet points as items
            lines = [l.strip() for l in entry.content.split("\n") if l.strip()]
            if len(lines) < min_items:
                return False
        
        # Must have substantial content
        if config.get("require_substantial", True):
            if not entry.is_substantial:
                return False
        
        return True
    
    def get_quest_suggestions(
        self,
        entry_type: JournalEntryType,
    ) -> list[SatisfactionType]:
        """Get quest satisfaction types that match a journal entry type."""
        from models.quest import JOURNAL_SATISFACTION_MAP
        
        matches = [SatisfactionType.JOURNAL_ANY]  # Any journal entry always matches
        
        if satisfaction_type := JOURNAL_SATISFACTION_MAP.get(entry_type.value):
            matches.append(satisfaction_type)
        
        return matches
    
    def get_mood_trend(self, days: int = 7) -> Optional[float]:
        """
        Calculate average mood change from journaling over recent days.
        Positive = writing improves mood.
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_entries = [
            e for e in self.entries 
            if e.created_at >= cutoff and e.mood_change is not None
        ]
        
        if not recent_entries:
            return None
        
        total_change = sum(e.mood_change for e in recent_entries)
        return total_change / len(recent_entries)
    
    def get_entry_stats(self) -> dict:
        """Get statistics about journal entries."""
        if not self.entries:
            return {
                "total_entries": 0,
                "total_words": 0,
                "streak": 0,
                "entries_by_type": {},
                "avg_mood_change": None,
            }
        
        # Count by type
        by_type = {}
        for entry in self.entries:
            type_name = entry.entry_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "total_words": sum(e.word_count for e in self.entries),
            "streak": self.get_streak(),
            "entries_by_type": by_type,
            "avg_mood_change": self.get_mood_trend(),
        }
    
    def load_entries(self, entries_data: list[dict]) -> None:
        """Load entries from serialized data."""
        self.entries = [JournalEntry.from_dict(data) for data in entries_data]
    
    def save_entries(self) -> list[dict]:
        """Serialize all entries for storage."""
        return [entry.to_dict() for entry in self.entries]

