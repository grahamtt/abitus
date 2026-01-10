"""Journal view for reflective writing."""

import flet as ft
from typing import Callable, Optional
from datetime import datetime

from utils.compat import colors, icons
from models.journal import JournalEntry, JournalEntryType, ENTRY_PROMPTS, get_random_prompt
from models.quest import Quest, QuestStatus
from services.journal import JournalService


class JournalView(ft.Container):
    """Journal view for creating and viewing journal entries."""
    
    def __init__(
        self,
        journal_service: JournalService,
        active_quests: list[Quest],
        on_entry_saved: Callable[[JournalEntry, list[Quest]], None],
        on_back: Callable[[], None],
        initial_entry_type: Optional[JournalEntryType] = None,  # Start with new entry of this type
        completed_quest_context: Optional[Quest] = None,  # Quest to write about
    ):
        self.journal_service = journal_service
        self.active_quests = active_quests
        self.on_entry_saved = on_entry_saved
        self.on_back = on_back
        self.completed_quest_context = completed_quest_context
        
        # State - if initial_entry_type provided, start in new entry mode
        self.current_view = "new" if initial_entry_type or completed_quest_context else "list"
        self.selected_entry: Optional[JournalEntry] = None
        self.selected_type = initial_entry_type or JournalEntryType.LESSON if completed_quest_context else JournalEntryType.FREE_FORM
        self.filter_type: Optional[JournalEntryType] = None  # For filtering entries list
        self.mood_before: Optional[int] = None
        self.mood_after: Optional[int] = None
        self.editing_entry: Optional[JournalEntry] = None
        self._preserved_content: Optional[str] = None  # To preserve content during refresh
        
        # Controls
        self.content_field: Optional[ft.TextField] = None
        self.main_content: Optional[ft.Column] = None
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def _build_content(self) -> ft.Control:
        self.main_content = ft.Column(
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=self._get_view_controls(),
        )
        return self.main_content
    
    def _get_view_controls(self) -> list[ft.Control]:
        """Get controls for the current view."""
        if self.current_view == "list":
            return self._build_list_view()
        elif self.current_view == "new":
            return self._build_new_entry_view()
        elif self.current_view == "edit":
            return self._build_edit_entry_view()
        else:
            return self._build_entry_detail_view()
    
    def _refresh_view(self):
        """Refresh the current view."""
        if self.main_content:
            self.main_content.controls = self._get_view_controls()
            self.main_content.update()
    
    def _build_list_view(self) -> list[ft.Control]:
        """Build the journal entries list."""
        entries = self.journal_service.get_entries(limit=50)
        # Filter entries by type if a filter is selected
        if self.filter_type:
            entries = [e for e in entries if e.entry_type == self.filter_type]
        stats = self.journal_service.get_entry_stats()
        
        # Header section
        header = ft.Container(
            content=ft.Column(
                spacing=16,
                controls=[
                    # Title and new entry button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.IconButton(
                                        icon=icons.ARROW_BACK,
                                        on_click=lambda e: self.on_back(),
                                    ),
                                    ft.Text(
                                        "📜 Chronicle",
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.ElevatedButton(
                                "New Entry",
                                icon=icons.EDIT,
                                on_click=lambda e: self._show_new_entry(),
                            ),
                        ],
                    ),
                    # Stats row
                    ft.Row(
                        spacing=16,
                        controls=[
                            self._build_stat_chip(
                                f"🔥 {stats['streak']} day streak" if stats['streak'] > 0 else "Start your streak!",
                                colors.ORANGE_700,
                            ),
                            self._build_stat_chip(
                                f"📝 {stats['total_entries']} entries",
                                colors.BLUE_700,
                            ),
                            self._build_stat_chip(
                                f"✍️ {stats['total_words']:,} words",
                                colors.GREEN_700,
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 20, 20, 16),
            bgcolor=colors.with_opacity(0.05, colors.PRIMARY),
        )
        
        # Journal-satisfiable quests prompt
        journal_quests = [q for q in self.active_quests if q.requires_journal and q.status == QuestStatus.ACTIVE]
        quest_prompt = None
        if journal_quests:
            quest_prompt = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "📋 Active journal quests:",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=colors.AMBER_700,
                        ),
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    f"• {q.title} ({q.satisfaction_description})",
                                    size=13,
                                    color=colors.with_opacity(0.8, colors.ON_SURFACE),
                                )
                                for q in journal_quests[:3]
                            ],
                        ),
                    ],
                ),
                padding=ft.Padding(20, 12, 20, 12),
                bgcolor=colors.with_opacity(0.1, colors.AMBER),
                border_radius=8,
                margin=ft.Margin(20, 0, 20, 16),
            )
        
        # Entry type filters
        type_filter = ft.Container(
            content=ft.Row(
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    self._build_type_chip(None, "All"),
                    self._build_type_chip(JournalEntryType.FREE_FORM, "📝 Free"),
                    self._build_type_chip(JournalEntryType.GRATITUDE, "🙏 Gratitude"),
                    self._build_type_chip(JournalEntryType.REFLECTION, "🪞 Reflection"),
                    self._build_type_chip(JournalEntryType.EMOTION, "💭 Emotion"),
                    self._build_type_chip(JournalEntryType.GOAL, "🎯 Goals"),
                    self._build_type_chip(JournalEntryType.LESSON, "📖 Lessons"),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 16),
        )
        
        # Entries list
        if entries:
            entries_list = ft.Column(
                spacing=12,
                controls=[
                    self._build_entry_card(entry)
                    for entry in entries
                ],
            )
        else:
            entries_list = ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Text("📜", size=64),
                        ft.Text(
                            "Your chronicle awaits",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Begin writing your story by creating your first entry.",
                            size=14,
                            color=colors.with_opacity(0.7, colors.ON_SURFACE),
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Write First Entry",
                            icon=icons.EDIT,
                            on_click=lambda e: self._show_new_entry(),
                        ),
                    ],
                ),
                padding=ft.Padding(40, 60, 40, 60),
                alignment=ft.Alignment(0, 0),
            )
        
        controls = [header]
        if quest_prompt:
            controls.append(quest_prompt)
        controls.append(type_filter)
        controls.append(
            ft.Container(
                content=entries_list,
                padding=ft.Padding(20, 0, 20, 20),
            )
        )
        
        return controls
    
    def _build_new_entry_view(self) -> list[ft.Control]:
        """Build the new entry creation view."""
        # Use special prompt if writing about a completed quest
        if self.completed_quest_context:
            quest = self.completed_quest_context
            prompt = f"You completed '{quest.title}'! What did you do, learn, or experience?"
        else:
            prompt = get_random_prompt(self.selected_type)
        
        # Check which quests this entry type could satisfy
        potential_quests = [
            q for q in self.active_quests
            if q.requires_journal and 
               q.status == QuestStatus.ACTIVE and
               q.can_be_satisfied_by_journal(self.selected_type.value)
        ]
        
        # Header
        header = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.IconButton(
                                icon=icons.CLOSE,
                                on_click=lambda e: self._cancel_entry(),
                            ),
                            ft.Text(
                                "New Entry",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.ElevatedButton(
                        "Save",
                        icon=icons.CHECK,
                        on_click=lambda e: self._save_entry(),
                    ),
                ],
            ),
            padding=ft.Padding(20, 20, 20, 16),
        )
        
        # Entry type selector
        type_selector = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(
                        "Entry Type",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        spacing=8,
                        wrap=True,
                        controls=[
                            self._build_type_selector_chip(JournalEntryType.FREE_FORM, "📝 Free Writing"),
                            self._build_type_selector_chip(JournalEntryType.GRATITUDE, "🙏 Gratitude"),
                            self._build_type_selector_chip(JournalEntryType.REFLECTION, "🪞 Reflection"),
                            self._build_type_selector_chip(JournalEntryType.EMOTION, "💭 Emotion"),
                            self._build_type_selector_chip(JournalEntryType.GOAL, "🎯 Goal"),
                            self._build_type_selector_chip(JournalEntryType.LESSON, "📖 Lesson"),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 16),
        )
        
        # Completed quest context indicator
        completed_quest_indicator = None
        if self.completed_quest_context:
            quest = self.completed_quest_context
            completed_quest_indicator = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text("✨", size=20),
                                ft.Text(
                                    "Quest Completed!",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#22c55e",
                                ),
                            ],
                        ),
                        ft.Text(
                            quest.title,
                            size=13,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "Record what you did, learned, or experienced.",
                            size=12,
                            color=colors.with_opacity(0.7, colors.ON_SURFACE),
                        ),
                    ],
                ),
                padding=ft.Padding(16, 12, 16, 12),
                bgcolor=colors.with_opacity(0.1, "#22c55e"),
                border_radius=10,
                margin=ft.Margin(20, 0, 20, 16),
            )
        
        # Quest satisfaction indicator - show which quests could be completed
        quest_indicator = None
        if potential_quests:
            # Get the minimum word requirement from the quests
            min_words = max(
                (q.satisfaction_config.get("min_words", 10) for q in potential_quests),
                default=10
            )
            quest_indicator = ft.Container(
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(icons.AUTO_AWESOME, color=colors.AMBER_700, size=20),
                                ft.Text(
                                    f"Can complete: {', '.join(q.title for q in potential_quests[:2])}",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=colors.AMBER_700,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"Write at least {min_words} words to complete the quest",
                            size=12,
                            color=colors.with_opacity(0.8, colors.AMBER_700),
                        ),
                    ],
                ),
                padding=ft.Padding(20, 8, 20, 8),
                bgcolor=colors.with_opacity(0.1, colors.AMBER),
                border_radius=8,
                margin=ft.Margin(20, 0, 20, 16),
            )
        
        # Mood before
        mood_before_section = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(
                        "How are you feeling right now?",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            self._build_mood_button(1, "😢"),
                            self._build_mood_button(2, "😕"),
                            self._build_mood_button(3, "😐"),
                            self._build_mood_button(4, "🙂"),
                            self._build_mood_button(5, "😄"),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 16),
        )
        
        # Prompt
        prompt_section = ft.Container(
            content=ft.Container(
                content=ft.Text(
                    prompt,
                    size=16,
                    italic=True,
                    color=colors.with_opacity(0.8, colors.ON_SURFACE),
                ),
                padding=ft.Padding(16, 12, 16, 12),
                bgcolor=colors.with_opacity(0.05, colors.PRIMARY),
                border_radius=8,
            ),
            padding=ft.Padding(20, 0, 20, 8),
        )
        
        # Content field (restore preserved content if any)
        content_value = self._preserved_content if self._preserved_content is not None else ""
        self._preserved_content = None  # Clear after use
        
        self.content_field = ft.TextField(
            value=content_value,
            multiline=True,
            min_lines=8,
            max_lines=20,
            hint_text="Begin writing...",
            border_radius=8,
        )
        
        content_section = ft.Container(
            content=self.content_field,
            padding=ft.Padding(20, 0, 20, 20),
        )
        
        controls = [header, type_selector]
        if completed_quest_indicator:
            controls.append(completed_quest_indicator)
        if quest_indicator:
            controls.append(quest_indicator)
        controls.extend([mood_before_section, prompt_section, content_section])
        
        return controls
    
    def _build_edit_entry_view(self) -> list[ft.Control]:
        """Build the edit entry view."""
        if not self.editing_entry:
            return self._build_list_view()
        
        entry = self.editing_entry
        
        # Header
        header = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.IconButton(
                                icon=icons.CLOSE,
                                on_click=lambda e: self._cancel_edit(),
                            ),
                            ft.Text(
                                f"Edit {entry.type_name}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.ElevatedButton(
                        "Save",
                        icon=icons.CHECK,
                        on_click=lambda e: self._save_edit(),
                    ),
                ],
            ),
            padding=ft.Padding(20, 20, 20, 16),
        )
        
        # Metadata (read-only)
        metadata = ft.Container(
            content=ft.Row(
                spacing=16,
                controls=[
                    ft.Text(
                        f"{entry.type_icon} {entry.type_name}",
                        size=14,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                    ft.Text(
                        entry.created_at.strftime("%B %d, %Y"),
                        size=14,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 16),
        )
        
        # Prompt (if any)
        prompt_section = None
        if entry.prompt_used:
            prompt_section = ft.Container(
                content=ft.Container(
                    content=ft.Text(
                        entry.prompt_used,
                        size=14,
                        italic=True,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                    padding=ft.Padding(12, 8, 12, 8),
                    bgcolor=colors.with_opacity(0.05, colors.PRIMARY),
                    border_radius=8,
                ),
                padding=ft.Padding(20, 0, 20, 8),
            )
        
        # Content field (pre-populated, use preserved content if available)
        content_value = self._preserved_content if self._preserved_content is not None else entry.content
        self._preserved_content = None  # Clear after use
        
        self.content_field = ft.TextField(
            value=content_value,
            multiline=True,
            min_lines=8,
            max_lines=20,
            hint_text="Edit your entry...",
            border_radius=8,
        )
        
        content_section = ft.Container(
            content=self.content_field,
            padding=ft.Padding(20, 0, 20, 16),
        )
        
        # Mood after (optional update)
        mood_after_section = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(
                        "How do you feel now? (optional)",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            self._build_mood_after_button(1, "😢"),
                            self._build_mood_after_button(2, "😕"),
                            self._build_mood_after_button(3, "😐"),
                            self._build_mood_after_button(4, "🙂"),
                            self._build_mood_after_button(5, "😄"),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 20),
        )
        
        controls = [header, metadata]
        if prompt_section:
            controls.append(prompt_section)
        controls.extend([content_section, mood_after_section])
        
        return controls
    
    def _build_entry_detail_view(self) -> list[ft.Control]:
        """Build the entry detail view."""
        if not self.selected_entry:
            return self._build_list_view()
        
        entry = self.selected_entry
        
        # Header
        header = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.IconButton(
                                icon=icons.ARROW_BACK,
                                on_click=lambda e: self._show_list(),
                            ),
                            ft.Text(
                                f"{entry.type_icon} {entry.type_name}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=icons.EDIT_OUTLINED,
                                icon_color=colors.PRIMARY,
                                on_click=lambda e: self._edit_entry(entry),
                                tooltip="Edit entry",
                            ),
                            ft.IconButton(
                                icon=icons.DELETE_OUTLINE,
                                icon_color=colors.ERROR,
                                on_click=lambda e: self._delete_entry(entry),
                                tooltip="Delete entry",
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 20, 20, 16),
        )
        
        # Metadata
        metadata = ft.Container(
            content=ft.Row(
                spacing=16,
                controls=[
                    ft.Text(
                        entry.created_at.strftime("%B %d, %Y at %I:%M %p"),
                        size=14,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                    ft.Text(
                        f"{entry.word_count} words",
                        size=14,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                ],
            ),
            padding=ft.Padding(20, 0, 20, 8),
        )
        
        # Mood change
        mood_section = None
        if entry.mood_before is not None or entry.mood_after is not None:
            mood_items = []
            if entry.mood_before is not None:
                mood_items.append(ft.Text(f"Before: {self._mood_emoji(entry.mood_before)}", size=14))
            if entry.mood_after is not None:
                mood_items.append(ft.Text(f"After: {self._mood_emoji(entry.mood_after)}", size=14))
            if entry.mood_change is not None:
                change_text = "+" + str(entry.mood_change) if entry.mood_change > 0 else str(entry.mood_change)
                mood_items.append(
                    ft.Text(
                        f"Change: {change_text}",
                        size=14,
                        color=colors.GREEN if entry.mood_change > 0 else colors.RED if entry.mood_change < 0 else None,
                    )
                )
            
            mood_section = ft.Container(
                content=ft.Row(spacing=16, controls=mood_items),
                padding=ft.Padding(20, 0, 20, 16),
            )
        
        # Prompt used
        prompt_section = None
        if entry.prompt_used:
            prompt_section = ft.Container(
                content=ft.Container(
                    content=ft.Text(
                        entry.prompt_used,
                        size=14,
                        italic=True,
                        color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    ),
                    padding=ft.Padding(12, 8, 12, 8),
                    bgcolor=colors.with_opacity(0.05, colors.PRIMARY),
                    border_radius=8,
                ),
                padding=ft.Padding(20, 0, 20, 16),
            )
        
        # Content
        content_section = ft.Container(
            content=ft.Text(
                entry.content,
                size=16,
                selectable=True,
            ),
            padding=ft.Padding(20, 0, 20, 20),
        )
        
        controls = [header, metadata]
        if mood_section:
            controls.append(mood_section)
        if prompt_section:
            controls.append(prompt_section)
        controls.append(content_section)
        
        return controls
    
    def _build_entry_card(self, entry: JournalEntry) -> ft.Control:
        """Build a card for a journal entry."""
        # Truncate content for preview
        preview = entry.content[:150] + "..." if len(entry.content) > 150 else entry.content
        
        return ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    # Header row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(entry.type_icon, size=20),
                                    ft.Text(
                                        entry.type_name,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.Text(
                                self._format_date(entry.created_at),
                                size=12,
                                color=colors.with_opacity(0.6, colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    # Content preview
                    ft.Text(
                        preview,
                        size=14,
                        color=colors.with_opacity(0.8, colors.ON_SURFACE),
                    ),
                    # Footer
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text(
                                f"{entry.word_count} words",
                                size=12,
                                color=colors.with_opacity(0.5, colors.ON_SURFACE),
                            ),
                            *([
                                ft.Text(
                                    f"Mood: {self._mood_emoji(entry.mood_before)} → {self._mood_emoji(entry.mood_after)}",
                                    size=12,
                                )
                            ] if entry.mood_before and entry.mood_after else []),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(16, 12, 16, 12),
            bgcolor=colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=12,
            on_click=lambda e, ent=entry: self._view_entry(ent),
        )
    
    def _build_stat_chip(self, text: str, color: str) -> ft.Control:
        return ft.Container(
            content=ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=colors.WHITE),
            padding=ft.Padding(12, 6, 12, 6),
            bgcolor=color,
            border_radius=16,
        )
    
    def _build_type_chip(self, entry_type: Optional[JournalEntryType], label: str) -> ft.Control:
        is_selected = self.filter_type == entry_type
        return ft.Container(
            content=ft.Text(
                label, 
                size=12,
                weight=ft.FontWeight.BOLD if is_selected else None,
                color=colors.WHITE if is_selected else None,
            ),
            padding=ft.Padding(12, 6, 12, 6),
            bgcolor=colors.PRIMARY if is_selected else colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=16,
            on_click=lambda e, t=entry_type: self._filter_entries(t),
        )
    
    def _filter_entries(self, entry_type: Optional[JournalEntryType]):
        """Filter entries by type."""
        self.filter_type = entry_type
        self._refresh_view()
    
    def _build_type_selector_chip(self, entry_type: JournalEntryType, label: str) -> ft.Control:
        is_selected = self.selected_type == entry_type
        return ft.Container(
            content=ft.Text(
                label,
                size=13,
                weight=ft.FontWeight.BOLD if is_selected else None,
                color=colors.ON_PRIMARY if is_selected else None,
            ),
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor=colors.PRIMARY if is_selected else colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=20,
            on_click=lambda e, t=entry_type: self._select_type(t),
        )
    
    def _build_mood_button(self, mood: int, emoji: str) -> ft.Control:
        is_selected = self.mood_before == mood
        return ft.Container(
            content=ft.Text(emoji, size=28),
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor=colors.PRIMARY if is_selected else colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=12,
            on_click=lambda e, m=mood: self._select_mood(m),
        )
    
    def _build_mood_after_button(self, mood: int, emoji: str) -> ft.Control:
        is_selected = self.mood_after == mood
        return ft.Container(
            content=ft.Text(emoji, size=28),
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor=colors.PRIMARY if is_selected else colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=12,
            on_click=lambda e, m=mood: self._select_mood_after(m),
        )
    
    def _mood_emoji(self, mood: int) -> str:
        emojis = {1: "😢", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}
        return emojis.get(mood, "❓")
    
    def _format_date(self, dt: datetime) -> str:
        """Format date for display."""
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "Just now"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60}m ago"
            else:
                return f"{diff.seconds // 3600}h ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime("%b %d")
    
    # Actions
    def _show_new_entry(self):
        self.current_view = "new"
        self.selected_type = JournalEntryType.FREE_FORM
        self.mood_before = None
        self._refresh_view()
    
    def _show_list(self):
        self.current_view = "list"
        self.selected_entry = None
        self._refresh_view()
    
    def _view_entry(self, entry: JournalEntry):
        self.selected_entry = entry
        self.current_view = "view"
        self._refresh_view()
    
    def _edit_entry(self, entry: JournalEntry):
        self.editing_entry = entry
        self.mood_after = entry.mood_after
        self.current_view = "edit"
        self._refresh_view()
    
    def _cancel_edit(self):
        self.editing_entry = None
        self.mood_after = None
        self._view_entry(self.selected_entry)
    
    def _save_edit(self):
        if not self.content_field or not self.editing_entry:
            return
        
        content = self.content_field.value.strip() if self.content_field.value else ""
        if not content:
            return
        
        # Update the entry
        self.journal_service.update_entry(
            entry_id=self.editing_entry.id,
            content=content,
            mood_after=self.mood_after,
        )
        
        # Callback to save (reuse the entry saved callback with empty quest list)
        self.on_entry_saved(self.editing_entry, [])
        
        # Update selected entry reference and return to view
        self.selected_entry = self.editing_entry
        self.editing_entry = None
        self.mood_after = None
        self.current_view = "view"
        self._refresh_view()
    
    def _select_mood_after(self, mood: int):
        # Preserve content before refreshing
        if self.content_field:
            self._preserved_content = self.content_field.value
        self.mood_after = mood
        self._refresh_view()
    
    def _cancel_entry(self):
        self._show_list()
    
    def _select_type(self, entry_type: JournalEntryType):
        # Preserve content before refreshing
        if self.content_field:
            self._preserved_content = self.content_field.value
        self.selected_type = entry_type
        self._refresh_view()
    
    def _select_mood(self, mood: int):
        # Preserve content before refreshing
        if self.content_field:
            self._preserved_content = self.content_field.value
        self.mood_before = mood
        self._refresh_view()
    
    def _save_entry(self):
        if not self.content_field or not self.content_field.value:
            return
        
        content = self.content_field.value.strip()
        if not content:
            return
        
        # Create the entry
        entry = self.journal_service.create_entry(
            entry_type=self.selected_type,
            content=content,
            use_prompt=True,
            mood_before=self.mood_before,
        )
        
        # Find quests that this entry satisfies
        satisfied_quests = self.journal_service.find_satisfiable_quests(entry, self.active_quests)
        
        # Link entry to first satisfied quest
        if satisfied_quests:
            entry.satisfied_quest_id = satisfied_quests[0].id
        
        # Callback
        self.on_entry_saved(entry, satisfied_quests)
        
        # Return to list
        self._show_list()
    
    def _delete_entry(self, entry: JournalEntry):
        self.journal_service.delete_entry(entry.id)
        self._show_list()

