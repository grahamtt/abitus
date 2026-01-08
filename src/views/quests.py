"""Quests view with quest log and management."""

import flet as ft
from typing import Callable
from datetime import datetime

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
    ):
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.completed_quests = completed_quests
        self.on_quest_accept = on_quest_accept
        self.on_quest_complete = on_quest_complete
        self.on_quest_abandon = on_quest_abandon
        self.on_back = on_back
        
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
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.on_back(),
                        icon_color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "Quest Log",
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE,
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
                                    color=ft.Colors.ON_SURFACE if i == self.current_tab else ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        str(count),
                                        size=11,
                                        color=ft.Colors.WHITE if i == self.current_tab else ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                    ),
                                    bgcolor="#6366f1" if i == self.current_tab else ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
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
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
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
                )
                for quest in self.active_quests
            ],
        )
    
    def _build_available_tab(self) -> ft.Control:
        if not self.available_quests:
            return self._build_empty_state(
                "✨",
                "All Quests Accepted!",
                "You've accepted all available quests. Complete them or wait for new ones tomorrow."
            )
        
        # Group by quest type
        daily = [q for q in self.available_quests if q.quest_type == QuestType.DAILY]
        weekly = [q for q in self.available_quests if q.quest_type == QuestType.WEEKLY]
        random = [q for q in self.available_quests if q.quest_type == QuestType.RANDOM]
        other = [q for q in self.available_quests if q.quest_type not in [QuestType.DAILY, QuestType.WEEKLY, QuestType.RANDOM]]
        
        sections = []
        
        if daily:
            sections.append(self._quest_section("🗡️ Daily Quests", daily))
        if weekly:
            sections.append(self._quest_section("🛡️ Weekly Challenges", weekly))
        if random:
            sections.append(self._quest_section("🎲 Random Encounters", random))
        if other:
            sections.append(self._quest_section("⚔️ Other Quests", other))
        
        return ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=sections,
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
                                    ft.Icons.CHECK_CIRCLE,
                                    size=20,
                                    color="#22c55e",
                                ),
                                bgcolor=ft.Colors.with_opacity(0.1, "#22c55e"),
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
                                                color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
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
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
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
                        color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            expand=True,
            alignment=ft.alignment.center,
        )
    
    def refresh(self, active_quests: list[Quest], available_quests: list[Quest],
                completed_quests: list[Quest]):
        """Refresh the view with updated data."""
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.completed_quests = completed_quests
        self.content = self._build_content()
        self.update()

