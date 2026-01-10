"""
Abitus RPG - Level up your real life through epic quests
Main application entry point.
"""

import flet as ft
from datetime import datetime, timedelta

from utils.compat import colors, icons
from models.character import Character
from models.quest import Quest, QuestStatus, SatisfactionType
from models.achievement import Achievement, create_default_achievements
from models.stats import StatType

from services.storage import StorageService
from services.quest_generator import QuestGenerator
from services.progression import ProgressionService
from services.journal import JournalService

from views.home import HomeView
from views.character import CharacterView
from views.quests import QuestsView
from views.interview import InterviewView
from views.settings import SettingsView
from views.journal import JournalView
from views.custom_quest import CustomQuestView

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
        self.journal_service = JournalService()
        
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
                background="#1a1a2e",
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
    
    def _on_nav_change(self, e):
        """Handle bottom navigation bar changes."""
        index = e.control.selected_index
        if index == 0:
            self.show_home()
        elif index == 1:
            self.show_journal()
        elif index == 2:
            self.show_quests()
        elif index == 3:
            self.show_character()
        elif index == 4:
            self.show_settings()
    
    def load_data(self):
        """Load all data from storage."""
        self.character = self.storage.load_character()
        self.achievements = self.storage.load_achievements()
        self.quests = self.storage.load_quests()
        
        # Load journal entries
        journal_data = self.storage.load_journal()
        if journal_data:
            self.journal_service.load_entries(journal_data)
        
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
            on_write_entry=self.show_journal_for_quest,
            on_log_progress=self.show_log_progress_dialog,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=home,
                expand=True,
            )
        )
        # Add bottom navigation with Journal and Settings
        self.page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=icons.HOME_OUTLINED,
                    selected_icon=icons.HOME,
                    label="Home",
                ),
                ft.NavigationBarDestination(
                    icon=icons.BOOK_OUTLINED,
                    selected_icon=icons.BOOK,
                    label="Journal",
                ),
                ft.NavigationBarDestination(
                    icon=icons.ASSIGNMENT_OUTLINED,
                    selected_icon=icons.ASSIGNMENT,
                    label="Quests",
                ),
                ft.NavigationBarDestination(
                    icon=icons.PERSON_OUTLINED,
                    selected_icon=icons.PERSON,
                    label="Character",
                ),
                ft.NavigationBarDestination(
                    icon=icons.SETTINGS_OUTLINED,
                    selected_icon=icons.SETTINGS,
                    label="Settings",
                ),
            ],
            selected_index=0,
            on_change=self._on_nav_change,
        )
        self.page.floating_action_button = None
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
        if self.page.navigation_bar:
            self.page.navigation_bar.selected_index = 3
        self.page.update()
    
    def show_quests(self):
        """Show the quest log."""
        self.current_view = "quests"
        
        # Check weekly resets for custom quests
        for quest in self.quests:
            if quest.is_custom:
                quest.check_weekly_reset()
                self.storage.save_quest(quest)
        
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
            on_write_entry=self.show_journal_for_quest,
            on_log_progress=self.show_log_progress_dialog,
            on_create_custom_quest=self.show_create_custom_quest,
            on_edit_custom_quest=self.show_edit_custom_quest,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=quests_view,
                expand=True,
            )
        )
        self.page.floating_action_button = None
        if self.page.navigation_bar:
            self.page.navigation_bar.selected_index = 2
        self.page.update()
    
    def show_create_custom_quest(self):
        """Show the custom quest creation view."""
        self.current_view = "create_custom_quest"
        
        custom_quest_view = CustomQuestView(
            on_save=self.save_custom_quest,
            on_cancel=self.show_quests,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=custom_quest_view,
                expand=True,
            )
        )
        self.page.navigation_bar = None
        self.page.update()
    
    def show_edit_custom_quest(self, quest: Quest):
        """Show the custom quest edit view."""
        self.current_view = "edit_custom_quest"
        
        custom_quest_view = CustomQuestView(
            on_save=self.save_custom_quest,
            on_cancel=self.show_quests,
            on_delete=self.delete_custom_quest,
            existing_quest=quest,
        )
        
        self.page.clean()
        self.page.add(
            ft.SafeArea(
                content=custom_quest_view,
                expand=True,
            )
        )
        self.page.navigation_bar = None
        self.page.update()
    
    def save_custom_quest(self, quest: Quest):
        """Save a new or edited custom quest."""
        # Check if it's a new quest (not in our list)
        existing = next((q for q in self.quests if q.id == quest.id), None)
        
        if existing:
            # Update existing quest in list
            idx = self.quests.index(existing)
            self.quests[idx] = quest
        else:
            # Add new quest
            self.quests.append(quest)
        
        # Save to storage
        self.storage.save_quest(quest)
        
        # Show success message
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"✨ Quest '{quest.title}' saved!"),
            bgcolor="#22c55e",
        )
        self.page.snack_bar.open = True
        
        # Go back to quests view
        self.show_quests()
    
    def delete_custom_quest(self, quest: Quest):
        """Delete a custom quest."""
        # Remove from list
        self.quests = [q for q in self.quests if q.id != quest.id]
        
        # Remove from storage
        self.storage.delete_quest(quest.id)
        
        # Show message
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Quest '{quest.title}' deleted"),
        )
        self.page.snack_bar.open = True
        
        # Go back to quests view
        self.show_quests()
    
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
        if self.page.navigation_bar:
            self.page.navigation_bar.selected_index = 4
        self.page.update()
    
    def show_journal(self, initial_entry_type=None, completed_quest_context=None):
        """Show the journal view, optionally starting a new entry of a specific type."""
        self.current_view = "journal"
        
        active_quests = [q for q in self.quests if q.status == QuestStatus.ACTIVE]
        
        journal_view = JournalView(
            journal_service=self.journal_service,
            active_quests=active_quests,
            on_entry_saved=self.on_journal_entry_saved,
            on_back=self.show_home,
            initial_entry_type=initial_entry_type,
            completed_quest_context=completed_quest_context,
        )
        
        self.page.clean()
        self.page.add(
        ft.SafeArea(
                content=journal_view,
            expand=True,
            )
        )
        self.page.floating_action_button = None
        if self.page.navigation_bar:
            self.page.navigation_bar.selected_index = 1
        self.page.update()
    
    def show_journal_for_quest(self, quest: Quest):
        """Open journal with the entry type needed to satisfy a quest."""
        from models.journal import JournalEntryType
        from models.quest import SatisfactionType
        
        # Map satisfaction types to journal entry types
        satisfaction_to_entry = {
            SatisfactionType.JOURNAL_ANY: JournalEntryType.FREE_FORM,
            SatisfactionType.JOURNAL_GRATITUDE: JournalEntryType.GRATITUDE,
            SatisfactionType.JOURNAL_REFLECTION: JournalEntryType.REFLECTION,
            SatisfactionType.JOURNAL_EMOTION: JournalEntryType.EMOTION,
            SatisfactionType.JOURNAL_GOAL: JournalEntryType.GOAL,
            SatisfactionType.JOURNAL_LESSON: JournalEntryType.LESSON,
        }
        
        entry_type = satisfaction_to_entry.get(quest.satisfied_by, JournalEntryType.FREE_FORM)
        self.show_journal(initial_entry_type=entry_type)
    
    def on_journal_entry_saved(self, entry, satisfied_quests):
        """Handle journal entry saved - complete any satisfied quests."""
        for quest in satisfied_quests:
            if quest.can_complete:
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
                
                # Show notifications
                if results["levels_gained"]:
                    self.show_level_up_notification(results["levels_gained"])
                
                for achievement in results["achievements_unlocked"]:
                    self.show_achievement_notification(achievement)
        
        # Save journal entries
        self.storage.save_journal(self.journal_service.save_entries())
        
        # Show completion message if any quests were satisfied
        if satisfied_quests:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✨ Quest completed: {satisfied_quests[0].title}!"),
                bgcolor=colors.GREEN_700,
            )
            self.page.snack_bar.open = True
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
        
        # Handle custom quest weekly tracking
        if quest.is_custom and quest.weekly_target > 0:
            quest.record_weekly_completion()
            
            # Reset quest to available for repeated completion (until weekly target met)
            if not quest.weekly_target_met:
                quest.status = QuestStatus.AVAILABLE
                quest.accepted_at = None
                quest.completed_at = None
        
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
        
        # For manual quests, offer to log what was done
        if quest.satisfied_by == SatisfactionType.MANUAL and not quest.is_custom:
            self._show_log_completion_dialog(quest)
            return  # Don't refresh view yet - dialog will handle it
        
        # Show weekly progress for custom quests
        if quest.is_custom and quest.weekly_target > 0:
            if quest.weekly_target_met:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"🎯 Weekly goal met! You did '{quest.title}' {quest.weekly_target} times!"),
                    bgcolor="#22c55e",
                )
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✨ {quest.weekly_progress_display}"),
                    bgcolor="#6366f1",
                )
            self.page.snack_bar.open = True
        
        # Refresh view
        self.refresh_current_view()
    
    def abandon_quest(self, quest: Quest):
        """Abandon an active quest."""
        quest.abandon()
        self.storage.save_quest(quest)
        self.refresh_current_view()
    
    def _show_log_completion_dialog(self, quest: Quest):
        """Show a dialog offering to log what was done for a completed quest."""
        from models.journal import JournalEntryType
        
        def close_and_refresh(e=None):
            dialog.open = False
            self.page.update()
            self.refresh_current_view()
        
        def log_in_journal(e):
            dialog.open = False
            self.page.update()
            # Navigate to journal with quest context
            self._show_journal_for_completed_quest(quest)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Text("✨", size=24),
                    ft.Text("Quest Complete!", weight=ft.FontWeight.W_600),
                ],
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"You completed: {quest.title}",
                        size=14,
                    ),
                    ft.Text(
                        f"+{quest.xp_reward} XP earned!",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color="#f59e0b",
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Would you like to write about what you did?",
                        size=13,
                        color=colors.with_opacity(0.8, colors.ON_SURFACE),
                    ),
                    ft.Text(
                        "Recording your activities helps track your journey.",
                        size=12,
                        color=colors.with_opacity(0.6, colors.ON_SURFACE),
                        italic=True,
                    ),
                ],
            ),
            actions=[
                ft.TextButton("Skip", on_click=close_and_refresh),
                ft.ElevatedButton(
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(icons.EDIT_NOTE, size=18),
                            ft.Text("Write Entry"),
                        ],
                    ),
                    on_click=log_in_journal,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_journal_for_completed_quest(self, quest: Quest):
        """Open journal with context pre-filled for a completed quest."""
        from models.journal import JournalEntryType
        
        self.show_journal(
            initial_entry_type=JournalEntryType.LESSON,
            completed_quest_context=quest,
        )
    
    def show_log_progress_dialog(self, quest: Quest):
        """Show a dialog to log incremental progress for a quest."""
        if not quest.progress_trackable:
            return
        
        # Create text field for amount
        amount_field = ft.TextField(
            label=f"Add {quest.progress_unit}",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text=f"e.g. 15",
            autofocus=True,
            expand=True,
        )
        
        # Quick add buttons for common amounts
        quick_amounts = [5, 10, 15, 30] if "minute" in quest.progress_unit.lower() else [1, 2, 5]
        
        def close_dialog(e=None):
            dialog.open = False
            self.page.update()
        
        def add_progress(amount: float):
            was_complete = quest.is_progress_complete
            target_reached = quest.add_progress(amount)
            
            # Save the updated quest
            self.storage.save_quest(quest)
            
            # Close dialog first
            dialog.open = False
            self.page.update()
            
            # If target reached, show a notification
            if target_reached:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"🎯 Target reached! You can now complete '{quest.title}'"),
                    bgcolor="#22c55e",
                )
                self.page.snack_bar.open = True
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"📝 Progress logged: {quest.progress_display}"),
                )
                self.page.snack_bar.open = True
            
            # Refresh view
            self.refresh_current_view()
        
        def log_custom_amount(e):
            try:
                amount = float(amount_field.value or 0)
                if amount > 0:
                    add_progress(amount)
            except ValueError:
                pass
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"📝 Log Progress"),
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    ft.Text(
                        quest.title,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        f"Current: {quest.progress_display}",
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                    # Progress bar
                    ft.Container(
                        content=ft.ProgressBar(
                            value=quest.progress_percentage / 100,
                            color="#22c55e",
                            bgcolor=colors.with_opacity(0.2, colors.ON_SURFACE),
                        ),
                        height=8,
                        border_radius=4,
                    ),
                    ft.Divider(),
                    # Quick add buttons
                    ft.Text(
                        "Quick add:",
                        size=12,
                        color=colors.with_opacity(0.6, colors.ON_SURFACE),
                    ),
                    ft.Row(
                        spacing=8,
                        wrap=True,
                        controls=[
                            ft.OutlinedButton(
                                f"+{amt}",
                                on_click=lambda e, a=amt: add_progress(a),
                            )
                            for amt in quick_amounts
                        ],
                    ),
                    ft.Divider(),
                    # Custom amount
                    ft.Text(
                        "Or enter custom amount:",
                        size=12,
                        color=colors.with_opacity(0.6, colors.ON_SURFACE),
                    ),
                    amount_field,
                ],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Log Progress",
                    on_click=log_custom_amount,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
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
        elif self.current_view == "journal":
            self.show_journal()
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
                                    color=colors.WHITE,
                                ),
                                ft.Text(
                                    f"{stat_def.name} is now Level {new_level}!",
                                    size=13,
                                    color=colors.with_opacity(0.9, colors.WHITE),
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
                                color=colors.WHITE,
                            ),
                            ft.Text(
                                achievement.name,
                                size=13,
                                color=colors.with_opacity(0.9, colors.WHITE),
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
            dialog.open = False
            self.page.update()
        
        def do_reset(e):
            dialog.open = False
            self.page.update()
            self.reset_all_data()
        
        dialog = ft.AlertDialog(
            modal=True,
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
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                ],
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Reset Everything",
                    bgcolor=colors.ERROR,
                    color=colors.WHITE,
                    on_click=do_reset,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def reset_all_data(self):
        """Reset all data and restart with assessment."""
        # Clear all stored data
        self.storage.reset_all_data()
        
        # Clear in-memory data
        self.character = None
        self.achievements = []
        self.quests = []
        
        # Show assessment/interview
        self.show_assessment()


def main(page: ft.Page):
    """Application entry point."""
    AbitusApp(page)


# Run the app
ft.app(target=main)
