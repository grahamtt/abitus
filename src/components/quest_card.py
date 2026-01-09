"""Quest card component for displaying quest information."""

import flet as ft
from models.quest import Quest, QuestType, QuestStatus
from models.stats import STAT_DEFINITIONS


class QuestCard(ft.Container):
    """A card displaying quest information with actions."""
    
    def __init__(
        self,
        quest: Quest,
        on_accept=None,
        on_complete=None,
        on_abandon=None,
        on_write_entry=None,  # For journal-satisfiable quests
        expanded: bool = False,
    ):
        self.quest = quest
        self._on_accept = on_accept
        self._on_complete = on_complete
        self._on_abandon = on_abandon
        self._on_write_entry = on_write_entry
        self.expanded = expanded
        
        # Get stat color for theming
        self.stat_def = STAT_DEFINITIONS[quest.primary_stat]
        
        super().__init__(
            content=self._build_content(),
            padding=ft.Padding(16, 16, 16, 16),
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.border.all(1, ft.Colors.with_opacity(0.15, self.stat_def.color)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
    
    def _build_content(self) -> ft.Control:
        quest = self.quest
        
        # Status badge colors
        status_colors = {
            QuestStatus.AVAILABLE: "#22c55e",
            QuestStatus.ACTIVE: "#3b82f6",
            QuestStatus.COMPLETED: "#9ca3af",
            QuestStatus.FAILED: "#ef4444",
            QuestStatus.LOCKED: "#6b7280",
        }
        
        status_text = {
            QuestStatus.AVAILABLE: "Available",
            QuestStatus.ACTIVE: "In Progress",
            QuestStatus.COMPLETED: "Completed",
            QuestStatus.FAILED: "Failed",
            QuestStatus.LOCKED: "Locked",
        }
        
        return ft.Column(
            spacing=12,
            controls=[
                # Header row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                # Quest type icon
                                ft.Container(
                                    content=ft.Text(quest.type_icon, size=20),
                                    bgcolor=ft.Colors.with_opacity(0.15, self.stat_def.color),
                                    padding=ft.Padding(8, 8, 8, 8),
                                    border_radius=10,
                                ),
                                # Title and type
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            quest.title,
                                            size=16,
                                            weight=ft.FontWeight.W_600,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            f"{quest.quest_type.value.title()} Quest",
                                            size=12,
                                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Status badge
                        ft.Container(
                            content=ft.Text(
                                status_text[quest.status],
                                size=11,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=status_colors[quest.status],
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            border_radius=12,
                        ),
                    ],
                ),
                
                # Description
                ft.Text(
                    quest.description,
                    size=14,
                    color=ft.Colors.with_opacity(0.8, ft.Colors.ON_SURFACE),
                ),
                
                # Stats row
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    spacing=16,
                    controls=[
                        # XP reward
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.STAR, size=16, color="#f59e0b"),
                                ft.Text(
                                    f"+{quest.xp_reward} XP",
                                    size=13,
                                    weight=ft.FontWeight.W_500,
                                    color="#f59e0b",
                                ),
                            ],
                        ),
                        # Primary stat
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Text(self.stat_def.icon, size=14),
                                ft.Text(
                                    self.stat_def.name,
                                    size=13,
                                    color=self.stat_def.color,
                                ),
                            ],
                        ),
                        # Duration
                        ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.TIMER, size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE)),
                                ft.Text(
                                    f"{quest.duration_minutes} min",
                                    size=13,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                ),
                            ],
                        ) if quest.duration_minutes > 0 else ft.Container(),
                        # Difficulty
                        ft.Text(
                            quest.difficulty_stars,
                            size=12,
                            color="#f59e0b",
                        ),
                    ],
                ),
                
                # Action buttons
                self._build_actions(),
            ],
        )
    
    def _build_actions(self) -> ft.Control:
        """Build action buttons based on quest status."""
        quest = self.quest
        
        if quest.status == QuestStatus.AVAILABLE:
            return ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.FilledButton(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW, size=18),
                                ft.Text("Accept Quest", weight=ft.FontWeight.W_500),
                            ],
                        ),
                        bgcolor=self.stat_def.color,
                        color=ft.Colors.WHITE,
                        on_click=self._on_accept,
                    ),
                ],
            )
        
        elif quest.status == QuestStatus.ACTIVE:
            buttons = [
                ft.TextButton(
                    content=ft.Text("Abandon", color=ft.Colors.ERROR),
                    on_click=self._on_abandon,
                ),
            ]
            
            # Add "Write Entry" button for journal-satisfiable quests
            if quest.requires_journal and self._on_write_entry:
                buttons.append(
                    ft.FilledButton(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.EDIT_NOTE, size=18),
                                ft.Text("Write Entry", weight=ft.FontWeight.W_500),
                            ],
                        ),
                        bgcolor="#6366f1",
                        color=ft.Colors.WHITE,
                        on_click=self._on_write_entry,
                    ),
                )
            
            buttons.append(
                ft.FilledButton(
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.CHECK, size=18),
                            ft.Text("Complete", weight=ft.FontWeight.W_500),
                        ],
                    ),
                    bgcolor="#22c55e",
                    color=ft.Colors.WHITE,
                    on_click=self._on_complete,
                ),
            )
            
            return ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=buttons,
            )
        
        elif quest.status == QuestStatus.COMPLETED:
            return ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color="#22c55e"),
                            ft.Text(
                                "Quest Completed!",
                                color="#22c55e",
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                ],
            )
        
        return ft.Container()  # No actions for other states


class QuestListItem(ft.Container):
    """A compact quest list item for quest logs."""
    
    def __init__(self, quest: Quest, on_click=None):
        self.quest = quest
        self.stat_def = STAT_DEFINITIONS[quest.primary_stat]
        
        super().__init__(
            content=self._build_content(),
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, self.stat_def.color),
            on_click=on_click,
            ink=True,
        )
    
    def _build_content(self) -> ft.Control:
        quest = self.quest
        
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Text(quest.type_icon, size=20),
                        ft.Column(
                            spacing=2,
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
                                        ft.Text(self.stat_def.icon, size=12),
                                        ft.Text(
                                            f"+{quest.xp_reward} XP",
                                            size=12,
                                            color="#f59e0b",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Icon(
                    ft.Icons.CHEVRON_RIGHT,
                    size=20,
                    color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
                ),
            ],
        )
