"""Character sheet view."""

import flet as ft
from typing import Callable
from datetime import datetime

from models.character import Character
from models.achievement import Achievement
from models.stats import StatType, STAT_DEFINITIONS
from components.stat_bar import StatBar
from components.achievement_badge import AchievementBadge


class CharacterView(ft.Container):
    """Full character sheet with stats and achievements."""
    
    def __init__(
        self,
        character: Character,
        achievements: list[Achievement],
        on_back: Callable[[], None],
    ):
        self.character = character
        self.achievements = achievements
        self.on_back = on_back
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def _build_content(self) -> ft.Control:
        char = self.character
        unlocked_achievements = [a for a in self.achievements if a.is_unlocked]
        
        return ft.Column(
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Header
                self._build_header(),
                
                # Content
                ft.Container(
                    content=ft.Column(
                        spacing=24,
                        controls=[
                            # Character summary card
                            self._build_summary_card(),
                            
                            # Stats section
                            self._build_stats_section(),
                            
                            # Achievements section
                            self._build_achievements_section(),
                            
                            # Statistics section
                            self._build_statistics_section(),
                        ],
                    ),
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
                        "Character Sheet",
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
    
    def _build_summary_card(self) -> ft.Control:
        char = self.character
        
        # Calculate days since joining
        days_active = (datetime.now() - char.created_at).days + 1
        
        return ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    # Avatar and name
                    ft.Container(
                        content=ft.Text("🧙", size=64),
                        bgcolor=ft.Colors.with_opacity(0.1, "#6366f1"),
                        padding=20,
                        border_radius=50,
                    ),
                    ft.Text(
                        char.name,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=ft.Text(
                            char.title,
                            size=14,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor="#6366f1",
                        padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                        border_radius=16,
                    ),
                    
                    # Quick stats
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=24,
                        controls=[
                            self._summary_stat("📅", f"{days_active}", "Days"),
                            self._summary_stat("⚔️", f"{char.total_quests_completed}", "Quests"),
                            self._summary_stat("⭐", f"{char.total_xp:,}", "XP"),
                            self._summary_stat("🔥", f"{char.longest_streak}", "Best Streak"),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(24, 24, 24, 24),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=20,
        )
    
    def _summary_stat(self, icon: str, value: str, label: str) -> ft.Control:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(icon, size=20),
                ft.Text(
                    value,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    label,
                    size=11,
                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                ),
            ],
        )
    
    def _build_stats_section(self) -> ft.Control:
        char = self.character
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "📊 Life Stats",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(
                            f"Total Level: {char.total_level}",
                            size=14,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ),
                *[
                    StatBar(stat=stat, show_xp=True)
                    for stat in char.stats.values()
                ],
            ],
        )
    
    def _build_achievements_section(self) -> ft.Control:
        unlocked = [a for a in self.achievements if a.is_unlocked]
        locked = [a for a in self.achievements if not a.is_unlocked and not a.is_hidden]
        
        # Sort by rarity and recency
        unlocked.sort(key=lambda a: (a.unlocked_at or datetime.min), reverse=True)
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "🏆 Achievements",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(
                            f"{len(unlocked)}/{len(self.achievements)} unlocked",
                            size=14,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ),
                
                # Unlocked achievements
                ft.Text(
                    "Unlocked",
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                ) if unlocked else ft.Container(),
                
                ft.Container(
                    content=ft.Row(
                        wrap=True,
                        spacing=8,
                        run_spacing=8,
                        controls=[
                            AchievementBadge(achievement=a, size="medium")
                            for a in unlocked[:8]  # Show first 8
                        ],
                    ),
                ) if unlocked else ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Text("🎯", size=32),
                            ft.Text(
                                "No achievements yet",
                                size=14,
                                color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                            ),
                            ft.Text(
                                "Complete quests to unlock achievements!",
                                size=12,
                                color=ft.Colors.with_opacity(0.4, ft.Colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    padding=ft.Padding(20, 20, 20, 20),
                ),
                
                # Next achievements (locked but visible)
                ft.Text(
                    "In Progress",
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                ) if locked else ft.Container(),
                
                ft.Container(
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            self._locked_achievement_item(a)
                            for a in sorted(locked, key=lambda x: -x.progress_percent)[:3]
                        ],
                    ),
                ) if locked else ft.Container(),
            ],
        )
    
    def _locked_achievement_item(self, achievement: Achievement) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Text(achievement.icon, size=24, opacity=0.5),
                    ft.Column(
                        spacing=4,
                        expand=True,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        achievement.name,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        f"{int(achievement.progress_percent)}%",
                                        size=12,
                                        color=achievement.rarity_color,
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=ft.Stack(
                                    controls=[
                                        ft.Container(
                                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
                                            border_radius=2,
                                            height=4,
                                            expand=True,
                                        ),
                                        ft.Container(
                                            bgcolor=achievement.rarity_color,
                                            border_radius=2,
                                            height=4,
                                            width=achievement.progress_percent * 2,  # Scale to ~200px
                                        ),
                                    ],
                                ),
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                border_radius=2,
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(12, 12, 12, 12),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=10,
            opacity=0.7,
        )
    
    def _build_statistics_section(self) -> ft.Control:
        char = self.character
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "📈 Statistics",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            self._stat_row("Quests Completed", str(char.total_quests_completed)),
                            self._stat_row("Current Streak", f"{char.current_streak} days"),
                            self._stat_row("Longest Streak", f"{char.longest_streak} days"),
                            self._stat_row("Total XP Earned", f"{char.total_xp:,}"),
                            self._stat_row("Average Level", f"{char.average_level:.1f}"),
                            self._stat_row("Highest Stat", f"{char.highest_stat.definition.name} (Lv.{char.highest_stat.level})"),
                            self._stat_row("Lowest Stat", f"{char.lowest_stat.definition.name} (Lv.{char.lowest_stat.level})"),
                            self._stat_row("Member Since", char.created_at.strftime("%b %d, %Y")),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _stat_row(self, label: str, value: str) -> ft.Control:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    label,
                    size=14,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                ),
                ft.Text(
                    value,
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        )
    
    def refresh(self, character: Character, achievements: list[Achievement]):
        """Refresh the view with updated data."""
        self.character = character
        self.achievements = achievements
        self.content = self._build_content()
        self.update()

