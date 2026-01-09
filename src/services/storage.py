"""SQLite storage service for persistent data."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import os

from models.character import Character
from models.quest import Quest, QuestStatus
from models.achievement import Achievement, create_default_achievements
from models.stats import StatType


class StorageService:
    """Handles all data persistence using SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize storage with database path."""
        if db_path is None:
            # Use app data directory
            data_dir = Path.home() / ".abitus"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "abitus.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Character table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Quests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                status TEXT NOT NULL,
                quest_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                is_unlocked INTEGER NOT NULL DEFAULT 0,
                unlocked_at TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Journal table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Character methods
    def save_character(self, character: Character):
        """Save or update character."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = json.dumps(character.to_dict())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO character (id, data, updated_at)
            VALUES (?, ?, ?)
        """, (character.id, data, now))
        
        conn.commit()
        conn.close()
    
    def load_character(self) -> Optional[Character]:
        """Load the player's character (there's only one)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM character LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row["data"])
            return Character.from_dict(data)
        return None
    
    def delete_character(self):
        """Delete all character data (for reset)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM character")
        conn.commit()
        conn.close()
    
    # Quest methods
    def save_quest(self, quest: Quest):
        """Save or update a quest."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = json.dumps(quest.to_dict())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO quests (id, data, status, quest_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (quest.id, data, quest.status.value, quest.quest_type.value, 
              quest.created_at.isoformat(), now))
        
        conn.commit()
        conn.close()
    
    def save_quests(self, quests: list[Quest]):
        """Save multiple quests at once."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        for quest in quests:
            data = json.dumps(quest.to_dict())
            cursor.execute("""
                INSERT OR REPLACE INTO quests (id, data, status, quest_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (quest.id, data, quest.status.value, quest.quest_type.value,
                  quest.created_at.isoformat(), now))
        
        conn.commit()
        conn.close()
    
    def load_quest(self, quest_id: str) -> Optional[Quest]:
        """Load a specific quest by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM quests WHERE id = ?", (quest_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row["data"])
            return Quest.from_dict(data)
        return None
    
    def load_quests(self, status: Optional[QuestStatus] = None, 
                    quest_type: Optional[str] = None) -> list[Quest]:
        """Load quests with optional filtering."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT data FROM quests WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if quest_type:
            query += " AND quest_type = ?"
            params.append(quest_type)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        quests = []
        for row in rows:
            data = json.loads(row["data"])
            quests.append(Quest.from_dict(data))
        
        return quests
    
    def load_active_quests(self) -> list[Quest]:
        """Load all active quests."""
        return self.load_quests(status=QuestStatus.ACTIVE)
    
    def load_available_quests(self) -> list[Quest]:
        """Load all available quests."""
        return self.load_quests(status=QuestStatus.AVAILABLE)
    
    def delete_quest(self, quest_id: str):
        """Delete a quest."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quests WHERE id = ?", (quest_id,))
        conn.commit()
        conn.close()
    
    def clear_completed_quests(self):
        """Clear all completed non-recurring quests."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM quests 
            WHERE status = ? 
            AND data NOT LIKE '%"is_recurring": true%'
        """, (QuestStatus.COMPLETED.value,))
        conn.commit()
        conn.close()
    
    # Achievement methods
    def save_achievement(self, achievement: Achievement):
        """Save or update an achievement."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = json.dumps(achievement.to_dict())
        now = datetime.now().isoformat()
        unlocked_at = achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO achievements (id, data, is_unlocked, unlocked_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (achievement.id, data, int(achievement.is_unlocked), unlocked_at, now))
        
        conn.commit()
        conn.close()
    
    def save_achievements(self, achievements: list[Achievement]):
        """Save multiple achievements at once."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        for achievement in achievements:
            data = json.dumps(achievement.to_dict())
            unlocked_at = achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
            cursor.execute("""
                INSERT OR REPLACE INTO achievements (id, data, is_unlocked, unlocked_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (achievement.id, data, int(achievement.is_unlocked), unlocked_at, now))
        
        conn.commit()
        conn.close()
    
    def load_achievements(self) -> list[Achievement]:
        """Load all achievements."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM achievements ORDER BY is_unlocked DESC, id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            # Initialize with default achievements
            defaults = create_default_achievements()
            self.save_achievements(defaults)
            return defaults
        
        achievements = []
        for row in rows:
            data = json.loads(row["data"])
            achievements.append(Achievement.from_dict(data))
        
        return achievements
    
    def load_unlocked_achievements(self) -> list[Achievement]:
        """Load only unlocked achievements."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM achievements WHERE is_unlocked = 1 ORDER BY unlocked_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        achievements = []
        for row in rows:
            data = json.loads(row["data"])
            achievements.append(Achievement.from_dict(data))
        
        return achievements
    
    # Settings methods
    def save_setting(self, key: str, value: str):
        """Save a setting."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, value))
        
        conn.commit()
        conn.close()
    
    def load_setting(self, key: str, default: str = "") -> str:
        """Load a setting."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row["value"] if row else default
    
    def reset_all_data(self):
        """Reset all data (nuclear option)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM character")
        cursor.execute("DELETE FROM quests")
        cursor.execute("DELETE FROM achievements")
        cursor.execute("DELETE FROM settings")
        cursor.execute("DELETE FROM journal")
        
        conn.commit()
        conn.close()
    
    # Journal methods
    def save_journal(self, entries_data: list[dict]):
        """Save all journal entries (replaces existing)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Clear existing entries and save new ones
        cursor.execute("DELETE FROM journal")
        
        now = datetime.now().isoformat()
        data = json.dumps(entries_data)
        
        cursor.execute("""
            INSERT INTO journal (id, data, updated_at)
            VALUES (?, ?, ?)
        """, ("journal_data", data, now))
        
        conn.commit()
        conn.close()
    
    def load_journal(self) -> list[dict]:
        """Load all journal entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM journal WHERE id = 'journal_data'")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row["data"])
        return []

