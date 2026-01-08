"""Quest generator that creates personalized quests."""

import random
from datetime import datetime, timedelta
from typing import Optional

from models.character import Character
from models.quest import Quest, QuestType, QuestStatus
from models.stats import StatType, STAT_DEFINITIONS


# Quest templates organized by stat and difficulty
QUEST_TEMPLATES = {
    StatType.INTELLECT: [
        # Difficulty 1
        {"title": "The Scholar's Path", "description": "Read for 20 minutes", "icon": "📖", "duration": 20, "xp": 15, "difficulty": 1},
        {"title": "Mind Sharpener", "description": "Complete a puzzle or brain game", "icon": "🧩", "duration": 10, "xp": 10, "difficulty": 1},
        {"title": "Curious Explorer", "description": "Learn one new fact about any topic", "icon": "🔍", "duration": 5, "xp": 8, "difficulty": 1},
        # Difficulty 2
        {"title": "Knowledge Seeker", "description": "Watch an educational video or documentary", "icon": "🎬", "duration": 30, "xp": 20, "difficulty": 2},
        {"title": "The Written Word", "description": "Write in a journal or blog for 15 minutes", "icon": "✍️", "duration": 15, "xp": 18, "difficulty": 2},
        {"title": "Language Learner", "description": "Practice a new language for 15 minutes", "icon": "🗣️", "duration": 15, "xp": 18, "difficulty": 2},
        # Difficulty 3
        {"title": "Deep Dive", "description": "Study a complex topic for 45 minutes", "icon": "📚", "duration": 45, "xp": 35, "difficulty": 3},
        {"title": "The Creator", "description": "Write 500 words on any topic", "icon": "📝", "duration": 30, "xp": 30, "difficulty": 3},
    ],
    StatType.VITALITY: [
        # Difficulty 1
        {"title": "Morning Stretch", "description": "Do a 5-minute stretch routine", "icon": "🤸", "duration": 5, "xp": 8, "difficulty": 1},
        {"title": "Hydration Quest", "description": "Drink 8 glasses of water today", "icon": "💧", "duration": 5, "xp": 10, "difficulty": 1},
        {"title": "Step Counter", "description": "Take a 10-minute walk", "icon": "🚶", "duration": 10, "xp": 12, "difficulty": 1},
        # Difficulty 2
        {"title": "Iron Body Initiation", "description": "Complete a 15-minute workout", "icon": "💪", "duration": 15, "xp": 20, "difficulty": 2},
        {"title": "Healthy Choices", "description": "Prepare a nutritious meal from scratch", "icon": "🥗", "duration": 30, "xp": 22, "difficulty": 2},
        {"title": "Rest and Recovery", "description": "Get 8 hours of sleep", "icon": "😴", "duration": 480, "xp": 25, "difficulty": 2},
        # Difficulty 3
        {"title": "Warrior's Training", "description": "Complete a 30-minute intense workout", "icon": "🏋️", "duration": 30, "xp": 35, "difficulty": 3},
        {"title": "Cardio Challenge", "description": "Run or cycle for 20 minutes", "icon": "🏃", "duration": 20, "xp": 30, "difficulty": 3},
    ],
    StatType.SPIRIT: [
        # Difficulty 1
        {"title": "Moment of Peace", "description": "Practice 5 minutes of deep breathing", "icon": "🌬️", "duration": 5, "xp": 8, "difficulty": 1},
        {"title": "The Gratitude Scroll", "description": "Write 3 things you're grateful for", "icon": "🙏", "duration": 5, "xp": 10, "difficulty": 1},
        {"title": "Digital Detox", "description": "Spend 30 minutes without screens", "icon": "📵", "duration": 30, "xp": 15, "difficulty": 1},
        # Difficulty 2
        {"title": "Inner Calm", "description": "Meditate for 10 minutes", "icon": "🧘", "duration": 10, "xp": 18, "difficulty": 2},
        {"title": "Nature's Embrace", "description": "Spend 20 minutes in nature", "icon": "🌳", "duration": 20, "xp": 20, "difficulty": 2},
        {"title": "Emotional Check-in", "description": "Journal about your feelings for 10 minutes", "icon": "📔", "duration": 10, "xp": 18, "difficulty": 2},
        # Difficulty 3
        {"title": "Deep Meditation", "description": "Complete a 20-minute guided meditation", "icon": "🕯️", "duration": 20, "xp": 30, "difficulty": 3},
        {"title": "Mindful Day", "description": "Practice mindfulness throughout the day", "icon": "☯️", "duration": 60, "xp": 40, "difficulty": 3},
    ],
    StatType.BONDS: [
        # Difficulty 1
        {"title": "Quick Connect", "description": "Send a thoughtful message to someone", "icon": "💬", "duration": 5, "xp": 10, "difficulty": 1},
        {"title": "Active Listener", "description": "Have a 10-minute uninterrupted conversation", "icon": "👂", "duration": 10, "xp": 12, "difficulty": 1},
        {"title": "Kindness Token", "description": "Do a small act of kindness for someone", "icon": "💝", "duration": 5, "xp": 12, "difficulty": 1},
        # Difficulty 2
        {"title": "The Social Guild", "description": "Reach out to a friend you haven't spoken to", "icon": "📞", "duration": 15, "xp": 20, "difficulty": 2},
        {"title": "Quality Time", "description": "Spend 30 minutes of focused time with loved ones", "icon": "👨‍👩‍👧", "duration": 30, "xp": 25, "difficulty": 2},
        {"title": "Appreciation Note", "description": "Write a heartfelt thank you message", "icon": "💌", "duration": 10, "xp": 18, "difficulty": 2},
        # Difficulty 3
        {"title": "Deep Connection", "description": "Have a meaningful 1-hour conversation", "icon": "🤝", "duration": 60, "xp": 35, "difficulty": 3},
        {"title": "Community Builder", "description": "Organize or attend a social gathering", "icon": "🎉", "duration": 120, "xp": 50, "difficulty": 3},
    ],
    StatType.PROSPERITY: [
        # Difficulty 1
        {"title": "Budget Check", "description": "Review your expenses for 10 minutes", "icon": "📊", "duration": 10, "xp": 12, "difficulty": 1},
        {"title": "Career Reflection", "description": "Write down one professional goal", "icon": "🎯", "duration": 5, "xp": 10, "difficulty": 1},
        {"title": "Skill Spotlight", "description": "Identify one skill to develop", "icon": "💡", "duration": 5, "xp": 8, "difficulty": 1},
        # Difficulty 2
        {"title": "Network Builder", "description": "Connect with a professional contact", "icon": "🤝", "duration": 15, "xp": 20, "difficulty": 2},
        {"title": "Learning Investment", "description": "Take an online course lesson", "icon": "🎓", "duration": 30, "xp": 25, "difficulty": 2},
        {"title": "Side Quest", "description": "Work on a side project for 30 minutes", "icon": "💼", "duration": 30, "xp": 25, "difficulty": 2},
        # Difficulty 3
        {"title": "Financial Planning", "description": "Create or update your budget plan", "icon": "💰", "duration": 45, "xp": 35, "difficulty": 3},
        {"title": "Career Advancement", "description": "Work on resume or portfolio for 1 hour", "icon": "📈", "duration": 60, "xp": 45, "difficulty": 3},
    ],
    StatType.MASTERY: [
        # Difficulty 1
        {"title": "Daily Practice", "description": "Practice a skill for 10 minutes", "icon": "🎸", "duration": 10, "xp": 12, "difficulty": 1},
        {"title": "Creative Spark", "description": "Spend 10 minutes on a creative hobby", "icon": "🎨", "duration": 10, "xp": 12, "difficulty": 1},
        {"title": "Tool Time", "description": "Learn one new feature of a tool you use", "icon": "🔧", "duration": 10, "xp": 10, "difficulty": 1},
        # Difficulty 2
        {"title": "The Artisan's Trial", "description": "Spend 30 minutes on a creative hobby", "icon": "🖌️", "duration": 30, "xp": 22, "difficulty": 2},
        {"title": "Project Progress", "description": "Work on a personal project for 30 minutes", "icon": "🛠️", "duration": 30, "xp": 25, "difficulty": 2},
        {"title": "Skill Builder", "description": "Complete a tutorial or lesson in your craft", "icon": "📚", "duration": 30, "xp": 22, "difficulty": 2},
        # Difficulty 3
        {"title": "Deep Work", "description": "Focus on mastery practice for 1 hour", "icon": "⚒️", "duration": 60, "xp": 40, "difficulty": 3},
        {"title": "Creation Complete", "description": "Finish a small creative project", "icon": "✨", "duration": 90, "xp": 50, "difficulty": 3},
    ],
}

# Weekly quest templates
WEEKLY_TEMPLATES = [
    {"title": "Knowledge Marathon", "description": "Read for a total of 2 hours this week", "icon": "📚", "stat": StatType.INTELLECT, "xp": 100, "difficulty": 3},
    {"title": "Fitness Journey", "description": "Exercise 4 times this week", "icon": "💪", "stat": StatType.VITALITY, "xp": 120, "difficulty": 3},
    {"title": "Inner Peace Week", "description": "Meditate every day this week", "icon": "🧘", "stat": StatType.SPIRIT, "xp": 100, "difficulty": 3},
    {"title": "Social Butterfly", "description": "Connect with 3 different friends this week", "icon": "💝", "stat": StatType.BONDS, "xp": 100, "difficulty": 3},
    {"title": "Career Focus", "description": "Dedicate 3 hours to professional development", "icon": "💰", "stat": StatType.PROSPERITY, "xp": 110, "difficulty": 3},
    {"title": "Craft Master", "description": "Practice your craft for 3 hours total", "icon": "🎯", "stat": StatType.MASTERY, "xp": 100, "difficulty": 3},
]


class QuestGenerator:
    """Generates personalized quests based on character state."""
    
    def __init__(self):
        self.templates = QUEST_TEMPLATES
        self.weekly_templates = WEEKLY_TEMPLATES
    
    def generate_daily_quests(self, character: Character, count: int = 5) -> list[Quest]:
        """Generate a set of daily quests for the character."""
        quests = []
        
        # Calculate stat priorities based on gap between current and target
        stat_priorities = self._calculate_stat_priorities(character)
        
        # Determine difficulty based on character's challenge preference
        max_difficulty = min(3, character.challenge_level)
        
        # Generate quests weighted by stat priority
        used_templates = set()
        
        for _ in range(count):
            # Pick a stat based on priority weights
            stat_type = self._weighted_stat_choice(stat_priorities)
            
            # Get available templates for this stat
            available = [
                t for t in self.templates.get(stat_type, [])
                if t["difficulty"] <= max_difficulty
                and t["duration"] <= character.available_time_minutes
                and (stat_type.value, t["title"]) not in used_templates
            ]
            
            if not available:
                # Fallback to any stat
                for st in StatType:
                    available = [
                        t for t in self.templates.get(st, [])
                        if t["difficulty"] <= max_difficulty
                        and t["duration"] <= character.available_time_minutes
                        and (st.value, t["title"]) not in used_templates
                    ]
                    if available:
                        stat_type = st
                        break
            
            if available:
                template = random.choice(available)
                used_templates.add((stat_type.value, template["title"]))
                
                quest = Quest(
                    title=template["title"],
                    description=template["description"],
                    icon=template["icon"],
                    quest_type=QuestType.DAILY,
                    status=QuestStatus.AVAILABLE,
                    primary_stat=stat_type,
                    xp_reward=template["xp"],
                    duration_minutes=template["duration"],
                    difficulty=template["difficulty"],
                    is_recurring=True,
                    expires_at=datetime.now() + timedelta(days=1),
                )
                quests.append(quest)
        
        return quests
    
    def generate_weekly_quest(self, character: Character) -> Optional[Quest]:
        """Generate a weekly quest."""
        stat_priorities = self._calculate_stat_priorities(character)
        
        # Pick highest priority stat
        top_stat = max(stat_priorities.items(), key=lambda x: x[1])[0]
        
        # Find a weekly template for this stat
        matching = [t for t in self.weekly_templates if t["stat"] == top_stat]
        
        if not matching:
            matching = self.weekly_templates
        
        template = random.choice(matching)
        
        return Quest(
            title=template["title"],
            description=template["description"],
            icon=template["icon"],
            quest_type=QuestType.WEEKLY,
            status=QuestStatus.AVAILABLE,
            primary_stat=template["stat"],
            xp_reward=template["xp"],
            duration_minutes=0,  # Not applicable for weekly
            difficulty=template["difficulty"],
            is_recurring=False,
            expires_at=datetime.now() + timedelta(days=7),
        )
    
    def generate_random_encounter(self, character: Character) -> Quest:
        """Generate a random encounter quest with bonus XP."""
        stat_type = random.choice(list(StatType))
        
        # Random encounters are lower difficulty but time-limited
        available = [
            t for t in self.templates.get(stat_type, [])
            if t["difficulty"] <= 2
        ]
        
        if not available:
            available = self.templates[StatType.INTELLECT]
        
        template = random.choice(available)
        
        # Bonus XP for random encounters
        bonus_xp = int(template["xp"] * 0.5)
        
        return Quest(
            title=f"⚡ {template['title']}",
            description=f"{template['description']} (Bonus XP!)",
            icon="🎲",
            quest_type=QuestType.RANDOM,
            status=QuestStatus.AVAILABLE,
            primary_stat=stat_type,
            xp_reward=template["xp"] + bonus_xp,
            duration_minutes=template["duration"],
            difficulty=template["difficulty"],
            is_recurring=False,
            expires_at=datetime.now() + timedelta(hours=4),  # Short expiry
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

