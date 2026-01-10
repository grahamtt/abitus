"""Interview-based character assessment view."""

import flet as ft
from typing import Callable, Optional

from utils.compat import colors, icons
from models.character import Character
from models.stats import StatType, STAT_DEFINITIONS
from services.interview import InterviewService, InterviewSession


class InterviewView(ft.Container):
    """Multi-step interview flow for character assessment."""
    
    def __init__(self, on_complete: Callable[[Character], None]):
        self.on_complete = on_complete
        self.character = Character()
        
        # Initialize interview service and session
        self.service = InterviewService()
        self.session: Optional[InterviewSession] = None
        
        # UI state
        self.selected_answers: list[int] = []
        self.show_intro = True  # Show category intro
        
        # References for updating without full rebuild
        self._answer_containers: list[ft.Container] = []
        self._answer_icons: list[ft.Icon] = []
        self._continue_button: Optional[ft.ElevatedButton] = None
        
        super().__init__(
            content=self._build_content(),
            expand=True,
            padding=0,
        )
    
    def did_mount(self):
        """Called when view is mounted - start the session."""
        self.session = self.service.start_session()
        self._rebuild()
    
    def _rebuild(self):
        """Rebuild the current content."""
        self.content = self._build_content()
        self.update()
    
    def _build_content(self) -> ft.Control:
        """Build content based on current state."""
        if self.session is None:
            return self._build_loading()
        
        if self.session.is_complete:
            return self._build_completion()
        
        if self.show_intro:
            return self._build_category_intro()
        
        return self._build_question()
    
    def _build_loading(self) -> ft.Control:
        """Loading state."""
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Preparing your adventure...", size=16),
                ],
            ),
            expand=True,
        )
    
    def _build_category_intro(self) -> ft.Control:
        """Build category introduction screen."""
        category = self.session.current_category
        if not category:
            self.show_intro = False
            return self._build_question()
        
        # Category icons
        category_icons = {
            "daily_life": "🌅",
            "physical_prowess": "⚔️",
            "mind_and_learning": "📚",
            "spirit_and_emotion": "🧘",
            "relationships": "💝",
            "work_and_prosperity": "💰",
            "hobbies_and_mastery": "🎯",
            "goals_and_aspirations": "✨",
        }
        
        icon = category_icons.get(category.id, "📜")
        
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    # Progress indicator
                    self._build_progress_bar(),
                    
                    ft.Container(height=40),
                    
                    # Category icon
                    ft.Text(icon, size=80),
                    
                    ft.Container(height=20),
                    
                    # Category name
                    ft.Text(
                        category.name,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    
                    ft.Container(height=16),
                    
                    # Category intro
                    ft.Container(
                        content=ft.Text(
                            category.intro,
                            size=16,
                            italic=True,
                            text_align=ft.TextAlign.CENTER,
                            color=colors.with_opacity(0.8, colors.ON_SURFACE),
                        ),
                        padding=ft.Padding(left=32, right=32, top=0, bottom=0),
                    ),
                    
                    ft.Container(height=8),
                    
                    # Question count
                    ft.Text(
                        f"{len(category.questions)} questions",
                        size=14,
                        color=colors.with_opacity(0.5, colors.ON_SURFACE),
                    ),
                    
                    ft.Container(expand=True),
                    
                    # Continue button
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Begin", weight=ft.FontWeight.W_500),
                                    ft.Icon(icons.ARROW_FORWARD, size=18),
                                ],
                            ),
                            bgcolor="#6366f1",
                            color=colors.WHITE,
                            width=200,
                            on_click=lambda e: self._start_category(),
                        ),
                        padding=ft.Padding(0, 0, 0, 40),
                    ),
                ],
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[
                    colors.with_opacity(0.08, "#6366f1"),
                    colors.TRANSPARENT,
                ],
            ),
        )
    
    def _build_question(self) -> ft.Control:
        """Build question screen."""
        question = self.session.current_question
        if not question:
            return self._build_completion()
        
        category = self.session.current_category
        
        # Clear previous references
        self._answer_containers = []
        self._answer_icons = []
        
        # Build answer options and store references
        answer_controls = []
        for i, answer in enumerate(question.answers):
            container, icon = self._build_answer_option(i, answer, question.multiple_select)
            answer_controls.append(container)
            self._answer_containers.append(container)
            self._answer_icons.append(icon)
        
        # Build continue button with reference
        self._continue_button = ft.ElevatedButton(
            content=ft.Row(
                spacing=6,
                controls=[
                    ft.Text(
                        "Continue" if self.selected_answers else "Skip",
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Icon(icons.ARROW_FORWARD, size=18),
                ],
            ),
            bgcolor="#6366f1" if self.selected_answers else colors.with_opacity(0.3, "#6366f1"),
            color=colors.WHITE,
            on_click=lambda e: self._submit_answer(),
        )
        
        return ft.Container(
            content=ft.Column(
                expand=True,
                controls=[
                    # Progress bar
                    self._build_progress_bar(),
                    
                    # Category label
                    ft.Container(
                        content=ft.Text(
                            category.name if category else "",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color="#6366f1",
                        ),
                        padding=ft.Padding(left=24, right=24, top=16, bottom=0),
                    ),
                    
                    # Question text
                    ft.Container(
                        content=ft.Text(
                            question.text,
                            size=20,
                            weight=ft.FontWeight.W_500,
                            text_align=ft.TextAlign.LEFT,
                        ),
                        padding=ft.Padding(left=24, right=24, top=8, bottom=16),
                    ),
                    
                    # Multiple select hint
                    ft.Container(
                        content=ft.Text(
                            "Select all that apply" if question.multiple_select else "Choose one",
                            size=12,
                            color=colors.with_opacity(0.5, colors.ON_SURFACE),
                        ),
                        padding=ft.Padding(left=24, right=24, top=0, bottom=8),
                    ),
                    
                    # Answer options
                    ft.Container(
                        content=ft.Column(
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                            controls=answer_controls,
                        ),
                        expand=True,
                        padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                    ),
                    
                    # Navigation
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(icons.ARROW_BACK, size=18),
                                            ft.Text("Back"),
                                        ],
                                    ),
                                    on_click=lambda e: self._go_back(),
                                ),
                                self._continue_button,
                            ],
                        ),
                        padding=ft.Padding(16, 16, 16, 24),
                    ),
                ],
            ),
            expand=True,
        )
    
    def _build_answer_option(self, index: int, answer, multiple_select: bool) -> tuple[ft.Container, ft.Icon]:
        """Build a single answer option. Returns (container, icon) for later updates."""
        is_selected = index in self.selected_answers
        
        # Create icon with reference for later updates
        icon = ft.Icon(
            icons.CHECK_BOX if is_selected and multiple_select
            else icons.CHECK_BOX_OUTLINE_BLANK if multiple_select
            else icons.RADIO_BUTTON_CHECKED if is_selected
            else icons.RADIO_BUTTON_UNCHECKED,
            color="#6366f1" if is_selected else colors.with_opacity(0.4, colors.ON_SURFACE),
            size=22,
        )
        
        container = ft.Container(
            content=ft.Row(
                spacing=12,
                controls=[
                    # Selection indicator
                    ft.Container(content=icon),
                    # Answer text
                    ft.Container(
                        content=ft.Text(
                            answer.text,
                            size=15,
                            color=colors.ON_SURFACE if is_selected 
                                  else colors.with_opacity(0.8, colors.ON_SURFACE),
                        ),
                        expand=True,
                    ),
                ],
            ),
            padding=ft.Padding(16, 14, 16, 14),
            border_radius=12,
            bgcolor=colors.with_opacity(0.1, "#6366f1") if is_selected 
                    else colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.all(2, "#6366f1") if is_selected 
                   else ft.border.all(1, colors.with_opacity(0.1, colors.ON_SURFACE)),
            on_click=lambda e, idx=index: self._toggle_answer(idx, multiple_select),
            ink=True,
        )
        
        return container, icon
    
    def _build_progress_bar(self) -> ft.Control:
        """Build progress indicator."""
        progress = self.session.progress if self.session else 0
        
        return ft.Container(
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"Question {self.session.questions_answered + 1}" if self.session else "",
                                size=12,
                                color=colors.with_opacity(0.5, colors.ON_SURFACE),
                            ),
                            ft.Text(
                                f"{int(progress * 100)}%",
                                size=12,
                                color=colors.with_opacity(0.5, colors.ON_SURFACE),
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=progress,
                        color="#6366f1",
                        bgcolor=colors.with_opacity(0.1, "#6366f1"),
                        height=4,
                    ),
                ],
            ),
            padding=ft.Padding(left=24, right=24, top=16, bottom=0),
        )
    
    def _build_completion(self) -> ft.Control:
        """Build completion/summary screen."""
        # Calculate stats preview
        if self.session:
            # Apply scores temporarily to see results
            temp_char = Character()
            temp_char.apply_interview_scores(self.session.accumulated_scores)
            
            stat_summaries = []
            for stat_type in StatType:
                stat = temp_char.stats[stat_type]
                definition = stat.definition
                
                # Get strongest sub-facet for this stat
                strongest = stat.get_strongest_facets(1)
                strongest_name = strongest[0].definition.name if strongest else ""
                
                stat_summaries.append(
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=10,
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
                                                    f"Strongest: {strongest_name}",
                                                    size=11,
                                                    color=colors.with_opacity(0.5, colors.ON_SURFACE),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f"Lv.{stat.level}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=definition.color,
                                    ),
                                    bgcolor=colors.with_opacity(0.15, definition.color),
                                    padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                                    border_radius=12,
                                ),
                            ],
                        ),
                        padding=ft.Padding(12, 10, 12, 10),
                        bgcolor=colors.with_opacity(0.03, definition.color),
                        border_radius=10,
                    )
                )
        else:
            stat_summaries = []
        
        return ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Container(height=40),
                    
                    # Completion icon
                    ft.Text("🎉", size=64),
                    
                    ft.Container(height=16),
                    
                    ft.Text(
                        "Assessment Complete!",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    
                    ft.Container(height=8),
                    
                    ft.Text(
                        "Your character has been forged",
                        size=14,
                        color=colors.with_opacity(0.6, colors.ON_SURFACE),
                    ),
                    
                    ft.Container(height=24),
                    
                    # Stats summary
                    ft.Container(
                        content=ft.Column(
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            controls=stat_summaries,
                        ),
                        expand=True,
                        padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                    ),
                    
                    # Name input
                    ft.Container(
                        content=ft.TextField(
                            label="Your Name",
                            value=self.character.name if self.character.name != "Adventurer" else "",
                            hint_text="Enter your adventurer name",
                            border_radius=12,
                            text_size=16,
                            content_padding=ft.Padding(16, 12, 16, 12),
                            on_change=lambda e: setattr(self.character, 'name', e.control.value or "Adventurer"),
                        ),
                        padding=ft.Padding(left=20, right=20, top=16, bottom=0),
                    ),
                    
                    # Start button
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Begin Your Adventure!", weight=ft.FontWeight.W_600),
                                    ft.Icon(icons.ROCKET_LAUNCH, size=20),
                                ],
                            ),
                            bgcolor="#6366f1",
                            color=colors.WHITE,
                            width=280,
                            height=50,
                            on_click=lambda e: self._finish(),
                        ),
                        padding=ft.Padding(20, 24, 20, 40),
                    ),
                ],
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[
                    colors.with_opacity(0.05, "#10b981"),
                    colors.TRANSPARENT,
                ],
            ),
        )
    
    def _start_category(self):
        """Start answering questions in current category."""
        self.show_intro = False
        self.selected_answers = []
        self._rebuild()
    
    def _toggle_answer(self, index: int, multiple_select: bool):
        """Toggle answer selection - updates controls directly without full rebuild."""
        # Track previous selection for single-select mode
        prev_selected = list(self.selected_answers)
        
        if multiple_select:
            if index in self.selected_answers:
                self.selected_answers.remove(index)
            else:
                self.selected_answers.append(index)
        else:
            self.selected_answers = [index]
        
        # Update only the affected answer controls
        for i, (container, icon) in enumerate(zip(self._answer_containers, self._answer_icons)):
            is_selected = i in self.selected_answers
            was_selected = i in prev_selected
            
            # Only update if state changed
            if is_selected != was_selected:
                # Update icon
                if multiple_select:
                    icon.name = icons.CHECK_BOX if is_selected else icons.CHECK_BOX_OUTLINE_BLANK
                else:
                    icon.name = icons.RADIO_BUTTON_CHECKED if is_selected else icons.RADIO_BUTTON_UNCHECKED
                icon.color = "#6366f1" if is_selected else colors.with_opacity(0.4, colors.ON_SURFACE)
                
                # Update container styling
                container.bgcolor = colors.with_opacity(0.1, "#6366f1") if is_selected else colors.SURFACE_CONTAINER_HIGH
                container.border = ft.border.all(2, "#6366f1") if is_selected else ft.border.all(1, colors.with_opacity(0.1, colors.ON_SURFACE))
        
        # Update continue button
        if self._continue_button:
            has_selection = len(self.selected_answers) > 0
            self._continue_button.bgcolor = "#6366f1" if has_selection else colors.with_opacity(0.3, "#6366f1")
            # Update button text
            if self._continue_button.content and hasattr(self._continue_button.content, 'controls'):
                text_control = self._continue_button.content.controls[0]
                if hasattr(text_control, 'value'):
                    text_control.value = "Continue" if has_selection else "Skip"
        
        # Update only changed controls
        self.update()
    
    def _submit_answer(self):
        """Submit current answer and advance."""
        if not self.session:
            return
        
        # If no selection and not multiple select, don't advance
        question = self.session.current_question
        if not self.selected_answers and question and not question.multiple_select:
            # Allow skip with empty selection
            pass
        
        # Record the answer
        old_category = self.session.current_category_idx
        is_complete = self.session.answer_current(self.selected_answers)
        new_category = self.session.current_category_idx
        
        # Reset selection
        self.selected_answers = []
        
        # Show category intro if we moved to a new category
        if new_category != old_category and not is_complete:
            self.show_intro = True
        
        self._rebuild()
    
    def _go_back(self):
        """Go back to previous question."""
        if not self.session:
            return
        
        old_category = self.session.current_category_idx
        
        if self.session.go_back():
            new_category = self.session.current_category_idx
            
            # If we went back to previous category, show its intro? No, go to last question
            self.show_intro = False
            
            # Restore previous answer if any
            question = self.session.current_question
            if question and question.id in self.session.responses:
                self.selected_answers = list(self.session.responses[question.id])
            else:
                self.selected_answers = []
            
            self._rebuild()
    
    def _finish(self):
        """Finish assessment and create character."""
        if not self.session:
            return
        
        # Apply all scores to character
        self.session.apply_to_character(self.character)
        
        # Call completion handler
        self.on_complete(self.character)

