"""Home dashboard view."""

import flet as ft
from typing import Callable, Optional
from datetime import datetime

from models.character import Character
from models.quest import Quest, QuestStatus
from models.stats import StatType, STAT_DEFINITIONS
from components.stat_bar import StatBar, StatHexagon
from components.quest_card import QuestCard, QuestListItem


class HomeView(ft.Container):
    """Main dashboard showing character overview and active quests."""
    
    def __init__(
        self,
        character: Character,
        active_quests: list[Quest],
        available_quests: list[Quest],
        on_quest_accept: Callable[[Quest], None],
        on_quest_complete: Callable[[Quest], None],
        on_quest_abandon: Callable[[Quest], None],
        on_view_all_quests: Callable[[], None],
        on_view_character: Callable[[], None],
    ):
        self.character = character
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.on_quest_accept = on_quest_accept
        self.on_quest_complete = on_quest_complete
        self.on_quest_abandon = on_quest_abandon
        self.on_view_all_quests = on_view_all_quests
        self.on_view_character = on_view_character
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def _build_content(self) -> ft.Control:
        return ft.Column(
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Hero section with character summary
                self._build_hero_section(),
                
                # Main content
                ft.Container(
                    content=ft.Column(
                        spacing=24,
                        controls=[
                            # Active quests section
                            self._build_active_quests_section(),
                            
                            # Available quests section
                            self._build_available_quests_section(),
                            
                            # Quick stats
                            self._build_quick_stats_section(),
                        ],
                    ),
                    padding=ft.Padding(20, 20, 20, 20),
                ),
            ],
        )
    
    def _build_hero_section(self) -> ft.Control:
        """Build the hero section with character info."""
        char = self.character
        
        # Time-based greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
            emoji = "🌅"
        elif hour < 17:
            greeting = "Good afternoon"
            emoji = "☀️"
        elif hour < 21:
            greeting = "Good evening"
            emoji = "🌆"
        else:
            greeting = "Good night"
            emoji = "🌙"
        
        return ft.Container(
            content=ft.Column(
                spacing=16,
                controls=[
                    # Greeting row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        f"{emoji} {greeting},",
                                        size=14,
                                        color=ft.Colors.with_opacity(0.7, ft.Colors.ON_PRIMARY_CONTAINER),
                                    ),
                                    ft.Text(
                                        char.name,
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            char.title,
                                            size=12,
                                            color=ft.Colors.WHITE,
                                        ),
                                        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                                        border_radius=12,
                                    ),
                                ],
                            ),
                            # Character avatar
                            ft.Container(
                                content=ft.Text("🧙", size=48),
                                on_click=lambda e: self.on_view_character(),
                            ),
                        ],
                    ),
                    
                    # Stats overview row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            self._stat_pill(stat)
                            for stat in list(char.stats.values())[:3]
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            self._stat_pill(stat)
                            for stat in list(char.stats.values())[3:]
                        ],
                    ),
                    
                    # Quick stats row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            self._quick_stat_item("🔥", f"{char.current_streak}", "Day Streak"),
                            self._quick_stat_item("⚔️", f"{char.total_quests_completed}", "Quests Done"),
                            self._quick_stat_item("⭐", f"{char.total_xp:,}", "Total XP"),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(20, 20, 20, 20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#4f46e5", "#7c3aed"],
            ),
            border_radius=ft.BorderRadius(0, 0, 24, 24),
        )
    
    def _stat_pill(self, stat) -> ft.Control:
        """Small stat indicator."""
        return ft.Container(
            content=ft.Row(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(stat.definition.icon, size=14),
                    ft.Text(
                        f"{stat.level}",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ],
            ),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=12,
        )
    
    def _quick_stat_item(self, icon: str, value: str, label: str) -> ft.Control:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
            controls=[
                ft.Row(
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(icon, size=16),
                        ft.Text(
                            value,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                ),
                ft.Text(
                    label,
                    size=11,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                ),
            ],
        )
    
    def _build_active_quests_section(self) -> ft.Control:
        """Build active quests section."""
        if not self.active_quests:
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("🎯", size=32),
                        ft.Text(
                            "No Active Quests",
                            size=16,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "Accept a quest below to begin!",
                            size=13,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ),
                padding=ft.Padding(24, 24, 24, 24),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_radius=16,
            )
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "⚔️ Active Quests",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(
                            f"{len(self.active_quests)} in progress",
                            size=13,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ),
                *[
                    QuestCard(
                        quest=quest,
                        on_complete=lambda e, q=quest: self.on_quest_complete(q),
                        on_abandon=lambda e, q=quest: self.on_quest_abandon(q),
                    )
                    for quest in self.active_quests[:3]  # Show max 3
                ],
            ],
        )
    
    def _build_available_quests_section(self) -> ft.Control:
        """Build available quests section."""
        if not self.available_quests:
            return ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("✨", size=32),
                        ft.Text(
                            "All Quests Accepted!",
                            size=16,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "New quests will appear tomorrow",
                            size=13,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ),
                padding=ft.Padding(24, 24, 24, 24),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                border_radius=16,
            )
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "📜 Available Quests",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.TextButton(
                            content=ft.Text("View All"),
                            on_click=lambda e: self.on_view_all_quests(),
                        ),
                    ],
                ),
                *[
                    QuestCard(
                        quest=quest,
                        on_accept=lambda e, q=quest: self.on_quest_accept(q),
                    )
                    for quest in self.available_quests[:3]  # Show max 3
                ],
            ],
        )
    
    def _build_quick_stats_section(self) -> ft.Control:
        """Build quick stats overview."""
        char = self.character
        
        # Find recommended stat to focus on
        recommended = max(
            char.stats.values(),
            key=lambda s: s.target_level - s.level
        )
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "📊 Quick Stats",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Total Level", size=14),
                                    ft.Text(
                                        str(char.total_level),
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Longest Streak", size=14),
                                    ft.Text(
                                        f"{char.longest_streak} days",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            ft.Divider(height=1),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.LIGHTBULB, size=18, color="#f59e0b"),
                                    ft.Text(
                                        f"Focus on {recommended.definition.name} to reach your goal!",
                                        size=13,
                                        color=ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
                
                # View character button
                ft.Container(
                    content=ft.FilledButton(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text("📊", size=16),
                                ft.Text("View Full Character Sheet", weight=ft.FontWeight.W_500),
                            ],
                        ),
                        on_click=lambda e: self.on_view_character(),
                        width=float("inf"),
                    ),
                    padding=ft.Padding(left=0, right=0, top=8, bottom=0),
                ),
            ],
        )
    
    def refresh(self, character: Character, active_quests: list[Quest], 
                available_quests: list[Quest]):
        """Refresh the view with updated data."""
        self.character = character
        self.active_quests = active_quests
        self.available_quests = available_quests
        self.content = self._build_content()
        self.update()
