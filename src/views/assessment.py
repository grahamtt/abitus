"""Initial character assessment view."""

import flet as ft
from typing import Callable, Optional
from models.character import Character
from models.stats import StatType, STAT_DEFINITIONS


class AssessmentView(ft.Container):
    """Multi-step assessment flow to initialize character."""
    
    def __init__(self, on_complete: Callable[[Character], None]):
        self.on_complete = on_complete
        self.current_step = 0
        self.character = Character()
        
        # Assessment data
        self.name = ""
        self.stat_ratings: dict[StatType, int] = {st: 5 for st in StatType}
        self.stat_targets: dict[StatType, int] = {st: 10 for st in StatType}
        self.time_available = 30
        self.challenge_level = 2
        
        # References to update dynamically
        self._value_refs: dict[str, ft.Text] = {}
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def _build_content(self) -> ft.Control:
        # Clear refs when rebuilding
        self._value_refs = {}
        
        steps = [
            self._build_welcome_step,
            self._build_name_step,
            self._build_current_stats_step,
            self._build_target_stats_step,
            self._build_time_step,
            self._build_challenge_step,
            self._build_summary_step,
        ]
        
        return steps[self.current_step]()
    
    def _rebuild_current_step(self):
        """Rebuild just the current step's content."""
        self.content = self._build_content()
        self.update()
    
    def _build_step_container(self, title: str, subtitle: str, 
                               content: ft.Control, 
                               show_back: bool = True,
                               next_text: str = "Continue",
                               on_next: Optional[Callable] = None) -> ft.Control:
        """Build a consistent step layout."""
        
        def handle_next(e):
            if on_next:
                on_next()
            else:
                self._next_step()
        
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    title,
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    subtitle,
                                    size=14,
                                    color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                        ),
                        padding=ft.Padding(left=0, right=0, top=40, bottom=20),
                    ),
                    
                    # Content area - expand to fill available space
                    ft.Container(
                        content=content,
                        expand=True,
                        padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                    ),
                    
                    # Navigation
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN if show_back else ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.TextButton(
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.ARROW_BACK, size=18),
                                            ft.Text("Back"),
                                        ],
                                    ),
                                    on_click=lambda e: self._prev_step(),
                                ) if show_back else ft.Container(),
                                ft.FilledButton(
                                    content=ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Text(next_text, weight=ft.FontWeight.W_500),
                                            ft.Icon(ft.Icons.ARROW_FORWARD, size=18),
                                        ],
                                    ),
                                    bgcolor="#6366f1",
                                    color=ft.Colors.WHITE,
                                    on_click=handle_next,
                                ),
                            ],
                        ),
                        padding=ft.Padding(20, 20, 20, 20),
                    ),
                ],
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[
                    ft.Colors.with_opacity(0.05, "#6366f1"),
                    ft.Colors.TRANSPARENT,
                ],
            ),
        )
    
    def _build_welcome_step(self) -> ft.Control:
        return self._build_step_container(
            title="⚔️ Welcome, Adventurer!",
            subtitle="Your journey of self-improvement begins here",
            show_back=False,
            next_text="Begin Quest",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
                controls=[
                    ft.Container(
                        content=ft.Text("🎮", size=80),
                        padding=20,
                    ),
                    ft.Text(
                        "Abitus transforms your personal growth into an epic RPG adventure.",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE),
                    ),
                    ft.Container(
                        content=ft.Column(
                            spacing=12,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                self._feature_item("📊", "Track six life dimensions as character stats"),
                                self._feature_item("⚔️", "Complete quests to earn XP and level up"),
                                self._feature_item("🏆", "Unlock achievements and earn titles"),
                                self._feature_item("🎯", "Personalized quests based on your goals"),
                            ],
                        ),
                        padding=ft.Padding(left=10, right=10, top=20, bottom=20),
                    ),
                    ft.Text(
                        "Let's learn about you to create your character...",
                        size=14,
                        italic=True,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                    ),
                ],
            ),
        )
    
    def _feature_item(self, icon: str, text: str) -> ft.Control:
        return ft.Row(
            spacing=12,
            controls=[
                ft.Text(icon, size=20),
                ft.Text(text, size=14),
            ],
        )
    
    def _build_name_step(self) -> ft.Control:
        name_field = ft.TextField(
            label="Your Name",
            value=self.name,
            hint_text="Enter your adventurer name",
            border_radius=12,
            text_size=18,
            content_padding=ft.Padding(16, 16, 16, 16),
            on_change=lambda e: setattr(self, 'name', e.control.value),
        )
        
        return self._build_step_container(
            title="👤 What's Your Name?",
            subtitle="Choose a name for your character",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Container(
                        content=ft.Text("🧙", size=60),
                    ),
                    ft.Container(
                        content=name_field,
                        width=300,
                    ),
                    ft.Text(
                        "This is how you'll be known throughout your adventure",
                        size=12,
                        color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                    ),
                ],
            ),
        )
    
    def _build_current_stats_step(self) -> ft.Control:
        sliders = []
        for stat_type in StatType:
            slider_widget = self._build_stat_slider_widget(
                stat_type=stat_type,
                subtitle="Where are you now?",
                value=self.stat_ratings[stat_type],
                min_val=1,
                on_change=lambda val, st=stat_type: self._update_stat_rating(st, val),
            )
            sliders.append(slider_widget)
        
        return self._build_step_container(
            title="📊 Current Stats",
            subtitle="Rate yourself honestly in each life dimension (1-20)",
            content=ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=sliders,
            ),
        )
    
    def _build_target_stats_step(self) -> ft.Control:
        sliders = []
        for stat_type in StatType:
            slider_widget = self._build_stat_slider_widget(
                stat_type=stat_type,
                subtitle=f"Current: {self.stat_ratings[stat_type]}",
                value=self.stat_targets[stat_type],
                min_val=self.stat_ratings[stat_type],
                on_change=lambda val, st=stat_type: self._update_stat_target(st, val),
            )
            sliders.append(slider_widget)
        
        return self._build_step_container(
            title="🎯 Target Goals",
            subtitle="Where do you want to be? Set your target level for each stat",
            content=ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=sliders,
            ),
        )
    
    def _build_stat_slider_widget(self, stat_type: StatType, subtitle: str, 
                                   value: int, min_val: int, on_change) -> ft.Control:
        """Build a stat slider with reactive value display."""
        definition = STAT_DEFINITIONS[stat_type]
        
        # Create a ref for the value text so we can update it
        value_text = ft.Text(
            str(value),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=definition.color,
        )
        
        def handle_slider_change(e):
            new_val = int(e.control.value)
            value_text.value = str(new_val)
            value_text.update()
            on_change(new_val)
        
        return ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(definition.icon, size=20),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                definition.name,
                                                size=14,
                                                weight=ft.FontWeight.W_500,
                                            ),
                                            ft.Text(
                                                subtitle,
                                                size=11,
                                                color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=value_text,
                                bgcolor=ft.Colors.with_opacity(0.15, definition.color),
                                padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                                border_radius=12,
                            ),
                        ],
                    ),
                    ft.Slider(
                        value=value,
                        min=min_val,
                        max=20,
                        divisions=20 - min_val if 20 - min_val > 0 else 1,
                        active_color=definition.color,
                        on_change=handle_slider_change,
                    ),
                ],
            ),
            padding=ft.Padding(12, 12, 12, 12),
            bgcolor=ft.Colors.with_opacity(0.05, definition.color),
            border_radius=12,
        )
    
    def _update_stat_rating(self, stat_type: StatType, value: int):
        """Update stat rating value."""
        self.stat_ratings[stat_type] = value
        # Also update target if it's below the new rating
        if self.stat_targets[stat_type] < value:
            self.stat_targets[stat_type] = value
    
    def _update_stat_target(self, stat_type: StatType, value: int):
        """Update stat target value."""
        self.stat_targets[stat_type] = value
    
    def _build_time_step(self) -> ft.Control:
        time_options = [
            (15, "🌱", "Light", "15 minutes/day"),
            (30, "🌿", "Moderate", "30 minutes/day"),
            (60, "🌳", "Committed", "1 hour/day"),
            (120, "🏔️", "Intense", "2+ hours/day"),
        ]
        
        # Build option cards with current selection state
        option_cards = []
        for minutes, icon, label, desc in time_options:
            card = self._build_option_card(
                icon=icon,
                label=label,
                desc=desc,
                selected=self.time_available == minutes,
                on_click=lambda e, m=minutes: self._select_time(m),
            )
            option_cards.append(card)
        
        return self._build_step_container(
            title="⏰ Time Investment",
            subtitle="How much time can you dedicate to self-improvement daily?",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=option_cards,
            ),
        )
    
    def _select_time(self, minutes: int):
        """Handle time selection."""
        self.time_available = minutes
        self._rebuild_current_step()
    
    def _build_challenge_step(self) -> ft.Control:
        challenge_options = [
            (1, "🌸", "Gentle", "Easy quests, low pressure"),
            (2, "⚔️", "Balanced", "Moderate challenge"),
            (3, "🔥", "Ambitious", "Push yourself"),
            (4, "💀", "Hardcore", "Maximum growth mode"),
        ]
        
        option_cards = []
        for level, icon, label, desc in challenge_options:
            card = self._build_option_card(
                icon=icon,
                label=label,
                desc=desc,
                selected=self.challenge_level == level,
                on_click=lambda e, l=level: self._select_challenge(l),
            )
            option_cards.append(card)
        
        return self._build_step_container(
            title="🎮 Challenge Level",
            subtitle="How hard do you want to push yourself?",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=option_cards,
            ),
        )
    
    def _select_challenge(self, level: int):
        """Handle challenge level selection."""
        self.challenge_level = level
        self._rebuild_current_step()
    
    def _build_option_card(self, icon: str, label: str, desc: str,
                           selected: bool, on_click) -> ft.Control:
        """Build a selectable option card."""
        return ft.Container(
            content=ft.Row(
                spacing=16,
                controls=[
                    ft.Text(icon, size=28),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                label,
                                size=16,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Text(
                                desc,
                                size=12,
                                color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    ft.Container(expand=True),
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if selected else ft.Icons.CIRCLE_OUTLINED,
                        color="#6366f1" if selected else ft.Colors.with_opacity(0.3, ft.Colors.ON_SURFACE),
                        size=24,
                    ),
                ],
            ),
            padding=ft.Padding(16, 16, 16, 16),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.1, "#6366f1") if selected else ft.Colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.all(2, "#6366f1") if selected else ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
            on_click=on_click,
            ink=True,
        )
    
    def _build_summary_step(self) -> ft.Control:
        # Build stat summary rows
        stat_summary = []
        for stat_type in StatType:
            definition = STAT_DEFINITIONS[stat_type]
            current = self.stat_ratings[stat_type]
            target = self.stat_targets[stat_type]
            
            stat_summary.append(
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(definition.icon, size=18),
                                    ft.Text(definition.name, size=14),
                                ],
                            ),
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        f"Lv.{current}",
                                        size=14,
                                        color=definition.color,
                                    ),
                                    ft.Icon(ft.Icons.ARROW_FORWARD, size=14),
                                    ft.Text(
                                        f"Lv.{target}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=definition.color,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    bgcolor=ft.Colors.with_opacity(0.05, definition.color),
                    border_radius=8,
                )
            )
        
        # The entire content should be scrollable
        return self._build_step_container(
            title="✨ Ready to Begin!",
            subtitle="Here's your character summary",
            next_text="Start Adventure!",
            on_next=self._finish_assessment,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=[
                    # Character avatar and name
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text("🧙", size=48),
                                ft.Text(
                                    self.name or "Adventurer",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Novice Explorer",
                                    size=14,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                ),
                            ],
                        ),
                    ),
                    
                    ft.Divider(height=1),
                    
                    ft.Text(
                        "Your Stats",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                    ),
                    
                    # Stats list
                    ft.Column(
                        spacing=6,
                        controls=stat_summary,
                    ),
                    
                    ft.Divider(height=1),
                    
                    # Time and challenge settings
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=40,
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("⏰", size=24),
                                    ft.Text(
                                        f"{self.time_available} min/day",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        "Daily Time",
                                        size=11,
                                        color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                                    ),
                                ],
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("🎮", size=24),
                                    ft.Text(
                                        ["Gentle", "Balanced", "Ambitious", "Hardcore"][self.challenge_level - 1],
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        "Challenge",
                                        size=11,
                                        color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    
                    # Some bottom padding
                    ft.Container(height=20),
                ],
            ),
        )
    
    def _next_step(self):
        self.current_step += 1
        self.content = self._build_content()
        self.update()
    
    def _prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.content = self._build_content()
            self.update()
    
    def _finish_assessment(self):
        # Build the character with assessment data
        self.character.name = self.name or "Adventurer"
        self.character.assessment_completed = True
        self.character.available_time_minutes = self.time_available
        self.character.challenge_level = self.challenge_level
        
        # Set starting XP based on current ratings (each level = ~100 XP)
        for stat_type in StatType:
            current_level = self.stat_ratings[stat_type]
            target_level = self.stat_targets[stat_type]
            
            # Calculate XP to reach current level
            if current_level > 1:
                starting_xp = int(100 * ((current_level - 1) ** 1.5))
            else:
                starting_xp = 0
            
            self.character.stats[stat_type].current_xp = starting_xp
            self.character.stats[stat_type].target_level = target_level
        
        # Generate title
        self.character.title = self.character.get_title()
        
        # Call completion handler
        self.on_complete(self.character)
