"""
Abitus RPG - Level up your real life through epic quests
Main application entry point.
"""

import flet as ft
from datetime import datetime, timedelta

from models.character import Character
from models.quest import Quest, QuestStatus
from models.achievement import Achievement, create_default_achievements
from models.stats import StatType

from services.storage import StorageService
from services.quest_generator import QuestGenerator
from services.progression import ProgressionService

from views.home import HomeView
from views.character import CharacterView
from views.quests import QuestsView
from views.interview import InterviewView
from views.settings import SettingsView

from components.achievement_badge import AchievementNotification


# Feature flag: use new interview-based assessment
USE_NEW_INTERVIEW = True


class AbitusApp:
    """Main application controller."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # Initialize services
        self.storage = StorageService()
        self.quest_generator = QuestGenerator()
        self.progression = ProgressionService()
        
        # Load or initialize data
        self.character: Character | None = None
        self.achievements: list[Achievement] = []
        self.quests: list[Quest] = []
        
        # Current view
        self.current_view = "home"
        
        # Load data and start
        self.load_data()
        self.show_initial_view()
    
    def setup_page(self):
        """Configure the page settings."""
        self.page.title = "Abitus RPG"
        self.page.theme_mode = ft.ThemeMode.DARK
        
        # Custom theme
        self.page.theme = ft.Theme(
            color_scheme_seed="#6366f1",
            font_family="Segoe UI",
        )
        self.page.dark_theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#6366f1",
                secondary="#a855f7",
                surface="#1a1a2e",
                surface_container_highest="#252542",
                surface_container_high="#1f1f38",
                on_surface="#e2e8f0",
                on_primary="#ffffff",
                error="#ef4444",
            ),
            font_family="Segoe UI",
        )
        
        self.page.padding = 0
        self.page.spacing = 0
        
        # Handle window resize
        self.page.on_resized = self.on_resize
    
    def on_resize(self, e):
        """Handle window resize."""
        self.page.update()
    
    def load_data(self):
        """Load all data from storage."""
        self.character = self.storage.load_character()
        self.achievements = self.storage.load_achievements()
        self.quests = self.storage.load_quests()
        
        # Check if we need to generate new daily quests
        if self.character and self.character.assessment_completed:
            self.refresh_daily_quests()
    
    def save_data(self):
        """Save all data to storage."""
        if self.character:
            self.storage.save_character(self.character)
        self.storage.save_achievements(self.achievements)
        self.storage.save_quests(self.quests)
    
    def show_initial_view(self):
        """Show the appropriate initial view."""
        if self.character and self.character.assessment_completed:
            self.show_home()
        else:
            self.show_assessment()
    
    def show_assessment(self):
        """Show the initial assessment/interview flow."""
        self.current_view = "assessment"
        
        if USE_NEW_INTERVIEW:
            # Use new interview-based assessment
            assessment = InterviewView(
                on_complete=self.on_assessment_complete,
            )
        else:
            # Use legacy slider-based assessment
            from views.assessment import AssessmentView
            assessment = AssessmentView(
                on_complete=self.on_assessment_complete,
            )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=assessment,
                expand=True,
            )
        )
        self.page.floating_action_button = None
        self.page.update()
    
    def on_assessment_complete(self, character: Character):
        """Handle assessment completion."""
        self.character = character
        self.storage.save_character(character)
        
        # Initialize default achievements if needed
        if not self.achievements:
            self.achievements = create_default_achievements()
            self.storage.save_achievements(self.achievements)
        
        # Generate initial quests
        self.refresh_daily_quests()
        
        # Show home
        self.show_home()
    
    def show_home(self):
        """Show the home dashboard."""
        self.current_view = "home"
        
        active_quests = [q for q in self.quests if q.status == QuestStatus.ACTIVE]
        available_quests = [q for q in self.quests if q.status == QuestStatus.AVAILABLE]
        
        home = HomeView(
            character=self.character,
            active_quests=active_quests,
            available_quests=available_quests,
            on_quest_accept=self.accept_quest,
            on_quest_complete=self.complete_quest,
            on_quest_abandon=self.abandon_quest,
            on_view_all_quests=self.show_quests,
            on_view_character=self.show_character,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=home,
                expand=True,
            )
        )
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.SETTINGS,
            bgcolor="#6366f1",
            on_click=lambda e: self.show_settings(),
        )
        self.page.update()
    
    def show_character(self):
        """Show the character sheet."""
        self.current_view = "character"
        
        character_view = CharacterView(
            character=self.character,
            achievements=self.achievements,
            on_back=self.show_home,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=character_view,
                expand=True,
            )
        )
        self.page.floating_action_button = None
        self.page.update()
    
    def show_quests(self):
        """Show the quest log."""
        self.current_view = "quests"
        
        active = [q for q in self.quests if q.status == QuestStatus.ACTIVE]
        available = [q for q in self.quests if q.status == QuestStatus.AVAILABLE]
        completed = [q for q in self.quests if q.status == QuestStatus.COMPLETED]
        
        quests_view = QuestsView(
            active_quests=active,
            available_quests=available,
            completed_quests=completed,
            on_quest_accept=self.accept_quest,
            on_quest_complete=self.complete_quest,
            on_quest_abandon=self.abandon_quest,
            on_back=self.show_home,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=quests_view,
                expand=True,
            )
        )
        self.page.floating_action_button = None
        self.page.update()
    
    def show_settings(self):
        """Show settings view."""
        self.current_view = "settings"
        
        settings_view = SettingsView(
            character=self.character,
            on_back=self.show_home,
            on_reset_data=self.confirm_reset_data,
            on_update_settings=self.update_settings,
        )
        
        self.page.clean()
        self.page.add(
        ft.SafeArea(
                content=settings_view,
            expand=True,
            )
        )
        self.page.floating_action_button = None
        self.page.update()
    
    def accept_quest(self, quest: Quest):
        """Accept a quest."""
        if quest.accept():
            self.storage.save_quest(quest)
            self.refresh_current_view()
    
    def complete_quest(self, quest: Quest):
        """Complete a quest and award XP."""
        if not quest.can_complete:
            return
        
        # Process completion through progression service
        results = self.progression.complete_quest(
            self.character, 
            quest, 
            self.achievements
        )
        
        # Save updates
        self.storage.save_quest(quest)
        self.storage.save_character(self.character)
        
        # Save any unlocked achievements
        for achievement in results["achievements_unlocked"]:
            self.storage.save_achievement(achievement)
        
        # Show level up notifications
        if results["levels_gained"]:
            self.show_level_up_notification(results["levels_gained"])
        
        # Show achievement notifications
        for achievement in results["achievements_unlocked"]:
            self.show_achievement_notification(achievement)
        
        # Refresh view
        self.refresh_current_view()
    
    def abandon_quest(self, quest: Quest):
        """Abandon an active quest."""
        quest.abandon()
        self.storage.save_quest(quest)
        self.refresh_current_view()
    
    def refresh_daily_quests(self):
        """Refresh daily quests if needed."""
        if not self.character:
            return
        
        # Check if we have any available/active daily quests
        daily_quests = [
            q for q in self.quests 
            if q.quest_type.value == "daily" 
            and q.status in [QuestStatus.AVAILABLE, QuestStatus.ACTIVE]
            and not q.is_expired
        ]
        
        # Generate new quests if we have less than 3 available
        if len(daily_quests) < 3:
            new_quests = self.quest_generator.generate_daily_quests(
                self.character, 
                count=5 - len(daily_quests)
            )
            self.quests.extend(new_quests)
            self.storage.save_quests(new_quests)
        
        # Maybe generate a weekly quest
        weekly_quests = [
            q for q in self.quests 
            if q.quest_type.value == "weekly" 
            and q.status in [QuestStatus.AVAILABLE, QuestStatus.ACTIVE]
        ]
        
        if not weekly_quests:
            weekly = self.quest_generator.generate_weekly_quest(self.character)
            if weekly:
                self.quests.append(weekly)
                self.storage.save_quest(weekly)
        
        # Maybe spawn a random encounter
        if self.quest_generator.should_spawn_random_encounter():
            random_quests = [
                q for q in self.quests 
                if q.quest_type.value == "random" 
                and q.status == QuestStatus.AVAILABLE
            ]
            if not random_quests:
                random_quest = self.quest_generator.generate_random_encounter(self.character)
                self.quests.append(random_quest)
                self.storage.save_quest(random_quest)
    
    def refresh_current_view(self):
        """Refresh the current view."""
        if self.current_view == "home":
            self.show_home()
        elif self.current_view == "character":
            self.show_character()
        elif self.current_view == "quests":
            self.show_quests()
        elif self.current_view == "settings":
            self.show_settings()
    
    def show_level_up_notification(self, levels_gained: dict[StatType, int]):
        """Show level up notification."""
        from models.stats import STAT_DEFINITIONS
        
        for stat_type, levels in levels_gained.items():
            stat_def = STAT_DEFINITIONS[stat_type]
            new_level = self.character.stats[stat_type].level
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    spacing=12,
                    controls=[
                        ft.Text("🎉", size=24),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(
                                    "Level Up!",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    f"{stat_def.name} is now Level {new_level}!",
                                    size=13,
                                    color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                                ),
                            ],
                        ),
                    ],
                ),
                bgcolor=stat_def.color,
                duration=3000,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_achievement_notification(self, achievement: Achievement):
        """Show achievement unlocked notification."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Text(achievement.icon, size=28),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text(
                                "Achievement Unlocked!",
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                achievement.name,
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                    ),
                ],
            ),
            bgcolor=achievement.rarity_color,
            duration=4000,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def update_settings(self, settings: dict):
        """Update character/app settings."""
        if not self.character:
            return
        
        for key, value in settings.items():
            if hasattr(self.character, key):
                setattr(self.character, key, value)
        
        self.storage.save_character(self.character)
    
    def confirm_reset_data(self):
        """Show confirmation dialog for data reset."""
        
        def close_dialog(e):
            if dialog in self.page.overlay:
                self.page.overlay.remove(dialog)
            self.page.update()
        
        def do_reset(e):
            if dialog in self.page.overlay:
                self.page.overlay.remove(dialog)
            self.page.update()
            self.reset_all_data()
        
        dialog = ft.AlertDialog(
            modal=True,
            open=True,
            title=ft.Text("⚠️ Reset All Data?"),
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text(
                        "This will permanently delete:",
                    ),
                    ft.Container(height=8),
                    ft.Text("• Your character and all stats"),
                    ft.Text("• All quest history"),
                    ft.Text("• All achievements"),
                    ft.Text("• Interview responses"),
                    ft.Container(height=8),
                    ft.Text(
                        "You will need to complete the character assessment again.",
                        italic=True,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                    ),
                ],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton(
                    "Reset Everything",
                    bgcolor=ft.Colors.ERROR,
                    color=ft.Colors.WHITE,
                    on_click=do_reset,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        self.page.update()
    
    def reset_all_data(self):
        """Reset all data and restart with assessment."""
        # Clear all stored data
        self.storage.reset_all_data()
        
        # Clear in-memory data
        self.character = None
        self.achievements = []
        self.quests = []
        
        # Clear any overlays
        self.page.overlay.clear()
        
        # Show assessment/interview
        self.show_assessment()


def main(page: ft.Page):
    """Application entry point."""
    AbitusApp(page)


# Run the app
ft.run(main)
