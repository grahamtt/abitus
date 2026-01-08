"""Progression service for leveling and achievements."""

from typing import Optional
from datetime import datetime

from models.character import Character
from models.quest import Quest
from models.achievement import Achievement, AchievementType
from models.stats import StatType


class ProgressionService:
    """Handles character progression and achievement tracking."""
    
    def __init__(self):
        self.pending_notifications: list[dict] = []
    
    def complete_quest(self, character: Character, quest: Quest, 
                       achievements: list[Achievement]) -> dict:
        """
        Process quest completion and return results.
        
        Returns:
            dict with keys:
            - xp_gained: dict[StatType, int]
            - levels_gained: dict[StatType, int]
            - achievements_unlocked: list[Achievement]
        """
        results = {
            "xp_gained": {},
            "levels_gained": {},
            "achievements_unlocked": [],
        }
        
        # Complete the quest and get rewards
        rewards = quest.complete()
        
        # Apply XP to character
        for stat_type, xp in rewards.items():
            old_level = character.stats[stat_type].level
            character.add_xp(stat_type, xp)
            new_level = character.stats[stat_type].level
            
            results["xp_gained"][stat_type] = xp
            
            if new_level > old_level:
                results["levels_gained"][stat_type] = new_level - old_level
        
        # Update character stats
        character.complete_quest()
        character.title = character.get_title()
        
        # Check achievements
        newly_unlocked = self.check_achievements(character, achievements)
        results["achievements_unlocked"] = newly_unlocked
        
        return results
    
    def check_achievements(self, character: Character, 
                           achievements: list[Achievement]) -> list[Achievement]:
        """Check and unlock any achievements that have been earned."""
        newly_unlocked = []
        
        for achievement in achievements:
            if achievement.is_unlocked:
                continue
            
            unlocked = self._check_single_achievement(character, achievement)
            if unlocked:
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_single_achievement(self, character: Character, 
                                   achievement: Achievement) -> bool:
        """Check if a single achievement should be unlocked."""
        
        # Quest completion achievements
        if achievement.achievement_type == AchievementType.QUEST:
            if achievement.update_progress(character.total_quests_completed):
                return True
        
        # Streak achievements
        elif achievement.achievement_type == AchievementType.STREAK:
            # Check both current and longest streak
            best_streak = max(character.current_streak, character.longest_streak)
            if achievement.update_progress(best_streak):
                return True
        
        # Level milestones (any stat)
        elif achievement.achievement_type == AchievementType.MILESTONE:
            if "XP" in achievement.requirement_description:
                # XP milestone
                if achievement.update_progress(character.total_xp):
                    return True
            else:
                # Level milestone - check highest stat
                highest_level = character.highest_stat.level
                if achievement.update_progress(highest_level):
                    return True
        
        # Balance achievements (all stats at level)
        elif achievement.achievement_type == AchievementType.BALANCE:
            min_level = character.lowest_stat.level
            if achievement.update_progress(min_level):
                return True
        
        # Mastery achievements (single stat excellence)
        elif achievement.achievement_type == AchievementType.MASTERY:
            highest_level = character.highest_stat.level
            if achievement.update_progress(highest_level):
                return True
        
        return False
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a level."""
        if level <= 1:
            return 0
        return int(100 * ((level - 1) ** 1.5))
    
    def calculate_level_from_xp(self, xp: int) -> int:
        """Calculate level from total XP."""
        if xp <= 0:
            return 1
        level = int((xp / 100) ** (1/1.5)) + 1
        return max(1, min(level, 99))
    
    def get_stat_recommendation(self, character: Character) -> StatType:
        """Get recommendation for which stat to focus on."""
        # Find the stat with largest gap between target and current
        max_gap = -1
        recommended = StatType.INTELLECT
        
        for stat_type, stat in character.stats.items():
            gap = stat.target_level - stat.level
            if gap > max_gap:
                max_gap = gap
                recommended = stat_type
        
        return recommended
    
    def get_balance_score(self, character: Character) -> float:
        """
        Calculate how balanced the character's stats are.
        Returns 0-100 where 100 is perfectly balanced.
        """
        levels = [stat.level for stat in character.stats.values()]
        avg = sum(levels) / len(levels)
        
        if avg == 0:
            return 100.0
        
        # Calculate variance
        variance = sum((level - avg) ** 2 for level in levels) / len(levels)
        std_dev = variance ** 0.5
        
        # Convert to 0-100 score (lower deviation = higher score)
        # Max reasonable deviation is about half the average
        max_dev = avg / 2
        if max_dev == 0:
            return 100.0
        
        score = max(0, 100 - (std_dev / max_dev * 100))
        return round(score, 1)
    
    def get_next_achievement(self, character: Character, 
                             achievements: list[Achievement]) -> Optional[Achievement]:
        """Get the closest achievement to being unlocked."""
        locked = [a for a in achievements if not a.is_unlocked and not a.is_hidden]
        
        if not locked:
            return None
        
        # Find the one with highest progress
        return max(locked, key=lambda a: a.progress_percent)
    
    def estimate_time_to_level(self, stat: "Stat", avg_xp_per_day: int = 50) -> int:
        """Estimate days until next level based on average XP gain."""
        xp_needed = stat.xp_remaining
        
        if avg_xp_per_day <= 0:
            return 999
        
        return max(1, xp_needed // avg_xp_per_day)

