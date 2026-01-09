"""Quest generator that creates personalized quests from templates."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from models.character import Character
from models.quest import Quest, QuestType, QuestStatus, SatisfactionType
from models.stats import StatType, SubFacetType, STAT_DEFINITIONS


class QuestGenerator:
    """Generates personalized quests based on character state."""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> dict:
        """Load quest templates from JSON file."""
        # Find the data directory relative to this file
        current_dir = Path(__file__).parent.parent
        template_path = current_dir / "data" / "quest_templates.json"
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load quest templates: {e}")
            return {"daily_quests": {}, "weekly_quests": [], "epic_quests": [], "special_quests": []}
    
    def _parse_subfacets(self, subfacet_strings: list[str]) -> list[SubFacetType]:
        """Convert subfacet string names to SubFacetType enums."""
        result = []
        for sf_name in subfacet_strings:
            try:
                result.append(SubFacetType(sf_name))
            except ValueError:
                pass  # Skip invalid subfacet names
        return result
    
    def _parse_satisfaction(self, template: dict) -> tuple[SatisfactionType, dict]:
        """Parse satisfaction type and config from template."""
        satisfied_by_str = template.get("satisfied_by", "manual")
        try:
            satisfied_by = SatisfactionType(satisfied_by_str)
        except ValueError:
            satisfied_by = SatisfactionType.MANUAL
        
        satisfaction_config = template.get("satisfaction_config", {})
        return satisfied_by, satisfaction_config
    
    def generate_daily_quests(self, character: Character, count: int = 5) -> list[Quest]:
        """Generate a set of daily quests for the character."""
        quests = []
        
        # Calculate stat priorities based on gap between current and target
        stat_priorities = self._calculate_stat_priorities(character)
        
        # Determine difficulty based on character's challenge preference
        max_difficulty = min(3, character.challenge_level)
        
        # Generate quests weighted by stat priority
        used_templates = set()
        daily_templates = self.templates.get("daily_quests", {})
        
        for _ in range(count):
            # Pick a stat based on priority weights
            stat_type = self._weighted_stat_choice(stat_priorities)
            stat_name = stat_type.value
            
            # Get available templates for this stat
            available = [
                t for t in daily_templates.get(stat_name, [])
                if t.get("difficulty", 1) <= max_difficulty
                and t.get("duration_minutes", 15) <= character.available_time_minutes
                and (stat_name, t["title"]) not in used_templates
            ]
            
            if not available:
                # Fallback to any stat
                for st in StatType:
                    available = [
                        t for t in daily_templates.get(st.value, [])
                        if t.get("difficulty", 1) <= max_difficulty
                        and t.get("duration_minutes", 15) <= character.available_time_minutes
                        and (st.value, t["title"]) not in used_templates
                    ]
                    if available:
                        stat_type = st
                        stat_name = st.value
                        break
            
            if available:
                template = random.choice(available)
                used_templates.add((stat_name, template["title"]))
                satisfied_by, satisfaction_config = self._parse_satisfaction(template)
                
                quest = Quest(
                    title=template["title"],
                    description=template["description"],
                    icon=template.get("icon", "⚔️"),
                    quest_type=QuestType.DAILY,
                    status=QuestStatus.AVAILABLE,
                    primary_stat=stat_type,
                    xp_reward=template.get("xp_reward", 10),
                    target_subfacets=self._parse_subfacets(template.get("subfacets", [])),
                    duration_minutes=template.get("duration_minutes", 15),
                    difficulty=template.get("difficulty", 1),
                    is_recurring=True,
                    expires_at=datetime.now() + timedelta(days=1),
                    satisfied_by=satisfied_by,
                    satisfaction_config=satisfaction_config,
                )
                quests.append(quest)
        
        return quests
    
    def generate_weekly_quest(self, character: Character) -> Optional[Quest]:
        """Generate a weekly quest."""
        weekly_templates = self.templates.get("weekly_quests", [])
        if not weekly_templates:
            return None
            
        stat_priorities = self._calculate_stat_priorities(character)
        
        # Pick highest priority stat
        top_stat = max(stat_priorities.items(), key=lambda x: x[1])[0]
        
        # Find a weekly template for this stat
        matching = [t for t in weekly_templates if t.get("stat") == top_stat.value]
        
        if not matching:
            matching = weekly_templates
        
        template = random.choice(matching)
        satisfied_by, satisfaction_config = self._parse_satisfaction(template)
        
        return Quest(
            title=template["title"],
            description=template["description"],
            icon=template.get("icon", "🛡️"),
            quest_type=QuestType.WEEKLY,
            status=QuestStatus.AVAILABLE,
            primary_stat=StatType(template.get("stat", "intellect")),
            xp_reward=template.get("xp_reward", 100),
            target_subfacets=self._parse_subfacets(template.get("subfacets", [])),
            duration_minutes=0,  # Not applicable for weekly
            difficulty=template.get("difficulty", 3),
            is_recurring=False,
            expires_at=datetime.now() + timedelta(days=7),
            satisfied_by=satisfied_by,
            satisfaction_config=satisfaction_config,
            progress_trackable=template.get("progress_trackable", False),
            progress_target=template.get("progress_target", 0),
            progress_current=0,
            progress_unit=template.get("progress_unit", "units"),
        )
    
    def generate_epic_quest(self, character: Character) -> Optional[Quest]:
        """Generate an epic quest for long-term goals."""
        epic_templates = self.templates.get("epic_quests", [])
        if not epic_templates:
            return None
            
        stat_priorities = self._calculate_stat_priorities(character)
        
        # Pick highest priority stat
        top_stat = max(stat_priorities.items(), key=lambda x: x[1])[0]
        
        # Find an epic template for this stat
        matching = [t for t in epic_templates if t.get("stat") == top_stat.value]
        
        if not matching:
            matching = epic_templates
        
        template = random.choice(matching)
        satisfied_by, satisfaction_config = self._parse_satisfaction(template)
        
        return Quest(
            title=template["title"],
            description=template["description"],
            icon=template.get("icon", "🏰"),
            quest_type=QuestType.EPIC,
            status=QuestStatus.AVAILABLE,
            primary_stat=StatType(template.get("stat", "intellect")),
            xp_reward=template.get("xp_reward", 500),
            target_subfacets=self._parse_subfacets(template.get("subfacets", [])),
            duration_minutes=0,  # Not applicable for epic
            difficulty=template.get("difficulty", 4),
            is_recurring=False,
            expires_at=datetime.now() + timedelta(days=30),
            satisfied_by=satisfied_by,
            satisfaction_config=satisfaction_config,
            progress_trackable=template.get("progress_trackable", False),
            progress_target=template.get("progress_target", 0),
            progress_current=0,
            progress_unit=template.get("progress_unit", "units"),
        )
    
    def generate_random_encounter(self, character: Character) -> Quest:
        """Generate a random encounter quest with bonus XP."""
        stat_type = random.choice(list(StatType))
        daily_templates = self.templates.get("daily_quests", {})
        
        # Random encounters are lower difficulty but time-limited
        available = [
            t for t in daily_templates.get(stat_type.value, [])
            if t.get("difficulty", 1) <= 2
        ]
        
        if not available:
            # Fallback to intellect
            available = daily_templates.get("intellect", [])
            stat_type = StatType.INTELLECT
        
        if not available:
            # Ultimate fallback
            return Quest(
                title="⚡ Quick Challenge",
                description="Complete a brief task of your choosing",
                icon="🎲",
                quest_type=QuestType.RANDOM,
                status=QuestStatus.AVAILABLE,
                primary_stat=StatType.MASTERY,
                xp_reward=15,
                target_subfacets=[SubFacetType.DISCIPLINE],
                duration_minutes=10,
                difficulty=1,
                is_recurring=False,
                expires_at=datetime.now() + timedelta(hours=4),
            )
        
        template = random.choice(available)
        satisfied_by, satisfaction_config = self._parse_satisfaction(template)
        
        # Bonus XP for random encounters
        base_xp = template.get("xp_reward", 10)
        bonus_xp = int(base_xp * 0.5)
        
        return Quest(
            title=f"⚡ {template['title']}",
            description=f"{template['description']} (Bonus XP!)",
            icon="🎲",
            quest_type=QuestType.RANDOM,
            status=QuestStatus.AVAILABLE,
            primary_stat=stat_type,
            xp_reward=base_xp + bonus_xp,
            target_subfacets=self._parse_subfacets(template.get("subfacets", [])),
            duration_minutes=template.get("duration_minutes", 15),
            difficulty=template.get("difficulty", 1),
            is_recurring=False,
            expires_at=datetime.now() + timedelta(hours=4),  # Short expiry
            satisfied_by=satisfied_by,
            satisfaction_config=satisfaction_config,
        )
    
    def generate_special_quest(self, trigger: str = "random") -> Optional[Quest]:
        """Generate a special quest based on context (time of day, weekend, etc.)."""
        special_templates = self.templates.get("special_quests", [])
        if not special_templates:
            return None
        
        # Filter by trigger type
        matching = [t for t in special_templates if t.get("trigger") == trigger]
        
        if not matching:
            return None
        
        template = random.choice(matching)
        satisfied_by, satisfaction_config = self._parse_satisfaction(template)
        
        return Quest(
            title=template["title"],
            description=template["description"],
            icon=template.get("icon", "✨"),
            quest_type=QuestType.RANDOM,
            status=QuestStatus.AVAILABLE,
            primary_stat=StatType(template.get("stat", "spirit")),
            xp_reward=template.get("xp_reward", 25),
            target_subfacets=self._parse_subfacets(template.get("subfacets", [])),
            duration_minutes=template.get("duration_minutes", 30),
            difficulty=template.get("difficulty", 2),
            is_recurring=False,
            expires_at=datetime.now() + timedelta(days=1),
            satisfied_by=satisfied_by,
            satisfaction_config=satisfaction_config,
        )
    
    def _calculate_stat_priorities(self, character: Character) -> dict[StatType, float]:
        """Calculate priority weights for each stat based on gaps."""
        priorities = {}
        
        for stat_type, stat in character.stats.items():
            # Gap between target and current level
            gap = max(0, stat.target_level - stat.level)
            
            # Base priority from gap (higher gap = higher priority)
            priority = 1.0 + (gap * 0.3)
            
            # Boost for lowest stats to encourage balance
            if stat == character.lowest_stat:
                priority *= 1.5
            
            priorities[stat_type] = priority
        
        return priorities
    
    def _weighted_stat_choice(self, priorities: dict[StatType, float]) -> StatType:
        """Choose a stat based on priority weights."""
        stats = list(priorities.keys())
        weights = list(priorities.values())
        total = sum(weights)
        weights = [w / total for w in weights]
        
        return random.choices(stats, weights=weights, k=1)[0]
    
    def should_spawn_random_encounter(self) -> bool:
        """Determine if a random encounter should spawn (20% chance)."""
        return random.random() < 0.20
    
    def get_time_based_trigger(self) -> str:
        """Get the appropriate trigger based on current time."""
        hour = datetime.now().hour
        day = datetime.now().weekday()
        
        if day >= 5:  # Saturday or Sunday
            return "weekend"
        elif hour < 10:
            return "morning"
        elif hour >= 18:
            return "evening"
        else:
            return "random"
