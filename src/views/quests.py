"""Quests view with quest log and management."""

import flet as ft
from typing import Callable, Optional
from datetime import datetime

from utils.compat import colors, icons
from models.quest import Quest, QuestType, QuestStatus
from models.stats import STAT_DEFINITIONS
from components.quest_card import QuestCard


class QuestsView(ft.Container):
    """Quest log view with filtering and management."""
    
    def __init__(
        self,
        active_quests: list[Quest],
        available_quests: list[Quest],
        completed_quests: list[Quest],
        on_quest_accept: Callable[[Quest], None],
        on_quest_complete: Callable[[Quest], None],
        on_quest_abandon: Callable[[Quest], None],
        on_back: Callable[[], None],
        on_write_entry: Optional[Callable[[Quest], None]] = None,
        on_log_progress: Optional[Callable[[Quest], None]] = None,
        on_create_custom_quest: Optional[Callable[[], None]] = None,
        on_edit_custom_quest: Optional[Callable[[Quest], None]] = None,
    ):
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.completed_quests = completed_quests
        self.on_quest_accept = on_quest_accept
        self.on_quest_complete = on_quest_complete
        self.on_quest_abandon = on_quest_abandon
        self.on_back = on_back
        self.on_write_entry = on_write_entry
        self.on_log_progress = on_log_progress
        self.on_create_custom_quest = on_create_custom_quest
        self.on_edit_custom_quest = on_edit_custom_quest
        
        self.current_tab = 0
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def _build_content(self) -> ft.Control:
        return ft.Column(
            spacing=0,
            controls=[
                # Header
                self._build_header(),
                
                # Tabs
                self._build_tabs(),
                
                # Content based on tab
                ft.Container(
                    content=self._build_tab_content(),
                    expand=True,
                    padding=ft.Padding(20, 20, 20, 20),
                ),
            ],
        )
    
    def _build_header(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.IconButton(
                        icon=icons.ARROW_BACK,
                        on_click=lambda e: self.on_back(),
                        icon_color=colors.WHITE,
                    ),
                    ft.Text(
                        "Quest Log",
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=colors.WHITE,
                    ),
                    ft.Container(width=48),  # Spacer
                ],
            ),
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            bgcolor="#4f46e5",
        )
    
    def _build_tabs(self) -> ft.Control:
        tabs = [
            ("Active", len(self.active_quests)),
            ("Available", len(self.available_quests)),
            ("Completed", len(self.completed_quests)),
        ]
        
        def select_tab(index: int):
            self.current_tab = index
            self.content = self._build_content()
            self.update()
        
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    ft.Container(
                        content=ft.Row(
                            spacing=6,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    label,
                                    size=14,
                                    weight=ft.FontWeight.W_500 if i == self.current_tab else ft.FontWeight.NORMAL,
                                    color=colors.ON_SURFACE if i == self.current_tab else colors.with_opacity(0.6, colors.ON_SURFACE),
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        str(count),
                                        size=11,
                                        color=colors.WHITE if i == self.current_tab else colors.ON_SURFACE,
                                    ),
                                    bgcolor="#6366f1" if i == self.current_tab else colors.with_opacity(0.3, colors.ON_SURFACE),
                                    padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                    border_radius=10,
                                ) if count > 0 else ft.Container(),
                            ],
                        ),
                        padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                        border=ft.border.only(
                            bottom=ft.BorderSide(2, "#6366f1") if i == self.current_tab else None
                        ),
                        on_click=lambda e, idx=i: select_tab(idx),
                        ink=True,
                    )
                    for i, (label, count) in enumerate(tabs)
                ],
            ),
            bgcolor=colors.SURFACE_CONTAINER_HIGH,
        )
    
    def _build_tab_content(self) -> ft.Control:
        if self.current_tab == 0:
            return self._build_active_tab()
        elif self.current_tab == 1:
            return self._build_available_tab()
        else:
            return self._build_completed_tab()
    
    def _build_active_tab(self) -> ft.Control:
        if not self.active_quests:
            return self._build_empty_state(
                "🎯",
                "No Active Quests",
                "Accept a quest to get started!"
            )
        
        return ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                QuestCard(
                    quest=quest,
                    on_complete=lambda e, q=quest: self.on_quest_complete(q),
                    on_abandon=lambda e, q=quest: self.on_quest_abandon(q),
                    on_write_entry=lambda e, q=quest: self.on_write_entry(q) if self.on_write_entry else None,
                    on_log_progress=lambda e, q=quest: self.on_log_progress(q) if self.on_log_progress else None,
                )
                for quest in self.active_quests
            ],
        )
    
    def _build_available_tab(self) -> ft.Control:
        # Separate custom quests from generated quests
        custom_quests = [q for q in self.available_quests if getattr(q, 'is_custom', False)]
        generated_quests = [q for q in self.available_quests if not getattr(q, 'is_custom', False)]
        
        # Group generated quests by type
        daily = [q for q in generated_quests if q.quest_type == QuestType.DAILY]
        weekly = [q for q in generated_quests if q.quest_type == QuestType.WEEKLY]
        random = [q for q in generated_quests if q.quest_type == QuestType.RANDOM]
        other = [q for q in generated_quests if q.quest_type not in [QuestType.DAILY, QuestType.WEEKLY, QuestType.RANDOM]]
        
        sections = []
        
        # Custom quests section (always show, with create button)
        sections.append(self._custom_quests_section(custom_quests))
        
        if daily:
            sections.append(self._quest_section("🗡️ Daily Quests", daily))
        if weekly:
            sections.append(self._quest_section("🛡️ Weekly Challenges", weekly))
        if random:
            sections.append(self._quest_section("🎲 Random Encounters", random))
        if other:
            sections.append(self._quest_section("⚔️ Other Quests", other))
        
        if not self.available_quests and not self.on_create_custom_quest:
            return self._build_empty_state(
                "✨",
                "All Quests Accepted!",
                "You've accepted all available quests. Complete them or wait for new ones tomorrow."
            )
        
        return ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=sections,
        )
    
    def _custom_quests_section(self, quests: list[Quest]) -> ft.Control:
        """Build the custom quests section with create button."""
        quest_cards = [
            self._custom_quest_card(quest)
            for quest in quests
        ]
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "⭐ My Custom Quests",
                            size=16,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.OutlinedButton(
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(icons.ADD, size=16),
                                    ft.Text("Create"),
                                ],
                            ),
                            on_click=lambda e: self.on_create_custom_quest() if self.on_create_custom_quest else None,
                        ) if self.on_create_custom_quest else ft.Container(),
                    ],
                ),
                *quest_cards,
                # Show hint if no custom quests
                ft.Container(
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Create your own quests for things like:",
                                size=13,
                                color=colors.with_opacity(0.6, colors.ON_SURFACE),
                            ),
                            ft.Text(
                                "• Spending time with family\n• Learning a new skill\n• Building a daily habit",
                                size=12,
                                color=colors.with_opacity(0.5, colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=10,
                    visible=len(quests) == 0,
                ),
            ],
        )
    
    def _custom_quest_card(self, quest: Quest) -> ft.Control:
        """Build a card for a custom quest with edit capability."""
        stat_def = STAT_DEFINITIONS[quest.primary_stat]
        
        # Weekly progress display
        weekly_progress = ""
        if quest.weekly_target > 0:
            weekly_progress = f"{quest.weekly_completions}/{quest.weekly_target} this week"
        
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Text(quest.icon, size=24),
                                width=44,
                                height=44,
                                bgcolor=colors.with_opacity(0.2, stat_def.color),
                                border_radius=10,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        quest.title,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(
                                                f"+{quest.xp_reward} XP",
                                                size=12,
                                                color="#f59e0b",
                                            ),
                                            ft.Text(
                                                weekly_progress,
                                                size=11,
                                                color=colors.with_opacity(0.6, colors.ON_SURFACE),
                                            ) if weekly_progress else ft.Container(),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.IconButton(
                                icon=icons.EDIT_OUTLINED,
                                icon_size=18,
                                tooltip="Edit quest",
                                on_click=lambda e, q=quest: self.on_edit_custom_quest(q) if self.on_edit_custom_quest else None,
                            ),
                            ft.OutlinedButton(
                                "Accept",
                                on_click=lambda e, q=quest: self.on_quest_accept(q),
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(12, 12, 8, 12),
            bgcolor=colors.SURFACE_CONTAINER_HIGH,
            border_radius=10,
            border=ft.border.all(1, colors.with_opacity(0.3, stat_def.color)),
        )
    
    def _quest_section(self, title: str, quests: list[Quest]) -> ft.Control:
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.W_600,
                ),
                *[
                    QuestCard(
                        quest=quest,
                        on_accept=lambda e, q=quest: self.on_quest_accept(q),
                    )
                    for quest in quests
                ],
            ],
        )
    
    def _build_completed_tab(self) -> ft.Control:
        if not self.completed_quests:
            return self._build_empty_state(
                "📜",
                "No Completed Quests Yet",
                "Complete quests to build your legend!"
            )
        
        # Sort by completion date
        sorted_quests = sorted(
            self.completed_quests,
            key=lambda q: q.completed_at or datetime.min,
            reverse=True
        )
        
        return ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self._completed_quest_item(quest)
                for quest in sorted_quests[:20]  # Show last 20
            ],
        )
    
    def _completed_quest_item(self, quest: Quest) -> ft.Control:
        stat_def = STAT_DEFINITIONS[quest.primary_stat]
        
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    icons.CHECK_CIRCLE,
                                    size=20,
                                    color="#22c55e",
                                ),
                                bgcolor=colors.with_opacity(0.1, "#22c55e"),
                                padding=8,
                                border_radius=8,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        quest.title,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(
                                                f"+{quest.xp_reward} XP",
                                                size=12,
                                                color="#f59e0b",
                                            ),
                                            ft.Text(stat_def.icon, size=12),
                                            ft.Text(
                                                quest.completed_at.strftime("%b %d") if quest.completed_at else "",
                                                size=11,
                                                color=colors.with_opacity(0.5, colors.ON_SURFACE),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(12, 12, 12, 12),
            bgcolor=colors.SURFACE_CONTAINER_HIGH,
            border_radius=10,
        )
    
    def _build_empty_state(self, icon: str, title: str, subtitle: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text(icon, size=48),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        subtitle,
                        size=14,
                        color=colors.with_opacity(0.6, colors.ON_SURFACE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )
    
    def refresh(self, active_quests: list[Quest], available_quests: list[Quest],
                completed_quests: list[Quest]):
        """Refresh the view with updated data."""
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.completed_quests = completed_quests
        self.content = self._build_content()
        self.update()

