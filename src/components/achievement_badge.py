"""Achievement badge component for displaying achievements."""

import flet as ft

from utils.compat import colors
from models.achievement import Achievement


class AchievementBadge(ft.Container):
    """A badge displaying achievement status and progress."""
    
    def __init__(
        self,
        achievement: Achievement,
        size: str = "medium",  # small, medium, large
        on_click=None,
    ):
        self.achievement = achievement
        self.size = size
        
        # Size configurations
        sizes = {
            "small": {"icon": 24, "text": 11, "padding": 8, "radius": 10},
            "medium": {"icon": 32, "text": 13, "padding": 12, "radius": 12},
            "large": {"icon": 48, "text": 16, "padding": 16, "radius": 16},
        }
        self.config = sizes.get(size, sizes["medium"])
        
        p = self.config["padding"]
        super().__init__(
            content=self._build_content(),
            padding=ft.Padding(p, p, p, p),
            border_radius=self.config["radius"],
            bgcolor=self._get_background(),
            border=ft.border.all(2, self._get_border_color()),
            on_click=on_click,
            opacity=1.0 if achievement.is_unlocked else 0.5,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
    
    def _get_background(self) -> str:
        if self.achievement.is_unlocked:
            return colors.with_opacity(0.15, self.achievement.rarity_color)
        return colors.with_opacity(0.05, colors.ON_SURFACE)
    
    def _get_border_color(self) -> str:
        if self.achievement.is_unlocked:
            return colors.with_opacity(0.5, self.achievement.rarity_color)
        return colors.with_opacity(0.2, colors.ON_SURFACE)
    
    def _build_content(self) -> ft.Control:
        achievement = self.achievement
        config = self.config
        
        if self.size == "small":
            return self._build_small()
        elif self.size == "large":
            return self._build_large()
        
        # Medium (default)
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                # Icon
                ft.Text(
                    achievement.icon if achievement.is_unlocked or not achievement.is_hidden else "❓",
                    size=config["icon"],
                ),
                # Name
                ft.Text(
                    achievement.name if achievement.is_unlocked or not achievement.is_hidden else "???",
                    size=config["text"],
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                # Rarity badge
                ft.Container(
                    content=ft.Text(
                        achievement.rarity_name,
                        size=10,
                        color=colors.WHITE,
                    ),
                    bgcolor=achievement.rarity_color,
                    padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                    border_radius=8,
                ) if achievement.is_unlocked else ft.Container(),
            ],
        )
    
    def _build_small(self) -> ft.Control:
        """Compact badge for lists."""
        achievement = self.achievement
        
        return ft.Row(
            spacing=8,
            controls=[
                ft.Text(
                    achievement.icon if achievement.is_unlocked or not achievement.is_hidden else "❓",
                    size=self.config["icon"],
                ),
                ft.Text(
                    achievement.name if achievement.is_unlocked or not achievement.is_hidden else "???",
                    size=self.config["text"],
                    weight=ft.FontWeight.W_500,
                ),
            ],
        )
    
    def _build_large(self) -> ft.Control:
        """Detailed badge with description."""
        achievement = self.achievement
        config = self.config
        
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                # Icon with glow effect for unlocked
                ft.Container(
                    content=ft.Text(
                        achievement.icon if achievement.is_unlocked or not achievement.is_hidden else "❓",
                        size=config["icon"],
                    ),
                    shadow=ft.BoxShadow(
                        spread_radius=4,
                        blur_radius=16,
                        color=colors.with_opacity(0.4, achievement.rarity_color),
                    ) if achievement.is_unlocked else None,
                ),
                # Name
                ft.Text(
                    achievement.name if achievement.is_unlocked or not achievement.is_hidden else "???",
                    size=config["text"],
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                # Description
                ft.Text(
                    achievement.description if achievement.is_unlocked or not achievement.is_hidden else "Complete hidden requirements",
                    size=12,
                    color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                ),
                # Rarity and unlock date
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                achievement.rarity_name,
                                size=11,
                                color=colors.WHITE,
                            ),
                            bgcolor=achievement.rarity_color,
                            padding=ft.Padding(left=10, right=10, top=3, bottom=3),
                            border_radius=10,
                        ),
                        ft.Text(
                            achievement.unlocked_at.strftime("%b %d, %Y") if achievement.unlocked_at else "",
                            size=11,
                            color=colors.with_opacity(0.5, colors.ON_SURFACE),
                        ) if achievement.is_unlocked else ft.Container(),
                    ],
                ) if achievement.is_unlocked else ft.Container(),
                # Progress bar for locked
                ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    ft.Container(
                                        bgcolor=colors.with_opacity(0.2, colors.ON_SURFACE),
                                        border_radius=4,
                                        height=6,
                                        width=120,
                                    ),
                                    ft.Container(
                                        bgcolor=achievement.rarity_color,
                                        border_radius=4,
                                        height=6,
                                        width=achievement.progress_percent * 1.2,  # 120 max
                                        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                                    ),
                                ],
                            ),
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            border_radius=4,
                        ),
                        ft.Text(
                            f"{achievement.progress}/{achievement.requirement_value}",
                            size=11,
                            color=colors.with_opacity(0.5, colors.ON_SURFACE),
                        ),
                    ],
                ) if not achievement.is_unlocked and achievement.requirement_value > 0 else ft.Container(),
            ],
        )


class AchievementNotification(ft.Container):
    """Popup notification for newly unlocked achievements."""
    
    def __init__(self, achievement: Achievement, on_dismiss=None):
        self.achievement = achievement
        
        super().__init__(
            content=self._build_content(),
            padding=ft.Padding(20, 20, 20, 20),
            border_radius=16,
            bgcolor=colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.border.all(2, achievement.rarity_color),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=colors.with_opacity(0.3, achievement.rarity_color),
                offset=ft.Offset(0, 4),
            ),
            on_click=on_dismiss,
            animate=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
        )
    
    def _build_content(self) -> ft.Control:
        achievement = self.achievement
        
        return ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Text(
                    "🎉 Achievement Unlocked!",
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=achievement.rarity_color,
                ),
                ft.Text(achievement.icon, size=48),
                ft.Text(
                    achievement.name,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    achievement.description,
                    size=13,
                    color=colors.with_opacity(0.7, colors.ON_SURFACE),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=ft.Text(
                        achievement.rarity_name,
                        size=12,
                        color=colors.WHITE,
                        weight=ft.FontWeight.W_500,
                    ),
                    bgcolor=achievement.rarity_color,
                    padding=ft.Padding(left=14, right=14, top=5, bottom=5),
                    border_radius=12,
                ),
            ],
        )
