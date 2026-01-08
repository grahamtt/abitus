"""Stat bar component for displaying character stats."""

import flet as ft
from models.stats import Stat, STAT_DEFINITIONS


class StatBar(ft.Container):
    """A visual stat bar showing level and XP progress."""
    
    def __init__(
        self,
        stat: Stat,
        compact: bool = False,
        show_xp: bool = True,
        on_click=None,
    ):
        self.stat = stat
        self.compact = compact
        self.show_xp = show_xp
        self._on_click = on_click
        
        super().__init__(
            content=self._build_content(),
            padding=ft.Padding(12, 12, 12, 12) if not compact else ft.Padding(8, 8, 8, 8),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.1, stat.definition.color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, stat.definition.color)),
            on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
    
    def _build_content(self) -> ft.Control:
        definition = self.stat.definition
        
        if self.compact:
            return self._build_compact()
        
        # Full stat bar
        return ft.Column(
            spacing=8,
            controls=[
                # Header row with icon, name, and level
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Text(definition.icon, size=24),
                                ft.Text(
                                    definition.name,
                                    size=16,
                                    weight=ft.FontWeight.W_600,
                                    color=definition.color,
                                ),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"Lv.{self.stat.level}",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=definition.color,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            border_radius=20,
                        ),
                    ],
                ),
                # Progress bar
                ft.Container(
                    content=ft.Stack(
                        controls=[
                            # Background
                            ft.Container(
                                bgcolor=ft.Colors.with_opacity(0.2, definition.color),
                                border_radius=4,
                                height=8,
                                expand=True,
                            ),
                            # Fill
                            ft.Container(
                                bgcolor=definition.color,
                                border_radius=4,
                                height=8,
                                width=self.stat.xp_progress * 300,  # Max width
                                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                            ),
                        ],
                    ),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border_radius=4,
                ),
                # XP text
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            f"{self.stat.current_xp - self.stat.xp_for_current_level} / {self.stat.xp_for_next_level - self.stat.xp_for_current_level} XP",
                            size=11,
                            color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                        ),
                        ft.Text(
                            f"{self.stat.xp_remaining} to next level",
                            size=11,
                            color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                        ),
                    ],
                ) if self.show_xp else ft.Container(),
            ],
        )
    
    def _build_compact(self) -> ft.Control:
        """Build compact version for quick overview."""
        definition = self.stat.definition
        
        return ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(definition.icon, size=20),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    definition.name,
                                    size=13,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    f"Lv.{self.stat.level}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=definition.color,
                                ),
                            ],
                        ),
                        # Mini progress bar
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    ft.Container(
                                        bgcolor=ft.Colors.with_opacity(0.2, definition.color),
                                        border_radius=2,
                                        height=4,
                                        width=100,
                                    ),
                                    ft.Container(
                                        bgcolor=definition.color,
                                        border_radius=2,
                                        height=4,
                                        width=self.stat.xp_progress * 100,
                                        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                                    ),
                                ],
                            ),
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            border_radius=2,
                        ),
                    ],
                ),
            ],
        )
    
    def update_stat(self, stat: Stat):
        """Update the stat and refresh display."""
        self.stat = stat
        self.content = self._build_content()
        self.bgcolor = ft.Colors.with_opacity(0.1, stat.definition.color)
        self.border = ft.border.all(1, ft.Colors.with_opacity(0.2, stat.definition.color))


class StatHexagon(ft.Container):
    """Hexagonal stat overview showing all stats at once."""
    
    def __init__(self, stats: dict, size: int = 200):
        self.stats = stats
        self.size = size
        
        super().__init__(
            content=self._build_content(),
            width=size,
            height=size,
        )
    
    def _build_content(self) -> ft.Control:
        # Simple grid representation of stats
        stat_list = list(self.stats.values())
        
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                # Top row (2 stats)
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        self._build_mini_stat(stat_list[0]) if len(stat_list) > 0 else ft.Container(),
                        self._build_mini_stat(stat_list[1]) if len(stat_list) > 1 else ft.Container(),
                    ],
                ),
                # Middle rows
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        self._build_mini_stat(stat_list[2]) if len(stat_list) > 2 else ft.Container(),
                        self._build_mini_stat(stat_list[3]) if len(stat_list) > 3 else ft.Container(),
                    ],
                ),
                # Bottom row
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        self._build_mini_stat(stat_list[4]) if len(stat_list) > 4 else ft.Container(),
                        self._build_mini_stat(stat_list[5]) if len(stat_list) > 5 else ft.Container(),
                    ],
                ),
            ],
        )
    
    def _build_mini_stat(self, stat: Stat) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Text(stat.definition.icon, size=18),
                    ft.Text(
                        str(stat.level),
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=stat.definition.color,
                    ),
                ],
            ),
            width=60,
            height=50,
            bgcolor=ft.Colors.with_opacity(0.1, stat.definition.color),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, stat.definition.color)),
        )
