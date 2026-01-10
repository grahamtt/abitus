"""Settings view for app configuration."""

import flet as ft
from typing import Callable

from utils.compat import colors, icons
from models.character import Character


class SettingsView(ft.Container):
    """Settings and preferences view."""
    
    def __init__(
        self,
        character: Character,
        on_back: Callable[[], None],
        on_reset_data: Callable[[], None],
        on_update_settings: Callable[[dict], None],
    ):
        self.character = character
        self.on_back = on_back
        self.on_reset_data = on_reset_data
        self.on_update_settings = on_update_settings
        
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
                
                # Content
                ft.Container(
                    content=ft.Column(
                        spacing=24,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            # Profile section
                            self._build_profile_section(),
                            
                            # Quest preferences
                            self._build_quest_preferences_section(),
                            
                            # App settings
                            self._build_app_settings_section(),
                            
                            # Data management
                            self._build_data_section(),
                            
                            # About
                            self._build_about_section(),
                        ],
                    ),
                    padding=ft.Padding(20, 20, 20, 20),
                    expand=True,
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
                        "Settings",
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
    
    def _build_profile_section(self) -> ft.Control:
        char = self.character
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "👤 Profile",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            # Name
                            ft.TextField(
                                label="Character Name",
                                value=char.name,
                                border_radius=10,
                                on_change=lambda e: self._update_setting("name", e.control.value),
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _build_quest_preferences_section(self) -> ft.Control:
        char = self.character
        
        time_options = [
            (15, "15 minutes"),
            (30, "30 minutes"),
            (60, "1 hour"),
            (120, "2 hours"),
        ]
        
        challenge_options = [
            (1, "Gentle 🌸"),
            (2, "Balanced ⚔️"),
            (3, "Ambitious 🔥"),
            (4, "Hardcore 💀"),
        ]
        
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "⚔️ Quest Preferences",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            # Daily time
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Daily Time Available",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Dropdown(
                                        value=str(char.available_time_minutes),
                                        options=[
                                            ft.dropdown.Option(str(v), label)
                                            for v, label in time_options
                                        ],
                                        border_radius=10,
                                        on_change=lambda e: self._update_setting(
                                            "available_time_minutes", 
                                            int(e.control.value)
                                        ),
                                    ),
                                ],
                            ),
                            
                            # Challenge level
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "Challenge Level",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Dropdown(
                                        value=str(char.challenge_level),
                                        options=[
                                            ft.dropdown.Option(str(v), label)
                                            for v, label in challenge_options
                                        ],
                                        border_radius=10,
                                        on_change=lambda e: self._update_setting(
                                            "challenge_level",
                                            int(e.control.value)
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _build_app_settings_section(self) -> ft.Control:
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "⚙️ App Settings",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            self._setting_toggle(
                                "Notifications",
                                "Get reminders for daily quests",
                                "notifications",
                                True,
                            ),
                            ft.Divider(height=1),
                            self._setting_toggle(
                                "Sound Effects",
                                "Play sounds on quest completion",
                                "sounds",
                                True,
                            ),
                            ft.Divider(height=1),
                            self._setting_toggle(
                                "Random Encounters",
                                "Enable surprise quest opportunities",
                                "random_encounters",
                                True,
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _setting_toggle(self, title: str, subtitle: str, key: str, 
                        default: bool) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                title,
                                size=14,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                subtitle,
                                size=12,
                                color=colors.with_opacity(0.6, colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    ft.Switch(
                        value=default,
                        active_color="#6366f1",
                        on_change=lambda e, k=key: self._update_setting(k, e.control.value),
                    ),
                ],
            ),
            padding=ft.Padding(left=0, right=0, top=8, bottom=8),
        )
    
    def _build_data_section(self) -> ft.Control:
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "💾 Data Management",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text(
                                "Your data is stored locally on this device.",
                                size=13,
                                color=colors.with_opacity(0.7, colors.ON_SURFACE),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=8,
                                    controls=[
                                        ft.Icon(icons.DELETE_FOREVER, size=18, color=colors.ERROR),
                                        ft.Text(
                                            "Reset All Data",
                                            color=colors.ERROR,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                    ],
                                ),
                                on_click=lambda e: self._confirm_reset(),
                            ),
                        ],
                    ),
                    padding=ft.Padding(16, 16, 16, 16),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _build_about_section(self) -> ft.Control:
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "ℹ️ About",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                        controls=[
                            ft.Text("🎮", size=40),
                            ft.Text(
                                "Abitus RPG",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Version 1.0.0",
                                size=13,
                                color=colors.with_opacity(0.6, colors.ON_SURFACE),
                            ),
                            ft.Text(
                                "Level up your real life through epic quests and meaningful progression.",
                                size=13,
                                text_align=ft.TextAlign.CENTER,
                                color=colors.with_opacity(0.7, colors.ON_SURFACE),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    '"The journey of a thousand miles begins with a single quest." 🌟',
                                    size=12,
                                    italic=True,
                                    text_align=ft.TextAlign.CENTER,
                                    color=colors.with_opacity(0.5, colors.ON_SURFACE),
                                ),
                                padding=ft.Padding(left=0, right=0, top=8, bottom=0),
                            ),
                        ],
                    ),
                    padding=ft.Padding(20, 20, 20, 20),
                    bgcolor=colors.SURFACE_CONTAINER_HIGH,
                    border_radius=12,
                ),
            ],
        )
    
    def _update_setting(self, key: str, value):
        """Update a setting."""
        self.on_update_settings({key: value})
    
    def _confirm_reset(self):
        """Show reset confirmation dialog."""
        # This will be handled by the main app
        self.on_reset_data()
    
    def refresh(self, character: Character):
        """Refresh the view with updated data."""
        self.character = character
        self.content = self._build_content()
        self.update()

